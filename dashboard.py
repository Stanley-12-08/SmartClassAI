import streamlit as st
import sqlite3

def show_dashboard(active_scope="ALL"):
    st.markdown("## Operational Analytics Dashboard")
    st.markdown("<p style='color: #64748b;'>Real-time telemetry and student attendance status overview.</p>", unsafe_allow_html=True)

    conn = sqlite3.connect('students.db')
    cursor = conn.cursor()

    if active_scope and active_scope != "ALL":
        cursor.execute("SELECT COUNT(*) FROM students WHERE class_name = ?", (active_scope,))
        total_students = cursor.fetchone()[0]
        cursor.execute("SELECT student_id, name, class_name FROM students WHERE class_name = ?", (active_scope,))
    else:
        cursor.execute("SELECT COUNT(*) FROM students")
        total_students = cursor.fetchone()[0]
        cursor.execute("SELECT student_id, name, class_name FROM students")

    students = cursor.fetchall()
    conn.close()

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f'<div class="futuristic-card"><h4>Active Scope</h4><h2>Class {active_scope}</h2></div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="futuristic-card"><h4>Enrolled Students</h4><h2>{total_students}</h2></div>', unsafe_allow_html=True)
    with col3:
        st.markdown(f'<div class="futuristic-card"><h4>System Status</h4><h2 style="color:#10b981;">Operational</h2></div>', unsafe_allow_html=True)

    st.markdown("---")
    st.subheader("Attendance Compliance & Low-Attendance Flags")

    if not students:
        st.info("No registered students found for telemetry analysis.")
        return

    conn = sqlite3.connect('students.db')
    cursor = conn.cursor()

    for s_id, s_name, s_class in students:
        cursor.execute("SELECT COUNT(*) FROM attendance WHERE student_id = ? AND status = 'Present'", (s_id,))
        present_days = cursor.fetchone()[0]
        
        attendance_pct = (present_days / 20) * 100 if present_days > 0 else 0.0

        badge_color = "#10b981" if attendance_pct >= 75 else "#ef4444"
        status_label = "Compliant" if attendance_pct >= 75 else "Low Attendance Warning (<75%)"

        st.markdown(f"""
            <div style="background: white; padding: 16px; border-radius: 10px; border: 1px solid #cbd5e1; margin-bottom: 10px; display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <strong>{s_name}</strong> (ID: {s_id}) &nbsp;|&nbsp; Class: {s_class}
                </div>
                <div>
                    <span style="color: {badge_color}; font-weight: 600;">{attendance_pct:.1f}% Present ({status_label})</span>
                </div>
            </div>
        """, unsafe_allow_html=True)

    conn.close()