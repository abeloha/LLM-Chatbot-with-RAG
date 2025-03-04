import streamlit as st
from landing import show_landing_page
from chat import show_chat_page
import state

# Validate required secrets
REQUIRED_SECRETS = ["APP_NAME", "DB_HOST", "DB_USER", "DB_PASSWORD", "DB_NAME"]
for secret in REQUIRED_SECRETS:
    if secret not in st.secrets:
        st.error(f"Missing required secret: {secret}")
        st.stop()

# Configure page
st.set_page_config(
    page_title=st.secrets.get("APP_NAME", "Chat Assistant"),
    page_icon=st.secrets.get("APP_ICON", "🤖"),
    layout="centered",
    initial_sidebar_state="collapsed",
)

st.markdown("""
    <style>
        body {
            background-color: #0B3D2E; 
            color: white;
        }
        .main-title {
            text-align: center;
            color: #FFD700; /* Gold */
            font-size: 26px;
            font-weight: bold;
        }
        .sub-title {
            text-align: center;
            color: white;
            font-size: 16px;
            font-weight: bold;
        }
        .stTextInput, .stRadio, .stDateInput {
            color: black !important;
            border-radius: 8px;
        }
        .stButton > button {
            background-color: #FFD700 !important; /* Gold Buttons */
            color: black !important;
            font-size: 16px;
            font-weight: bold;
            border-radius: 10px;
            padding: 10px;
        }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
state.initialize_session_state()

# Router
if st.session_state.guest_id:
    show_chat_page()
else:
    show_landing_page()