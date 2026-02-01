import sqlite3

conn = sqlite3.connect("appointments.db")
cur = conn.cursor()

rows = cur.execute("SELECT * FROM appointments").fetchall()

for row in rows:
    print(row)

conn.close()
