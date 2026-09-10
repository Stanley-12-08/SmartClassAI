import streamlit as st

from database import get_students
from attendance import get_today_attendance
from tracking import get_today_movements


def show_dashboard():
    st.title("🏫 AI Smart Classroom")

    students = get_students()
    attendance = get_today_attendance()
    movements = get_today_movements()

    total_students = len(students)
    present_today = len(attendance)
    movement_records = len(movements)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Total Students",
            total_students
        )

    with col2:
        st.metric(
            "Present Today",
            present_today
        )

    with col3:
        st.metric(
            "Movement Records",
            movement_records
        )

    st.divider()

    st.subheader("📊 Today's Attendance")

    if attendance:
        for record in attendance:
            student_id, name, class_name, date, time, status = record

            st.write(
                f"**{student_id}** — {name} — "
                f"Class: {class_name} — "
                f"{time} — {status}"
            )
    else:
        st.info("No attendance recorded today.")

    st.subheader("🚪 Today's Entry / Exit")

    if movements:
        for record in movements:
            student_id, name, class_name, date, entry, exit_time = record

            st.write(
                f"**{student_id}** — {name} — "
                f"Entry: {entry or '-'} — "
                f"Exit: {exit_time or 'Still inside'}"
            )
    else:
        st.info("No movement records today.")