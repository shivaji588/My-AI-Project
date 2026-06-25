import os
import sqlite3
from flask import *
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, render_template, request, redirect, session ,url_for
from werkzeug.security import generate_password_hash, check_password_hash


app = Flask(__name__)
app.secret_key = "academic_copilot"


# ---------------- DATABASE ----------------

def init_db():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT
        )
    """)

    conn.commit()
    conn.close()


init_db()


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


@app.route("/papers")
def papers():
    return render_template("papers.html")


# ---------------- SUBJECT ----------------

@app.route("/subjects")
def subjects():
    return render_template("subjects.html")


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

#----------------DASHBOARD------------------

@app.route('/dashboard')
def dashboard():

    if 'user' in session:
        return render_template('dashboard.html')

    return redirect('/login')


# ---------------- REGISTER ----------------

@app.route('/register', methods=['GET','POST'])
def register():

    if request.method=="POST":

        username=request.form['username']
        password=request.form['password']

        try:
            con=sqlite3.connect("database.db")
            cur=con.cursor()

            cur.execute(
            "INSERT INTO users(username,password) VALUES (?,?)",(username,password))

            con.commit()
        except sqlite3.IntegrityError:
            return "User name already exit"
        finally:
            con.close()

        return redirect('/')
    return render_template('register.html')

# ---------------- LOGIN ----------------

@app.route('/login', methods=['GET','POST'])
def login():

    if request.method=="POST":

        username=request.form['username']
        password=request.form['password']

        con=sqlite3.connect("database.db")
        cur=con.cursor()

        cur.execute(
        "SELECT * FROM users WHERE username=? AND password=?",
        (username,password))

        user=cur.fetchone()

        con.close()

        if user:
            session['user']=username
            return redirect('/dashboard')

        else:
            return "Wrong Username or Password"

    return render_template('login.html')


# ---------------- LOGOUT ----------------

@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("login"))

# ---------------- MAIN ----------------

if __name__ == "__main__":
    app.run(debug=True)





'''import os
from flask import Flask, render_template, request, redirect, session, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = "academic_copilot"

# ---------------- DATABASE ----------------

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


# ---------------- MODELS (NOTES SYSTEM) ----------------

class Subject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    icon = db.Column(db.String(10))
    description = db.Column(db.String(200))


class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    content = db.Column(db.Text)
    subject_id = db.Column(db.Integer, db.ForeignKey("subject.id"))


# ---------------- CREATE DB ----------------

with app.app_context():
    db.create_all()


# ======================================================
# 🔵 BASIC PAGES
# ======================================================

@app.route("/")
def home():
    return render_template("home.html")


@app.route("/index")
def index():
    return render_template("index.html")


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/papers")
def papers():
    return render_template("papers.html")


@app.route("/subjects")
def subjects():
    return render_template("subjects.html")


# ======================================================
# 📚 NOTES SYSTEM (DB BASED)
# ======================================================

@app.route("/notes")
def notes():
    subjects = Subject.query.all()
    return render_template("notes.html", subjects=subjects)


@app.route("/subject/<int:id>")
def subject_notes(id):
    subject = Subject.query.get_or_404(id)
    notes = Note.query.filter_by(subject_id=id).all()

    return render_template(
        "subject_notes.html",
        subject=subject,
        notes=notes
    )


@app.route("/note/<int:id>")
def view_note(id):
    note = Note.query.get_or_404(id)
    return render_template("view_note.html", note=note)


@app.route("/add-note", methods=["GET", "POST"])
def add_note():

    if "user" not in session:
        return redirect("/login")

    subjects = Subject.query.all()

    if request.method == "POST":

        new_note = Note(
            title=request.form["title"],
            content=request.form["content"],
            subject_id=request.form["subject_id"]
        )

        db.session.add(new_note)
        db.session.commit()

        return redirect("/notes")

    return render_template("add_note.html", subjects=subjects)


# ======================================================
# 🤖 CHATBOT
# ======================================================

@app.route("/chatbot", methods=["GET", "POST"])
def chatbot():

    answer = ""

    if request.method == "POST":

        question = request.form["question"].lower()

        if "hello" in question or "hi" in question:
            answer = "Hello 👋 I am your AI Academic Copilot."

        elif "flask" in question:
            answer = "Flask is a Python web framework."

        elif "python" in question:
            answer = "Python is a high-level programming language."

        elif "java" in question:
            answer = "Java is object-oriented language."

        elif "dbms" in question:
            answer = "DBMS is used to manage databases."

        elif "css" in question:
            answer = "CSS is used for styling web pages."

        elif "html" in question:
            answer = "HTML is structure of web pages."

        else:
            answer = "Sorry, I don't know that answer."

    return render_template("chatbot.html", answer=answer)


# ======================================================
# 🧪 QUIZ
# ======================================================

@app.route("/quiz")
def quiz():
    return render_template("quiz.html")


# ======================================================
# 🔐 AUTH SYSTEM (SQLite simple)
# ======================================================

import sqlite3

def init_db():
    conn = sqlite3.connect("database.db")
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT
        )
    """)

    try:
        conn.execute("ALTER TABLE users AND COLUME role TEXT DEFAULT 'student")
    except:
        #colume already exits
        pass

    conn.commit()
    conn.close()

init_db()


@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        try:
            con = sqlite3.connect("database.db")
            cur = con.cursor()

            cur.execute(
                "INSERT INTO users(username,password) VALUES (?,?)",
                (username, password)
            )

            con.commit()
            con.close()

            return redirect("/login")

        except:
            return "User already exists"

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        con = sqlite3.connect("database.db")
        cur = con.cursor()

        cur.execute(
            "SELECT * FROM users WHERE username=? AND password=?",
            (username, password)
        )

        user = cur.fetchone()
        con.close()

        if user:
            session["user"] = username
            return redirect("/dashboard")

        return "Invalid login"

    return render_template("login.html")


@app.route("/dashboard")
def dashboard():

    if "user" in session:
        return render_template("dashboard.html")

    return redirect("/login")


@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/login")


# ======================================================
# 🟢 ADD SUBJECTS (RUN ONCE)
# ======================================================

@app.route("/add-subjects")
def add_subjects():

    if Subject.query.first():
        return "Already exists"

    subjects = [
        Subject(name="Python", icon="🐍", description="Python Programming"),
        Subject(name="Java", icon="☕", description="Java OOP"),
        Subject(name="C", icon="💻", description="C Language"),
        Subject(name="C++", icon="⚡", description="C++ Programming"),
        Subject(name="DBMS", icon="🗄", description="Database Management"),
        Subject(name="OS", icon="🖥", description="Operating System")
    ]

    db.session.add_all(subjects)
    db.session.commit()

    return "Subjects Added"


# ======================================================
# RUN APP
# ======================================================

if __name__ == "__main__":
    app.run(debug=True)'''