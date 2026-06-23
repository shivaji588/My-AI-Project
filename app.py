import os
import sqlite3
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

@app.route('/quiz')
def quiz():
    return render_template('quiz.html')

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
