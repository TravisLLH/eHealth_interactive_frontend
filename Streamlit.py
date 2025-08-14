import json
import requests
import redis
import streamlit as st
from streamlit_autorefresh import st_autorefresh
from Controller.VideoController import VideoController
from display_format import get_yes_no_question_html, get_scale_question_html, get_plain_text_html, get_image_html, get_gif_html
from utils import get_base64_image
from datetime import datetime

DEFAULT_DOMAIN = "http://localhost:5050/"

redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

st.set_page_config(layout="wide")

hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            .stApp [data-testid="stStatusWidget"] {display: none;}
            html, body, .stApp {overflow: hidden; height: 100vh; margin: 0; padding: 0;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)

def send_session_id():
    session_id = st.session_state.user_id
    url = f"{st.session_state.domain}/post_session_id"
    payload = {'session_id': session_id}
    try:
        requests.post(url, json=payload).raise_for_status()
    except requests.exceptions.RequestException as e:
        st.error(f"Error sending Session ID: {str(e)}")

st.session_state.setdefault('user_id', None)
st.session_state.setdefault('domain', DEFAULT_DOMAIN)
st.session_state.setdefault('response', None)
st.session_state.setdefault('video_controller', None)
st.session_state.setdefault('language', 'en')

current_session_id = redis_client.get('current_session_id')
if current_session_id and current_session_id != st.session_state.user_id:
    current_domain = st.session_state.domain
    st.session_state.clear()
    st.session_state.user_id = current_session_id
    st.session_state.domain = current_domain
    st.rerun()

with st.sidebar:
    st.text_input(label="Session ID:", value=st.session_state.user_id or "", key="input_user_id")
    if st.session_state.input_user_id and st.session_state.input_user_id != st.session_state.user_id:
        new_id = st.session_state.input_user_id
        current_domain = st.session_state.domain
        st.session_state.clear()
        st.session_state.user_id = new_id
        st.session_state.domain = current_domain
        send_session_id()
        st.rerun()
    st.text_input(label="Flask Domain:", key="domain", value=st.session_state.domain)

def get_content_html(response):
    if not response: return ""
    content_type = response.get('type')
    msg = response.get('message')
    qfmt = response.get('question_format')
    min_v = response.get('MIN')
    max_v = response.get('MAX')
    order = response.get('order', 'ascending')
    language = response.get('language', st.session_state.language)
    font_size = response.get('font_size', 100)
    if qfmt == "yes_no": return get_yes_no_question_html(msg, language)
    elif qfmt == "scale": return get_scale_question_html(msg, order, min_v, max_v, language)
    else:
        if content_type == "image": return get_image_html(msg)
        elif content_type == "gif" and st.session_state.video_controller: return ''
        elif content_type == "gif": return get_gif_html(msg)
        else: return get_plain_text_html(msg, font_size)



if __name__ == "__main__":
    session_id = st.session_state.user_id
    if not session_id:
        st.info("Please provide a Session ID to begin.")
    else:
        message_data = redis_client.get(f'message:{session_id}')
        if message_data:
            try:
                new_response = json.loads(message_data)
                if new_response != st.session_state.get('response'):
                    st.session_state.response = new_response
                    if new_response.get('type') == "video":
                        video_url = new_response.get('message')
                        start_at = new_response.get('start_at')
                        end_at = new_response.get('end_at')
                        subtitle = new_response.get('subtitle')
                        st.session_state.video_controller = VideoController(
                            video_url, start_at=start_at, end_at=end_at, subtitle=subtitle
                        )
                    elif new_response.get('type') == "gif" and st.session_state.video_controller: pass
                    else: st.session_state.video_controller = None
                    st.rerun()
            except json.JSONDecodeError as e: st.error(f"Error parsing message data: {e}")

        playing = False
        move_to = None
        if st.session_state.video_controller:
            video_data = redis_client.get(f'video_command:{session_id}')
            if video_data:
                try:
                    command = json.loads(video_data)
                    playing = command.get('start_or_stop', False)
                    move_to = command.get('move_to')
                except (json.JSONDecodeError, AttributeError) as e: st.error(f"Error parsing video command: {e}")

        response = st.session_state.get('response')
        loading_command = {}
        loading_data = redis_client.get(f'loading_gif:{session_id}')
        if loading_data:
            try: loading_command = json.loads(loading_data)
            except json.JSONDecodeError as e: st.error(f"Error parsing loading GIF command: {e}")
        load_overlay = loading_command.get('load', False)

        if st.session_state.video_controller:
            st.session_state.video_controller.render(playing)
        else:
            content_html = get_content_html(response)
            st.markdown(f'<div style="display: flex; justify-content: center; align-items: center; height: 100vh;">{content_html}</div>', unsafe_allow_html=True)

        if load_overlay:
            base64_gif = get_base64_image("images/gif/pleaseWait.gif")
            st.markdown('<style> body::before { content: ""; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background-color: rgba(0, 0, 0, 0.5); z-index: 9998; } </style>', unsafe_allow_html=True)
            st.markdown(f'<div style="position: fixed; top: 0; left: 0; width: 100%; height: 100%; display: flex; justify-content: center; align-items: center; z-index: 9999; pointer-events: none;"> <img src="data:image/gif;base64,{base64_gif}" style="width:30%; height:auto;"> </div>', unsafe_allow_html=True)

    # FIX: Restore the unconditional autorefresh. The JS is now designed to work with it.
    st_autorefresh(interval=2000, limit=None, key="main_refresh")