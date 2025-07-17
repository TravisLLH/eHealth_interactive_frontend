import streamlit as st
from streamlit_elements import elements, media
import uuid

class VideoController:
    """
    A controller for the video player using streamlit-elements.
    This version has been simplified to address playback issues.
    """

    def __init__(self, url: str, key_prefix: str = "video_controller"):
        """
        Initialize the controller with a video URL.
        """
        self.url = url
        self.state_key = f"{key_prefix}_{self.url}"

        # Initialize the state for this video URL if it doesn't exist.
        # The 'has_played_once' flag has been removed to simplify state.
        if self.state_key not in st.session_state:
            st.session_state[self.state_key] = {
                "playing": False,
                "player_key": f"player_{uuid.uuid4()}"
            }

    def render(self):
        """
        Renders the media player based on the current session state.
        """
        state = st.session_state[self.state_key]
        is_playing = state['playing']

        with elements(state['player_key']):
            media.Player(
                url=self.url,
                playing=is_playing,
                controls=True,
                # By setting muted to False, we rely on the user to handle
                # any browser autoplay restrictions if they occur.
                muted=False,
                width="100%",
                height="400px"
            )

    def set_playing(self, playing: bool):
        """
        Updates the video's playing state in the session.
        """
        st.session_state[self.state_key]['playing'] = playing