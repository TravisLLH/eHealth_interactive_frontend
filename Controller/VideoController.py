import streamlit as st
import streamlit.components.v1 as components
import uuid
from urllib.parse import urlparse, urlunparse, parse_qs, urlencode
import re
from utils import convert_time_to_seconds

def create_youtube_embed_url(url: str) -> str:
    """Creates a base YouTube embed URL with JS API enabled."""
    video_id_match = re.search(r'(?:v=|youtu\.be\/|embed\/)([a-zA-Z0-9_-]{11})', url)
    if not video_id_match: return "Error: Could not extract video ID from the URL."
    video_id = video_id_match.group(1)
    
    embed_url = f"https://www.youtube.com/embed/{video_id}?enablejsapi=1"
    return embed_url

class VideoController:
    def __init__(self, url: str, key_prefix: str = "video_controller", start_at: str = None, end_at: str = None, subtitle=True):
        self.video_id = create_youtube_embed_url(url).split('/embed/')[1].split('?')[0]
        self.subtitle = subtitle
        
        self.start_seconds = convert_time_to_seconds(start_at)
        self.end_seconds = convert_time_to_seconds(end_at)

        self.player_dom_id = f"youtube_player_{uuid.uuid4().hex}"


    def render(self, playing: bool):
        session_id = st.session_state.get('user_id', '')
        flask_domain = st.session_state.get('domain', '').strip('/')

        final_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                html, body {{ margin: 0; padding: 0; width: 100%; height: 100%; overflow: hidden; }}
            </style>
        </head>
        <body>
            <div id="{self.player_dom_id}" style="width: 100%; height: 100vh;"></div>

            <script>
                // **THE DEFINITIVE FIX (1/3): One-Time Setup vs. Every-Time Update**
                // We use a guard on the window object to ensure the core player setup happens only ONCE.
                if (!window.myPlayerManager) {{
                    window.myPlayerManager = {{
                        player: null,
                        hasNotified: false,
                        isReady: false,
                        
                        // This is the single, persistent event handler.
                        onPlayerStateChange: function(event) {{
                            // YT.PlayerState.ENDED is 0, YT.PlayerState.PAUSED is 2.
                            if (event.data === 0 || event.data === 2) {{
                                if (!window.myPlayerManager.hasNotified) {{
                                    window.myPlayerManager.hasNotified = true;
                                    console.log(`Video stopped (State: ${{event.data}}). Notifying backend...`);
                                    fetch('{flask_domain}/video_ended', {{
                                        method: 'POST',
                                        headers: {{ 'Content-Type': 'application/json' }},
                                        body: JSON.stringify({{ session_id: '{session_id}' }})
                                    }}).catch(error => console.error('Error notifying backend:', error));
                                }}
                            }}
                        }},

                        // This is called once when the player is first created.
                        onPlayerReady: function(event) {{
                            console.log("SUCCESS: YouTube Player is ready.");
                            window.myPlayerManager.isReady = true;
                        }},

                        // This creates the player.
                        initialize: function() {{
                            this.player = new YT.Player('{self.player_dom_id}', {{
                                videoId: '{self.video_id}',
                                playerVars: {{
                                    'start': {self.start_seconds},
                                    'end': {self.end_seconds if self.end_seconds > 0 else 'null'},
                                    'rel': 0, 
                                    'iv_load_policy': 3,
                                    'cc_load_policy': {1 if self.subtitle else 0},
                                    'cc_lang_pref': 'en'
                                }},
                                events: {{
                                    'onReady': this.onPlayerReady,
                                    'onStateChange': this.onPlayerStateChange
                                }}
                            }});
                        }}
                    }};

                    // Load the YouTube API script, which will call onYouTubeIframeAPIReady when done.
                    var tag = document.createElement('script');
                    tag.src = "https://www.youtube.com/iframe_api";
                    var firstScriptTag = document.getElementsByTagName('script')[0];
                    firstScriptTag.parentNode.insertBefore(tag, firstScriptTag);
                    
                    // The API calls this global function once loaded.
                    window.onYouTubeIframeAPIReady = function() {{
                        window.myPlayerManager.initialize();
                    }};
                }}

                // **THE DEFINITIVE FIX (2/3): Reset the notification flag on EVERY re-render.**
                // This makes the video replayable.
                window.myPlayerManager.hasNotified = false;

                // **THE DEFINITIVE FIX (3/3): This is the function that runs on EVERY re-render.**
                // It applies the latest state from Python to the persistent player object.
                function applyPythonState() {{
                    const shouldBePlaying = {'true' if playing else 'false'};
                    const manager = window.myPlayerManager;

                    if (manager && manager.isReady && manager.player) {{
                        const currentState = manager.player.getPlayerState();
                        
                        if (shouldBePlaying && currentState !== 1) {{ // 1 is PLAYING
                            manager.player.playVideo();
                        }} else if (!shouldBePlaying && currentState === 1) {{
                            // This is the remote stop command. Calling .pauseVideo() will trigger
                            // the persistent onPlayerStateChange handler, which sends the notification.
                            manager.player.pauseVideo();
                        }}
                    }} else {{
                        // If player isn't ready, retry shortly.
                        setTimeout(applyPythonState, 100);
                    }}
                }}
                
                // Always try to apply the state.
                applyPythonState();

            </script>
        </body>
        </html>
        """

        components.html(final_html, height=800)