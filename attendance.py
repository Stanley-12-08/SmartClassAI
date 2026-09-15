import streamlit as st
import pandas as pd
from datetime import datetime
import sqlite3

def get_students():
    """Fetch registered students from SQLite database."""
    conn = sqlite3.connect('students.db')
    cursor = conn.cursor()
    cursor.execute("SELECT student_id, name FROM students")
    students = cursor.fetchall()
    conn.close()
    return students

def get_student_attendance(student_id):
    """Fetch attendance records for a specific student."""
    conn = sqlite3.connect('students.db')
    cursor = conn.cursor()
    cursor.execute("SELECT date, status FROM attendance WHERE student_id = ?", (student_id,))
    records = cursor.fetchall()
    conn.close()
    return {row[0]: row[1] for row in records}

def show_attendance_page():
    st.markdown("## 📅 Student Attendance Matrix")
    st.write("Select a student to review their attendance records.")

    students = get_students()
    if not students:
        st.warning("No students found in the database. Please register students first.")
        return

    # Student selector dropdown
    student_options = {f"{name} ({s_id})": s_id for s_id, name in students}
    selected_display = st.selectbox("Select Student", list(student_options.keys()))
    selected_student_id = student_options[selected_display]

    # Fetch actual attendance records from DB
    attendance_data = get_student_attendance(selected_student_id)

    total_records = len(attendance_data)
    present_count = sum(1 for status in attendance_data.values() if status == 'Present')
    absent_count = sum(1 for status in attendance_data.values() if status == 'Absent')

    # Summary stat cards
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f'<div class="portal-card"><span class="pill-wd">Total Records: {total_records}</span></div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="portal-card"><span class="pill-present">Present: {present_count}</span></div>', unsafe_allow_html=True)
    with col3:
        st.markdown(f'<div class="portal-card"><span class="pill-absent">Absent: {absent_count}</span></div>', unsafe_allow_html=True)
    with col4:
        st.markdown(f'<div class="portal-card"><span class="pill-holiday">Holiday: 0</span></div>', unsafe_allow_html=True)

    st.markdown("---")
    st.subheader("Monthly Attendance Calendar Grid")

    year_month_mapping = {
        "Apr 2026": "2026-04", "May 2026": "2026-05", "Jun 2026": "2026-06",
        "Jul 2026": "2026-07", "Aug 2026": "2026-08", "Sep 2026": "2026-09",
        "Oct 2026": "2026-10", "Nov 2026": "2026-11", "Dec 2026": "2026-12",
        "Jan 2027": "2027-01", "Feb 2027": "2027-02", "Mar 2027": "2027-03"
    }

    data = {"DATE": list(range(1, 32))}

    for m_label, ym_prefix in year_month_mapping.items():
        column_values = []
        for day in range(1, 32):
            date_str = f"{ym_prefix}-{day:02d}"
            status = attendance_data.get(date_str)
            if status == 'Present':
                column_values.append("✅")
            elif status == 'Absent':
                column_values.append("❌")
            else:
                column_values.append("")
        data[m_label] = column_values

    df_matrix = pd.DataFrame(data)

    st.dataframe(
        df_matrix.set_index("DATE"),
        use_container_width=True,
        height=600
    )

def mark_attendance(student_id):
    """Marks attendance for a student for the current date in SQLite database."""
    conn = sqlite3.connect('students.db')
    cursor = conn.cursor()
    
    today = datetime.now().strftime('%Y-%m-%d')
    current_time = datetime.now().strftime('%H:%M:%S')
    
    try:
        cursor.execute('''
            INSERT OR IGNORE INTO attendance (student_id, date, time, status)
            VALUES (?, ?, ?, 'Present')
        ''', (student_id, today, current_time))
        conn.commit()
    except Exception as e:
        print(f"Error marking attendance: {e}")
    finally:
        conn.close()