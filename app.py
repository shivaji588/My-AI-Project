from database import init_db
import os
import sqlite3
import datetime
from werkzeug.utils import secure_filename
from groq import Groq
from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request, redirect, send_from_directory, url_for, flash, session
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

BASE_DIR = os.path.dirname(os.path.abspath(__file__))   #Base path app.py ka path show
DB_PATH = os.path.join(BASE_DIR, "database.db")         #Database Path

init_db()  # Initialize the database on app startup

# ---------------- HOME ----------------

@app.route("/")
def home():
    return render_template("home.html")

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


    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
        SELECT id, fullname, email, username, role, profile_image
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

    conn = sqlite3.connect(DB_PATH)
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

    conn = sqlite3.connect(DB_PATH)
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


    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()


    cur.execute("""
    SELECT id, fullname, email, username, role, profile_image
    FROM users
    WHERE id=?
    """,(id,))


    user = cur.fetchone()

    conn.close()


    return render_template(
        "user_details.html",
        user=user
    )
#================ ADMIN CHAT HISTORY =================

@app.route("/chat_history")
def chat_history():

    if session.get("role") != "admin":
        flash("Admin access only!", "danger")
        return redirect(url_for("dashboard"))

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    search = request.args.get("search", "")

    # ================= DASHBOARD STATS =================

    cur.execute("SELECT COUNT(*) FROM chat_history")
    total_chats = cur.fetchone()[0]

    cur.execute("""
        SELECT COUNT(*)
        FROM chat_history
        WHERE feedback='Helpful'
    """)
    helpful = cur.fetchone()[0]

    cur.execute("""
        SELECT COUNT(*)
        FROM chat_history
        WHERE feedback='Not Helpful'
    """)
    not_helpful = cur.fetchone()[0]

    cur.execute("""
        SELECT COUNT(DISTINCT user_id)
        FROM chat_history
    """)
    total_users = cur.fetchone()[0]

    # ================= CHAT LIST =================

    if search:

        cur.execute("""
        SELECT
            chat_history.id,
            users.username,
            chat_history.subject,
            chat_history.question,
            chat_history.answer,
            chat_history.feedback,
            chat_history.created_at

        FROM chat_history

        JOIN users
        ON chat_history.user_id = users.id

        WHERE
            users.username LIKE ?
            OR chat_history.subject LIKE ?
            OR chat_history.question LIKE ?

        ORDER BY chat_history.id DESC
        """,
        (
            "%" + search + "%",
            "%" + search + "%",
            "%" + search + "%"
        ))

    else:

        cur.execute("""
        SELECT
            chat_history.id,
            users.username,
            chat_history.subject,
            chat_history.question,
            chat_history.answer,
            chat_history.feedback,
            chat_history.created_at

        FROM chat_history

        JOIN users
        ON chat_history.user_id = users.id

        ORDER BY chat_history.id DESC
        """)

    chats = cur.fetchall()

    conn.close()

    return render_template(
        "chat_history.html",
        chats=chats,
        total_chats=total_chats,
        helpful=helpful,
        not_helpful=not_helpful,
        total_users=total_users
    )
#================ DELETE CHAT =================

@app.route("/delete_chat/<int:id>")
def delete_chat(id):

    if session.get("role") != "admin":
        return "Unauthorized Access",403


    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()


    cur.execute("""
    DELETE FROM chat_history
    WHERE id=?
    """,(id,))


    conn.commit()
    conn.close()


    flash(
        "Chat deleted successfully",
        "success"
    )


    return redirect("/chat_history")
#----------------NOTES----------------
@app.route("/notes")
def notes():

    if "user_id" not in session:
        flash("Please login first to access this page.", "warning")
        return redirect(url_for("login"))

    conn = sqlite3.connect(DB_PATH)
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

#=====================notes view========================

@app.route("/notes/<subject>")
def show_notes(subject):

    prompt = f"""
    Generate detailed MSBTE diploma notes for {subject} subject.

    Include:
    - Unit wise topics
    - Definition
    - Important points
    - Examples
    - Exam points

    Make it simple and easy to understand.
    create attractive notes
    use diploma books for reference
    use related emoji for notes
    use spaces for notes
    """


    response = client.chat.completions.create(

        model="llama-3.1-8b-instant",

        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],

        temperature=0.5
    )


    notes = response.choices[0].message.content


    return render_template(
        "notes_view.html",
        subject=subject,
        notes=notes
    )
    
#--------------papers--------------------
@app.route("/papers")
def papers():   
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM papers")
    papers_list = cursor.fetchall()
    conn.close()

    return render_template("papers.html", papers=papers_list)   

#======================== paper add ================================

UPLOAD_FOLDER = "static/uploads"

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


@app.route("/add_paper", methods=["GET","POST"])
def add_paper():

    if request.method == "POST":


        title = request.form["title"]

        year = request.form["year"]


        file = request.files["paper_file"]



        if file.filename == "":

            flash("Please select PDF file","danger")

            return redirect("/add_paper")



        filename = secure_filename(file.filename)



        # create upload folder if not exists

        if not os.path.exists(UPLOAD_FOLDER):

            os.makedirs(UPLOAD_FOLDER)



        # save pdf

        file.save(
            os.path.join(
                UPLOAD_FOLDER,
                filename
            )
        )

        # save filename in database

        conn = sqlite3.connect(DB_PATH)

        cur = conn.cursor()



        cur.execute("""
        INSERT INTO papers(title, year, file_name)
        VALUES(?,?,?)
        """,
        (
            title,
            year,
            filename
        ))



        conn.commit()

        conn.close()



        flash(
            "Paper Added Successfully",
            "success"
        )


        return redirect("/papers")



    return render_template("add_paper.html")

#========================paper manage================================ 
@app.route("/manage_papers")
def manage_papers():

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("SELECT * FROM papers")

    papers = cur.fetchall()

    conn.close()

    return render_template(
        "manage_papers.html",
        papers=papers
    )  

#======================== delete paper ========================

@app.route("/admin/delete/<int:id>")
def delete_paper(id):

    # only admin access
    if session.get("role") != "admin":
        return "Unauthorized Access",403


    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()


    # get file name before delete
    cur.execute(
        "SELECT file_name FROM papers WHERE id=?",
        (id,)
    )

    paper = cur.fetchone()



    if paper:

        file_path = os.path.join(
            "static/uploads",
            paper[0]
        )


        # delete pdf file
        if os.path.exists(file_path):

            os.remove(file_path)



        # delete database record
        cur.execute(
            "DELETE FROM papers WHERE id=?",
            (id,)
        )

        paper = cur.fetchone()

        print("PAPER DATA:", paper)

        conn.commit()



    conn.close()


    flash(
        "Paper Deleted Successfully",
        "success"
    )


    return redirect("/manage_papers")

#======================== edit paper ========================

@app.route("/admin/edit/<int:id>", methods=["GET","POST"])
def edit_paper(id):

    if session.get("role") != "admin":
        return "Unauthorized Access",403


    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()


    # POST UPDATE
    if request.method == "POST":

        title = request.form["title"]
        year = request.form["year"]

        new_file = request.files.get("paper_file")


        # old file get
        cur.execute(
            "SELECT file_name FROM papers WHERE id=?",
            (id,)
        )

        old_paper = cur.fetchone()

        old_file = old_paper[0]



        # if new pdf uploaded
        if new_file and new_file.filename != "":

            filename = new_file.filename


            upload_path = os.path.join(
                "static/uploads",
                filename
            )


            new_file.save(upload_path)



            # delete old pdf
            old_path = os.path.join(
                "static/uploads",
                old_file
            )


            if os.path.exists(old_path):
                os.remove(old_path)



            cur.execute("""
            UPDATE papers
            SET title=?, year=?, file_name=?
            WHERE id=?
            """,
            (
                title,
                year,
                filename,
                id
            ))


        else:


            cur.execute("""
            UPDATE papers
            SET title=?, year=?
            WHERE id=?
            """,
            (
                title,
                year,
                id
            ))



        conn.commit()
        conn.close()


        flash(
            "Paper Updated Successfully",
            "success"
        )


        return redirect("/manage_papers")




    # GET DATA

    cur.execute(
        "SELECT * FROM papers WHERE id=?",
        (id,)
    )

    paper = cur.fetchone()


    conn.close()


    return render_template(
        "edit_paper.html",
        paper=paper
    )

#======================== view paper ========================

@app.route("/view_paper/<int:id>")
def view_paper(id):

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM papers WHERE id=?",
        (id,)
    )

    paper = cursor.fetchone()

    conn.close()


    if paper:

        return render_template(
            "paper_view.html",
            paper=paper
        )


    return "Paper Not Found",404
# ---------------- SUBJECTS----------------
@app.route("/subjects")
def subjects():
    return render_template("subjects.html")

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

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    user_id = session.get("user_id")

    if not user_id:
        return redirect(url_for("login"))

    # ===================== POST =====================
    if request.method == "POST":

        data = request.get_json()

        subject = data.get("subject")
        question = data.get("question")

        system_prompt = f"""
You are AI Academic Copilot.

You are an AI assistant specially designed for Diploma and Engineering students.

Rules:
1. Answer ONLY academic questions.
2. Subjects include:
   - Python
   - Java
   - DBMS
   - Operating System
   - Computer Networks (DCN)
   - Data Structures
   - Software Engineering
   - Digital Electronics
   - Microprocessor
   - C Programming
   - Mathematics
3. Explain concepts in simple and easy language.
4. Give examples whenever possible.
5. If the user asks anything unrelated to academics (movies, cricket, celebrities, politics, jokes, etc.), politely reply:
6.Give answer in 2 lines if user says definaation otherwise explain  

"Sorry! I am an Academic AI Assistant. I can answer only Diploma and Engineering academic questions."

Current Subject: {subject}
"""

        try:

            response = client.chat.completions.create(

                model="llama-3.3-70b-versatile",

                messages=[
                    {
                        "role": "system",
                        "content": system_prompt
                    },
                    {
                        "role": "user",
                        "content": question
                    }
                ],

                temperature=0.5,
                max_tokens=1000

            )

            answer = response.choices[0].message.content

        except Exception as e:

            answer = f"Error: {str(e)}"

        # Save Chat History
        cur.execute("""
            INSERT INTO chat_history
            (user_id, subject, question, answer)
            VALUES (?, ?, ?, ?)
        """, (
            user_id,
            subject,
            question,
            answer
        ))


        # get inserted chat id
        chat_id = cur.lastrowid


        conn.commit()
        conn.close()


        return jsonify({
            "answer": answer,
            "chat_id": chat_id
        })
    # ===================== GET =====================

    cur.execute("""
        SELECT *
        FROM chat_history
        WHERE user_id=?
        ORDER BY id ASC
    """, (user_id,))

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

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
    DELETE FROM chat_history
    WHERE user_id=?
    """,(session["user_id"],))

    conn.commit()
    conn.close()

    return redirect(url_for("chatbot"))

#================ CHAT FEEDBACK =================

@app.route("/chat_feedback/<int:id>/<status>")
def chat_feedback(id,status):

    if "user_id" not in session:
        return redirect(url_for("login"))


    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()


    cur.execute("""
    UPDATE chat_history
    SET feedback=?
    WHERE id=? AND user_id=?
    """,
    (
        status,
        id,
        session["user_id"]
    ))


    conn.commit()
    conn.close()


    return redirect(url_for("chatbot"))

# ---------------- QUIZ ----------------------------------------

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

#================ AI QUIZ GENERATOR =================

import json


@app.route('/ai_quiz_generator')
def ai_quiz_generator():

    if 'user_id' not in session:
        return redirect('/login')


    subject = request.args.get('subject')


    prompt = f"""

Generate exactly 10 multiple choice quiz questions for {subject}.

IMPORTANT RULES:
- Return ONLY valid JSON.
- Do not add markdown.
- Do not add ```json.
- Do not add any extra text.
- Start response with [
- End response with ]

JSON FORMAT:

[
 {{
 "question":"Question text",
 "options":[
    "Option 1",
    "Option 2",
    "Option 3",
    "Option 4"
 ],
 "answer":"Correct option exactly same as options",
 "explanation":"Short explanation"
 }}
]


Rules:
- Questions should be diploma student level.
- Each question must have exactly 4 options.
- Answer must match one option exactly.
- Explanation should be 1 or 2 lines only.

Subject: {subject}

"""


    try:

        response = client.chat.completions.create(

            model="llama-3.1-8b-instant",

            messages=[
                {
                    "role":"user",
                    "content":prompt
                }
            ],

            temperature=0.2
        )


        ai_response = response.choices[0].message.content


        print("========= AI RESPONSE =========")
        print(ai_response)
        print("===============================")



        # Remove markdown
        ai_response = ai_response.replace(
            "```json",
            ""
        )

        ai_response = ai_response.replace(
            "```",
            ""
        )


        ai_response = ai_response.strip()



        # Extract JSON only

        start = ai_response.find("[")

        end = ai_response.rfind("]") + 1



        if start == -1 or end == 0:

            raise Exception(
                "JSON not found"
            )



        json_text = ai_response[start:end]



        quiz_data = json.loads(
            json_text
        )



        if not isinstance(quiz_data,list):

            raise Exception(
                "Invalid quiz list"
            )



    except Exception as e:


        print(
            "JSON ERROR:",
            e
        )


        print(
            "FAILED RESPONSE:",
            ai_response
        )


        return """
        <h2>
        AI generated invalid quiz format
        </h2>

        <a href="javascript:history.back()">
        Try Again
        </a>
        """



    # Store quiz

    session["ai_quiz"] = quiz_data

    session["ai_subject"] = subject

    session["current_question"] = 0

    session["ai_answers"] = {}



    return render_template(

        "ai_quiz_generator.html",

        subject=subject,

        question=quiz_data[0],

        number=1,

        total=len(quiz_data),

        current=0,

        selected=None,

        correct=None,

        explanation=None

    )
#================ NEXT AI QUESTION =================
@app.route('/next_ai_question')
def next_ai_question():

    quiz = session.get("ai_quiz")

    index = session.get("current_question",0)

    if index < len(quiz)-1:
        index += 1

    session["current_question"] = index


    question = quiz[index]


    selected = session.get("ai_answers",{}).get(str(index))


    return render_template(
        "ai_quiz_generator.html",
        subject=session.get("ai_subject"),
        quiz=quiz,
        question=question,
        number=index+1,
        total=len(quiz),
        current=index,
        selected=selected,
        correct=None,
        explanation=None
    )
#================ PREVIOUS AI QUESTION =================
@app.route('/previous_ai_question')
def previous_ai_question():

    quiz = session.get("ai_quiz")

    index = session.get("current_question",0)


    if index > 0:
        index -= 1


    session["current_question"] = index
    question = quiz[index]
    selected = session.get("ai_answers",{}).get(str(index))

    return render_template(
        "ai_quiz_generator.html",
        subject=session.get("ai_subject"),
        quiz=quiz,
        question=question,
        number=index+1,
        total=len(quiz),
        current=index,
        selected=selected,
        correct=None,
        explanation=None
    )
#================ SHOW CURRENT AI QUESTION =================
@app.route('/ai_quiz_page')
def ai_quiz_page():

    if 'ai_quiz' not in session:
        return redirect('/quiz')


    quiz = session['ai_quiz']

    index = session.get(
        'current_question',
        0
    )


    question = quiz[index]


    return render_template(
        "ai_quiz_generator.html",
        subject=session.get('ai_subject'),
        quiz=quiz,
        question=question,
        number=index+1,
        total=len(quiz),
        current=index
    )

#================ CHECK AI ANSWER =================

@app.route('/check_ai_answer', methods=['POST'])
def check_ai_answer():

    if 'ai_quiz' not in session:
        return redirect('/quiz')


    answer = request.form.get("answer")

    index = session.get("current_question",0)

    quiz = session['ai_quiz']

    question = quiz[index]


    session['ai_answers'][str(index)] = answer

    session.modified = True


    correct = question["answer"]

    is_correct = (answer == correct)



    return render_template(
        "ai_quiz_generator.html",

        subject=session['ai_subject'],

        quiz=quiz,

        question=question,

        number=index+1,

        total=len(quiz),

        current=index,


        checked=True,

        selected_answer=answer,

        correct=correct,

        is_correct=is_correct,

        explanation=question["explanation"]
    )
#============== FINISH AI QUIZ =================

@app.route('/finish_ai_quiz')
def finish_ai_quiz():

    quiz = session.get("ai_quiz")

    answers = session.get(
        "ai_answers",
        {}
    )


    score = 0


    for i,q in enumerate(quiz):

        if answers.get(str(i)) == q["answer"]:
            score += 1



    save_score(
        session["ai_subject"],
        score,
        len(quiz)
    )


    return render_template(
        "result.html",
        score=score,
        total=len(quiz)
    )
#=============quiz result show on admin panel==============
@app.route('/quiz_results')
def quiz_results():

    if 'user_id' not in session:
        return redirect('/login')

    if session.get('role') != 'admin':
        return redirect('/')

    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    cur.execute("""
        SELECT 
            quiz_results.id,
            users.fullname,
            quiz_results.subject,
            quiz_results.score,
            quiz_results.total
        FROM quiz_results
        JOIN users
        ON quiz_results.user_id = users.id
        ORDER BY quiz_results.id DESC
    """)

    results = cur.fetchall()

    conn.close()

    return render_template(
        "quiz_results.html",
        results=results
    )
#=============delete quiz result from admin panel==============

@app.route('/delete_quiz_result/<int:id>')
def delete_quiz_result(id):

    if 'user_id' not in session:
        return redirect('/login')

    if session.get('role') != 'admin':
        return redirect('/')

    conn = sqlite3.connect("database.db")
    cur = conn.cursor()

    cur.execute(
        "DELETE FROM quiz_results WHERE id=?",
        (id,)
    )

    conn.commit()
    conn.close()

    return redirect('/quiz_results')
#----------------------LEADERBOARD-----------

from flask import request, session, render_template
from datetime import date, timedelta

@app.route("/leaderboard")
def leaderboard():

    conn = get_db()
    cur = conn.cursor()

    subject = request.args.get("subject", "All")
    period = request.args.get("period", "all")

    # Pagination
    page = request.args.get("page", 1, type=int)
    per_page = 5

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

    # Fetch all records
    cur.execute(query, params)
    all_data = cur.fetchall()

    # Total pages
    total_records = len(all_data)
    total_pages = (total_records + per_page - 1) // per_page

    # Current page data
    start = (page - 1) * per_page
    end = start + per_page
    data = all_data[start:end]

    # Logged-in user
    current_user = session.get("username")

    # Find overall rank
    your_rank = None
    for i, row in enumerate(all_data, start=1):
        if row["username"] == current_user:
            your_rank = i
            break

    return render_template(
        "leaderboard.html",
        data=data,
        selected_subject=subject,
        selected_period=period,
        current_user=current_user,
        your_rank=your_rank,
        page=page,
        per_page=per_page,
        total_pages=total_pages
    )
# ---------------- REGISTER ----------------

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        fullname = request.form["fullname"]
        email = request.form["email"]
        username = request.form["username"]

        # 🔥 FIX HERE
        password = generate_password_hash(request.form["password"])

        conn = sqlite3.connect(DB_PATH)
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

        conn = sqlite3.connect(DB_PATH)
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

            conn2 = sqlite3.connect(DB_PATH)
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

    conn = sqlite3.connect(DB_PATH)
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


    # ================= AI LEARNING SCORE =================

    user_id = session.get('user_id')


    # AI Chat Score
    cur.execute("""
        SELECT COUNT(*)
        FROM chat_history
        WHERE user_id=?
    """,(user_id,))

    chat_count = cur.fetchone()[0]


    chat_score = min(chat_count * 3, 30)



    # Quiz Score
    cur.execute("""
        SELECT AVG(score*100/total)
        FROM quiz_results
        WHERE user_id=?
    """,(user_id,))


    quiz_result = cur.fetchone()[0]


    if quiz_result:
        quiz_score = min(int(quiz_result * 0.3),30)
    else:
        quiz_score = 0



    # Study Activity Score

    cur.execute("""
        SELECT COUNT(*)
        FROM user_activity
        WHERE user_id=?
    """,(user_id,))


    activity_count = cur.fetchone()[0]


    activity_score = min(activity_count,20)



    # Notes Score

    cur.execute("""
        SELECT COUNT(*)
        FROM user_activity
        WHERE user_id=?
        AND action='Notes Generated'
    """,(user_id,))


    notes_count = cur.fetchone()[0]


    notes_score = min(notes_count*2,20)



    ai_score = (
        chat_score +
        quiz_score +
        activity_score +
        notes_score
    )
    # ================= RECENT ACTIVITY =================


    cur.execute("""
        SELECT login_date, action
        FROM user_activity
        ORDER BY id DESC
        LIMIT 10
    """)


    timeline = cur.fetchall()

    user_id = session.get('user_id')


    progress = conn.execute(
        """
        SELECT xp, streak, level
        FROM user_progress
        WHERE user_id=?
        """,
        (user_id,)
    ).fetchone()

    if progress is None:
        progress = {
        "level":1,
        "xp":0,
        "streak":0
    }

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

        timeline=timeline,

        level=progress['level'],
        xp=progress['xp'],
        streak=progress['streak'],
        ai_score=ai_score
    )
# ---------------- PROFILE ----------------

@app.route("/profile")
def profile():

    if "user_id" not in session:
        return redirect("/login")


    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()


    # User Details
    cur.execute("""
    SELECT id, fullname, email, username, role, profile_image, notifications, dark_theme
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


    notes_count = 0


    # Total Login Days
    cur.execute("""
    SELECT COUNT(DISTINCT login_date)
    FROM user_activity
    WHERE user_id=?
    """,(session["user_id"],))

    login_days = cur.fetchone()[0]


    # Learning Progress

    total_activity = quiz_count + login_days

    target = 50

    progress = int(
        (total_activity / target) * 100
    )


    if progress > 100:
        progress = 100


    # Login Streak

    streak = login_days


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



# ---------------- UPDATE PROFILE ----------------


from werkzeug.security import check_password_hash, generate_password_hash


@app.route("/update_profile", methods=["POST"])
def update_profile():

    if "user_id" not in session:
        return redirect("/login")


    fullname = request.form["fullname"]
    username = request.form["username"]
    email = request.form["email"]


    notifications = 1 if request.form.get("notifications") else 0
    dark_theme = 1 if request.form.get("dark_theme") else 0


    current_password = request.form.get("current_password")
    new_password = request.form.get("new_password")
    confirm_password = request.form.get("confirm_password")


    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()



    # PASSWORD CHANGE

    if current_password and new_password and confirm_password:


        cur.execute(
            "SELECT password FROM users WHERE id=?",
            (session["user_id"],)
        )


        db_password = cur.fetchone()[0]


        if not check_password_hash(db_password, current_password):

            flash("Current password is incorrect.", "danger")
            conn.close()
            return redirect("/profile")


        if new_password != confirm_password:

            flash("New passwords do not match.", "danger")
            conn.close()
            return redirect("/profile")


        hashed_password = generate_password_hash(new_password)


        cur.execute("""
            UPDATE users
            SET password=?
            WHERE id=?
        """,
        (
            hashed_password,
            session["user_id"]
        ))



    # PROFILE IMAGE UPLOAD

    image = request.files.get("profile_image")


    if image and image.filename != "":


        filename = image.filename


        upload_folder = os.path.join(
            "static",
            "uploads",
            "profile"
        )


        os.makedirs(upload_folder, exist_ok=True)


        image.save(
            os.path.join(
                upload_folder,
                filename
            )
        )


        cur.execute("""
            UPDATE users
            SET profile_image=?
            WHERE id=?
        """,
        (
            filename,
            session["user_id"]
        ))



    # UPDATE PROFILE DETAILS

    cur.execute("""
        UPDATE users
        SET fullname=?,
            username=?,
            email=?,
            notifications=?,
            dark_theme=?
        WHERE id=?
    """,
    (
        fullname,
        username,
        email,
        notifications,
        dark_theme,
        session["user_id"]
    ))

    conn.commit()
    conn.close() 

    session["username"] = username

    flash("Profile updated successfully!", "success")

    return redirect("/profile")
# ---------------- LOGOUT ----------------
@app.route("/logout")
def logout():

    session.clear()

    flash("Logged Out Successfully","success")

    return redirect(url_for("login"))

# ---------------- MAIN ----------------

if __name__ == "__main__":
    app.run(debug=True)
    