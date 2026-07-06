import sqlite3

conn = sqlite3.connect("database.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fullname TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS user_activity (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    login_date TEXT
)
""")
cursor.execute("""
ALTER TABLE user_activity ADD COLUMN action TEXT;
""")

# role column add (safe)
try:
    cursor.execute("""
    ALTER TABLE users
    ADD COLUMN role TEXT DEFAULT 'student'
    """)
except sqlite3.OperationalError:
    pass

conn.commit()
conn.close()

print("Database Created Successfully!")