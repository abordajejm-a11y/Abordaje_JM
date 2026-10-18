import sqlite3
from flask import Flask, jsonify, request, render_template

app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect('students.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def home():
    return render_template('index.html')

# Get all students
@app.route('/students')
def get_students():

    conn = get_db_connection()

    students = conn.execute(
        'SELECT * FROM students'
    ).fetchall()

    conn.close()

    return jsonify([dict(student) for student in students])

# Get one student by ID
@app.route('/students/<student_id>')
def get_student(student_id):

    conn = get_db_connection()

    student = conn.execute(
        'SELECT * FROM students WHERE student_id = ?',
        (student_id,)
    ).fetchone()

    conn.close()

    if student is None:
        return jsonify({
            "error": "Student not found"
        }), 404

    return jsonify(dict(student))

@app.route('/hello')
def say_hello():

    name = request.args.get('name', 'Student')

    return jsonify({
        "message": f"Hello, {name}!"
    })

@app.route('/grades')
def grades():

    student_id = request.args.get('student_id')

    return jsonify({
        "student_id": student_id,
        "grades": {
            "IT 3110": "1.25",
            "IT 3120": "1.50",
            "IT 3130": "1.25"
        }
    })

@app.route('/students/program/BSIT')
def get_students_by_program():

    conn = get_db_connection()

    students = conn.execute(
        'SELECT * FROM students WHERE program = ?',
        ('BSIT',)
    ).fetchall()

    conn.close()

    return jsonify([dict(student) for student in students])

if __name__ == '__main__':
    app.run(debug=True)