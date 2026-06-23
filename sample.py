# What is Flask
# Flask is a micro Web framework written in python
# Flask is a library

# Flask Concept :
#Browser (Chorme) --> request --> Flask --> Python code
#Browser (Chorme) <-- response <-- Flask <-- Python code

#@app.route('/') --> This handle URL
#def home(): --> This is function
#return... -->This is take to browser


@app.route('/')
def home():
    student_name="Rahul"
    return render_template('homee.html',name=student)

python side -------------------------------------------
student_name="Rahul"
    return render_template('homee.html',name=student)