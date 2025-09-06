# Chatbot.py
import importlib
import streamlit as st
from config import (
    chat_models,
    gemini_models,
    non_gemini_google_models,
    openai_models,
    claude_models,
)

# ---- App config (do this once) ----
st.set_page_config(page_title="ROI GenAI Playground")

# ---- Cached helpers ----
@st.cache_resource
def _load_md_dict():
    # Avoid doing this at import-time; cache for container lifetime
    from config import load_markdown_files
    return load_markdown_files()

md_dict = _load_md_dict()
st.markdown(md_dict.get("styles", ""), unsafe_allow_html=True)

# ---- Lazy backend resolver ----
MODULE_MAP = {
    "gemini": "gemini",
    "google_legacy": "non_gemini",
    "openai": "open_ai",
    "claude": "claude",
}

def _get_backend_module(model_name: str):
    """
    Import provider modules only when the chosen model requires them.
    This prevents heavy SDKs (vertexai, openai, anthropic) from loading on the home screen.
    """
    if model_name in gemini_models:
        return importlib.import_module(MODULE_MAP["gemini"])
    if model_name in non_gemini_google_models:
        return importlib.import_module(MODULE_MAP["google_legacy"])
    if model_name in openai_models:
        return importlib.import_module(MODULE_MAP["openai"])
    if model_name in claude_models:
        return importlib.import_module(MODULE_MAP["claude"])
    raise ValueError(f"Unknown model: {model_name}")

# ---- State utilities ----
def clear_chat():
    """Clear chat history and any cached per-provider chat clients in session."""
    st.session_state["messages"] = []
    # If providers cached chat clients in session, drop them here so they are rebuilt lazily
    for key in ("gemini_chat_client", "non_gemini_chat_client", "openai_chat_client", "claude_chat_client"):
        st.session_state.pop(key, None)

# ---- UI: Sidebar & header ----
def show_sidebar():
    """Model picker + quick reset button."""
    # Import inside to avoid importing extras unless the sidebar renders
    try:
        from streamlit_extras.add_vertical_space import add_vertical_space
    except Exception:
        add_vertical_space = None

    with st.sidebar:
        if add_vertical_space:
            add_vertical_space(1)
        else:
            st.write("")  # simple spacer fallback

        col1, col2 = st.columns([4, 1])
        with col1:
            current = st.session_state.get("model_name", None)
            model_choice = st.selectbox(
                "Select model",
                tuple(chat_models.keys()),
                index=(tuple(chat_models.keys()).index(current) if current in chat_models else 0),
                on_change=clear_chat,
            )
            st.session_state["model_name"] = model_choice

        with col2:
            st.container(height=14, border=False)
            if st.button("↻", use_container_width=True):
                clear_chat()

def show_intro():
    """Top-of-page intro and greeting."""
    st.image("static/roilogo.png", width=200)
    st.title("Generative AI Playground - Chat")
    st.divider()
    # Show the friendly assistant greeting once per (empty) session
    if not st.session_state.get("messages"):
        with st.chat_message("assistant"):
            st.markdown("Hi! I'm the ROI Chatbot. How can I help you?")

# ---- Main page flow ----
if "model_name" not in st.session_state:
    # Keep your original default
    st.session_state["model_name"] = "Gemini-Pro 1.5"

if "messages" not in st.session_state:
    st.session_state["messages"] = []

show_sidebar()
show_intro()

# Render prior messages (backends typically append to session_state["messages"])
for msg in st.session_state["messages"]:
    st.chat_message(msg["role"]).markdown(msg["content"], unsafe_allow_html=True)

# Handle new user input
if prompt := st.chat_input():
    st.chat_message("user").write(prompt)
    with st.chat_message("assistant"):
        # Lazy import and delegate to the chosen backend
        backend = _get_backend_module(st.session_state["model_name"])
        # Each backend implements: get_response(prompt, response_container, ...)
        backend.get_response(prompt, st.empty())
