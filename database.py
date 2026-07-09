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
        role TEXT DEFAULT 'student'
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

    #chat history page
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chat_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        subject TEXT,
        question TEXT NOT NULL,
        answer TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )   
    """)

    conn.commit()
    conn.close()


if __name__ == "__main__":
    init_db()
    print("✅ Database created successfully!")