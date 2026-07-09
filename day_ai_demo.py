from groq import Groq 

client = Groq(api_key="YOUR_API_KEY")

student_name = "John"
student_marks = 80
student_subject = "DBMS"

# step 1 : create a prompt for the AI model
prompt = f"""
student name: {student_name}
student marks: {student_marks}/100
student subject: {student_subject}
please provide practical study tips,it should not be more than 3 lines and should be easy to understand for a student.
"""

# step 2 :API call to Groq API to get the response from the AI model
response = client.chat.completions.create(
    model="llama-3.1-8b-instant",
    messages=[
        {
            "role": "user",
            "content": prompt
        }
    ]
)

# step 3 : print the response from the AI model
tip = response.choices[0].message.content

print(tip)