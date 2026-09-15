import streamlit as st
import pandas as pd
from datetime import datetime
import sqlite3

def show_attendance_page():
    st.markdown("## 📅 Student Attendance Overview")
    st.write("Detailed matrix record mapping daily attendance across months.")

    # Top Summary Stat Pills Layout
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown('<div class="portal-card"><span class="pill-wd">Working Days (WD): 81</span></div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="portal-card"><span class="pill-present">Present (P): 81</span></div>', unsafe_allow_html=True)
    with col3:
        st.markdown('<div class="portal-card"><span class="pill-absent">Absent (A): 0</span></div>', unsafe_allow_html=True)
    with col4:
        st.markdown('<div class="portal-card"><span class="pill-holiday">Holiday (H): 10</span></div>', unsafe_allow_html=True)

    st.markdown("---")
    st.subheader("Attendance Matrix Grid (2026 - 2027)")

    # Generate sample matrix layout matching the reference image format
    months = ["Apr 2026", "May 2026", "Jun 2026", "Jul 2026", "Aug 2026", "Sep 2026", 
              "Oct 2026", "Nov 2026", "Dec 2026", "Jan 2027", "Feb 2027", "Mar 2027"]
    
    # Create days 1 to 31 rows
    data = {}
    data["DATE"] = list(range(1, 32))
    
    for month in months:
        column_values = []
        for day in range(1, 32):
            if day in [3, 5] and month == "Apr 2026":
                column_values.append("H")
            elif day <= 15 and month in ["Apr 2026", "Jul 2026", "Aug 2026", "Sep 2026"]:
                column_values.append("✅")
            else:
                column_values.append("")
        data[month] = column_values

    df_matrix = pd.DataFrame(data)

    # Render the interactive dataframe table with custom styling
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