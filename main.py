import streamlit as st

# =========================================================
# PAGE CONFIG & STYLING
# =========================================================

st.set_page_config(
    page_title="SmartClassAI - Futuristic Portal",
    page_icon="🛡️",
    layout="wide"
)

# Futuristic Light Theme CSS with Custom Sidebar & Dropdown Accents
st.markdown("""
    <style>
    /* Futuristic Light Background */
    .stApp {
        background: linear-gradient(135deg, #f5f7fa 0%, #e4e9f2 100%);
        font-family: 'Rajdhani', 'Segoe UI', sans-serif;
    }
    
    /* Custom Sidebar (Deep Indigo Theme) */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1e1b4b 0%, #312e81 100%);
        color: #ffffff;
        border-right: 1px solid rgba(255, 255, 255, 0.1);
    }
    [data-testid="stSidebar"] .stMarkdown, [data-testid="stSidebar"] label {
        color: #f8fafc !important;
    }

    /* Custom Dropdown / Selectbox Accent Styling */
    div[data-baseweb="select"] > div {
        background-color: #ffffff;
        border: 2px solid #6366f1;
        border-radius: 10px;
        color: #1e1b4b;
        font-weight: 600;
        box-shadow: 0 4px 12px rgba(99, 102, 241, 0.1);
    }
    div[data-baseweb="select"] span {
        color: #1e1b4b !important;
    }

    /* Cyberpunk / Futuristic Glass Cards */
    .futuristic-card {
        background: rgba(255, 255, 255, 0.85);
        backdrop-filter: blur(10px);
        padding: 22px;
        border-radius: 16px;
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.07);
        border: 1px solid rgba(255, 255, 255, 0.18);
        border-left: 5px solid #6366f1;
        margin-bottom: 20px;
        transition: all 0.3s ease;
    }
    .futuristic-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 12px 40px 0 rgba(99, 102, 241, 0.15);
    }
    
    /* Attendance Status Pills */
    .pill-wd { background-color: #0284c7; color: white; padding: 6px 12px; border-radius: 20px; font-weight: 600; font-size: 14px; }
    .pill-present { background-color: #16a34a; color: white; padding: 6px 12px; border-radius: 20px; font-weight: 600; font-size: 14px; }
    .pill-absent { background-color: #dc2626; color: white; padding: 6px 12px; border-radius: 20px; font-weight: 600; font-size: 14px; }
    .pill-holiday { background-color: #7c3aed; color: white; padding: 6px 12px; border-radius: 20px; font-weight: 600; font-size: 14px; }
    </style>
""", unsafe_allow_html=True)

from database import (
    create_database,
    add_student,
    get_students,
    delete_student
)

from dashboard import show_dashboard
from attendance import show_attendance_page
from tracking import show_tracking_page
from face_recognition import (
    show_face_registration_page,
    show_live_camera,
    show_face_recognition_page
)


# =========================================================
# DATABASE & TITLE
# =========================================================

create_database()

st.title("🏫 AI Smart Classroom")
st.write("Smart Classroom Monitoring System")
st.divider()


# =========================================================
# NAVIGATION
# =========================================================

st.sidebar.title("Navigation")

page = st.sidebar.radio(
    "Navigation Menu",
    [
        "Dashboard",
        "Student Registration",
        "Face Registration",
        "Attendance",
        "Entry Exit",
        "Live Camera",
        "Face Recognition"
    ]
)


# =========================================================
# ROUTING
# =========================================================

if page == "Dashboard":
    show_dashboard()

elif page == "Student Registration":
    st.header("👨‍🎓 Student Registration")

    with st.form("student_form"):
        student_id = st.text_input("Student ID", placeholder="S001")
        name = st.text_input("Student Name", placeholder="Test Student")
        class_name = st.text_input("Class", placeholder="10-A")

        submitted = st.form_submit_button("➕ Register Student")

        if submitted:
            if not student_id or not name or not class_name:
                st.warning("Please fill in all fields.")
            else:
                success = add_student(student_id.strip(), name.strip(), class_name.strip())
                if success:
                    st.success(f"{name} registered successfully! 🎉")
                    st.rerun()
                else:
                    st.error("This Student ID already exists.")

    st.divider()
    st.subheader("📋 Registered Students")

    students = get_students()
    if students:
        for student in students:
            s_id, s_name, s_class, s_enc = student[0], student[1], student[2], student[3]
            col1, col2 = st.columns([5, 1])

            with col1:
                face_status = "🟢 Face Registered" if s_enc else "⚪ Face Not Registered"
                st.write(f"**{s_id}** — {s_name} — Class {s_class} — {face_status}")

            with col2:
                if st.button("🗑️ Delete", key=f"delete_{s_id}"):
                    try:
                        if delete_student(s_id):
                            st.success(f"✅ {s_name} deleted.")
                            st.rerun()
                        else:
                            st.error("❌ Student not found.")
                    except Exception as error:
                        st.error(f"❌ Error: {error}")
    else:
        st.info("No students registered yet.")

elif page == "Face Registration":
    show_face_registration_page()

elif page == "Attendance":
    show_attendance_page()

elif page == "Entry Exit":
    show_tracking_page()

elif page == "Live Camera":
    show_live_camera()

elif page == "Face Recognition":
    show_face_recognition_page()