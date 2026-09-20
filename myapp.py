from flask import Flask, jsonify, request

app = Flask(__name__)

@app.route('/')
def home():
    return "Welcome to my first API!"

@app.route('/profile')
def profile():
    return jsonify({
        "student_id": "24-00111",
        "name": "JM Abordaje",
        "program": "BSIT",
        "year": 3,
        "section": "A",
        "email": "jmabordaje@gmail.com",
        "skills": [
            "Python",
            "HTML",
            "Netwroking"
        ]
    })

@app.route('/student')
def get_student():
    return jsonify({
        "student_id": "24-00111",
        "name": "JM Abordaje",
        "program": "BSIT",
        "year": 3,
        "section": "A"
    })

@app.route('/course')
def get_course():
    return jsonify({
        "course_code": "IT3120",
        "course_title": "System Integration",
        "instructor": "Dr. Rene Arduo",
        "semester": 1,
        "academic_year": 2026,
    })

@app.route('/hello')
def say_hello():
    name = request.args.get('name', 'Student')
    return jsonify({
        "message": f"Hello, {name}!"
    })

@app.route('/greet')
def greet():
    name = request.args.get('name','JM Abordaje')
    section = request.args.get('section','A')
    return jsonify({
        "message": f"Hello, {name}! from BSIT {section}"
    })

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)