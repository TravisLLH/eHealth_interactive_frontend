import glob
import json
import requests
from menu import render_sidebar
from utils import parse_copd_history, validate_session_history, parse_patient_answer, check_ic_scores_are_valid_from_json
import streamlit as st
from streamlit_autorefresh import st_autorefresh
from translation import translations
from Config import config
import os
import yaml

questionnaire_path = None
QUESTIONNAIRE = None

st.set_page_config(
    page_title="Questionnaire",
    page_icon="💬",
    layout="wide"
)

# config
if 'language' not in st.session_state:
    st.session_state.language = config.language
lang = st.session_state.language
NGROK_DOMAIN = config.ngrok_domain


def set_questionnaire(language=lang):
    override_questionnaire = False

    # Use Questionnaire with default language
    questionnaire_path = f"{os.path.join(config.questionnaire_path, "_".join([config.questionnaire_title, language]))}.yaml"

    # Check if Questionnaire with different language
    if not os.path.exists(questionnaire_path):
        # print("Check the corresponding questionnaire with different language...")
        all_questionnaires = glob.glob("Questionnaire/*")
        questionnaire_path = next((questionnaire for questionnaire in all_questionnaires if config.questionnaire_title in questionnaire), None)
        override_questionnaire = True

    if questionnaire_path:
        with open(questionnaire_path, "r") as f:
            questions = yaml.safe_load(f)
            QUESTIONNAIRE = questions["QUESTIONNAIRE"]

        if override_questionnaire:
            QUESTIONNAIRE["title"] = f"{config.questionnaire_title.split("_")[0]} {translations['test_result'][lang]}"
    else:
        # print("Cannot found the questionnaire inside the Questionnaire folder, please check the folder or modify the config 'QUESTIONNAIRE_TITLE' setting.")
        QUESTIONNAIRE = {
            "title" : f"{config.questionnaire_title.split("_")[0]} {translations['test_result'][lang]}"
        }
    return QUESTIONNAIRE, questionnaire_path

# print(f"Frontend Page st.session_state: {st.session_state}")
# print(f"Frontend Page config._current_session_id: {config._current_session_id}")

current_session_id = st.session_state.get('user_id')
if current_session_id is not None:
    config._current_session_id = current_session_id

session_id, domain = render_sidebar()
# print(f"Frontend Page original session_id: {session_id}")

if session_id == "" and current_session_id:
    session_id = current_session_id

QUESTIONNAIRE,questionnaire_path = set_questionnaire(lang)
st.markdown(f'<h1 style="font-size:38px;"> 💬&nbsp;&nbsp;{QUESTIONNAIRE['title']}  </h1>', unsafe_allow_html=True)

st_autorefresh(interval=5 * 1000, key="dataframerefresh")  # Refresh every 5 seconds

if __name__ == "__main__":
    QUESTIONNAIRE, questionnaire_path = set_questionnaire(lang)
    config.set_rubric()

    # Case Handle: Redirect Test Result to the Front Page, and no receive the New user input Session id, we will use the previous input session id
    # and show the Questionnaire details record
    if not session_id:
        if 'redirect_FrontPage' in st.session_state:
            if st.session_state.redirect_FrontPage and "current_session_id" in st.session_state:
                session_id = st.session_state.current_session_id
                st.session_state.redirect_FrontPage = False # reset redirect param

        else:
            st.info("Please input your Session ID on the left pane to check your conversation summary.")
            st.stop()
    # if not domain:
    #     st.info("Please input your domain on the left pane to start conversation.")
    #     st.stop()
    if domain != NGROK_DOMAIN:
        NGROK_DOMAIN = domain

    response = requests.post(f"{NGROK_DOMAIN}/get_ehealth_result", json={"session_id": session_id})
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
    patient_answer = response.get("response1", {})
    icscore_list = response.get("response2", {})

    # ## -------------------------------------------------------------------------------------------------------- ##
    # ##TODO: Temporary use Test JSON for testing the GUI
    # with open("test/answers.json", "r") as f:        # override test
    #     patient_answer = json.load(f)                # override test
    # ## -------------------------------------------------------------------------------------------------------- ##

    # # with open("exp_data/sample/1.json", "r") as f:
    # #     response_data = json.load(f)
    # validate_session_history(response_data)
    #
    # conversation_history = response_data.pop(f"{translations['conversation_history'][lang]}", [])
    # session_id = response_data.pop("sessionID", "")
    # patient_answer = response_data.pop("patient_answer", [])


    conversation_history = patient_answer.pop(f"{translations['conversation_history'][lang]}", [])
    session_id = patient_answer.pop("sessionID", session_id)

    if config.debug_mode: st.write(f"#### Session ID: {session_id}")  # Only for Test

    # Create two columns
    col1, col2 = st.columns([9, 2])
    col1.write(f"#### {translations['questionnaire'][lang]}")

    # ## -------------------------------------------------------------------------------------------------------- ##
    # ##TODO: Temporary use Test JSON for testing the GUI
    # with open("test/ic_scores.json", "r") as fr:
    #     score_json = json.load(fr)
    # ## -------------------------------------------------------------------------------------------------------- ##
    icscore_ready = check_ic_scores_are_valid_from_json(icscore_list)

    if not icscore_ready:
        col2.button(f"{translations['check_result'][lang]}", use_container_width=True,disabled=True)

    if icscore_ready and col2.button(f"{translations['check_result'][lang]}", use_container_width=True):
        # st.session_state.current_session_id = session_id
        # st.session_state.redirect_TestPage = True
        config._current_session_id = session_id
        config._redirect_TestPage = True
        st.switch_page("pages/Test_Result.py")

    parsed_patient_answer = parse_patient_answer(patient_answer, questionnaire_path, lang)
    edited_data = st.data_editor(data=parsed_patient_answer, use_container_width=True, height=530, key="qanda")  # Unique key for the first table

    ## --------------- Conversation History Details ---------------
    # st.write(f"### {translations['details'][lang]}")
    # [history_tab] = st.tabs([f"{translations['conversation_history'][lang]}"])
    # with history_tab:
    #     st.write(f"#### {translations["conversation_history"][lang]}")
    #     with st.container(height=400):
    #         parsed_conversation_history = parse_copd_history(conversation_history)
    #         for role, utterance in parsed_conversation_history:
    #             with st.chat_message(role):
    #                 st.write(utterance)