import sqlite3

conn = sqlite3.connect('college-planner.db')

with open('schema.sql') as file:
  conn.executescript(file.read())

cur = conn.cursor()

"""
cur.execute("insert into users (name, email, curr_semester_id) VALUES (?, ?, ?)",
            ('Testing', 'test@purdue.edu', 1))
cur.execute("insert into semesters (user_id, season, year) VALUES (?, ?, ?)",
            (1, 'Fall', '2023'))
conn.commit()
"""

conn.close()