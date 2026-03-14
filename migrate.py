import sqlite3
conn = sqlite3.connect('potolki.db')
conn.execute('ALTER TABLE portfolio ADD COLUMN photo TEXT')
conn.commit()
conn.close()
print('Done')
