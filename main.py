import streamlit as st

# =========================================================
# PAGE CONFIG & MINT BLUE THEME STYLING
# =========================================================

st.set_page_config(
    page_title="SmartClassAI - Portal",
    page_icon="⚡",
    layout="wide"
)

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Rajdhani:wght@500;600;700&display=swap');

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

    div[data-baseweb="select"] > div {
        background-color: #ffffff;
        border: 1px solid #b5c7eb;
        border-radius: 8px;
        color: #0f172a;
        font-weight: 500;
    }

    .futuristic-card {
        background: rgba(255, 255, 255, 0.9);
        backdrop-filter: blur(10px);
        padding: 24px;
        border-radius: 14px;
        box-shadow: 0 10px 25px -5px rgba(181, 199, 235, 0.25);
        border: 1px solid #cbd5e1;
        border-left: 4px solid #3b82f6;
        margin-bottom: 20px;
    }

    h1, h2, h3 {
        font-family: 'Rajdhani', sans-serif !important;
        color: #1e3a8a;
    }

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
        transform: translateY(-1px);
    }

    .status-dot-active {
        height: 9px; width: 9px; background-color: #10b981; border-radius: 50%; display: inline-block; margin-right: 8px;
    }
    .status-dot-inactive {
        height: 9px; width: 9px; background-color: #94a3b8; border-radius: 50%; display: inline-block; margin-right: 8px;
    }
    </style>
""", unsafe_allow_html=True)

from database import (
    create_database,
    verify_user,
    create_teacher_account,
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

create_database()

# =========================================================
# SESSION STATE INITIALIZATION
# =========================================================

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.role = ""
    st.session_state.assigned_class = ""

# =========================================================
# LOGIN GATE SCREEN
# =========================================================

if not st.session_state.logged_in:
    st.markdown("<br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1.2, 1])
    
    with col2:
        st.markdown('<div class="futuristic-card">', unsafe_allow_html=True)
        st.markdown("## Portal Authentication")
        st.markdown("<p style='color: #64748b;'>Enter credentials to access system telemetry.</p>", unsafe_allow_html=True)
        
        with st.form("login_form"):
            username_input = st.text_input("Username", placeholder="admin or teacher1")
            password_input = st.text_input("Password", type="password", placeholder="••••••••")
            login_submitted = st.form_submit_button("Authenticate Session")
            
            if login_submitted:
                role, assigned_class = verify_user(username_input, password_input)
                if role:
                    st.session_state.logged_in = True
                    st.session_state.username = username_input
                    st.session_state.role = role
                    st.session_state.assigned_class = assigned_class
                    st.success(f"Access Granted. Role: {role.upper()} | Scope: {assigned_class}")
                    st.rerun()
                else:
                    st.error("Authentication Failed: Invalid username or password.")
        
        st.markdown("<p style='font-size: 12px; color: #64748b; margin-top: 15px;'>Admin Demo: <b>admin</b> / <b>admin123</b><br>Teacher Demo: <b>teacher1</b> / <b>password123</b></p>", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

else:
    # =========================================================
    # MAIN PORTAL (AFTER SUCCESSFUL LOGIN)
    # =========================================================

    st.title("Smart Classroom Intelligence")
    st.markdown(f"<p style='color: #475569; font-size: 1rem; margin-top: -10px;'>Logged in as: <b>{st.session_state.username}</b> ({st.session_state.role.upper()}) &nbsp;|&nbsp; Scope: <b>{st.session_state.assigned_class}</b></p>", unsafe_allow_html=True)
    st.divider()

    st.sidebar.title("Navigation")
    st.sidebar.markdown(f"<p style='font-size: 13px; color: #1e3a8a;'>Role: <b>{st.session_state.role.upper()}</b></p>", unsafe_allow_html=True)
    
    nav_options = [
        "Dashboard",
        "Student Registration",
        "Face Registration",
        "Attendance",
        "Entry Exit",
        "Live Camera",
        "Face Recognition"
    ]

    # Add Admin Panel option if user is admin
    if st.session_state.role == "admin":
        nav_options.insert(1, "Admin Panel")

    page = st.sidebar.radio("Navigation Menu", nav_options)

    st.sidebar.divider()
    if st.sidebar.button("Terminate Session"):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.session_state.role = ""
        st.session_state.assigned_class = ""
        st.rerun()

    class_filter = st.session_state.assigned_class

    # =========================================================
    # PAGE ROUTING
    # =========================================================

    if page == "Dashboard":
        show_dashboard(class_filter)

    elif page == "Admin Panel" and st.session_state.role == "admin":
        st.markdown("## Master Administration Panel")
        st.markdown("<p style='color: #64748b;'>Create new faculty accounts and manage class assignments.</p>", unsafe_allow_html=True)

        with st.form("create_teacher_form"):
            new_user = st.text_input("New Teacher Username", placeholder="teacher3")
            new_pass = st.text_input("New Teacher Password", type="password", placeholder="securepassword")
            new_class = st.text_input("Assigned Class", placeholder="10-C")
            create_btn = st.form_submit_button("Create Teacher Account")

            if create_btn:
                if not new_user or not new_pass or not new_class:
                    st.warning("All fields are required.")
                else:
                    success = create_teacher_account(new_user, new_pass, new_class)
                    if success:
                        st.success(f"Account successfully created for {new_user} assigned to Class {new_class}!")
                    else:
                        st.error("Username already exists. Choose a different username.")

    elif page == "Student Registration":
        st.markdown("## Student Directory Management")

        with st.form("student_form"):
            student_id = st.text_input("Student Identifier Code", placeholder="S001")
            name = st.text_input("Full Legal Name", placeholder="Alex Mercer")
            
            # If admin, let them type class name; if teacher, lock to their assigned class
            if st.session_state.role == "admin":
                class_name = st.text_input("Assigned Class", placeholder="10-A")
            else:
                class_name = st.text_input("Assigned Class", value=class_filter, disabled=True)

            submitted = st.form_submit_button("Register New Student")

            if submitted:
                target_class = class_filter if st.session_state.role != "admin" else class_name
                if not student_id or not name or not target_class:
                    st.warning("Validation Warning: All input fields are required.")
                else:
                    success = add_student(student_id.strip(), name.strip(), target_class.strip())
                    if success:
                        st.success(f"Record successfully initialized for {name} in Class {target_class}.")
                        st.rerun()
                    else:
                        st.error("System Conflict: Target Student ID already exists.")

        st.divider()
        st.markdown(f"## Registered Student Records (Scope: {class_filter})")

        students = get_students(class_filter)
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
            st.info(f"No active student records registered for scope: {class_filter}.")

    elif page == "Face Registration":
        show_face_registration_page(class_filter)

    elif page == "Attendance":
        show_attendance_page(class_filter)

    elif page == "Entry Exit":
        show_tracking_page(class_filter)

    elif page == "Live Camera":
        show_live_camera(class_filter)

    elif page == "Face Recognition":
        show_face_recognition_page(class_filter)