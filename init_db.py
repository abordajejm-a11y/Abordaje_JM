import sqlite3

conn = sqlite3.connect('students.db')
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id TEXT NOT NULL,
    name TEXT NOT NULL,
    program TEXT NOT NULL,
    year INTEGER NOT NULL,
    section TEXT NOT NULL,
    source TEXT DEFAULT 'Local'
)
""")

# Add the 'source' column if students.db was created by an older version
# (CREATE TABLE IF NOT EXISTS does not change an existing table)
columns = [row[1] for row in cursor.execute("PRAGMA table_info(students)")]
if 'source' not in columns:
    cursor.execute("ALTER TABLE students ADD COLUMN source TEXT DEFAULT 'Local'")
    print("Added missing 'source' column.")

# Clear existing records
cursor.execute("DELETE FROM students")

students = [
    ('2024-00329', 'Eljhon Baxinela', 'BSIT', 3, 'A'),
    ('2024-00302', 'Mary Joy Debaja', 'BSIT', 3, 'A'),
    ('2024-00357', 'Mariel Alada', 'BSIT', 3, 'A'),
    ('2024-00109', 'Eden Mark Aguilar', 'BSIT', 3, 'A'),
    ('2026-1538-EB', 'Francine Marie Orellanes', 'BSIT', 2, 'B')
]

cursor.executemany("""
INSERT INTO students
(student_id, name, program, year, section)
VALUES (?, ?, ?, ?, ?)
""", students)

conn.commit()
conn.close()

print("Database created successfully.")