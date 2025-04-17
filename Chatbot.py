import streamlit as st
import gemini
import non_gemini
import open_ai
import claude
from config import (
    chat_models, 
    gemini_models,
    non_gemini_google_models,
    openai_models,
    md_dict,
    claude_models
)

st.set_page_config(
    page_title='ROI GenAI Playground',
    page_icon='./static/ROISquareLogo.png',
)

st.markdown(md_dict['styles'], unsafe_allow_html=True)

def clear_chat():
    """
    Clears the chat messages and resets the chat clients.
    """
    st.session_state["messages"] = []
    
    if "gemini_chat_client" in st.session_state:
        del st.session_state["gemini_chat_client"]
    
    if "non_gemini_chat_client" in st.session_state:
        del st.session_state["non_gemini_chat_client"]

def show_sidebar():
    """
    Displays the sidebar with a selectbox to choose a model.
    Updates the session state with the selected model type.
    """
    from streamlit_extras.add_vertical_space import add_vertical_space
    with st.sidebar:
        add_vertical_space(1)
        col1, col2 = st.columns([4, 1])
        with col1:
            if model_name := st.selectbox(
                "Select model",
                (key for key in chat_models.keys()),
                on_change=clear_chat
            ):
                st.session_state['model_name'] = model_name
        with col2:
            st.container(height=14, border=False)
            if st.button("↻", use_container_width=True):
                clear_chat()
        
def show_intro():
    """
    Displays the introduction section of the GenAI Playground application.
    """
    st.image(
        "https://storage.googleapis.com/files.roitraining.com/images/logo.png",
        width=300
    )
    st.title("Generative AI Playground - Chat")
    st.divider()


if "model_name" not in st.session_state:
    st.session_state["model_name"] = 'Gemini-Pro 1.5'
    
show_sidebar()
show_intro()

with st.chat_message("assistant"):
    st.markdown("Hi! I'm the ROI Chatbot. How can I help you?")

if "messages" not in st.session_state:
    st.session_state["messages"] = []

if "gemini_chat_client" in st.session_state:
    client = st.session_state["gemini_chat_client"]

if "non_gemini_chat_client" in st.session_state:
    client = st.session_state["non_gemini_chat_client"]

for msg in st.session_state["messages"]:
    st.chat_message(msg['role']).markdown(msg['content'], unsafe_allow_html=True)

if prompt := st.chat_input():
    st.chat_message("user").write(prompt)
    with st.chat_message("assistant"):
        if st.session_state['model_name'] in gemini_models:
            gemini.get_response(prompt, st.empty())
        if st.session_state['model_name'] in non_gemini_google_models:
            non_gemini.get_response(prompt, st.empty())
        if st.session_state['model_name'] in openai_models:
            open_ai.get_response(prompt, st.empty())
        if st.session_state['model_name'] in claude_models:
            claude.get_response(prompt, st.empty())
