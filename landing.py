import streamlit as st
import state
import base64

def get_base64_image(image_path):
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except FileNotFoundError:
        st.error(f"Image not found: {image_path}")
        return ""

def show_landing_page():
    config = {
        "logo_path": "logo.png",
        "main_title": st.secrets.get("APP_NAME", "Chat Assistant"),
        "description": st.secrets.get("APP_DESCRIPTION", "Secure AI-powered chat interface")
    }

    # Header Section
    st.markdown(f"""
        <h1 aria-label="Application Title" class="main-title">
            {config['main_title']}
        </h1>
        <div role="contentinfo" class="app-description">
            {config['description']}
        </div>
    """, unsafe_allow_html=True)

    # Logo Handling
    if config.get("logo_path"):
        logo_base64 = get_base64_image(config["logo_path"])
        if logo_base64:
            st.markdown(f"""
                <div class="logo-container">
                    <img alt="Application Logo" class="logo-img" 
                        src="data:image/png;base64,{logo_base64}">
                </div>
            """, unsafe_allow_html=True)

        st.write()
        st.markdown("---")


    # Session Start
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        if st.button(
            st.secrets.get("START_BUTTON_TEXT", "🚀 Start Chat Session"),
            key="guest_auth"
        ):
            if state.guest_start_session():
                st.rerun()

                