import sqlite3
import streamlit as st
from datetime import datetime

from database import DB_NAME


def mark_attendance(student_id):
    now = datetime.now()

    date = now.strftime("%Y-%m-%d")
    time = now.strftime("%H:%M:%S")

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    try:
        cursor.execute("""
            INSERT INTO attendance
            (student_id, date, time, status)
            VALUES (?, ?, ?, ?)
        """, (
            student_id,
            date,
            time,
            "Present"
        ))

        conn.commit()
        result = True

    except sqlite3.IntegrityError:
        result = False

    finally:
        conn.close()

    return result


def get_today_attendance():
    today = datetime.now().strftime("%Y-%m-%d")

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            attendance.student_id,
            students.name,
            students.class_name,
            attendance.date,
            attendance.time,
            attendance.status
        FROM attendance
        LEFT JOIN students
        ON attendance.student_id = students.student_id
        WHERE attendance.date = ?
        ORDER BY attendance.time DESC
    """, (today,))

    records = cursor.fetchall()
    conn.close()

    return records


def show_attendance_page():
    st.title("📋 Attendance")

    records = get_today_attendance()

    if records:
        st.success(f"{len(records)} student(s) present today.")

        for record in records:
            student_id, name, class_name, date, time, status = record

            st.write(
                f"**{student_id}** — {name} — "
                f"Class: {class_name} — "
                f"{time} — {status}"
            )
    else:
        st.info("No attendance has been recorded today.")