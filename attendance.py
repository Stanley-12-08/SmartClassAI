import streamlit as st
import pandas as pd
from datetime import datetime
import sqlite3

def get_students():
    conn = sqlite3.connect('students.db')
    cursor = conn.cursor()
    cursor.execute("SELECT student_id, name FROM students")
    students = cursor.fetchall()
    conn.close()
    return students

def get_student_attendance(student_id):
    conn = sqlite3.connect('students.db')
    cursor = conn.cursor()
    cursor.execute("SELECT date, status FROM attendance WHERE student_id = ?", (student_id,))
    records = cursor.fetchall()
    conn.close()
    return {row[0]: row[1] for row in records}

# Primary Indian National & Religious Calendar Holidays (2026-2027)
PRIMARY_INDIAN_HOLIDAYS = {
    "2026-01-26": "Republic Day",
    "2026-03-03": "Holi",
    "2026-03-31": "Id-ul-Fitr",
    "2026-08-15": "Independence Day",
    "2026-10-02": "Mahatma Gandhi Birthday",
    "2026-10-20": "Dussehra",
    "2026-11-08": "Diwali",
    "2026-12-25": "Christmas Day",
    "2027-01-26": "Republic Day",
    "2027-03-22": "Id-ul-Fitr",
    "2027-03-24": "Holi"
}

def show_attendance_page():
    st.markdown("## Student Attendance Matrix")
    st.write("Select an active student profile to analyze biometric logs and attendance distribution.")

    students = get_students()
    if not students:
        st.warning("No student records found in database. Register students to view matrix tracking.")
        return

    # Student Selector Dropdown (No default preview until chosen)
    student_options = {"-- Select Student Profile --": None}
    for s_id, name in students:
        student_options[f"{name} ({s_id})"] = s_id

    selected_display = st.selectbox("Student Directory", list(student_options.keys()))
    selected_student_id = student_options[selected_display]

    if not selected_student_id:
        st.info("Select a student from the dropdown above to render their attendance matrix.")
        return

    attendance_data = get_student_attendance(selected_student_id)

    total_logs = len(attendance_data)
    present_count = sum(1 for status in attendance_data.values() if status == 'Present')
    absent_count = sum(1 for status in attendance_data.values() if status == 'Absent')
    holiday_count = len(PRIMARY_INDIAN_HOLIDAYS)

    # High-Tech Metric Cards (No Emojis)
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f'<div class="futuristic-card"><h4>Logged Days</h4><h2>{total_logs}</h2></div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="futuristic-card"><h4>Present</h4><h2 style="color:#10b981;">{present_count}</h2></div>', unsafe_allow_html=True)
    with col3:
        st.markdown(f'<div class="futuristic-card"><h4>Absent</h4><h2 style="color:#ef4444;">{absent_count}</h2></div>', unsafe_allow_html=True)
    with col4:
        st.markdown(f'<div class="futuristic-card"><h4>National/Festival Holidays</h4><h2 style="color:#8b5cf6;">{holiday_count}</h2></div>', unsafe_allow_html=True)

    st.markdown("---")
    st.subheader("Interactive Calendar Matrix (2026 - 2027)")

    months_mapping = {
        "Apr 2026": "2026-04", "May 2026": "2026-05", "Jun 2026": "2026-06",
        "Jul 2026": "2026-07", "Aug 2026": "2026-08", "Sep 2026": "2026-09",
        "Oct 2026": "2026-10", "Nov 2026": "2026-11", "Dec 2026": "2026-12",
        "Jan 2027": "2027-01", "Feb 2027": "2027-02", "Mar 2027": "2027-03"
    }

    matrix_data = {"DATE": list(range(1, 32))}

    for m_label, ym_prefix in months_mapping.items():
        column_values = []
        for day in range(1, 32):
            date_str = f"{ym_prefix}-{day:02d}"
            if date_str in PRIMARY_INDIAN_HOLIDAYS:
                column_values.append("HOLIDAY")
            else:
                status = attendance_data.get(date_str)
                if status == 'Present':
                    column_values.append("PRESENT")
                elif status == 'Absent':
                    column_values.append("ABSENT")
                else:
                    column_values.append("")
        matrix_data[m_label] = column_values

    df_matrix = pd.DataFrame(matrix_data)
    st.dataframe(df_matrix.set_index("DATE"), use_container_width=True, height=550)

def mark_attendance(student_id):
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
        return True
    except Exception:
        return False
    finally:
        conn.close()