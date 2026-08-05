import sqlite3
import os


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_NAME = os.path.join(BASE_DIR, "database.db")


def init_db():

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()


    # USERS TABLE
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fullname TEXT,
    email TEXT,
    username TEXT UNIQUE,
    password TEXT,
    role TEXT DEFAULT 'student',
    profile_image TEXT DEFAULT 'default.png',
    notifications INTEGER DEFAULT 1,
    dark_theme INTEGER DEFAULT 0
    )
    """)

    # PAPERS TABLE
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS papers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        year TEXT,
        file_name TEXT
    )
    """)


    # USER ACTIVITY TABLE
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS user_activity (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        login_date TEXT,
        action TEXT
    )
    """)


    # QUIZ RESULTS TABLE
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

    # CHAT HISTORY TABLE
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS chat_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    subject TEXT,
    question TEXT NOT NULL,
    answer TEXT NOT NULL,
    feedback TEXT DEFAULT 'Not Rated',
    chat_id TEXT,
    chat_title TEXT,
    is_reported INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(user_id) REFERENCES users(id)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS user_progress(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        xp INTEGER DEFAULT 0,
        streak INTEGER DEFAULT 0,
        level INTEGER DEFAULT 1
    )
    """)      

    # ================= USERS TABLE MIGRATION =================
    try:
        cursor.execute("""
            ALTER TABLE users
            ADD COLUMN profile_image TEXT DEFAULT 'default.jpg'
        """)
    except sqlite3.OperationalError:
        pass


    try:
        cursor.execute("""
            ALTER TABLE users
            ADD COLUMN notifications INTEGER DEFAULT 1
        """)
    except sqlite3.OperationalError:
        pass


    try:
        cursor.execute("""
            ALTER TABLE users
            ADD COLUMN dark_theme INTEGER DEFAULT 0
        """)
    except sqlite3.OperationalError:
        pass


    # ================= CHAT HISTORY MIGRATION =================

    # Add chat_id column
    try:
        cursor.execute("""
            ALTER TABLE chat_history 
            ADD COLUMN chat_id TEXT
        """)
    except sqlite3.OperationalError:
        pass


    # Add chat_title column
    try:
        cursor.execute("""
            ALTER TABLE chat_history 
            ADD COLUMN chat_title TEXT
        """)
    except sqlite3.OperationalError:
        pass

    # Add report status column
    try:
        cursor.execute("""
            ALTER TABLE chat_history 
            ADD COLUMN is_reported INTEGER DEFAULT 0
        """)
    except sqlite3.OperationalError:
        pass

    conn.commit()
    conn.close()


if __name__ == "__main__":
    init_db()
    print("✅ Database created successfully!")