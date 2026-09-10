import sqlite3
import pickle
from datetime import datetime


DB_NAME = "students.db"


# =========================================================
# CREATE DATABASE
# =========================================================

def create_database():

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            class_name TEXT NOT NULL,
            face_encoding BLOB,
            created_at TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT NOT NULL,
            date TEXT NOT NULL,
            time TEXT NOT NULL,
            status TEXT NOT NULL,
            UNIQUE(student_id, date)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS movement_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT NOT NULL,
            date TEXT NOT NULL,
            entry_time TEXT,
            exit_time TEXT
        )
    """)

    conn.commit()
    conn.close()


# =========================================================
# ADD STUDENT
# =========================================================

def add_student(student_id, name, class_name):

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    try:

        cursor.execute("""
            INSERT INTO students
            (
                student_id,
                name,
                class_name,
                created_at
            )
            VALUES (?, ?, ?, ?)
        """, (
            student_id,
            name,
            class_name,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ))

        conn.commit()

        return True

    except sqlite3.IntegrityError:

        return False

    finally:

        conn.close()


# =========================================================
# GET STUDENTS
# =========================================================

def get_students():

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            student_id,
            name,
            class_name,
            face_encoding
        FROM students
        ORDER BY id DESC
    """)

    students = cursor.fetchall()

    conn.close()

    return students


# =========================================================
# SAVE FACE
# =========================================================

def save_face_encoding(student_id, encoding):

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE students
        SET face_encoding = ?
        WHERE student_id = ?
    """, (
        pickle.dumps(encoding),
        student_id
    ))

    conn.commit()
    conn.close()


# =========================================================
# DELETE STUDENT + ALL DATA
# =========================================================

def delete_student(student_id):

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    try:

        # Delete attendance
        cursor.execute("""
            DELETE FROM attendance
            WHERE student_id = ?
        """, (student_id,))

        # Delete entry/exit records
        cursor.execute("""
            DELETE FROM movement_logs
            WHERE student_id = ?
        """, (student_id,))

        # Delete student
        cursor.execute("""
            DELETE FROM students
            WHERE student_id = ?
        """, (student_id,))

        deleted_rows = cursor.rowcount

        conn.commit()

        return deleted_rows > 0

    except Exception:

        conn.rollback()

        raise

    finally:

        conn.close()