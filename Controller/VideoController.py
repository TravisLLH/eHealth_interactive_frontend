import streamlit as st
from streamlit_elements import elements, media
import uuid
from urllib.parse import urlparse, urlunparse, parse_qs, urlencode

import re


def convert_time_to_seconds(time_str: str) -> int:
    """
    Converts a time string (e.g., '1h3m2s') into total seconds.

    This function reads a string and extracts the numbers for hours (h),
    minutes (m), and seconds (s). It handles cases where parts of the
    time string are missing (e.g., '5m30s' or '2h').

    Args:
        time_str: A string representing time, like "1h3m2s".

    Returns:
        The total number of seconds as an integer.
    """

    if not isinstance(time_str, str):
        return None

    hours = 0
    minutes = 0
    seconds = 0

    # --- Explanation of the regular expressions ---
    # The pattern r'(\d+)h' looks for a sequence of one or more digits (\d+)
    # that is immediately followed by the letter 'h'. The parentheses capture
    # the digits so we can extract them.
    
    # Find hours
    hours_match = re.search(r'(\d+)h', time_str)
    if hours_match:
        hours = int(hours_match.group(1))

    # Find minutes
    minutes_match = re.search(r'(\d+)m', time_str)
    if minutes_match:
        minutes = int(minutes_match.group(1))

    # Find seconds
    seconds_match = re.search(r'(\d+)s', time_str)
    if seconds_match:
        seconds = int(seconds_match.group(1))

    # Calculate the total seconds
    total_seconds = (hours * 3600) + (minutes * 60) + seconds

    return total_seconds


def create_youtube_embed_url(url: str, start_at: int = None, end_at: int = None) -> str:
    """
    Converts a standard YouTube URL into an embeddable URL with optional start and end times.

    Args:
        url: The original YouTube URL. 
             Handles formats like:
             - https://www.youtube.com/watch?v=VIDEO_ID
             - https://youtu.be/VIDEO_ID
             - https://www.youtube.com/embed/VIDEO_ID
        start_at: The start time in seconds (optional).
        end_at: The end time in seconds (optional).

    Returns:
        A formatted YouTube embed URL.
        Returns an error message if the URL is invalid.
    """
    # This regular expression is designed to find the 11-character video ID
    # from the most common YouTube URL formats.
    # It looks for patterns like 'v=', 'youtu.be/', or '/embed/' and captures the 11 characters that follow.
    video_id_match = re.search(r'(?:v=|youtu\.be\/|embed\/)([a-zA-Z0-9_-]{11})', url)

    if not video_id_match:
        return "Error: Could not extract video ID from the URL."

    video_id = video_id_match.group(1)

    # Construct the base URL for embedding
    embed_url = f"https://www.youtube.com/embed/{video_id}"

    # A list to hold our URL parameters (e.g., start, end)
    params = []
    if start_at is not None:
        params.append(f"start={start_at}")

    if end_at is not None:
        params.append(f"end={end_at}")

    params.append("autoplay=0")

    # If there are any parameters, join them together and append to the URL
    if params:
        embed_url += "?" + "&".join(params)

    return embed_url



class VideoController:
    """
    Stateless controller for the video player using streamlit-elements.
    """
    def __init__(self, url: str, key_prefix: str = "video_controller", start_at: str = None, end_at: str = None, subtitle=True):
        print(f"substitle: {subtitle}")

        self.start_at = start_at if isinstance(start_at, int) else convert_time_to_seconds(start_at)
        self.end_at = end_at if isinstance(end_at, int) else convert_time_to_seconds(end_at)

        if self.start_at is not None or self.end_at is not None:
            url = create_youtube_embed_url(url, self.start_at, self.end_at)

        self.url = url
        self.subtitle = subtitle
        self.state_key = f"{key_prefix}_{self.url}"
        if self.state_key not in st.session_state:
            st.session_state[self.state_key] = {
                "player_key": f"player_{uuid.uuid4()}"
            }

    def render(self, playing: bool):

        state = st.session_state[self.state_key]
        with elements(state['player_key']):
            # Define the YouTube player configuration
            youtube_config = {
                "playerVars": {
                    "cc_load_policy": 1 if self.subtitle else 0,  # Force captions to be shown by default. [1]
                    "cc_lang_pref": "en"  # Set default caption language to English. [1]
                }
            }

            print(f"youtube_config['playerVars']['cc_load_policy']: {youtube_config['playerVars']['cc_load_policy']}")

            media.Player(
                url=self.url,
                playing=playing,
                controls=True,
                muted=False,
                width="100%",
                height="700px",
                # Add the config parameter here
                config={"youtube": youtube_config}
            )