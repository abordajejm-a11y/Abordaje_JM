import sqlite3
import requests
from flask import Flask, jsonify, request, render_template

app = Flask(__name__)


def get_db_connection():
    conn = sqlite3.connect('students.db')
    conn.row_factory = sqlite3.Row
    return conn


def ensure_source_column():
    """FIX: make sure the students table has the 'source' column that
    /import-student writes to (older databases were created without it)."""
    conn = get_db_connection()
    columns = [row['name'] for row in conn.execute("PRAGMA table_info(students)")]
    if columns and 'source' not in columns:
        conn.execute("ALTER TABLE students ADD COLUMN source TEXT DEFAULT 'Local'")
        conn.commit()
    conn.close()


ensure_source_column()


def ensure_unique_student_id():
    """NEW: database-level guard so the same student_id can never be stored
    twice (ignores upper/lower case and surrounding spaces).
    If the table ALREADY contains duplicates, SQLite refuses to create the
    index; we skip it quietly and the checks in the routes still protect you.
    Delete the old duplicates and restart to enable the index."""
    conn = get_db_connection()
    try:
        conn.execute(
            'CREATE UNIQUE INDEX IF NOT EXISTS idx_students_student_id '
            'ON students (LOWER(TRIM(student_id)))'
        )
        conn.commit()
    except sqlite3.Error as e:
        print('Unique index not created (duplicates already exist?):', e)
    finally:
        conn.close()


ensure_unique_student_id()


def student_exists(conn, student_id, exclude_id=None):
    """NEW: True if a student with this student_id is already stored.
    exclude_id lets an edit keep its own student_id without a false match."""
    sid = str(student_id).strip().lower()

    if exclude_id is None:
        row = conn.execute(
            'SELECT 1 FROM students WHERE LOWER(TRIM(student_id)) = ?',
            (sid,)
        ).fetchone()
    else:
        row = conn.execute(
            'SELECT 1 FROM students WHERE LOWER(TRIM(student_id)) = ? AND id != ?',
            (sid, exclude_id)
        ).fetchone()

    return row is not None


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

    data = request.get_json(silent=True)

    if not data:
        return jsonify({
            "error": "No data received"
        }), 400

    required = ['student_id', 'name', 'program', 'year', 'section']
    missing = [k for k in required if not str(data.get(k, '')).strip()]

    if missing:
        return jsonify({
            "error": "Missing fields: " + ", ".join(missing)
        }), 400

    # Records sent by an external client (e.g. a partner) that don't say
    # where they came from are labeled 'External API'.
    source = data.get('source', 'External API')

    conn = get_db_connection()

    try:
        # NEW: don't store the same student twice
        if student_exists(conn, data['student_id']):
            return jsonify({
                "error": "Student already exists in your database"
            }), 409

        cursor = conn.execute(
            '''
            INSERT INTO students
            (
                student_id,
                name,
                program,
                year,
                section,
                source
            )
            VALUES (?, ?, ?, ?, ?, ?)
            ''',
            (
                data['student_id'],
                data['name'],
                data['program'],
                data['year'],
                data['section'],
                source
            )
        )

        conn.commit()

        new_id = cursor.lastrowid

    except sqlite3.IntegrityError:
        # NEW: the unique index caught a duplicate (e.g. two requests at once)
        return jsonify({
            "error": "Student already exists in your database"
        }), 409

    finally:
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

    # NEW: an edit must not turn this record into a duplicate of another one
    if student_exists(conn, data['student_id'], exclude_id=id):

        conn.close()

        return jsonify({
            "error": "Another student already has that Student ID"
        }), 409

    try:
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

    except sqlite3.IntegrityError:
        return jsonify({
            "error": "Another student already has that Student ID"
        }), 409

    finally:
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


# =====================================
# PARTNER RECORDS
# Partner Database -> Partner Flask API -> Internet
# -> This Flask app -> Web interface
# =====================================

@app.route('/partner-records')
def partner_records():
    partner_url = "https://maryjoydebaja.onrender.com/students"

    try:
        # Render free hosting can take up to ~a minute to wake up
        response = requests.get(partner_url, timeout=60)
        response.raise_for_status()
        return jsonify(response.json())

    except requests.RequestException:
        return jsonify({
            "error": "Unable to retrieve partner data"
        }), 502


@app.route('/import-student', methods=['POST'])
def import_student():
    data = request.get_json(silent=True)
    required = ['student_id', 'name', 'program', 'year', 'section']

    # FIX: validate input instead of crashing with a KeyError (500)
    if not data or any(not str(data.get(k, '')).strip() for k in required):
        return jsonify({
            "error": "Missing student fields"
        }), 400

    conn = get_db_connection()

    try:
        # FIX: don't import the same student twice
        # (now ignores upper/lower case and extra spaces)
        if student_exists(conn, data['student_id']):
            return jsonify({
                "error": "Student already exists in your database"
            }), 409

        conn.execute(
            '''
            INSERT INTO students
            (student_id, name, program, year, section, source)
            VALUES (?, ?, ?, ?, ?, ?)
            ''',
            (
                str(data['student_id']).strip(),
                data['name'],
                data['program'],
                data['year'],
                data['section'],
                'Partner API'
            )
        )

        conn.commit()

    except sqlite3.IntegrityError:
        # NEW: the unique index blocked a duplicate that slipped past the
        # check above (for example, a double-click or two tabs at once)
        return jsonify({
            "error": "Student already exists in your database"
        }), 409

    except sqlite3.Error as e:
        # FIX: return the real database error so it is visible on the card
        return jsonify({
            "error": str(e)
        }), 500

    finally:
        conn.close()

    return jsonify({
        "message": "Remote record saved"
    }), 201

if __name__ == '__main__':
    app.run(debug=True)