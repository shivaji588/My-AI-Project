import sqlite3

conn = sqlite3.connect("database.db")
conn.row_factory = sqlite3.Row
cur = conn.cursor()

print("===== USERS =====")
cur.execute("SELECT * FROM users")
for row in cur.fetchall():
    print(dict(row))

print("\n===== QUIZ RESULTS =====")
cur.execute("SELECT * FROM quiz_results")
for row in cur.fetchall():
    print(dict(row))

conn.close()
