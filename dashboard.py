import streamlit as st
import sqlite3

def show_dashboard():
    st.markdown("## System Command Center")
    st.write("Real-time telemetry and biometric status overview.")

    # Fetch live counts from database
    try:
        conn = sqlite3.connect('students.db')
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM students")
        total_students = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(DISTINCT student_id) FROM attendance WHERE date = date('now')")
        present_today = cursor.fetchone()[0]
        
        conn.close()
    except Exception:
        total_students = 0
        present_today = 0

    rate = f"{(present_today / total_students * 100):.1f}%" if total_students > 0 else "0.0%"

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f'''
            <div class="futuristic-card">
                <p style="color:#64748b; font-size:14px; font-weight:600; text-transform:uppercase;">Total Registered Students</p>
                <h2 style="font-size:36px; color:#0f172a; margin-top:5px;">{total_students}</h2>
            </div>
        ''', unsafe_allow_html=True)
    with col2:
        st.markdown(f'''
            <div class="futuristic-card">
                <p style="color:#64748b; font-size:14px; font-weight:600; text-transform:uppercase;">Present Today</p>
                <h2 style="font-size:36px; color:#10b981; margin-top:5px;">{present_today}</h2>
            </div>
        ''', unsafe_allow_html=True)
    with col3:
        st.markdown(f'''
            <div class="futuristic-card">
                <p style="color:#64748b; font-size:14px; font-weight:600; text-transform:uppercase;">Attendance Rate</p>
                <h2 style="font-size:36px; color:#6366f1; margin-top:5px;">{rate}</h2>
            </div>
        ''', unsafe_allow_html=True)