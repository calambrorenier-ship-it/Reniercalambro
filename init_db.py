
import sqlite3

conn = sqlite3.connect('students.db')
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id TEXT NOT NULL,
    name TEXT NOT NULL,
    program TEXT NOT NULL,
    year INTEGER NOT NULL,
    section TEXT NOT NULL
)
''')

cursor.execute("DELETE FROM students")

students = [
    ('2026-00101', 'Alex Reyes', 'BSIT', 1, 'A'),
    ('2026-00102', 'Sofia Garcia', 'BSIT', 1, 'B'),
    ('2026-00103', 'Daniel Cruz', 'BSCS', 2, 'A'),
    ('2026-00104', 'Mia Santos', 'BSCS', 2, 'B'),
    ('2026-00105', 'Joshua Mendoza', 'BSIT', 3, 'A')
]

cursor.executemany('''
INSERT INTO students (student_id, name, program, year, section)
VALUES (?, ?, ?, ?, ?)
''', students)

conn.commit()
conn.close()

print("Database created successfully.")
