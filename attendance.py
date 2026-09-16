import streamlit as st
import pandas as pd
from datetime import datetime
import sqlite3
from database import get_custom_holidays, add_custom_holiday, delete_custom_holiday

def get_students(class_filter=None):
    conn = sqlite3.connect('students.db')
    cursor = conn.cursor()
    if class_filter and class_filter != "ALL":
        cursor.execute("SELECT student_id, name FROM students WHERE class_name = ?", (class_filter,))
    else:
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

PRIMARY_INDIAN_HOLIDAYS = {
    "2026-01-26": "Republic Day",
    "2026-03-03": "Holi",
    "2026-03-31": "Id-ul-Fitr",
    "2026-08-15": "Independence Day",
    "2026-10-02": "Mahatma Gandhi Birthday",
    "2026-10-20": "Dussehra",
    "2026-11-08": "Diwali",
    "2026-12-25": "Christmas Day"
}

def show_attendance_page(active_scope="ALL"):
    st.markdown("## Student Attendance Matrix & Reports")
    st.markdown("<p style='color: #64748b;'>Analyze real-time attendance matrix logs, manage emergency holidays, and export reports.</p>", unsafe_allow_html=True)

    if st.session_state.get("role") == "admin":
        with st.expander("Emergency Holiday Management (Admin Override)"):
            with st.form("holiday_form"):
                h_date = st.date_input("Select Emergency Holiday Date")
                h_reason = st.text_input("Reason for Holiday", placeholder="e.g., Extreme Weather / Unforeseen Closure")
                h_submit = st.form_submit_button("Declare Emergency Holiday")
                if h_submit:
                    date_str = h_date.strftime("%Y-%m-%d")
                    add_custom_holiday(date_str, h_reason)
                    st.success(f"Emergency holiday successfully declared for {date_str}.")
                    st.rerun()

            custom_holidays = get_custom_holidays()
            if custom_holidays:
                st.markdown("### Active Emergency Declarations")
                for c_date, reason in custom_holidays.items():
                    col_h1, col_h2 = st.columns([4, 1])
                    with col_h1:
                        st.write(f"**{c_date}** — {reason}")
                    with col_h2:
                        if st.button("Revoke", key=f"rev_{c_date}"):
                            delete_custom_holiday(c_date)
                            st.success(f"Holiday revoked for {c_date}.")
                            st.rerun()

    students = get_students(active_scope)
    if not students:
        st.warning("System Notice: No student records found for the active scope.")
        return

    student_options = {"-- Select Student Profile --": None}
    for s_id, name in students:
        student_options[f"{name} ({s_id})"] = s_id

    selected_display = st.selectbox("Student Directory", list(student_options.keys()))
    selected_student_id = student_options[selected_display]

    if not selected_student_id:
        st.info("Awaiting selection: Choose a student from the dropdown above to display their matrix.")
        return

    attendance_data = get_student_attendance(selected_student_id)
    all_holidays = {**PRIMARY_INDIAN_HOLIDAYS, **get_custom_holidays()}

    total_logs = len(attendance_data)
    present_count = sum(1 for status in attendance_data.values() if status == 'Present')
    absent_count = sum(1 for status in attendance_data.values() if status == 'Absent')
    holiday_count = len(all_holidays)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f'<div class="futuristic-card"><h4>Logged Days</h4><h2>{total_logs}</h2></div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="futuristic-card"><h4>Present</h4><h2 style="color:#10b981;">{present_count}</h2></div>', unsafe_allow_html=True)
    with col3:
        st.markdown(f'<div class="futuristic-card"><h4>Absent</h4><h2 style="color:#ef4444;">{absent_count}</h2></div>', unsafe_allow_html=True)
    with col4:
        st.markdown(f'<div class="futuristic-card"><h4>Total Holidays</h4><h2 style="color:#3b82f6;">{holiday_count}</h2></div>', unsafe_allow_html=True)

    st.markdown("---")
    st.subheader("Interactive Calendar Matrix (2026)")

    months_mapping = {
        "Jan 2026": "2026-01", "Feb 2026": "2026-02", "Mar 2026": "2026-03",
        "Apr 2026": "2026-04", "May 2026": "2026-05", "Jun 2026": "2026-06",
        "Jul 2026": "2026-07", "Aug 2026": "2026-08", "Sep 2026": "2026-09",
        "Oct 2026": "2026-10", "Nov 2026": "2026-11", "Dec 2026": "2026-12"
    }

    matrix_data = {"DATE": list(range(1, 32))}

    for m_label, ym_prefix in months_mapping.items():
        column_values = []
        for day in range(1, 32):
            date_str = f"{ym_prefix}-{day:02d}"
            if date_str in all_holidays:
                column_values.append("HOLIDAY")
            else:
                status = attendance_data.get(date_str)
                if status == 'Present':
                    column_values.append("✓")
                elif status == 'Absent':
                    column_values.append("×")
                else:
                    column_values.append("")
        matrix_data[m_label] = column_values

    df_matrix = pd.DataFrame(matrix_data)
    st.dataframe(df_matrix.set_index("DATE"), use_container_width=True, height=450)

    csv_data = df_matrix.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Download Attendance Report (CSV)",
        data=csv_data,
        file_name=f"attendance_report_{selected_student_id}.csv",
        mime="text/csv",
    )
def mark_attendance(student_id, status="Present"):
    """Marks or updates attendance for a student on the current date."""
    conn = sqlite3.connect('students.db')
    cursor = conn.cursor()

    today_str = datetime.now().strftime("%Y-%m-%d")
    time_str = datetime.now().strftime("%H:%M:%S")

    try:
        cursor.execute("""
            INSERT INTO attendance (student_id, date, time, status)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(student_id, date)
            DO UPDATE SET time = ?, status = ?
        """, (student_id, today_str, time_str, status, time_str, status))

        conn.commit()
        return True
    except Exception as e:
        print(f"Error marking attendance: {e}")
        return False
    finally:
        conn.close()