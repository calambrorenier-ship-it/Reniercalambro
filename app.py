
import sqlite3
import requests

from flask import Flask, jsonify, request, render_template
from classmate_config import CLASSMATE_API_URL

app = Flask(__name__)


# DATABASE CONNECTION
def get_db_connection():
    conn = sqlite3.connect('students.db')
    conn.row_factory = sqlite3.Row
    return conn


# HOME PAGE
@app.route('/')
def home():
    return render_template('index.html')


# READ - DISPLAY ALL STUDENTS
@app.route('/students')
def get_students():
    conn = get_db_connection()
    students = conn.execute(
        'SELECT * FROM students'
    ).fetchall()
    conn.close()

    return jsonify([dict(student) for student in students])


# READ - GET ONE STUDENT
@app.route('/students/<int:id>')
def get_student_by_id(id):
    conn = get_db_connection()

    student = conn.execute(
        'SELECT * FROM students WHERE id = ?', (id,)
    ).fetchone()

    conn.close()

    if student is None:
        return jsonify({"error": "Student not found"}), 404

    return jsonify(dict(student))


# CREATE - ADD STUDENT
@app.route('/api/students', methods=['POST'])
def add_student():
    data = request.get_json(silent=True)

    if not data:
        return jsonify({"error": "Invalid JSON data"}), 400

    required = ['student_id', 'name', 'program', 'year', 'section']

    if any(data.get(field) in (None, '') for field in required):
        return jsonify({"error": "All fields are required"}), 400

    try:
        year = int(data['year'])

        if year < 1:
            return jsonify({"error": "Invalid year level"}), 400

        conn = get_db_connection()

        cursor = conn.execute(
            '''INSERT INTO students
            (student_id, name, program, year, section)
            VALUES (?, ?, ?, ?, ?)''',
            (
                data['student_id'],
                data['name'],
                data['program'],
                year,
                data['section']
            )
        )

        conn.commit()
        new_id = cursor.lastrowid
        conn.close()

        return jsonify({
            "message": "Student added successfully",
            "id": new_id
        }), 201

    except (ValueError, TypeError):
        return jsonify({"error": "Year must be a number"}), 400


# READ - API GET ALL STUDENTS
@app.route('/api/students', methods=['GET'])
def api_students():
    conn = get_db_connection()

    rows = conn.execute(
        'SELECT * FROM students'
    ).fetchall()

    conn.close()

    return jsonify([dict(row) for row in rows])


# READ - API GET ONE STUDENT
@app.route('/api/students/<int:id>', methods=['GET'])
def api_get_student(id):
    conn = get_db_connection()

    student = conn.execute(
        'SELECT * FROM students WHERE id = ?', (id,)
    ).fetchone()

    conn.close()

    if student is None:
        return jsonify({"error": "Student not found"}), 404

    return jsonify(dict(student))


# UPDATE - EDIT STUDENT
@app.route('/api/students/<int:id>', methods=['PUT'])
def update_student(id):
    data = request.get_json(silent=True)

    if not data:
        return jsonify({"error": "Invalid JSON data"}), 400

    required = ['student_id', 'name', 'program', 'year', 'section']

    if any(data.get(field) in (None, '') for field in required):
        return jsonify({"error": "All fields are required"}), 400

    try:
        year = int(data['year'])

        if year < 1:
            return jsonify({"error": "Invalid year level"}), 400

        conn = get_db_connection()

        cursor = conn.execute(
            '''UPDATE students SET
            student_id = ?,
            name = ?,
            program = ?,
            year = ?,
            section = ?
            WHERE id = ?''',
            (
                data['student_id'],
                data['name'],
                data['program'],
                year,
                data['section'],
                id
            )
        )

        conn.commit()
        updated = cursor.rowcount
        conn.close()

        if updated == 0:
            return jsonify({"error": "Student not found"}), 404

        return jsonify({
            "message": "Student updated successfully"
        })

    except (ValueError, TypeError):
        return jsonify({"error": "Year must be a number"}), 400


# DELETE - REMOVE STUDENT
@app.route('/api/students/<int:id>', methods=['DELETE'])
def delete_student(id):
    conn = get_db_connection()

    cursor = conn.execute(
        'DELETE FROM students WHERE id = ?', (id,)
    )

    conn.commit()
    deleted = cursor.rowcount
    conn.close()

    if deleted == 0:
        return jsonify({"error": "Student not found"}), 404

    return jsonify({
        "message": "Student deleted successfully"
    })


# SEARCH STUDENTS BY PROGRAM
@app.route('/students/program/<program>')
def get_students_by_program(program):
    conn = get_db_connection()

    students = conn.execute(
        'SELECT * FROM students WHERE UPPER(program) = ?',
        (program.upper(),)
    ).fetchall()

    conn.close()

    return jsonify([dict(student) for student in students])


# CLASSMATE API - READ ONLY
@app.route('/classmate-students')
def get_classmate_students():
    try:
        response = requests.get(
            CLASSMATE_API_URL,
            timeout=30
        )

        response.raise_for_status()

        data = response.json()

        if not isinstance(data, list):
            return jsonify({
                "error": "Invalid classmate API response"
            }), 502

        return jsonify(data)

    except requests.exceptions.RequestException as error:
        app.logger.error("Classmate API error: %s", error)

        return jsonify({
            "error": "Unable to connect to classmate API"
        }), 502

    except ValueError:
        return jsonify({
            "error": "Invalid JSON from classmate API"
        }), 502


# RUN APPLICATION
if __name__ == '__main__':
    app.run(debug=True)
