import sqlite3
import requests
from flask import Flask, jsonify, request, render_template

app = Flask(__name__)


def get_db_connection():
    conn = sqlite3.connect('students.db')
    conn.row_factory = sqlite3.Row
    return conn


@app.route('/')
def home():
    return render_template('index.html')


# =====================================
# ORIGINAL ENDPOINTS
# =====================================

@app.route('/students')
def get_students():

    conn = get_db_connection()

    students = conn.execute(
        'SELECT * FROM students'
    ).fetchall()

    conn.close()

    return jsonify([
        dict(student)
        for student in students
    ])


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
def hello():

    name = request.args.get(
        'name',
        'Student'
    )

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


@app.route('/students/program/<program>')
def get_students_by_program(program):

    conn = get_db_connection()

    students = conn.execute(
        'SELECT * FROM students WHERE program = ?',
        (program,)
    ).fetchall()

    conn.close()

    return jsonify([
        dict(student)
        for student in students
    ])


# =====================================
# CRUD API
# =====================================

@app.route('/api/students', methods=['GET'])
def get_all_students():

    conn = get_db_connection()

    students = conn.execute(
        'SELECT * FROM students'
    ).fetchall()

    conn.close()

    return jsonify([
        dict(student)
        for student in students
    ])


@app.route('/api/students', methods=['POST'])
def add_student():

    data = request.get_json()

    if not data:
        return jsonify({
            "error": "No data received"
        }), 400

    conn = get_db_connection()

    cursor = conn.execute(
        '''
        INSERT INTO students
        (
            student_id,
            name,
            program,
            year,
            section
        )
        VALUES (?, ?, ?, ?, ?)
        ''',
        (
            data['student_id'],
            data['name'],
            data['program'],
            data['year'],
            data['section']
        )
    )

    conn.commit()

    new_id = cursor.lastrowid

    conn.close()

    return jsonify({
        "message": "Student added",
        "id": new_id
    }), 201


@app.route('/api/students/<int:id>', methods=['GET'])
def get_student_by_id(id):

    conn = get_db_connection()

    student = conn.execute(
        'SELECT * FROM students WHERE id = ?',
        (id,)
    ).fetchone()

    conn.close()

    if student is None:
        return jsonify({
            "error": "Student not found"
        }), 404

    return jsonify(dict(student))


@app.route('/api/students/<int:id>', methods=['PUT'])
def update_student(id):

    data = request.get_json()

    conn = get_db_connection()

    student = conn.execute(
        'SELECT * FROM students WHERE id = ?',
        (id,)
    ).fetchone()

    if student is None:

        conn.close()

        return jsonify({
            "error": "Student not found"
        }), 404

    conn.execute(
        '''
        UPDATE students
        SET
            student_id = ?,
            name = ?,
            program = ?,
            year = ?,
            section = ?
        WHERE id = ?
        ''',
        (
            data['student_id'],
            data['name'],
            data['program'],
            data['year'],
            data['section'],
            id
        )
    )

    conn.commit()
    conn.close()

    return jsonify({
        "message": "Student updated"
    })


@app.route('/api/students/<int:id>', methods=['DELETE'])
def delete_student(id):

    conn = get_db_connection()

    student = conn.execute(
        'SELECT * FROM students WHERE id = ?',
        (id,)
    ).fetchone()

    if student is None:

        conn.close()

        return jsonify({
            "error": "Student not found"
        }), 404

    conn.execute(
        'DELETE FROM students WHERE id = ?',
        (id,)
    )

    conn.commit()
    conn.close()

    return jsonify({
        "message": "Student deleted"
    })


@app.route('/api/studentid/<student_id>', methods=['GET'])
def search_student_id(student_id):

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


# =====================================
# CLASSMATE PROXY
# =====================================

@app.route('/api/classmate-students')
def classmate_students():

    try:
        r = requests.get(
            'https://maryjoydebaja.onrender.com/students',
            timeout=60
        )

        r.raise_for_status()

        return jsonify(r.json())

    except requests.RequestException as e:
        return jsonify({
            "error": str(e)
        }), 502


if __name__ == '__main__':
    app.run(debug=True)