import base64
import streamlit as st
from streamlit_autorefresh import st_autorefresh
from menu import render_sidebar
from translation import translations
from utils import parse_score, parse_content, check_ic_scores_are_valid_from_json, encode_image_to_base64
from Config import config
import requests
from pathlib import Path

lang = config.language

st.set_page_config(
    page_title="Test Result",
    layout="wide"
)

# current_session_id = config._current_session_id
current_session_id = st.session_state.get('user_id')
if current_session_id is not None:
    config._current_session_id = current_session_id

session_id, domain = render_sidebar()
# print(f"Test Result Page original session_id: {session_id}")

if session_id == "" and current_session_id:
    session_id = current_session_id

# print(f"Test Result Page receive session_id input: {session_id}")


# ## -------------------------------------------------------------------------------------------------------- ##
# ##TODO: Temporary use Test JSON for testing the GUI
# with open("test/ic_scores.json", "r") as fr:
#     score_json = json.load(fr)
# ## -------------------------------------------------------------------------------------------------------- ##

response = requests.post(f"{config.ngrok_domain}/get_ehealth_result", json={"session_id": session_id})
# response = requests.post(f"{NGROK_DOMAIN}/get_copd_result", json={"session_id": session_id})

# If the response is not successful, print the error message
if response.status_code != 200:
    st.warning(
        f"The Interview with Session ID {session_id} hasn't started yet, please wait. \n\nIf you have already started the interview, please ensure the Session ID and domain name is correct."
    )
    # st.warning(f"")
    # st.warning("If you believe this is an error, please contact the administrator with the following information")
    st.stop()

response = response.json()
icscore_list = response.get("response2", {})


# Frontend Page
st.markdown(f'<h1 style="font-size:38px;"> 📝&nbsp;&nbsp;{translations['test_result'][lang]} </h1>', unsafe_allow_html=True)
st.write("\n")

# TODO: Case 1: Not Receive any input (No redirect and input from the user)
if not session_id:
    st.info("Please input your Session ID on the left pane to check your test result summary.")
    st.stop()

response = requests.post(f"{st.session_state.domain}/get_ehealth_result", json={"session_id": session_id})
# TODO: Case 2: If the response is not successful, print the error message/ The Seesion ID not start yet
if response.status_code != 200:
    st.warning(
        f"The Interview with Session ID {session_id} hasn't started yet, please wait. \n\nIf you have already started the interview, please ensure the Session ID and domain name is correct."
    )
    st.stop()

iscore_ready = check_ic_scores_are_valid_from_json(icscore_list)
# TODO: Case 3: Session ID existed BUT the Questionnaire is still processing, However the user click in this page via navigation sidebar
if not iscore_ready:
    if st.button(f"{translations['return_questionnaire'][lang]}", ):
        # st.session_state.current_session_id = 0
        st.session_state.redirect_FrontPage = True
        st.switch_page("frontend_display_result.py")
    st.warning(
        f"The test result for the interview with Session ID {session_id} is not ready. Please complete the questionnaire first and check this page again later. \n\nIf you want to check the result of a completed interview, please enter the Session ID and domain name in the left pane."
    )
    st.stop()

## ---------------------- Generate the Test Output ---------------------- ##
if config.debug_mode: st.write(f"#### Session ID: {session_id}")  # Only for Test

# total_ic_score = sum(item["IC Score"] for item in score_json)
total_ic_score = sum(
    int(item["IC Score"]) for item in icscore_list
    if isinstance(item.get("IC Score"), (int, float)) or (isinstance(item.get("IC Score"), str) and item["IC Score"].strip() != "")
)

# Create two columns
if lang =="zh":
    col1, col2 = st.columns([7, 2])
else: # basically 'en'
    col1, col2 = st.columns([7, 2])

with open(f"images/scales/{total_ic_score}.png", "rb") as image_file:
    encoded_string = base64.b64encode(image_file.read()).decode()
image_url = f"data:image/png;base64,{encoded_string}"

col1.markdown(
    f"""
    <h4 style='display: flex; align-items: center; margin: 0;'>
        {translations['total_intrinsic_capacity_score'][config.language]} :
    </h4>
    """,

    # {translations['total_intrinsic_capacity_score'][config.language]} :&nbsp;&nbsp;<img src="{image_url}" width="40" style='margin-left: 10;'>
    unsafe_allow_html=True
)

# Button with matching alignment
with col2:
    st.markdown(
        """
        <style>
        .stButton > button {
            vertical-align: middle;
            margin-top: -15px;  /* Adjust this value to fine-tune alignment */
        }
        </style>
        """,
        unsafe_allow_html=True
    )
    if st.button(f"{translations['return_questionnaire'][lang]}", use_container_width=True):
        st.session_state.redirect_FrontPage = True
        st.switch_page("frontend_display_result.py")


# Adjustable spacing between the images
spacing = 13  # Adjust this value to control spacing between images

# Example `total_ic_score` value
# total_ic_score = 2 # Replace this with your actual score or logic

# Create Base64-encoded image strings
images_html = []
for i in range(6):  # Assuming 6 images
    if i == total_ic_score:
        image_path = f"images/scales/{i}.png"  # Highlighted image
        image_width = 50  # Larger size for highlighted image
    else:
        image_path = f"images/scales/{i}_gray.png"  # Gray image
        image_width = 30  # Smaller size for gray image

    # Encode the image to Base64
    if Path(image_path).exists():
        img_base64 = encode_image_to_base64(image_path)
        images_html.append(
            f"<div style='margin-right: {spacing}px; text-align: center;'>"
            f"<img src='data:image/png;base64,{img_base64}' style='width: {image_width}px;'>"
            f"</div>"
        )
    else:
        st.error(f"Image not found: {image_path}")

# Generate the HTML layout
html_content = f"<div style='display: flex; align-items: baseline;'>{''.join(images_html)}</div>"

# Render the HTML in Streamlit
st.markdown(html_content, unsafe_allow_html=True)

# Parse the ic score
st.write("\n"); st.write("\n")
st.write(f"#### {translations['score_details'][lang]}")
parsed_score_result = parse_score(icscore_list, config.rubric_path, config.language)
parsed_score_data = st.data_editor(data=parsed_score_result, use_container_width=True, height=220, key="score")

ICScore_code = config.rubric["ICScore"][total_ic_score]
ICScore_conclusion = config.rubric["Conclusion"][ICScore_code]

# Conclusion
st.write("\n")
st.write(f"#### {translations['conclusion'][lang]}")
parse_content(ICScore_conclusion['Result'])

# Recommendation
st.write("\n")
[recommendation_tab, videoAndResource_tab] = st.tabs([f"{translations['recommendation'][config.language]}", f"{translations['video_and_resources'][config.language]}"])

# Tab 0: Recommendation tab
with recommendation_tab:
    recommendation = ICScore_conclusion['Recommendation']
    parse_content(recommendation)

    generalConclusion = config.rubric["Conclusion"]['General_Ending_For_All_Tests']
    parse_content(generalConclusion)

# Tab 1: Video and Resources tab
with videoAndResource_tab:
    videoAndResources = config.rubric['Video and Resources']
    parse_content(videoAndResources)

st_autorefresh(interval=5 * 1000, key="dataframerefresh")  # Refresh every 5 seconds
