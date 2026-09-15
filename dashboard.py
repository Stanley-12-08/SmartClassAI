import streamlit as st

def show_dashboard():
    # Custom CSS for Modern Clean UI and Card Effects
    st.markdown("""
        <style>
        .metric-card {
            background: linear-gradient(135deg, #1e1e2f 0%, #2a2a40 100%);
            padding: 20px;
            border-radius: 15px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
            color: white;
            text-align: center;
            border: 1px solid rgba(255,255,255,0.1);
            transition: transform 0.3s ease;
        }
        .metric-card:hover {
            transform: translateY(-5px);
        }
        .stButton>button {
            border-radius: 10px;
            font-weight: 600;
            transition: all 0.3s ease;
        }
        </style>
    """, unsafe_allow_html=True)

    st.title("📊 SmartClassAI Dashboard")
    st.write("Welcome back! Here is your real-time classroom overview.")

    # Modern Clean Metric Layout
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
            <div class="metric-card">
                <h3>Total Students</h3>
                <h2>42</h2>
            </div>
        """, unsafe_allow_html=True)
        
    with col2:
        st.markdown("""
            <div class="metric-card">
                <h3>Present Today</h3>
                <h2>38</h2>
            </div>
        """, unsafe_allow_html=True)
        
    with col3:
        st.markdown("""
            <div class="metric-card">
                <h3>Attendance Rate</h3>
                <h2>90.4%</h2>
            </div>
        """, unsafe_allow_html=True)