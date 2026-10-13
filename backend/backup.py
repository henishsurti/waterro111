"""Scheduled, consistent backups of the SQLite database.

Runs forever (one backup at start-up, then every BACKUP_EVERY_HOURS) or once with --once.
Uses SQLite's online backup API, so it is safe while the app is running, and verifies each copy.
"""
import os, sqlite3, sys, time
from datetime import datetime
from pathlib import Path

DB=Path(os.getenv('AQUAFLOW_DB','/app/data/aquaflow.db'))
OUT=Path(os.getenv('BACKUP_DIR','/backups'))
EVERY=float(os.getenv('BACKUP_EVERY_HOURS','24'))*3600
KEEP=int(os.getenv('BACKUP_KEEP','30'))

def backup_once()->Path:
    OUT.mkdir(parents=True,exist_ok=True)
    dest=OUT/f"aquaflow-{datetime.now().strftime('%Y%m%d-%H%M%S')}.db"
    src=sqlite3.connect(f'file:{DB}?mode=ro',uri=True); dst=sqlite3.connect(dest)
    try: src.backup(dst)
    finally: dst.close(); src.close()
    chk=sqlite3.connect(dest)
    try: ok=chk.execute('PRAGMA integrity_check').fetchone()[0]
    finally: chk.close()
    if ok!='ok': dest.unlink(missing_ok=True); raise RuntimeError(f'backup failed integrity check: {ok}')
    for old in sorted(OUT.glob('aquaflow-*.db'))[:-KEEP]: old.unlink()
    return dest

if __name__=='__main__':
    once='--once' in sys.argv
    while True:
        try:
            if DB.exists(): print('backup written:',backup_once(),flush=True)
            else: print('database not created yet; skipping',flush=True)
        except Exception as e: print('BACKUP ERROR:',e,flush=True)
        if once: break
        time.sleep(EVERY)
