import json
import requests
import redis
import streamlit as st
from streamlit_autorefresh import st_autorefresh
from Controller.VideoController import VideoController
from display_format import display_yes_no_question, display_scale_question, display_plain_text, display_image, display_gif
# from Config import config
from datetime import datetime

# DEFAULT_DOMAIN = "http://localhost:5050/"
DEFAULT_DOMAIN = "http://10.79.26.12:5050/"

redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

st.set_page_config(layout="wide")

# ---------- CSS to hide the default Streamlit running indicators ----------
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            .stApp [data-testid="stStatusWidget"] {display: none;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)
# ---------------------------------------------------------------------------

def send_session_id():
    session_id = st.session_state.user_id
    url = f"{st.session_state.domain}/post_session_id"
    payload = {'session_id': session_id}
    try:
        requests.post(url, json=payload).raise_for_status()
    except requests.exceptions.RequestException as e:
        st.error(f"Error sending Session ID: {str(e)}")

# Initialize session state keys to avoid errors on first run.
# This is where we will "remember" the previous response.
st.session_state.setdefault('user_id', None)
st.session_state.setdefault('domain', DEFAULT_DOMAIN)
st.session_state.setdefault('response', None)
st.session_state.setdefault('video_controller', None)
st.session_state.setdefault('language', 'en')

# Check for session ID changes from Redis
current_session_id = redis_client.get('current_session_id')
if current_session_id and current_session_id != st.session_state.user_id:
    current_domain = st.session_state.domain
    st.session_state.clear()
    st.session_state.user_id = current_session_id
    st.session_state.domain = current_domain
    st.rerun()

with st.sidebar:
    st.text_input(
        label="Session ID:",
        value=st.session_state.user_id or "",
        key="input_user_id",
    )
    # Handle manual session ID input
    if st.session_state.input_user_id and st.session_state.input_user_id != st.session_state.user_id:
        new_id = st.session_state.input_user_id
        current_domain = st.session_state.domain
        st.session_state.clear()
        st.session_state.user_id = new_id
        st.session_state.domain = current_domain
        send_session_id()
        st.rerun()
        
    st.text_input(label="Flask Domain:", key="domain", value=st.session_state.domain)

def display_content(response):
    content_type = response.get('type')
    msg = response.get('message')
    qfmt = response.get('question_format')
    min_v = response.get('MIN')
    max_v = response.get('MAX')
    order = response.get('order', 'ascending')
    language = response.get('language', st.session_state.language)
    font_size = response.get('font_size', 100)

    if qfmt == "yes_no":
        display_yes_no_question(msg, language)
    elif qfmt == "scale":
        display_scale_question(msg, order, min_v, max_v, language)
    else:
        if content_type == "image":
            display_image(msg)
        elif content_type == "gif":
            display_gif(msg)
        else:
            display_plain_text(msg, font_size)

if __name__ == "__main__":
    session_id = st.session_state.user_id

    if not session_id:
        st.info("Please provide a Session ID to begin.")
    else:
        message_data = redis_client.get(f'message:{session_id}')
        if message_data:
            try:
                new_response = json.loads(message_data)
                
                # Compare the new data from Redis with the data from the previous run.
                # st.session_state.get('response') holds the "previous response".
                if new_response != st.session_state.get('response'):
                    # If data is new, update the session state.
                    st.session_state.response = new_response
                    
                    # Update the video controller based on the new response.
                    if new_response.get('type') == "video":
                        video_url = new_response.get('message')
                        start_at = new_response.get('start_at')
                        end_at = new_response.get('end_at')
                        subtitle = new_response.get('subtitle')

                        if video_url and (st.session_state.video_controller is None or st.session_state.video_controller.url != video_url):
                            st.session_state.video_controller = VideoController(video_url, start_at=start_at, end_at=end_at, subtitle=subtitle)
                    else:
                        st.session_state.video_controller = None
                    
                    # This is the key: Trigger an immediate rerun to display the new content.
                    st.rerun()

            except json.JSONDecodeError as e:
                st.error(f"Error parsing message data: {e}")

        # The rest of the script renders the UI based on the current session state.
        # This part will now only execute fully when a change is detected.
        playing = False
        if st.session_state.video_controller:
            video_data = redis_client.get(f'video_command:{session_id}')
            if video_data:
                try:
                    command = json.loads(video_data).get('start_or_stop')
                    if isinstance(command, bool):
                        playing = command
                except (json.JSONDecodeError, AttributeError) as e:
                    st.error(f"Error parsing video command: {e}")

        response = st.session_state.get('response')
        has_display_content = response and response.get('type') in ["text", "image", "gif"]

        # Rendering logic for the page content
        if st.session_state.video_controller:
            if has_display_content:
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.session_state.video_controller.render(playing)
                with col2:
                    display_content(response)
            else:
                st.session_state.video_controller.render(playing)
        elif has_display_content:
            display_content(response)

    # The interval is increased to 2000ms (2 seconds) to improve performance.
    # Its only job is to trigger this script so the comparison logic can run.
    st_autorefresh(interval=2000, limit=None, key="autofresh")