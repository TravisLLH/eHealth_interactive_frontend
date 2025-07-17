import streamlit as st
from translation import translations
from Config import config

def render_sidebar():
    with st.sidebar:
        st.page_link("frontend_display_result.py", label=f"💬&nbsp;&nbsp;{translations['main_page'][config.language]}")
        st.page_link("pages/Test_Result.py", label=f"📝&nbsp;&nbsp;{translations['test_result'][config.language]}")
        st.divider()

        session_id = st.text_input(
            label=translations['input_session_id'][config.language],
            key="user_id",
            type="default",
            value=config._current_session_id if config._current_session_id is not None else "",
        )
        domain = st.text_input(
            label=translations['input_chatbot_domain'][config.language],
            key="domain",
            type="default",
            value=config.ngrok_domain,
        )

        # Language selection dropdown
        options = list(translations['language'].values())

        # Map display labels to language codes
        language_map = {v: k for k, v in translations['language'].items()}

        # Show the dropdown with the current language selected
        selected_label = translations['language'][config.language]
        new_label = st.selectbox(
            translations['select_language'][config.language],
            options,
            index=options.index(selected_label),
            key="lang_select"
        )

        # If the language changes, update session state and refresh
        new_lang = language_map[new_label]
        if new_lang != config.language:
            config.language = new_lang
            st.session_state.language = config.language
            config.set_rubric()

            # print(f"new_lang: {new_lang}")
            # print(f"lang: {lang}")
            # print(f"config.language: {config.language}")
            st.rerun()

        return session_id, domain

        # st.header("My App Sidebar")
        # # st.image("logo.png", use_column_width=True)
        # # Custom navigation links
        # st.page_link("frontend_display_result.py", label="Main Page (Page 1)", icon="📄")
        # st.page_link("pages/Test_Result.py", label="Home", icon="🏠")
        # # st.page_link("pages/page2.py", label="Page 2", icon="📊")
        # # Initialize session state for selectbox
        # if "sidebar_selectbox" not in st.session_state:
        #     st.session_state.sidebar_selectbox = "Option 1"
        # st.selectbox(
        #     "Choose an option",
        #     ["Option 1", "Option 2", "Option 3"],
        #     key="sidebar_selectbox"
        # )
        # if st.button("Apply", key="sidebar_button"):
        #     st.write(f"Selected: {st.session_state.sidebar_selectbox}")