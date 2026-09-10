import sqlite3
import streamlit as st
from datetime import datetime

from database import DB_NAME


def record_entry_exit(student_id):
    now = datetime.now()

    date = now.strftime("%Y-%m-%d")
    time = now.strftime("%H:%M:%S")

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, entry_time, exit_time
        FROM movement_logs
        WHERE student_id = ? AND date = ?
        ORDER BY id DESC
        LIMIT 1
    """, (student_id, date))

    record = cursor.fetchone()

    if record is None:
        cursor.execute("""
            INSERT INTO movement_logs
            (student_id, date, entry_time, exit_time)
            VALUES (?, ?, ?, ?)
        """, (
            student_id,
            date,
            time,
            None
        ))

        result = "Entry recorded"

    elif record[2] is None:
        cursor.execute("""
            UPDATE movement_logs
            SET exit_time = ?
            WHERE id = ?
        """, (
            time,
            record[0]
        ))

        result = "Exit recorded"

    else:
        cursor.execute("""
            INSERT INTO movement_logs
            (student_id, date, entry_time, exit_time)
            VALUES (?, ?, ?, ?)
        """, (
            student_id,
            date,
            time,
            None
        ))

        result = "Entry recorded"

    conn.commit()
    conn.close()

    return result


def get_today_movements():
    today = datetime.now().strftime("%Y-%m-%d")

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            movement_logs.student_id,
            students.name,
            students.class_name,
            movement_logs.date,
            movement_logs.entry_time,
            movement_logs.exit_time
        FROM movement_logs
        LEFT JOIN students
        ON movement_logs.student_id = students.student_id
        WHERE movement_logs.date = ?
        ORDER BY movement_logs.id DESC
    """, (today,))

    records = cursor.fetchall()
    conn.close()

    return records


def show_tracking_page():
    st.title("🚪 Entry / Exit Tracking")

    records = get_today_movements()

    if records:
        for record in records:
            student_id, name, class_name, date, entry, exit_time = record

            st.write(
                f"**{student_id}** — {name} — "
                f"Class: {class_name} — "
                f"Entry: {entry or '-'} — "
                f"Exit: {exit_time or 'Still inside'}"
            )
    else:
        st.info("No entry or exit records for today.")