import streamlit as st
from streamlit_elements import elements, media
import uuid

class VideoController:
    """
    A robust controller that handles browser autoplay policies by muting the initial play.
    It uses streamlit-elements for all video types.
    """

    def __init__(self, url: str, key_prefix: str = "video_controller"):
        """
        Initialize the controller with a video URL.
        """
        self.url = url
        self.state_key = f"{key_prefix}_{self.url}"

        if self.state_key not in st.session_state:
            st.session_state[self.state_key] = {
                "playing": False,
                # --- KEY CHANGE: Add a flag to track the first play ---
                "has_played_once": False,
                "player_key": f"player_{uuid.uuid4()}"
            }

    def render(self):
        """
        Renders the media player. It mutes the video if it's the first time
        it's being played programmatically, to comply with browser autoplay policies.
        """
        state = st.session_state[self.state_key]
        is_playing = state['playing']

        # --- KEY CHANGE: Determine if the video should be muted ---
        # Mute if it's playing but has never been successfully played before.
        should_be_muted = is_playing and not state['has_played_once']

        with elements(state['player_key']):
            media.Player(
                url=self.url,
                playing=is_playing,
                controls=True,
                muted=should_be_muted,  # Apply the muted state
                width="100%",
                height="400px"
            )

        # --- KEY CHANGE: If we just started playing, update the flag ---
        # This ensures subsequent plays are not muted.
        if is_playing:
            st.session_state[self.state_key]['has_played_once'] = True

    def set_playing(self, playing: bool):
        """
        Updates the video's playing state in the session.
        """
        st.session_state[self.state_key]['playing'] = playing