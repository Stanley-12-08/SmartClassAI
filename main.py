import streamlit as st

st.set_page_config(page_title="SmartClassAI Portal", page_icon="⚡", layout="wide")

# 1. THEME SWITCH TOGGLE (Top Right)
top_col1, top_col2 = st.columns([8, 2])
with top_col2:
    is_dark = st.toggle("🌙 Dark Mode", value=True)

# 2. ADVANCED COLOR PALETTE & GLOW EFFECTS
if is_dark:
    bg_main = "#0b0f19"           # Deep space dark
    sidebar_bg = "#070a10"        # Darker sidebar
    card_bg = "#151b28"           # Slightly elevated card color
    text_primary = "#ffffff"      # Pure white for absolute visibility
    text_secondary = "#94a3b8"    # Cool gray
    mint_accent = "#00f5d4"       # Neon Mint
    mint_glow = "rgba(0, 245, 212, 0.4)" # Hover glow shadow
    card_border = "1px solid rgba(0, 245, 212, 0.15)"
    input_bg = "#1e293b"          # Input field background
else:
    bg_main = "#f8fafc"           # Clean crisp light gray
    sidebar_bg = "#f1f5f9"
    card_bg = "#ffffff"           # Solid white card
    text_primary = "#0f172a"      # Deep slate text
    text_secondary = "#64748b"    # Subdued text
    mint_accent = "#0d9488"       # Deep Mint Blue (high contrast)
    mint_glow = "rgba(13, 148, 136, 0.3)"
    card_border = "1px solid rgba(13, 148, 136, 0.2)"
    input_bg = "#f8fafc"

# 3. DEEP CSS INJECTION (Fixes invisible text, adds animations & hover states)
st.markdown(f"""
<style>
    /* Hide top header bar & footer */
    #MainMenu, footer, header {{ visibility: hidden; }}

    /* 🟢 ANIMATIONS */
    @keyframes fadeUp {{
        from {{ opacity: 0; transform: translateY(20px); }}
        to {{ opacity: 1; transform: translateY(0); }}
    }}

    @keyframes pulseGlow {{
        0% {{ box-shadow: 0 0 0 0 {mint_glow}; }}
        70% {{ box-shadow: 0 0 15px 10px rgba(0,0,0,0); }}
        100% {{ box-shadow: 0 0 0 0 rgba(0,0,0,0); }}
    }}

    /* 🟢 GLOBAL VISIBILITY & BACKGROUNDS */
    .stApp, [data-testid="stAppViewContainer"], section.main {{
        background-color: {bg_main} !important;
        color: {text_primary} !important;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }}
    
    [data-testid="stSidebar"] {{
        background-color: {sidebar_bg} !important;
    }}

    /* Force all text elements to obey visibility colors */
    h1, h2, h3, h4, p, span, label, div {{
        color: {text_primary} !important;
    }}
    .brand-subtitle {{ color: {text_secondary} !important; font-size: 1.1rem; margin-bottom: 24px; }}
    .brand-title {{ font-size: 2.8rem; font-weight: 900; color: {mint_accent} !important; letter-spacing: -1px; margin-bottom: 4px; }}

    /* 🟢 MODERN HOVER CARDS */
    .flux-card {{
        background-color: {card_bg};
        border: {card_border};
        border-radius: 20px;
        padding: 30px;
        box-shadow: 0 8px 30px rgba(0, 0, 0, 0.1);
        margin-top: 15px;
        margin-bottom: 20px;
        animation: fadeUp 0.6s cubic-bezier(0.16, 1, 0.3, 1) forwards;
        transition: transform 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275), box-shadow 0.3s ease;
        cursor: default;
    }}
    
    .flux-card:hover {{
        transform: translateY(-6px);
        box-shadow: 0 15px 35px {mint_glow};
        border: 1px solid {mint_accent};
    }}

    /* 🟢 INPUT FIELDS & DROPDOWNS (Fixes Invisible Typing) */
    div[data-baseweb="input"] > div, 
    div[data-baseweb="base-input"],
    div[data-baseweb="select"] > div {{
        background-color: {input_bg} !important;
        border: 1px solid rgba(148, 163, 184, 0.2) !important;
        border-radius: 12px !important;
        transition: all 0.3s ease !important;
    }}

    /* Fixes the actual text you type so you can see it */
    input, textarea, div[data-baseweb="select"] span {{
        color: {text_primary} !important;
        -webkit-text-fill-color: {text_primary} !important;
        font-weight: 500 !important;
    }}

    /* Input & Dropdown Hover/Focus Effects */
    div[data-baseweb="input"]:hover > div, 
    div[data-baseweb="select"]:hover > div {{
        border-color: {mint_accent} !important;
        box-shadow: 0 0 10px {mint_glow} !important;
        cursor: text;
    }}
    div[data-baseweb="select"]:hover > div {{
        cursor: pointer;
    }}

    /* Fix Dropdown Popover Menu Visibility */
    ul[role="listbox"] {{ background-color: {card_bg} !important; border: {card_border} !important; border-radius: 12px !important; }}
    li[role="option"] {{ color: {text_primary} !important; transition: all 0.2s ease; }}
    li[role="option"]:hover {{ background-color: {mint_accent} !important; color: #000000 !important; font-weight: bold; transform: translateX(5px); }}

    /* 🟢 INTERACTIVE BUTTONS */
    .stButton > button {{
        background: linear-gradient(135deg, {mint_accent}, #00b4d8) !important;
        color: #000000 !important;
        font-weight: 800 !important;
        font-size: 1.05rem !important;
        border-radius: 30px !important;
        border: none !important;
        padding: 12px 28px !important;
        box-shadow: 0 4px 15px {mint_glow} !important;
        transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1) !important;
        cursor: pointer !important;
        width: 100%;
    }}

    /* Button Hover 3D Scale & Glow */
    .stButton > button:hover {{
        transform: scale(1.03) translateY(-3px) !important;
        box-shadow: 0 10px 25px {mint_glow} !important;
    }}
    
    .stButton > button:active {{
        transform: scale(0.97) !important;
    }}
</style>
""", unsafe_allow_html=True)

# 4. BRAND HEADER
with top_col1:
    st.markdown('<div class="brand-title">⚡ SmartClassAI Portal</div>', unsafe_allow_html=True)
    st.markdown('<div class="brand-subtitle">Automated classroom telemetry & analytics interface</div>', unsafe_allow_html=True)

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
        st.markdown('<div class="flux-card">', unsafe_allow_html=True)
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
        st.markdown('<div class="flux-card">', unsafe_allow_html=True)
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
        st.markdown('</div>', unsafe_allow_html=True)

        st.divider()
        st.markdown("## Active Faculty Accounts Directory")
        
        teachers = get_teachers()
        if teachers:
            for teacher in teachers:
                t_user, t_class, t_role = teacher[0], teacher[1], teacher[2]
                st.markdown('<div class="flux-card" style="padding: 15px; margin-bottom: 10px;">', unsafe_allow_html=True)
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
                st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info("No faculty accounts found.")

    elif page == "Student Registration":
        st.markdown('<div class="flux-card">', unsafe_allow_html=True)
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
        st.markdown('</div>', unsafe_allow_html=True)

        st.divider()
        st.markdown(f"## Registered Student Records (Scope: {active_scope})")

        students = get_students(active_scope)
        if students:
            for student in students:
                s_id, s_name, s_class, s_enc = student[0], student[1], student[2], student[3]
                st.markdown('<div class="flux-card" style="padding: 15px; margin-bottom: 10px;">', unsafe_allow_html=True)
                col1, col2 = st.columns([5, 1])

                with col1:
                    face_status_html = (
                        '<span class="status-dot-active" style="color:#00f5d4;">●</span> Biometric Active'
                        if s_enc
                        else '<span class="status-dot-inactive" style="color:#ff4d4d;">●</span> Awaiting Biometrics'
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
                st.markdown('</div>', unsafe_allow_html=True)
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