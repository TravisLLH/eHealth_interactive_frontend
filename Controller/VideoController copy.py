# filename: VideoController.py
import streamlit as st
from streamlit_elements import elements, media
import uuid

class VideoController:
    """
    A simplified and robust controller that uses streamlit-elements for all video types,
    including YouTube, to enable programmatic control.
    """

    def __init__(self, url: str, key_prefix: str = "video_controller"):
        """
        Initialize the controller with a video URL.
        """
        self.url = url
        # A unique key for this controller's state, based on the URL.
        self.state_key = f"{key_prefix}_{self.url}"

        # Initialize the state for this specific video if it doesn't exist.
        if self.state_key not in st.session_state:
            st.session_state[self.state_key] = {
                # CRITICAL: Always initialize in a predictable 'paused' state.
                "playing": False,
                # A unique key for the elements() context to ensure it's stable.
                "player_key": f"player_{uuid.uuid4()}"
            }

    def render(self):
        """
        Renders the media player using streamlit-elements.
        The player's state is bound to our session state, making it controllable.
        """
        # Retrieve the current playing state for this video.
        is_playing = st.session_state[self.state_key]['playing']
        player_key = st.session_state[self.state_key]['player_key']

        # Use the streamlit-elements context. This component is stateful and will persist
        # across Streamlit reruns, unlike st.components.v1.html.
        with elements(player_key):
            # The media.Player component handles both regular video URLs and YouTube URLs.
            media.Player(
                url=self.url,
                playing=is_playing,
                controls=True,  # Show the native video controls
                width="100%",
                height="400px"
            )

    def set_playing(self, playing: bool):
        """
        Updates the video's playing state in the session.
        Streamlit-elements will automatically apply this new state on the next rerun.
        """
        # This is now the ONLY action needed. No more custom JavaScript.
        st.session_state[self.state_key]['playing'] = playing