import sqlite3

conn = sqlite3.connect('data/prospecton.db')
cur = conn.cursor()

cur.execute('SELECT name FROM sqlite_master WHERE type="table"')
tables = cur.fetchall()
print('=== TABELAS NO BANCO ===')
for t in tables:
    name = t[0]
    count = cur.execute(f'SELECT COUNT(*) FROM "{name}"').fetchone()[0]
    print(f'  {name}: {count} registros')

conn.close()
