import streamlit as st

# =========================================================
# PAGE CONFIG & ADVANCED LIGHT THEME
# =========================================================

st.set_page_config(
    page_title="SmartClassAI - Advanced Portal",
    page_icon="⚡",
    layout="wide"
)

# Advanced Light Theme CSS with Custom Sidebar, Dropdowns, and Animations
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Rajdhani:wght@500;600;700&display=swap');

    /* Mint Blue & Ice Blue Theme Background */
    .stApp {
        background: linear-gradient(135deg, #f0f4f8 0%, #e2e8f5 100%);
        font-family: 'Inter', sans-serif;
        color: #0f172a;
        animation: fadeIn 0.5s ease-out;
    }

    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(4px); }
        to { opacity: 1; transform: translateY(0); }
    }

    /* Mint Blue Custom Sidebar Styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #dbeafe 0%, #eff6ff 100%);
        border-right: 1px solid #b5c7eb;
        box-shadow: 4px 0 24px rgba(181, 199, 235, 0.2);
    }
    [data-testid="stSidebar"] .stMarkdown, [data-testid="stSidebar"] label {
        color: #1e3a8a !important;
        font-family: 'Inter', sans-serif;
        font-weight: 600;
    }

    /* Active Radio / Navigation Selection Styling */
    [data-testid="stSidebar"] [checked] + div {
        background-color: #3b82f6 !important;
        color: white !important;
    }

    /* Custom Dropdown / Selectbox Styling */
    div[data-baseweb="select"] > div {
        background-color: #ffffff;
        border: 1px solid #b5c7eb;
        border-radius: 8px;
        color: #0f172a;
        font-weight: 500;
        box-shadow: 0 2px 6px rgba(181, 199, 235, 0.2);
    }
    div[data-baseweb="select"] span {
        color: #0f172a !important;
    }

    /* Glassmorphism Cards with Mint/Blue Accents */
    .futuristic-card {
        background: rgba(255, 255, 255, 0.9);
        backdrop-filter: blur(10px);
        padding: 24px;
        border-radius: 14px;
        box-shadow: 0 10px 25px -5px rgba(181, 199, 235, 0.25), 0 8px 10px -6px rgba(0, 0, 0, 0.02);
        border: 1px solid #cbd5e1;
        border-left: 4px solid #3b82f6;
        margin-bottom: 20px;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    .futuristic-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 20px 35px -10px rgba(59, 130, 246, 0.2);
        border-color: #b5c7eb;
    }

    /* Typography Overrides */
    h1, h2, h3 {
        font-family: 'Rajdhani', sans-serif !important;
        letter-spacing: -0.02em;
        color: #1e3a8a;
    }

    /* Mint-Blue Accent Buttons */
    div.stButton > button {
        background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
        color: white;
        border: none;
        padding: 0.6rem 1.4rem;
        border-radius: 8px;
        font-weight: 600;
        font-family: 'Inter', sans-serif;
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.25);
        transition: all 0.2s ease;
    }
    div.stButton > button:hover {
        background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
        box-shadow: 0 6px 16px rgba(59, 130, 246, 0.4);
        transform: translateY(-1px);
    }

    /* Vector CSS Indicator Dots */
    .status-dot-active {
        height: 9px;
        width: 9px;
        background-color: #10b981;
        border-radius: 50%;
        display: inline-block;
        box-shadow: 0 0 8px rgba(16, 185, 129, 0.5);
        margin-right: 8px;
    }
    .status-dot-inactive {
        height: 9px;
        width: 9px;
        background-color: #94a3b8;
        border-radius: 50%;
        display: inline-block;
        margin-right: 8px;
    }
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

st.title("Smart Classroom Intelligence")
st.markdown("<p style='color: #64748b; font-size: 1.1rem; margin-top: -10px;'>Advanced Telemetry and Monitoring Portal</p>", unsafe_allow_html=True)
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
    st.markdown("## Student Directory Management")

    with st.form("student_form"):
        student_id = st.text_input("Student Identifier Code", placeholder="S001")
        name = st.text_input("Full Legal Name", placeholder="Alex Mercer")
        class_name = st.text_input("Assigned Class", placeholder="10-A")

        submitted = st.form_submit_button("Register New Student")

        if submitted:
            if not student_id or not name or not class_name:
                st.warning("Validation Warning: All input fields are required.")
            else:
                success = add_student(student_id.strip(), name.strip(), class_name.strip())
                if success:
                    st.success(f"Record successfully initialized for {name}.")
                    st.rerun()
                else:
                    st.error("System Conflict: Target Student ID already exists.")

    st.divider()
    st.markdown("## Registered Student Records")

    students = get_students()
    if students:
        for student in students:
            s_id, s_name, s_class, s_enc = student[0], student[1], student[2], student[3]
            col1, col2 = st.columns([5, 1])

            with col1:
                face_status_html = (
                    '<span class="status-dot-active"></span>Biometric Active'
                    if s_enc
                    else '<span class="status-dot-inactive"></span>Awaiting Biometrics'
                )
                st.markdown(
                    f"**ID: {s_id}** &nbsp;|&nbsp; Name: {s_name} &nbsp;|&nbsp; Class: {s_class} &nbsp;|&nbsp; {face_status_html}",
                    unsafe_allow_html=True
                )

            with col2:
                if st.button("Delete", key=f"delete_{s_id}"):
                    try:
                        if delete_student(s_id):
                            st.success(f"Record removed for {s_name}.")
                            st.rerun()
                        else:
                            st.error("Target record not found.")
                    except Exception as error:
                        st.error(f"Error: {error}")
    else:
        st.info("No active student records registered in the system.")

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