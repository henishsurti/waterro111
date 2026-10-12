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
