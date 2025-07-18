import streamlit as st
from streamlit_elements import elements, media
import uuid

class VideoController:
    """
    Stateless controller for the video player using streamlit-elements.
    """
    def __init__(self, url: str, key_prefix: str = "video_controller"):
        self.url = url
        self.state_key = f"{key_prefix}_{self.url}"
        if self.state_key not in st.session_state:
            st.session_state[self.state_key] = {
                "player_key": f"player_{uuid.uuid4()}"
            }

    def render(self, playing: bool):
        state = st.session_state[self.state_key]
        with elements(state['player_key']):
            media.Player(
                url=self.url,
                playing=playing,
                controls=True,
                muted=False,   # <-- Set to True to allow autoplay
                width="100%",
                height="400px"
            )