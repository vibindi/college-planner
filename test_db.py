import sqlite3

conn = sqlite3.connect('sqlite://main.db')

cur = conn.cursor()

print(cur.execute("select * from users;").fetchall())

conn.commit()

conn.close()