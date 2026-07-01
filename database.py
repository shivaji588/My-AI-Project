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


# Add role column in existing table
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