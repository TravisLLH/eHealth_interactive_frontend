import json
import requests
import redis
import streamlit as st
from streamlit_autorefresh import st_autorefresh
from Controller.VideoController import VideoController
from question_template import display_yes_no_question, display_scale_question

# Configuration constants
DEFAULT_DOMAIN = "http://localhost:5050/"

# Redis client connection
redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

def send_session_id():
    """Send the current session ID to the backend API."""
    session_id = st.session_state.user_id
    url = f"{st.session_state.domain}/post_session_id"
    payload = {'session_id': session_id}
    try:
        requests.post(url, json=payload).raise_for_status()
    except requests.exceptions.RequestException as e:
        st.error(f"Error sending Session ID: {str(e)}")

# --- Session State Initialization ---
st.session_state.setdefault('user_id', None)
st.session_state.setdefault('domain', DEFAULT_DOMAIN)
st.session_state.setdefault('response', None)
st.session_state.setdefault('last_video_command', None)
st.session_state.setdefault('video_controller', None)

# --- Poll for Session ID from Redis ---
current_session_id = redis_client.get('current_session_id')
if current_session_id and current_session_id != st.session_state.user_id:
    st.session_state.clear()
    st.session_state.user_id = current_session_id
    st.rerun()

# --- Sidebar ---
with st.sidebar:
    st.text_input(
        label="Session ID:",
        value=st.session_state.user_id or "",
        key="input_user_id"
    )
    if st.session_state.input_user_id and st.session_state.input_user_id != st.session_state.user_id:
        st.session_state.clear()
        st.session_state.user_id = st.session_state.input_user_id
        send_session_id()
        st.rerun()
    st.text_input(label="Flask Domain:", key="domain", value=DEFAULT_DOMAIN)

def display_question(response):
    msg = response.get('message')
    qfmt = response.get('question_format')
    # order = response.get('order')  # Unused in dummies, but available if needed
    min_v = response.get('MIN')
    max_v = response.get('MAX')

    if qfmt == "yes_no":
        display_yes_no_question(msg)
    elif qfmt == "scale":
        display_scale_question(msg, min_v, max_v)
    else:
        st.write(msg)  # Fallback for plain text

# --- Main Application Logic ---
if __name__ == "__main__":
    session_id = st.session_state.user_id

    if not session_id:
        st.info("Please provide a Session ID to begin.")
    else:
        # 1. Fetch latest message (to load a new video or update response)
        message_data = redis_client.get(f'message:{session_id}')
        if message_data:
            try:
                new_response = json.loads(message_data)
                if new_response != st.session_state.get('response'):
                    st.session_state.response = new_response
                    if new_response.get('type') == "video":
                        video_url = new_response.get('message')
                        if video_url and (st.session_state.video_controller is None or st.session_state.video_controller.url != video_url):
                            st.session_state.video_controller = VideoController(video_url)
                            st.session_state.last_video_command = None
                        # Do not set video_controller for other types to allow text alongside video
                    else:
                        st.session_state.video_controller = None
            except json.JSONDecodeError as e:
                st.error(f"Error parsing message data: {e}")

        # 2. Fetch and process video command (play/pause)
        if st.session_state.video_controller:
            video_data = redis_client.get(f'video_command:{session_id}')
            if video_data:
                try:
                    command_data = json.loads(video_data)
                    command = command_data.get('start_or_stop')
                    if command is not None and command != st.session_state.get('last_video_command'):
                        st.session_state.last_video_command = command
                        st.session_state.video_controller.set_playing(command)
                        redis_client.delete(f'video_command:{session_id}')
                        st.rerun()
                except (json.JSONDecodeError, AttributeError) as e:
                    st.error(f"Error parsing video command: {e}")

        # 3. Render the UI
        response = st.session_state.get('response')
        has_video = response is not None
        has_text = response and response.get('type') == "text"

        if st.session_state.video_controller:
            if has_text:
                col1, col2 = st.columns([2, 1])  # Video on left, text on right
                with col1:
                    st.session_state.video_controller.render()
                with col2:
                    display_question(response)
            else:
                st.session_state.video_controller.render()
        elif has_text:
            display_question(response)

    st_autorefresh(interval=1000, limit=None, key="autofresh")