import streamlit as st

# Set page config for a wide dashboard layout
st.set_page_config(page_title="SmartClassAI Portal", page_icon="⚡", layout="wide")

# Inject Modern Dashboard CSS Styling
st.markdown("""
<style>
    /* Main Background & Theme */
    .stApp {
        background-color: #0e1117;
        color: #ffffff;
    }
    
    /* Hide default Streamlit header/footer branding for a cleaner SaaS look */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Modern Card Containers */
    div.css-1r6slb0, div.stTensorboard, .metric-card {
        background: #161b22;
        border: 1px solid #30363d;
        border-radius: 16px;
        padding: 20px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.4);
    }

    /* Custom Metric Styling */
    [data-testid="stMetricValue"] {
        font-size: 28px;
        font-weight: 700;
        color: #58a6ff;
    }

    /* Pill-styled Buttons */
    .stButton>button {
        border-radius: 12px;
        font-weight: 600;
        border: 1px solid #30363d;
        background-color: #21262d;
        color: #c9d1d9;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #30363d;
        color: #ffffff;
        border-color: #8b949e;
    }

    /* Sidebar Customization */
    section[data-testid="stSidebar"] {
        background-color: #0d1117;
        border-right: 1px solid #30363d;
    }
</style>
""", unsafe_allow_html=True)

# Example Card Layout for your Dashboard
st.title("⚡ SmartClass AI Dashboard")
st.markdown("Take control of your attendance and class telemetry today.")

# Create modern metric columns
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("### 👥 Total Students")
    st.metric(label="Active Enrolled", value="142", delta="+4 this week")

with col2:
    st.markdown("### 📉 Low Attendance Flags")
    st.metric(label="Below 75%", value="8 Students", delta="-2 vs yesterday", delta_color="inverse")

with col3:
    st.markdown("### 🟢 Live Status")
    st.metric(label="System Core", value="Online", delta="99.9% uptime")

from database import (
    create_database,
    verify_user,
    create_teacher_account,
    get_teachers,
    delete_teacher,
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

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.role = ""
    st.session_state.assigned_class = ""

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
    st.title("Smart Classroom Intelligence")
    st.markdown(f"<p style='color: #475569; font-size: 1rem; margin-top: -10px;'>Logged in as: <b>{st.session_state.username}</b> ({st.session_state.role.upper()})</p>", unsafe_allow_html=True)
    st.divider()

    st.sidebar.title("Navigation")
    
    # Dynamic Master Scope Selector based on active database teacher accounts
    if st.session_state.role == "admin":
        st.sidebar.markdown("### Master Scope Selector")
        teachers_list = get_teachers()
        assigned_classes = sorted(list(set([t[1] for t in teachers_list if t[1] and t[1] != "ALL"])))
        scope_options = ["ALL"] + assigned_classes
        
        selected_scope = st.sidebar.selectbox("Active Class View", scope_options)
        active_scope = selected_scope
    else:
        active_scope = st.session_state.assigned_class
        st.sidebar.markdown(f"<p style='font-size: 13px; color: #1e3a8a;'>Assigned Class: <b>{active_scope}</b></p>", unsafe_allow_html=True)

    nav_options = [
        "Dashboard",
        "Student Registration",
        "Face Registration",
        "Attendance",
        "Entry Exit",
        "Live Camera",
        "Face Recognition"
    ]

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

    if page == "Dashboard":
        show_dashboard(active_scope)

    elif page == "Admin Panel" and st.session_state.role == "admin":
        st.markdown("## Master Administration Panel")
        st.markdown("<p style='color: #64748b;'>Create new faculty accounts, manage class assignments, and remove invalid profiles.</p>", unsafe_allow_html=True)

        with st.form("create_teacher_form"):
            st.subheader("Initialize Faculty Account")
            new_user = st.text_input("Teacher Username", placeholder="teacher3")
            new_pass = st.text_input("Teacher Password", type="password", placeholder="securepassword")
            new_class = st.text_input("Assigned Class Scope", placeholder="10-C")
            create_btn = st.form_submit_button("Create Teacher Account")

            if create_btn:
                if not new_user or not new_pass or not new_class:
                    st.warning("All fields are required.")
                else:
                    success = create_teacher_account(new_user, new_pass, new_class)
                    if success:
                        st.success(f"Account successfully created for {new_user} assigned to Class {new_class}!")
                        st.rerun()
                    else:
                        st.error("Username already exists. Choose a different username.")

        st.divider()
        st.markdown("## Active Faculty Accounts Directory")
        
        teachers = get_teachers()
        if teachers:
            for teacher in teachers:
                t_user, t_class, t_role = teacher[0], teacher[1], teacher[2]
                col1, col2 = st.columns([5, 1])

                with col1:
                    st.markdown(f"**Username:** {t_user} &nbsp;|&nbsp; **Class Scope:** {t_class} &nbsp;|&nbsp; **Role:** {t_role.upper()}")

                with col2:
                    if t_user != "admin":
                        if st.button("Delete", key=f"del_tr_{t_user}"):
                            st.session_state[f"confirm_del_tr_{t_user}"] = True

                if st.session_state.get(f"confirm_del_tr_{t_user}", False):
                    st.warning(f"Confirmation Required: Delete account '{t_user}'?")
                    cc1, cc2 = st.columns(2)
                    with cc1:
                        if st.button("Continue", key=f"yes_tr_{t_user}"):
                            delete_teacher(t_user)
                            st.session_state[f"confirm_del_tr_{t_user}"] = False
                            st.success(f"Teacher account '{t_user}' removed.")
                            st.rerun()
                    with cc2:
                        if st.button("Cancel", key=f"no_tr_{t_user}"):
                            st.session_state[f"confirm_del_tr_{t_user}"] = False
                            st.rerun()
        else:
            st.info("No faculty accounts found.")

    elif page == "Student Registration":
        st.markdown("## Student Directory Management")

        with st.form("student_form"):
            student_id = st.text_input("Student Identifier Code", placeholder="S001")
            name = st.text_input("Full Legal Name", placeholder="Alex Mercer")
            
            if st.session_state.role == "admin":
                class_name = st.text_input("Assigned Class", placeholder="10-A")
            else:
                class_name = st.text_input("Assigned Class", value=active_scope, disabled=True)

            submitted = st.form_submit_button("Register New Student")

            if submitted:
                target_class = active_scope if (st.session_state.role != "admin" or active_scope != "ALL") else class_name
                if not student_id or not name or not target_class or target_class == "ALL":
                    st.warning("Validation Warning: Provide a valid specific class name for registration.")
                else:
                    success = add_student(student_id.strip(), name.strip(), target_class.strip())
                    if success:
                        st.success(f"Record successfully initialized for {name} in Class {target_class}.")
                        st.rerun()
                    else:
                        st.error("System Conflict: Target Student ID already exists.")

        st.divider()
        st.markdown(f"## Registered Student Records (Scope: {active_scope})")

        students = get_students(active_scope)
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
            st.info(f"No active student records registered for scope: {active_scope}.")

    elif page == "Face Registration":
        show_face_registration_page()

    elif page == "Attendance":
        show_attendance_page(active_scope)

    elif page == "Entry Exit":
        show_tracking_page()

    elif page == "Live Camera":
        show_live_camera()

    elif page == "Face Recognition":
        show_face_recognition_page()