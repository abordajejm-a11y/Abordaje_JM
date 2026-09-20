from flask import Flask, jsonify, request

app = Flask(__name__)

@app.route('/')
def home():
    return "Welcome to my first API! An Activty created for System Integration (IT 3120)"

@app.route('/student')
def get_student():
    return jsonify({
        "student_id": "2024-00111",
        "name": "JM Abordaje",
        "program": "BSIT",
        "year": 3,
        "section": "A"
    })

@app.route('/hello')
def say_hello():
    name = request.args.get('name', 'Student')
    return jsonify({
        "message": f"Hello, {name}!"
    })

@app.route('/course')
def get_course():
    return jsonify({
        "course_code": "IT3120",
        "course_title": "System Integration",
        "instructor": "Dr. Rene Arduo",
        "semester": 1,
        "academic_year": 2026
    })

@app.route('/grades')
def get_grades():
    return jsonify({
        "student_id": "2024-00111",
        "grades": {
            "IT3122": "1.4",
            "IT3120": "1.5",
            "ITPE3": "1.3"
        }
    })

if __name__ == '__main__':
    app.run(debug=True)
