import sqlite3
import os

DB_NAME = "database.db"

conn = sqlite3.connect(DB_NAME)
cursor = conn.cursor()

# ---------------- USERS TABLE ----------------
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fullname TEXT,
    email TEXT,
    username TEXT UNIQUE,
    password TEXT,
    role TEXT DEFAULT 'student'
)
""")

# ---------------- PAPERS TABLE ----------------
cursor.execute("""
CREATE TABLE IF NOT EXISTS papers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    year TEXT,
    file_name TEXT
)
""")

# ---------------- USER ACTIVITY TABLE ----------------
cursor.execute("""
CREATE TABLE IF NOT EXISTS user_activity (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    login_date TEXT,
    action TEXT
)
""")
cursor.execute("""
CREATE TABLE IF NOT EXISTS quiz_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    subject TEXT,
    score INTEGER,
    total INTEGER,
    created_at TEXT
)
""")

# # ---------------- SAFE COLUMN CHECK (IMPORTANT) ----------------
# cursor.execute("PRAGMA table_info(user_activity)")
# columns = [col[1] for col in cursor.fetchall()]

# if "action" not in columns:
#     cursor.execute("ALTER TABLE user_activity ADD COLUMN action TEXT")

# ---------------- COMMIT & CLOSE ----------------
conn.commit()
conn.close()

print("✅ Database created successfully!")