import os
import sqlite3
import datetime
from tkinter import INSERT
from flask import Flask, render_template, request, redirect, url_for, flash, session
from sqlalchemy import values
from werkzeug.security import generate_password_hash, check_password_hash


app = Flask(__name__)
app.secret_key = "academic_copilot"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "database.db")
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


@app.route("/notes")
def notes():
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
    return render_template("papers.html")


# ---------------- SUBJECTS----------------
@app.route("/subjects")
def subjects():
    return render_template("subjects.html")

#---------------- SUBJECT DETAILS ----------------
from flask import render_template

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

# ---------------- CHATBOT ----------------

@app.route("/chatbot", methods=["GET", "POST"])
def chatbot():

    answer = ""

    if request.method == "POST":

        question = request.form["question"].lower()

        if "hello" in question or "hi" in question:
            answer = "Hello 👋 I am your AI Academic Copilot."

        elif "flask" in question:
            answer = "Flask is a Python framework used to create web applications."

        elif "html" in question:
            answer = "HTML is used to create the structure of web pages."

        elif "css" in question:
            answer = "CSS is used for designing and styling web pages."

        elif "python project" in question:
            answer = "Python project ideas: Chatbot, Quiz App, Student Portal, AI Assistant."

        elif "ai" in question or "artificial intelligence" in question:
            answer = "AI is a technology that enables machines to learn and solve problems."

        elif "python" in question:
            answer = "Python is a high-level programming language."

        elif "java" in question:
            answer = "Java is an object-oriented programming language."

        elif "dbms" in question or "database" in question:
            answer = "DBMS is used to store and manage data."

        elif "thank" in question:
            answer = "You're welcome 😊 Keep learning!"

        else:
            answer = "Sorry, I don't know. Try another academic question."

    return render_template("chatbot.html", answer=answer)


# ---------------- QUIZ ----------------
@app.route("/quiz")
def quiz():
    '''if 'username' not in session:
        flash("Please Login First","warning")
        return redirect(url_for('login'))'''
    return render_template("quiz.html")

@app.route("/python_quiz")
def python_quiz():
    return render_template("python_quiz.html")

@app.route("/submit_python_quiz", methods=["POST"])
def submit_python_quiz():

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

    for q, correct_answer in answers.items():
        if request.form.get(q) == correct_answer:
            score += 1

    return render_template(
        "result.html",
        score=score,
        total=10
    )

@app.route("/java_quiz")
def java_quiz():
    return render_template("java_quiz.html")

@app.route("/submit_java_quiz", methods=["POST"])
def submit_java_quiz():

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

    return render_template("result.html", score=score, total=10)

@app.route("/dbms_quiz")
def dbms_quiz():
    return render_template("dbms_quiz.html")

@app.route("/submit_dbms_quiz", methods=["POST"])
def submit_dbms_quiz():

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

    for q, correct_answer in answers.items():
        if request.form.get(q) == correct_answer:
            score += 1

    return render_template(
        "result.html",
        score=score,
        total=10
    )

@app.route("/ai_quiz")
def ai_quiz():
    return render_template("ai_quiz.html")

@app.route("/submit_ai_quiz", methods=["POST"])
def submit_ai_quiz():

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

    for q, correct_answer in answers.items():
        if request.form.get(q) == correct_answer:
            score += 1

    return render_template(
        "result.html",
        score=score,
        total=10
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
# @app.route("/login", methods=["GET","POST"])
# def login():

#     if request.method=="POST":

#         username=request.form["username"]
#         password=request.form["password"]

#         conn=sqlite3.connect("database.db")
#         cur=conn.cursor()

#         cur.execute("SELECT * FROM users WHERE username=?",(username,))
#         user=cur.fetchone()

#         conn.close()

#         if user and check_password_hash(user[4],password):

#             session["user_id"]=user[0]
#             session["username"]=user[3]

#             flash("Login Successful","success")

#             return redirect(url_for("dashboard"))

#         flash("Invalid Username or Password","danger")

#     return render_template("login.html")
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

            # 🔥 DAU TRACKING (ADD THIS)
            import datetime
            today = datetime.date.today().isoformat()

            conn2 = sqlite3.connect("database.db")
            cur2 = conn2.cursor()

            cur.execute("""
                INSERT INTO user_activity (user_id, login_date)
                VALUES (?, ?)
            """, (user[0], today))

            cur.execute("""
            INSERT INTO user_activity(user_id, login_date, action)
            VALUES(?, ?, ?)
            """, (user_id, today, "Login"))

            conn2.commit()
            conn2.close()

            flash("Login Successful","success")
            return redirect(url_for("dashboard"))

        else:
            flash("Invalid Username or Password","danger")

    return render_template("login.html")

# ---------------- DASHBOARD ----------------
# @app.route("/dashboard")
# def dashboard():

#     if "user_id" not in session:

#         flash("Please Login First","warning")

#         return redirect(url_for("login"))

#     return render_template(
#         "dashboard.html",
#         user=session["username"]
#     )


@app.route("/dashboard")
def dashboard():

    conn = sqlite3.connect("database.db")
    cur = conn.cursor()

    import datetime

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

    # 👥 Total Users
    cur.execute("SELECT COUNT(*) FROM users")
    total_users = cur.fetchone()[0]

    # 📊 DAU (today)
    today = datetime.date.today().isoformat()
    cur.execute("""
        SELECT COUNT(DISTINCT user_id)
        FROM user_activity
        WHERE login_date=?
    """, (today,))
    dau = cur.fetchone()[0]

    # 📅 WAU
    cur.execute("""
        SELECT COUNT(DISTINCT user_id)
        FROM user_activity
        WHERE login_date >= date('now','-7 day')
    """)
    wau = cur.fetchone()[0]

    # 🔥 Total logins
    cur.execute("SELECT COUNT(*) FROM user_activity")
    total_logins = cur.fetchone()[0]

    conn.close()

    return render_template(
        "dashboard.html",
        total_users=total_users,
        dau=dau,
        wau=wau,
        total_logins=total_logins,
        labels=dates,
        values=values
    )
# ---------------- PROFILE ----------------
@app.route("/profile")
def profile():

    if "user_id" not in session:
        return redirect(url_for("login"))

    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    cur.execute(
        "SELECT fullname,email,username FROM users WHERE id=?",
        (session["user_id"],)
    )

    user = cur.fetchone()

    conn.close()

    return render_template("profile.html", user=user)

# ---------------- LOGOUT ----------------
@app.route("/logout")
def logout():

    session.clear()

    flash("Logged Out Successfully","success")

    return redirect(url_for("login"))

# ---------------- MAIN ----------------

if __name__ == "__main__":
    app.run(debug=True)