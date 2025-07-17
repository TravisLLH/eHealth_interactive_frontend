import json
import re

import pandas as pd
import yaml
from jinja2.filters import do_min

from translation import translations

def parse_copd_history(conversation_history: dict):
    """Parse the conversation history into a list of tuples containing the role and utterance.

    Args:
        conversation_history (dict): The conversation history to be parsed.

    Returns:
        list: A list of tuples containing the role and utterance of each turn in the conversation history.
    """
    conversation = []
    for turn in conversation_history:
        role = "user" if turn["role"] == "Patient" else "assistant"
        conversation.append((role, turn["utterance"]))
    return conversation

def validate_session_history(session_history: dict):
    """Validate the session history format.

    Args:
        session_history (dict): The session history to be validated.

    Raises:
        ValueError: If the session history is empty.
        TypeError: If the session history is not a dictionary.
        ValueError: If the session history does not contain the necessary keys: name, sessionID, conversation_history and patient_answer.
        ValueError: If the conversation history is empty.
        TypeError: If the conversation history is not a list.
        TypeError: If each turn in the conversation history is not a dictionary.
        ValueError: If each turn in the conversation history does not have the keys: role and utterance.
        ValueError: If the role in the conversation history is not either "Patient" or "Grace".
        ValueError: If the name in the session history is not "COPD".
    """
    # Validate the session history format
    if not session_history:
        raise ValueError("Session history is empty.")
    if not isinstance(session_history, dict):
        raise TypeError("Session history should be a dictionary. But get: {}".format(session_history))
    # Check if the session history contains the necessary keys: name, sessionID, conversation_history and patient_answer
    if not all(key in session_history for key in ["name", "sessionID", "conversation_history", "patient_answer"]):
        raise ValueError("Session history should have keys: name, sessionID, conversation_history and patient_answer. But get: {}".format(session_history))
    session_id = session_history["sessionID"]
    # Check if the conversation history is a list of dicts, and the dicts should have keys: role and utterance
    conversation_history = session_history["conversation_history"]
    # Check the format of the conversation history
    if not conversation_history:
        # raise ValueError("Conversation history is empty.")
        print("[ID:%s] Session history is empty. Disable the validation." % session_id)
    if not isinstance(conversation_history, list):
        raise TypeError(
            "[ID:{}] Conversation history should be a list. But get: {}".format(
                session_id, conversation_history
            )
        )
    if not all(isinstance(turn, dict) for turn in conversation_history):
        raise TypeError(
            "[ID:{}] Each turn in conversation history should be a dictionary. But get: {}".format(
                session_id, conversation_history
            )
        )
    if not all("role" in turn and "utterance" in turn for turn in conversation_history):
        raise ValueError(
            "[ID:{}] Each turn in conversation history should have 'role' and 'utterance' keys. But get: {}".format(
                session_id, conversation_history
            )
        )
    # Check if the role is either "Patient" or "Grace"
    if not all(turn["role"] in ["Patient", "Grace"] for turn in conversation_history):
        raise ValueError(
            "[ID:{}] The role in conversation history should be either 'Patient' or 'Grace'. But get: {}".format(
                session_id, conversation_history
            )
        )
    # Check if the name is "COPD"
    if session_history["name"] != "COPD":
        raise ValueError(
            "[ID:{}] The name in session history should be 'COPD'. But get: {}".format(
                session_id, session_history["name"]
            )
        )
    

def parse_patient_answer(patient_answer: list, questionnaire_path=None, language=None):
    """Parse the patient answer into a DataFrame.

    Args:
        patient_answer (list): The patient answer to be parsed.
        questionnaire_path : the path that the questionnaire store
        language : the language that show on the UI

    Returns:
        pd.DataFrame: The parsed patient answer in a DataFrame format.
    """
    # Import the Questionnaire
    with open(questionnaire_path, "r") as f:
        questions = yaml.safe_load(f)
    questionnaire = questions["QUESTIONNAIRE"]
    lang = language if language is not None else questionnaire['language']

    # Parse the patient answer into a list of dicts, with key "Question" and "Patient Answer"
    parsed_patient_answer = []
    idx = 1
    for domain in questionnaire["question"]:
        if domain in patient_answer:
            patient_domain_answers = patient_answer[domain]
        else:
            patient_domain_answers = {}

        for q_code, question_text in questionnaire["question"][domain].items():
            answer = patient_domain_answers.get(q_code, "")
            translated_answer = translations.get(answer,{}).get(lang, answer)
            parsed_patient_answer.append(
                {
                    translations["question"][lang]: question_text,
                    translations["patient_answer"][lang]: translated_answer,
                    translations["index"][lang]: idx,
                    translations["notes"][lang]: "",
                }
            )
            idx += 1

    # Convert the answer to pd.DataFrame with "Index" as the dataframe index
    df = pd.DataFrame(parsed_patient_answer)
    df.set_index(translations["index"][lang], inplace=True)
    return df


def parse_score(score_result: list, rubric_path=None, language=None):
    """Parse the patient answer into a DataFrame.

    Args:
        score_result (list): The score result to be parsed.
        rubric_path : the path that the rubric store
        language : the language that show on the UI

    Returns:
        pd.DataFrame: The parsed patient answer in a DataFrame format.
    """
    with open(rubric_path, "r") as f:
        ruburic = yaml.safe_load(f)
    RUBRIC = ruburic["RUBRIC"]
    lang = language if language is not None else ruburic['language']

    # Parse the patient answer into a list of dicts, with key "Question" and "Patient Answer"
    parsed_score_result = []
    for i, item in enumerate(score_result):
        intrinsic_capacity_domains, ic_score = item["Intrinsic Capacity Domains"], item["IC Score"]
        ic_domain = RUBRIC[intrinsic_capacity_domains]
        parsed_score_result.append(
            {
                translations["intrinsic_capacity_domains"][lang]: ic_domain,
                translations["score"][lang]: ic_score,
                translations["index"][lang]: i + 1,
            },
        )

    # Convert the answer to pd.DataFrame with "Index" as the dataframe index
    df = pd.DataFrame(parsed_score_result)
    df.set_index(translations["index"][lang], inplace=True)
    return df


def parse_content(content: str):
    import streamlit as st
    for line in content.split('\n'):
        if line.startswith('[url]') and line.endswith('[url]'): # Video
            url = line[len('[url]'):-len('[url]')]
            st.video(url)
            st.write("\n\n")

        elif line.startswith('[subheader]') and line.endswith('[subheader]'): # Sub-Header
            header = line[len('[subheader]'):-len('[subheader]')]
            st.write(f"##### {header}")

        elif line.startswith('[header]') and line.endswith('[header]'): # Header
            header = line[len('[header]'):-len('[header]')]
            st.write("\n\n")
            st.write(f"#### {header}")

        elif '</a>' in line: # Hyperlink
            st.write(line, unsafe_allow_html=True)
        else:
            st.write(line)


def check_ic_scores_are_valid_from_json(score_json: json):
    for item in score_json:
        score = item.get("IC Score")
        if score is None or score == "": # icscore none and empty check
            return False
        if not isinstance(score, int):
            return False
    return True

def check_ic_scores_are_valid_from_path(icscore_json_path: str):
    with open(icscore_json_path, "r") as fr:
        score_json = json.load(fr)

    for item in score_json:
        score = item.get("IC Score")
        if score is None or score == "":
            return False
        if not isinstance(score, int):
            return False
    return True

# Function to encode an image into Base64
def encode_image_to_base64(image_path):
    import base64
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode("utf-8")





# def set_rubric(language="en", rubric_folder_path="Rubric", rubric_title=None):
#     import os
#     import glob
#     # Use Questionnaire with default language
#     # rubric_path = f"{os.path.join(config.RUBRIC_PATH, "_".join([config.Rubric_TITLE, language]))}.yaml"
#     rubric_path = f"{os.path.join(rubric_folder_path, "_".join([rubric_title, language]))}.yaml"
#     if not os.path.exists(rubric_path):
#         print(f"rubric_path: {rubric_path}")
#         raise f"[INFO] Rubric Path does not exist."
#
#     # Check if rubric with different language
#     if not os.path.exists(rubric_path):
#         # print("Check the corresponding questionnaire with different language...")
#         all_rubrics = glob.glob("Rubric/*")
#         # rubric_path = next((rubric for rubric in all_rubrics if config.Rubric_TITLE in rubric), None)
#         rubric_path = next((rubric for rubric in all_rubrics if rubric_title in rubric), None)
#
#     if rubric_path:
#         with open(rubric_path, "r") as f:
#             rubric = yaml.safe_load(f)
#             RUBRIC = rubric["RUBRIC"]
#     else:
#         RUBRIC = None
#         rubric_path = None
#
#     return RUBRIC, rubric_path

