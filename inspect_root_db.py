import sqlite3
from pathlib import Path

path = Path('voice_agent.db')
print('db path', path.resolve())
conn = sqlite3.connect(path)
cur = conn.cursor()
try:
    cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
    print('tables', cur.fetchall())
    cur.execute("SELECT id, name, phone, preferred_language FROM patients")
    print('patients', cur.fetchall())
    cur.execute("SELECT id, name, specialty, active FROM doctors")
    print('doctors', cur.fetchall())
except Exception as e:
    print('error', e)
finally:
    conn.close()
