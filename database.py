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

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS teachers (
            username TEXT PRIMARY KEY,
            password TEXT NOT NULL,
            assigned_class TEXT NOT NULL
        )
    """)

    # Insert default sample teachers if table is empty
    cursor.execute("SELECT COUNT(*) FROM teachers")
    if cursor.fetchone()[0] == 0:
        cursor.execute(
            "INSERT INTO teachers (username, password, assigned_class) VALUES (?, ?, ?)",
            ("teacher1", "password123", "10-A")
        )
        cursor.execute(
            "INSERT INTO teachers (username, password, assigned_class) VALUES (?, ?, ?)",
            ("teacher2", "password123", "10-B")
        )

    conn.commit()
    conn.close()


def verify_teacher(username, password):
    """Verifies teacher credentials and returns their assigned class."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT assigned_class FROM teachers WHERE username = ? AND password = ?",
        (username.strip(), password.strip())
    )
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None


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
# GET STUDENTS (With optional class filtering)
# =========================================================

def get_students(class_filter=None):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    if class_filter:
        cursor.execute("""
            SELECT student_id, name, class_name, face_encoding 
            FROM students 
            WHERE class_name = ? 
            ORDER BY id DESC
        """, (class_filter,))
    else:
        cursor.execute("""
            SELECT student_id, name, class_name, face_encoding 
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
        cursor.execute("""
            DELETE FROM attendance
            WHERE student_id = ?
        """, (student_id,))

        cursor.execute("""
            DELETE FROM movement_logs
            WHERE student_id = ?
        """, (student_id,))

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