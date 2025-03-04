import streamlit as st
import mysql.connector
import uuid
from datetime import datetime
from mysql.connector import pooling

# Get MySQL database credentials from .env
DB_CONFIG = {
    "host": st.secrets["DB_HOST"],
    "user": st.secrets["DB_USER"],
    "password": st.secrets["DB_PASSWORD"],
    "database": st.secrets["DB_NAME"]
}

def initialize_session_state():
    defaults = {
        "messages": [],
        "welcome_message_is_sent": False,
        "unsaved_ai_message": None,
        "guest_id": None
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


# Connect to MySQL database
def get_db_connection():
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS guest_messages (
            id INT AUTO_INCREMENT PRIMARY KEY,
            guest_id VARCHAR(50) NOT NULL,
            role ENUM('user', 'assistant') NOT NULL,
            content TEXT NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    conn.commit()
    return conn

def get_system_prompt():

    app_name = st.secrets["APP_NAME"]
    website = st.secrets["WEBSITE"]
    return f"""
    You are {app_name}, an AI assistant for the Abel Onuoha Technology Limited.
    - Use "The Knowledge" section as your primary information source
    - Only consult internal knowledge when:
      * The question is not directly related to the business but is not off-topic AND
      * The answer isn't in "The Knowledge" AND
      * You're certain the information is accurate AND current
    - If unsure, information might be outdated, or question is ambiguous:
      * Either respond using only "The Knowledge" section (if relevant) OR
      * State: "I don't have information on that. Please rephrase your question for clarity."
    - Never mention "The Knowledge" section or internal knowledge
    - Prioritize accuracy over completeness
    - Keep responses under 5 sentences
    - For completely unknown topics: "I don't have information on that yet. Visit our website {website} for more information."
    """


# Guest session management
def guest_start_session():
    try:
        st.session_state.guest_id = f"{datetime.now().strftime('%y%m%d%H%M')}-{uuid.uuid4().hex[:6]}"
        return True
    except Exception as e:
        st.error(f"Session start failed: {str(e)}")
        return False

def get_guest_id():
    return st.session_state.guest_id

def guest_save_message(guest_id, role, content):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO guest_messages (guest_id, role, content) VALUES (%s, %s, %s)",
            (guest_id, role, content)
        )
        conn.commit()
    except Exception as e:
        st.error(f"Error saving message: {str(e)}")
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()