from database import init_db
import os
import sqlite3
import datetime
from groq import Groq
from dotenv import load_dotenv
from tkinter import INSERT
from flask import Flask, jsonify, render_template, request, redirect, send_from_directory, url_for, flash, session
from sqlalchemy import values
from werkzeug.security import generate_password_hash, check_password_hash

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

app = Flask(__name__)
app.secret_key = "academic_copilot"

#Groq Client
load_dotenv()

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "database.db")

init_db()  # Initialize the database on app startup

# ---------------- HOME ----------------

@app.route("/")
def home():
    return render_template("home.html")


@app.route("/index")
def index():
    return render_template("index.html")


@app.route("/about")
def about():
    return render_template("about.html")

#-----------ADMIN PANAL--------------
@app.route("/admin")
def admin():

    if session.get("role") != "admin":
        flash("Access Denied! Admin only.", "danger")
        return redirect(url_for("dashboard"))

    return render_template("admin.html")

#===============manage users========================
@app.route("/manage_users")
def manage_users():

    if session.get("role") != "admin":
        return redirect("/")


    conn = sqlite3.connect("database.db")
    cur = conn.cursor()

    cur.execute("""
        SELECT id, fullname, email, username, role
        FROM users
    """)

    users = cur.fetchall()

    conn.close()


    return render_template(
        "manage_users.html",
        users=users
    )

#=============role change route=================
@app.route("/change_role/<int:id>")
def change_role(id):

    conn = sqlite3.connect("database.db")
    cur = conn.cursor()


    cur.execute("""
    UPDATE users
    SET role =
    CASE
        WHEN role='student' THEN 'admin'
        ELSE 'student'
    END
    WHERE id=?
    """,(id,))


    conn.commit()
    conn.close()


    return redirect("/manage_users")

#=================delete user route========================
@app.route("/delete_user/<int:id>")
def delete_user(id):

    conn = sqlite3.connect("database.db")
    cur = conn.cursor()


    cur.execute(
        "DELETE FROM users WHERE id=?",
        (id,)
    )


    conn.commit()
    conn.close()


    return redirect("/manage_users")

#=================user details route========================
@app.route("/user_details/<int:id>")
def user_details(id):

    if session.get("role") != "admin":
        return redirect("/")


    conn = sqlite3.connect("database.db")
    cur = conn.cursor()


    cur.execute("""
    SELECT id, fullname, email, username, role
    FROM users
    WHERE id=?
    """,(id,))


    user = cur.fetchone()

    conn.close()


    return render_template(
        "user_details.html",
        user=user
    )

#----------------NOTES----------------
@app.route("/notes")
def notes():

    if "user_id" not in session:
        flash("Please login first to access this page.", "warning")
        return redirect(url_for("login"))

    import datetime

    conn = sqlite3.connect("database.db")
    cur = conn.cursor()

    today = datetime.date.today().isoformat()

    cur.execute("""
        INSERT INTO user_activity(user_id, login_date, action)
        VALUES (?, ?, ?)
    """,
    (session["user_id"], today, "Notes"))

    conn.commit()
    conn.close()

    return render_template("notes.html")

#--------------notes_view--------------
@app.route("/notes/<subject>")
def show_notes(subject):

    notes_data = {
        "python": {
            "title": "🐍 Python Notes",
            "notes": ["Variables", "Loops", "Functions", "OOP"]
        },
        "java": {
            "title": "☕ Java Notes",
            "notes": ["Classes", "Objects", "Inheritance", "Polymorphism"]
        },
        "web": {
            "title": "🌐 Web Notes",
            "notes": ["HTML", "CSS", "Flask Routing"]
        },
        "dbms": {
            "title": "🗄 DBMS Notes",
            "notes": ["SQL", "Joins", "Normalization"]
        },
        "ai": {
            "title": "🤖 AI Notes",
            "notes": ["Search Algorithms", "Machine Learning Basics"]
        }
    }

    data = notes_data.get(subject)

    if data:
        return render_template("notes_view.html", data=data)
    else:
        return "Notes not found", 404

#--------------papers--------------------
@app.route("/papers")
def papers():   
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM papers")
    papers_list = cursor.fetchall()
    conn.close()

    return render_template("papers.html", papers=papers_list)   

#========================paper add================================
@app.route("/add_paper", methods=["GET","POST"])
def add_paper():

    if request.method == "POST":

        title = request.form["title"]
        year = request.form["year"]
        file_name = request.form["file_name"]


        conn = sqlite3.connect("database.db")
        cur = conn.cursor()


        cur.execute("""
        INSERT INTO papers(title, year, file_name)
        VALUES(?,?,?)
        """,
        (title, year, file_name))


        conn.commit()
        conn.close()


        flash("Paper Added Successfully","success")

        return redirect("/papers")


    return render_template("add_paper.html")   

#========================paper manage================================ 
@app.route("/manage_papers")
def manage_papers():

    conn = sqlite3.connect("database.db")
    cur = conn.cursor()

    cur.execute("SELECT * FROM papers")

    papers = cur.fetchall()

    conn.close()

    return render_template(
        "manage_papers.html",
        papers=papers
    )  
# ---------------- SUBJECTS----------------
@app.route("/subjects")
def subjects():
    return render_template("subjects.html")

#---------------- SUBJECT DETAILS ----------------
@app.route("/subject/<name>")
def subject_page(name):

    subjects_data = {
        "python": {
            "title": "🐍 Python",
            "desc": "Programming Fundamentals",
            "notes": ["Variables", "Loops", "Functions", "OOP"]
        },

        "java": {
            "title": "☕ Java",
            "desc": "Object Oriented Programming",
            "notes": ["Classes", "Objects", "Inheritance", "Polymorphism"]
        },

        "web": {
            "title": "🌐 Web Development",
            "desc": "HTML, CSS, Flask",
            "notes": ["HTML Basics", "CSS Styling", "Flask Routing"]
        },

        "dbms": {
            "title": "🗄️ DBMS",
            "desc": "Database Management System",
            "notes": ["SQL", "Joins", "Normalization"]
        },

        "ai": {
            "title": "🤖 AI",
            "desc": "Artificial Intelligence",
            "notes": ["Search Algorithms", "Machine Learning Basics"]
        },

        "datascience": {
            "title": "📊 Data Science",
            "desc": "Data Analysis & ML",
            "notes": ["Pandas", "Numpy", "Visualization"]
        }
    }

    subject = subjects_data.get(name)

    if subject:
        return render_template("subject.html",subject=subject,key=name)
    else:
        return "Subject not found", 404

# ---------------- CHATBOT ask ai----------------

def ask_ai(question, subject):

    question = question.lower()


    # Python

    if subject == "Python":

        if "list" in question:

            return """
📘 Python - List

Definition:
Python List is an ordered and mutable collection used to store multiple values.

✨ Features:
• Ordered collection
• Allows duplicate values
• Mutable (can be changed)
• Supports different data types

Example:

numbers = [10,20,30]

Used when we need to store multiple items together.
"""


        elif "function" in question:

            return """
📘 Python - Function

A function is a reusable block of code that performs a specific task.

✨ Advantages:
• Code reusability
• Easy debugging
• Reduces code repetition

Example:

def hello():
    print("Hello Student")
"""


        elif "python" in question:

            return """
🐍 Python Programming

Python is a high-level programming language known for simple syntax and powerful libraries.

📚 Used in:
• Web Development
• Data Science
• AI & Machine Learning
• Automation
"""


        else:

            return """
🤖 AI Academic Assistant

Python Topics Available:

1. Variables
2. Data Types
3. List
4. Tuple
5. Function
6. OOP Concepts

Ask your topic name to learn more.
"""



    # Java

    elif subject == "Java":

        return """
☕ Java Programming

Java is an object-oriented programming language.

Key Concepts:

• Class
• Object
• Inheritance
• Polymorphism
• Exception Handling

Ask any Java topic for explanation.
"""



    # DBMS

    elif subject == "DBMS":

        return """
🗄️ DBMS

Database Management System is software used to store,
manage and retrieve data.

Important Topics:

• SQL
• Primary Key
• Foreign Key
• Normalization
• ER Diagram
"""



    # DCN

    elif subject == "DCN":

        return """
🌐 Data Communication and Networks

DCN deals with communication between computers.

Important Topics:

• OSI Model
• TCP/IP
• Switching
• Transmission Media
• Network Devices
"""



    # Default

    else:

        return """
🤖 Welcome to AI Academic Copilot

I can help you with:

📘 Python
☕ Java
🗄️ DBMS
🌐 DCN
⚙️ Operating System

Select a subject and ask your doubt.
"""
#---------------AI Roadmap Function---------------------
def generate_roadmap(subject, goal, days, level):

    prompt = f"""
You are an expert academic mentor.

Create a detailed {days}-day study roadmap.

Subject: {subject}
Level: {level}
Goal: {goal}

For each day provide:

📘 Topics to Study
💻 Practice Tasks
📝 Revision Tips
💡 Motivation

Make the roadmap clear, professional, and easy for students to follow.
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response.choices[0].message.content

#-----------------------Roadmap-------------------------------
@app.route("/roadmap", methods=["GET", "POST"])
def roadmap():

    roadmap = ""

    if request.method == "POST":

        subject = request.form["subject"]
        goal = request.form["goal"]
        days = request.form["days"]
        level = request.form["level"]

        roadmap = generate_roadmap(
            subject,
            goal,
            days,
            level
        )

    return render_template(
        "roadmap.html",
        roadmap=roadmap
    )

#========================== CHATBOT =========================
@app.route("/chatbot", methods=["GET", "POST"])
def chatbot():

    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()


    user_id = session.get("user_id")


    if not user_id:
        return redirect(url_for("login"))



    # AJAX POST

    if request.method == "POST":


        data = request.get_json()


        subject = data.get("subject")

        question = data.get("question")



        # AI response generate

        answer = ask_ai(question, subject)



        # Save chat history

        cur.execute("""
        INSERT INTO chat_history
        (user_id, subject, question, answer)
        VALUES (?, ?, ?, ?)
        """,
        (
            user_id,
            subject,
            question,
            answer
        ))


        conn.commit()


        conn.close()



        return jsonify({

            "answer": answer

        })




    # GET request

    cur.execute("""
    SELECT *
    FROM chat_history
    WHERE user_id=?
    ORDER BY id ASC
    """,
    (user_id,))


    chats = cur.fetchall()


    conn.close()


    return render_template(
        "chatbot.html",
        chats=chats
    )
#==========clear chat history=========
@app.route("/clear_chat")
# @login_required
def clear_chat():

    conn = sqlite3.connect("database.db")
    cur = conn.cursor()

    cur.execute("""
    DELETE FROM chat_history
    WHERE user_id=?
    """,(session["user_id"],))

    conn.commit()
    conn.close()

    return redirect(url_for("chatbot"))

# ---------------- QUIZ ----------------

@app.route("/quiz")
def quiz():

    if "user_id" not in session:
        flash("Please login first to access this page.", "warning")
        return redirect(url_for("login"))

    return render_template("quiz.html")


# ---------------- QUIZ datetime ----------------
def save_score(subject, score, total):
    import datetime

    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO quiz_results(user_id, subject, score, total, created_at)
        VALUES (?, ?, ?, ?, ?)
    """, (
        session["user_id"],
        subject,
        score,
        total,
        datetime.date.today().isoformat()
    ))

    conn.commit()
    conn.close()

# --------------PYTHON QUIZ----------------
@app.route("/python_quiz")
def python_quiz():

    if "user_id" not in session:
        return redirect(url_for("login"))

    return render_template("python_quiz.html")

@app.route("/submit_python_quiz", methods=["POST"])
def submit_python_quiz():
    
    if "user_id" not in session:
        return redirect(url_for("login"))

    score = 0

    answers = {
        "q1": "Guido van Rossum",
        "q2": "Programming Language",
        "q3": ".py",
        "q4": "Interpreted",
        "q5": "def",
        "q6": "Object Oriented",
        "q7": "1991",
        "q8": "Open Source",
        "q9": "Block of code",
        "q10": "AI & ML"
    }

    for q, correct in answers.items():
        if request.form.get(q) == correct:
            score += 1

    save_score("Python", score, 10)
    return render_template("result.html", score=score, total=10)


# ---------------- JAVA QUIZ ----------------

@app.route("/java_quiz")
def java_quiz():

    if "user_id" not in session:
        return redirect(url_for("login"))

    return render_template("java_quiz.html")


@app.route("/submit_java_quiz", methods=["POST"])
def submit_java_quiz():

    if "user_id" not in session:
        return redirect(url_for("login"))

    score = 0

    answers = {
        "q1": "James Gosling",
        "q2": "new",
        "q3": "Object Oriented",
        "q4": ".java",
        "q5": "Java Virtual Machine",
        "q6": "Independent",
        "q7": "Pointers",
        "q8": "Multithreading",
        "q9": "0",
        "q10": "Sun Microsystems"
    }

    for q, correct in answers.items():
        if request.form.get(q) == correct:
            score += 1

    save_score("Java", score, 10)
    return render_template("result.html", score=score, total=10)


# ---------------- DBMS QUIZ ----------------

@app.route("/dbms_quiz")
def dbms_quiz():

    if "user_id" not in session:
        return redirect(url_for("login"))

    return render_template("dbms_quiz.html")


@app.route("/submit_dbms_quiz", methods=["POST"])
def submit_dbms_quiz():

    if "user_id" not in session:
        return redirect(url_for("login"))

    score = 0

    answers = {
        "q1": "Database Management System",
        "q2": "Uniquely identify record",
        "q3": "Structured Query Language",
        "q4": "MySQL",
        "q5": "Link tables",
        "q6": "Software",
        "q7": "MongoDB",
        "q8": "Remove redundancy",
        "q9": "SELECT",
        "q10": "Manage data"
    }

    for q, correct in answers.items():
        if request.form.get(q) == correct:
            score += 1

    save_score("DBMS", score, 10)
    return render_template("result.html", score=score, total=10)


# ---------------- AI QUIZ ----------------

@app.route("/ai_quiz")
def ai_quiz():

    if "user_id" not in session:
        return redirect(url_for("login"))

    return render_template("ai_quiz.html")


@app.route("/submit_ai_quiz", methods=["POST"])
def submit_ai_quiz():

    if "user_id" not in session:
        return redirect(url_for("login"))

    score = 0

    answers = {
        "q1": "Artificial Intelligence",
        "q2": "All fields",
        "q3": "AI",
        "q4": "ChatGPT",
        "q5": "Decision making",
        "q6": "Algorithms",
        "q7": "Data",
        "q8": "Technology",
        "q9": "AI",
        "q10": "Smart System"
    }

    for q, correct in answers.items():
        if request.form.get(q) == correct:
            score += 1

    save_score("AI", score, 10)
    return render_template("result.html", score=score, total=10)

#----------------------LEADERBOARD-----------

from flask import request,session,render_template
from datetime import date, timedelta

@app.route("/leaderboard")
def leaderboard():

    conn = get_db()
    cur = conn.cursor()

    subject = request.args.get("subject", "All")
    period = request.args.get("period", "all")

    query = """
        SELECT users.username,
               quiz_results.subject,
               quiz_results.score,
               quiz_results.total,
               quiz_results.created_at
        FROM quiz_results
        JOIN users
        ON quiz_results.user_id = users.id
    """

    conditions = []
    params = []

    if subject != "All":
        conditions.append("quiz_results.subject=?")
        params.append(subject)

    if period == "today":
        conditions.append("created_at=?")
        params.append(str(date.today()))

    elif period == "week":
        week = date.today() - timedelta(days=7)
        conditions.append("created_at>=?")
        params.append(str(week))

    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    query += " ORDER BY score DESC"

    cur.execute(query, params)
    data = cur.fetchall()

    # Logged-in username
    current_user = session.get("username")

    # Find current user's rank
    your_rank = None

    for i, row in enumerate(data, start=1):
        if row["username"] == current_user:
            your_rank = i
            break

    return render_template(
        "leaderboard.html",
        data=data,
        selected_subject=subject,
        selected_period=period,
        current_user=current_user,
        your_rank=your_rank
    )
# ---------------- REGISTER ----------------
# @app.route("/register", methods=["GET", "POST"])
# def register():

#     if request.method == "POST":

#         fullname = request.form["fullname"]
#         email = request.form["email"]
#         username = request.form["username"]
#         password = request.form["password"]

#         conn = sqlite3.connect("database.db")
#         cur = conn.cursor()

#         try:

#             cur.execute("""
#             INSERT INTO users(fullname,email,username,password)
#             VALUES(?,?,?,?)
#             """,(fullname,email,username,password))

#             conn.commit()

#             flash("Account Created Successfully ✅","success")

#             return redirect(url_for("login"))

#         except sqlite3.IntegrityError:

#             flash("Email or Username already exists","danger")

#         finally:

#             conn.close()

#     return render_template("register.html")

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        fullname = request.form["fullname"]
        email = request.form["email"]
        username = request.form["username"]

        # 🔥 FIX HERE
        password = generate_password_hash(request.form["password"])

        conn = sqlite3.connect("database.db")
        cur = conn.cursor()

        try:
            cur.execute("""
            INSERT INTO users(fullname,email,username,password)
            VALUES(?,?,?,?)
            """,(fullname,email,username,password))

            conn.commit()

            flash("Account Created Successfully ✅","success")
            return redirect(url_for("login"))

        except sqlite3.IntegrityError:
            flash("Email or Username already exists","danger")

        finally:
            conn.close()

    return render_template("register.html")


# ---------------- LOGIN ----------------

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect("database.db")
        cur = conn.cursor()

        cur.execute("SELECT * FROM users WHERE username=?", (username,))
        user = cur.fetchone()

        conn.close()

        if user and check_password_hash(user[4], password):

            # ✅ SESSION SET
            session["user_id"] = user[0]
            session["username"] = user[3]
            session["role"] = user[5]   # 🔥 THIS IS MAIN

            # 🔥 LOGIN TRACKING
            import datetime
            today = datetime.date.today().isoformat()

            conn2 = sqlite3.connect("database.db")
            cur2 = conn2.cursor()

            cur2.execute("""
                INSERT INTO user_activity (user_id, login_date, action)
                VALUES (?, ?, ?)
            """, (user[0], today, "Login"))

            conn2.commit()
            conn2.close()

            flash("Login Successful", "success")
            return redirect(url_for("dashboard"))

        else:
            flash("Invalid Username or Password", "danger")

    return render_template("login.html")

# ---------------- DASHBOARD ----------------

@app.route("/dashboard")
def dashboard():

    conn = sqlite3.connect("database.db")
    cur = conn.cursor()

    import datetime

    # ================= WEEKLY ACTIVITY GRAPH =================

    dates = []
    values = []

    for i in range(6, -1, -1):

        day = (datetime.date.today() - datetime.timedelta(days=i)).isoformat()

        dates.append(day)

        cur.execute("""
            SELECT COUNT(DISTINCT user_id)
            FROM user_activity
            WHERE login_date=?
        """, (day,))

        count = cur.fetchone()[0]

        values.append(count)



    # ================= TOTAL USERS =================

    cur.execute("SELECT COUNT(*) FROM users")

    total_users = cur.fetchone()[0]



    # ================= DAU =================

    today = datetime.date.today().isoformat()


    cur.execute("""
        SELECT COUNT(DISTINCT user_id)
        FROM user_activity
        WHERE login_date=?
    """, (today,))


    dau = cur.fetchone()[0]



    # ================= WAU =================

    cur.execute("""
        SELECT COUNT(DISTINCT user_id)
        FROM user_activity
        WHERE login_date >= date('now','-7 day')
    """)


    wau = cur.fetchone()[0]



    # ================= TOTAL LOGINS =================

    cur.execute("""
        SELECT COUNT(*)
        FROM user_activity
    """)


    total_logins = cur.fetchone()[0]



    # ================= TODAY ACTIVITY BAR GRAPH =================


    cur.execute("""
        SELECT action, COUNT(*)
        FROM user_activity
        WHERE login_date=?
        GROUP BY action
    """,(today,))


    today_activity = cur.fetchall()


    today_labels = []
    today_values = []


    for row in today_activity:

        today_labels.append(row[0])

        today_values.append(row[1])



    # ================= RECENT ACTIVITY =================


    cur.execute("""
        SELECT login_date, action
        FROM user_activity
        ORDER BY id DESC
        LIMIT 10
    """)


    timeline = cur.fetchall()



    conn.close()



    return render_template(
        "dashboard.html",

        total_users=total_users,

        dau=dau,

        wau=wau,

        total_logins=total_logins,


        # Weekly Graph
        labels=dates,

        values=values,


        # Today's Graph
        today_labels=today_labels,

        today_values=today_values,


        timeline=timeline
    )
# ---------------- PROFILE ----------------
@app.route("/profile")
def profile():

    if "user_id" not in session:
        return redirect("/login")


    conn = sqlite3.connect("database.db")
    cur = conn.cursor()


    # User Details
    cur.execute("""
    SELECT id, fullname, email, username, role
    FROM users
    WHERE id=?
    """,(session["user_id"],))

    user = cur.fetchone()



    # Quiz Completed Count
    cur.execute("""
    SELECT COUNT(*)
    FROM quiz_results
    WHERE user_id=?
    """,(session["user_id"],))

    quiz_count = cur.fetchone()[0]



    # Notes Count (जर notes table असेल तर)
    # नाही असेल तर 0 ठेवू
    notes_count = 0

        # Total Login Days
    cur.execute("""
    SELECT COUNT(DISTINCT login_date)
    FROM user_activity
    WHERE user_id=?
    """,(session["user_id"],))

    login_days = cur.fetchone()[0]


    # Learning Progress Calculation

    total_activity = quiz_count + login_days

    target = 50   # maximum expected activity

    progress = int(
        (total_activity / target) * 100
    )


    if progress > 100:
        progress = 100

    # Login Streak
    cur.execute("""
    SELECT COUNT(DISTINCT login_date)
    FROM user_activity
    WHERE user_id=?
    """,(session["user_id"],))

    streak = cur.fetchone()[0]

    # Last Active Date
    cur.execute("""
    SELECT login_date
    FROM user_activity
    WHERE user_id=?
    ORDER BY id DESC
    LIMIT 1
    """,(session["user_id"],))

    last_active = cur.fetchone()

    if last_active:
        last_active = last_active[0]
    else:
        last_active = "No Activity"

    conn.close()

    return render_template(
        "profile.html",
        user=user,
        quiz_count=quiz_count,
        streak=streak,
        notes_count=notes_count,
        progress=progress,
        last_active=last_active
    )
# ---------------- LOGOUT ----------------
@app.route("/logout")
def logout():

    session.clear()

    flash("Logged Out Successfully","success")

    return redirect(url_for("login"))

# ---------------- MAIN ----------------

if __name__ == "__main__":
    app.run(debug=True)
