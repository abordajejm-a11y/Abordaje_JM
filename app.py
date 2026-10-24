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


# GET ALL STUDENTS
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


# ADD STUDENT
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


# GET STUDENT BY DATABASE ID
@app.route('/api/students/<int:id>', methods=['GET'])
def get_student(id):

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


# UPDATE STUDENT
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


# DELETE STUDENT
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


# SEARCH BY STUDENT ID (e.g., 2024-00329)
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

@app.route('/api/students', methods=['GET'])
def api_students():
    conn = get_db_connection()

    rows = conn.execute(
        'SELECT * FROM students'
    ).fetchall()

    conn.close()

    return jsonify([
        dict(row)
        for row in rows
    ])

if __name__ == '__main__':
    app.run(debug=True)