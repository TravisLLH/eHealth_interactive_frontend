# First
import json
import random

import requests
import streamlit as st

# NGROK_DOMAIN = "http://eez115.ece.ust.hk:5000/"
NGROK_DOMAIN = "http://localhost:8080/"

with st.sidebar:
    user_id = st.text_input(
        label="Please input your User ID here:",
        key="user_id",
        type="default",
        value=None,
    )
    domain = st.text_input(
        "Please input the chatbot domain here:",
        key="domain",
        type="default",
        value=NGROK_DOMAIN,
    )
    display_mode = st.selectbox(
        label="Please select your display mode",
        options=("normal", "log"),
        key="select_display_mode",
    )

st.title("💬 PAF Chatbot")


def initialize():
    # st.session_state["session_id"] = random.randint(10000000, 500000000)
    fixed_session_id = 12345678
    r = requests.post(f"{NGROK_DOMAIN}/delete_session", json={"session_id": fixed_session_id})
    if r.status_code != 200:
        st.error("Fail to initialize a session. Please refresh the pages and try again.")
        st.stop()
    else:
        st.success("Session initialized! " + r.json().get("responses",{}).get("result", {}))
        # st.write(r.json())
    st.session_state["session_id"] = fixed_session_id
    query = {
        "text": "INITIALIZE-SESSION",
        "session_id": st.session_state["session_id"],
        "message_list": ["INITIALIZE-SESSION"],
        "redo": False,
    }
    r = requests.post(f"{NGROK_DOMAIN}/dialogue", json=query)
    if r.status_code != 200:
        chatbot_message = {
            "responses": {
                "next_question_text": "Sorry I didn't hear you due to network issue. Can you wait for a few seconds and type it again?"
            },
            "status": False,
        }
        st.error(
            "Network unstable. Please type your input and send again. Your history won't be lost."
        )
    else:
        # st.success("Message sent!")
        reply = r.json()
        chatbot_message = reply
        chatbot_message["status"] = True
    return chatbot_message


def send_message(text=""):
    if not text:
        return ""
    query = {
        "text": text,
        "session_id": st.session_state["session_id"],
        "message_list": [text],
        "redo": False,
    }
    st.success("Message sent! Start processing...")
    r = requests.post(f"{NGROK_DOMAIN}/dialogue", json=query)
    if r.status_code != 200:
        chatbot_message = {
            "responses": {
                "next_question_text": "Sorry I didn't hear you due to network issue. Can you wait for a few seconds and type it again?"
            },
            "status": False,
        }
        # "Sorry I didn't hear you due to network issue. Can you wait for a few seconds and type it again?"
        error_message = "Network unstable. Please type your input and send again. Your history won't be lost."
        st.error(error_message)
    else:
        reply = r.json()
        chatbot_message = reply
        chatbot_message["status"] = True
        st.success("Processing Finished!")
    return chatbot_message


def display_chat(mode: str = "normal"):
    """Display chat history

    Args:
        mode (str, optional): model of conversation, either "normal" or "log". Defaults to "normal".
    """
    if mode == "normal":
        for msg in st.session_state.messages:
            st.chat_message(msg["role"]).write(msg["content"])
    else:
        for msg in st.session_state.messages:
            if msg["role"] == "user":
                st.chat_message(msg["role"]).write(msg["content"])
            elif msg["role"] == "assistant":
                st.write(
                    {
                        "relevance": msg["relevance"],
                        "level": msg["level"],
                        "scaffold_method": msg["scaffold_method"],
                        "msg": msg
                    }
                )
                st.chat_message(msg["role"]).write(msg["content"])


def parse_greetings(greetings):
    greetings_translation = greetings.get("responses", {}).get("next_question_text", "")
    st.session_state["messages"] = [
        {
            "role": "assistant",
            "content": greetings_translation,
            "response": greetings,
            "relevance": greetings.get("user_input", {}).get(
                "relevance", "start conversation, not checked"
            ),
            "level": greetings.get("user_input", {}).get("level", ""),
            "scaffold_method": greetings.get("responses", {}).get(
                "scaffold_method", "start conversation, N.A."
            ),
            "original_response": greetings,
        }
    ]
    st.chat_message("assistant").write(greetings_translation)
    return greetings_translation


def parse_chatbot_reply(chatbot_sentence):
    chatbot_sentence_translation = chatbot_sentence.get("responses", {}).get(
        "next_question_text", ""
    )

    other_SFQs = {}
    sfq_list = chatbot_sentence.get("candidate_sf_questions", [])
    if sfq_list:
        for sfq in sfq_list:
            sf_method = sfq.get("scaffolding method", "")
            sf_question = sfq.get("question", "")
            if sf_method and sf_question:
                other_SFQs[sf_method] = sf_question

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": chatbot_sentence_translation,
            "response": chatbot_sentence,
            "relevance": chatbot_sentence.get("user_input", {}).get("relevance", ""),
            "level": chatbot_sentence.get("user_input", {}).get("level", ""),
            "scaffold_method": chatbot_sentence.get("responses", {}).get(
                "scaffold_method", ""
            ),
            "other_SFQs": other_SFQs if other_SFQs else {},
            "original_response": chatbot_sentence,
        }
    )
    st.chat_message("assistant").write(chatbot_sentence_translation)
    return chatbot_sentence_translation


if __name__ == "__main__":
    # if "user_id" not in st.session_state or st.session_state.get("user_id") is None:
    if not user_id:
        st.info("Please input your User ID on the left pane to start conversation.")
        st.stop()
    # if not domain:
    #     st.info("Please input your domain on the left pane to start conversation.")
    #     st.stop()
    NGROK_DOMAIN = domain

    # start conversation
    if "messages" not in st.session_state:
        # That indicates the first time user talk with the chatbot
        greetings = initialize()
        greetings_translation = greetings.get("responses", {}).get(
            "next_question_text", ""
        )
        st.session_state["messages"] = [
            {
                "role": "assistant",
                "content": greetings_translation,
                "response": greetings,
                "relevance": greetings.get("user_input", {}).get(
                    "relevance", "start conversation"
                ),
                "level": greetings.get("user_input", {}).get("level", ""),
                "scaffold_method": greetings.get("responses", {}).get(
                    "scaffold_method", "start conversation"
                ),
                "original_response": greetings,
            }
        ]
        st.chat_message("assistant").write(greetings_translation)
    else:
        display_chat(display_mode)

    if prompt := st.chat_input():
        st.chat_message("user").write(prompt)

        prompt_translation = prompt

        st.session_state.messages.append(
            {"role": "user", "content": prompt, "translation": prompt_translation}
        )

        chatbot_sentence = send_message(prompt_translation)

        chatbot_sentence_translation = chatbot_sentence.get("responses", {}).get(
            "next_question_text", ""
        )

        other_SFQs = {}
        sfq_list = chatbot_sentence.get("candidate_sf_questions", [])
        if sfq_list:
            for sfq in sfq_list:
                sf_method = sfq.get("scaffolding method", "")
                sf_question = sfq.get("question", "")
                if sf_method and sf_question:
                    other_SFQs[sf_method] = sf_question

        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": chatbot_sentence_translation,
                "response": chatbot_sentence,
                "relevance": chatbot_sentence.get("user_input", {}).get(
                    "relevance", ""
                ),
                "level": chatbot_sentence.get("user_input", {}).get("level", ""),
                "scaffold_method": chatbot_sentence.get("responses", {}).get(
                    "scaffold_method", ""
                ),
                "other_SFQs": other_SFQs if other_SFQs else {},
                "original_response": chatbot_sentence,
            }
        )
        st.chat_message("assistant").write(chatbot_sentence_translation)

    with st.sidebar:
        st.write("Your Session ID: ", st.session_state["session_id"])
        st.download_button(
            "Download Conversation History",
            data=json.dumps(st.session_state.messages, indent=4, ensure_ascii=False),
            file_name=f"{user_id}_conversation_history.json",
        )
