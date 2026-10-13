import os,sys,tempfile
from pathlib import Path
# Tests are intended to run with pytest and the backend dependencies installed.
import pytest
from fastapi.testclient import TestClient
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import app

@pytest.fixture()
def client(tmp_path,monkeypatch):
    app.DB_PATH=tmp_path/'test.db'
    app.SESSIONS.clear()
    app.init_db()
    with app.conn() as c:
        c.execute("INSERT INTO users(id,username,password_hash,role,name,status) VALUES(?,?,?,?,?,?)",('u1','admin',app.hash_password('admin123'),'admin','Admin','Active'))
    with TestClient(app.app) as c: yield c

def test_health(client):
    r=client.get('/api/health'); assert r.status_code==200 and r.json()['database'] is True

def test_login_and_me(client):
    r=client.post('/api/auth/login',json={'username':'admin','password':'admin123','role':'admin'}); assert r.status_code==200
    assert client.get('/api/auth/me').json()['user']['username']=='admin'

def test_bootstrap_requires_auth(client):
    assert client.get('/api/bootstrap').status_code==401


def _login(client):
    r=client.post('/api/auth/login',json={'username':'admin','password':'admin123','role':'admin'}); assert r.status_code==200
    return {'X-CSRF-Token':r.json()['csrf_token']}

def test_changes_revision_moves_on_sync(client):
    h=_login(client)
    rev0=client.get('/api/changes').json()['revision']
    r=client.post('/api/sync',json={'data':{'customers':[],'users':[{'id':'u1','username':'admin','role':'admin','name':'Admin'}]}},headers=h)
    assert r.status_code==200
    assert r.json()['revision']>rev0
    assert client.get('/api/changes').json()['revision']==r.json()['revision']
    assert client.get('/api/bootstrap').json()['revision']==r.json()['revision']

def test_stale_sync_is_rejected(client):
    h=_login(client)
    data={'users':[{'id':'u1','username':'admin','role':'admin','name':'Admin'}]}
    first=client.post('/api/sync',json={'data':data},headers=h).json()['revision']
    # someone else saves in the meantime
    client.post('/api/sync',json={'data':data},headers=h)
    stale=client.post('/api/sync',json={'data':data,'base_revision':first},headers=h)
    assert stale.status_code==409
    fresh=client.get('/api/changes').json()['revision']
    assert client.post('/api/sync',json={'data':data,'base_revision':fresh},headers=h).status_code==200

def test_database_and_code_are_not_served(client):
    for path in ('/aquaflow.db','/backend/app.py','/database.sql','/test.db'):
        assert client.get(path).status_code==404
    assert client.get('/').status_code==200

def test_bootstrap_returns_typed_settings(client):
    h=_login(client)
    with app.conn() as c:
        c.executemany('INSERT OR REPLACE INTO settings(key,value) VALUES(?,?)',[('amcReminderDays','60,30,15,7,1'),('serviceReminderDays','[1,2,3]'),('pushEnabled','true')])
    st=client.get('/api/bootstrap').json()['data']['settings']
    assert st['amcReminderDays']==[60,30,15,7,1] and st['serviceReminderDays']==[1,2,3] and st['pushEnabled'] is True
    # and they survive a browser sync round-trip as lists
    data=client.get('/api/bootstrap').json()['data']
    assert client.post('/api/sync',json={'data':data},headers=h).status_code==200
    assert client.get('/api/bootstrap').json()['data']['settings']['amcReminderDays']==[60,30,15,7,1]


def test_edited_customer_type_is_saved(client):
    # The browser edits `type`; a stale `customerType` from the last load must not win.
    h=_login(client)
    users=[{'id':'u1','username':'admin','role':'admin','name':'Admin'}]
    cust={'id':'c1','code':'CUS-1','name':'Test Co','mobile':'9000000000','customerType':'Residential','type':'Hospital'}
    r=client.post('/api/sync',json={'data':{'customers':[cust],'users':users}},headers=h); assert r.status_code==200
    got=client.get('/api/bootstrap').json()['data']['customers'][0]
    assert got['customerType']=='Hospital'


# ---- production hardening -------------------------------------------------

def test_first_admin_is_created_from_environment(tmp_path,monkeypatch):
    monkeypatch.setattr(app,'DB_PATH',tmp_path/'fresh.db'); monkeypatch.setattr(app,'ADMIN_USER','owner'); monkeypatch.setattr(app,'ADMIN_PASSWORD','a-long-password-1')
    monkeypatch.setattr(app,'PRODUCTION',True); app.SESSIONS.clear(); app.init_db()
    with TestClient(app.app) as c:
        assert c.post('/api/auth/login',json={'username':'owner','password':'wrong-password','role':'admin'}).status_code==401
        assert c.post('/api/auth/login',json={'username':'owner','password':'a-long-password-1','role':'admin'}).status_code==200
    app.init_db()  # a second start must not create a second admin
    with app.conn() as c: assert c.execute('SELECT COUNT(*) FROM users').fetchone()[0]==1

def test_production_refuses_to_start_without_admin_password(tmp_path,monkeypatch):
    monkeypatch.setattr(app,'DB_PATH',tmp_path/'fresh2.db'); monkeypatch.setattr(app,'ADMIN_PASSWORD',''); monkeypatch.setattr(app,'PRODUCTION',True)
    with pytest.raises(RuntimeError): app.init_db()
    monkeypatch.setattr(app,'ADMIN_PASSWORD','short')
    with pytest.raises(RuntimeError): app.init_db()

def test_login_is_rate_limited(client,monkeypatch):
    app.FAILS.clear(); monkeypatch.setattr(app,'LOGIN_MAX_FAILS',3)
    for _ in range(3): assert client.post('/api/auth/login',json={'username':'admin','password':'nope','role':'admin'}).status_code==401
    assert client.post('/api/auth/login',json={'username':'admin','password':'admin123','role':'admin'}).status_code==429
    app.FAILS.clear()

def _svc(i,tech,status='Assigned'):
    return {'id':i,'customerId':'c1','technicianId':tech,'type':'Repair','status':status,'priority':'Normal','paymentStatus':'Pending','partsCost':0,'laborCost':0,'additionalCharges':0,'discount':0,'totalAmount':0}

def test_technician_can_only_update_their_own_jobs(client):
    h=_login(client)
    base={'users':[{'id':'u1','username':'admin','role':'admin','name':'Admin'},{'id':'u2','username':'tech1','role':'technician','technicianId':'t1','name':'Tech One','password':'techpass-123'}],
          'technicians':[{'id':'t1','name':'Tech One'},{'id':'t2','name':'Tech Two'}],
          'customers':[{'id':'c1','code':'CUS-1','name':'Original Name','mobile':'9000000000'}],
          'services':[_svc('s1','t1'),_svc('s2','t2')]}
    assert client.post('/api/sync',json={'data':base},headers=h).status_code==200
    client.post('/api/auth/logout')
    r=client.post('/api/auth/login',json={'username':'tech1','password':'techpass-123','role':'technician'}); assert r.status_code==200
    th={'X-CSRF-Token':r.json()['csrf_token']}
    boot=client.get('/api/bootstrap').json(); data=boot['data']
    for s in data['services']:
        s['status']='Completed'; s['workPerformed']='tampered'      # s1 is theirs, s2 is not
    data['customers'][0]['name']='HACKED'                           # not a technician's data
    data['users'].append({'id':'u9','username':'evil','role':'admin','name':'Evil','password':'evil-pass-123'})
    r=client.post('/api/sync',json={'data':data,'base_revision':boot['revision']},headers=th); assert r.status_code==200
    out=client.get('/api/bootstrap').json()['data']
    svc={s['id']:s for s in out['services']}
    assert svc['s1']['status']=='Completed' and svc['s1']['workPerformed']=='tampered'
    assert svc['s2']['status']=='Assigned' and not svc['s2'].get('workPerformed')
    assert out['customers'][0]['name']=='Original Name'
    assert 'evil' not in [u['username'] for u in out['users']]
