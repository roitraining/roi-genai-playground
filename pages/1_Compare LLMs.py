import streamlit as st

st.set_page_config(
    page_title='ROI GenAI Playground',
    page_icon='./static/ROISquareLogo.png',
    layout="wide"
)

import openai
import open_ai, gemini, non_gemini, claude

from concurrent.futures import ThreadPoolExecutor, as_completed
from streamlit.runtime.scriptrunner import add_script_run_ctx
from config import (
    text_models,
    gemini_models,
    non_gemini_google_models,
    openai_models,
    claude_models,
)



google_header_style = """
    background-color: #4285f4;
    color: white;
    display: flex;
    justify-content: center;
    align-items: center;
    height: 100%;
    border-radius: 5px;
    margin-bottom: 10px;
"""

openai_header_style = """
    background-color: rgb(16, 163, 127);
    color: white;
    display: flex;
    justify-content: center;
    align-items: center;
    height: 100%;
    border-radius: 5px;
    margin-bottom: 10px;
"""

claude_header_style = """
    background-color: #F0EEE5;
    display: flex;
    justify-content: center;
    align-items: center;
    height: 100%;
    border-radius: 5px;
    margin-bottom: 10px;
"""

from config import load_secrets
secrets = load_secrets()

from config import load_markdown_files
md_dict = load_markdown_files()

st.markdown(md_dict['styles'], unsafe_allow_html=True)

openai.api_key = secrets['openai_api_key']

def gen_prompt_display(prompt):
    prompt_display_outline = """
        border: 1px solid rgba(49, 51, 63, 0.2);
        border-radius: 5px;
        padding: 10px 15px;
        display: block;
        margin-bottom: 10px;
    """

    prompt_display_title = """
        background-color: rgba(49, 51, 63, 0.2);
        display: flex;
        justify-content: center;
        align-items: center;
        height: 100%;
        border-radius: 5px;
        margin-bottom: 10px;
    """

    prompt_display_content =f"""
        <div style='{prompt_display_outline}'>
            <div style='{prompt_display_title}'>
                Prompt
            </div>
            {prompt}
        </div>
    """
    return prompt_display_content

def show_intro():
    """
    Displays the introduction section of the ROI Training GenAI Chat page.
    """
    st.image(
        "static/roilogo.png",
        width=200
    )
    st.title("Generative AI Playground - Compare LLMs")
    st.divider()

show_intro()

prompt_display_container = st.container()
prompt_display_empty = prompt_display_container.empty()

cols = [col for col in st.columns(3)]
containers = []
empties = []
for i, model in enumerate(text_models):
    header_style = ""
    if model in gemini_models or model in non_gemini_google_models:
        container = cols[0].container(border=True)
        header_style = google_header_style
    if model in openai_models:
        container = cols[1].container(border=True)
        header_style = openai_header_style
    if model in claude_models:
        container = cols[2].container(border=True)
        header_style = claude_header_style
    container.markdown(
        f"<div style='{header_style}'>{model}</div>",
        unsafe_allow_html=True)
    empty = container.empty()
    containers.append(container)
    empties.append(empty)

prompt = st.chat_input("Your prompt")
if prompt:
    prompt_display_empty.markdown(gen_prompt_display(prompt), unsafe_allow_html=True)
    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = []
        for i, model in enumerate(text_models):
            if model in openai_models:
                future = executor.submit(
                    open_ai.get_response, 
                    prompt, 
                    empties[i], 
                    chat=False, 
                    model_name=text_models[model],
                    parent=containers[i]
                )
                futures.append(future)
            if model in gemini_models:
                future = executor.submit(
                    gemini.get_response, 
                    prompt, 
                    empties[i],
                    chat=False,
                    model_name=text_models[model],
                    parent=containers[i]
                )
                futures.append(future)
            if model in non_gemini_google_models:
                future = executor.submit(
                    non_gemini.get_text_response,
                    prompt,
                    empties[i],
                    model_name=text_models[model],
                    parent=containers[i]
                )
                futures.append(future)
            if model in claude_models:
                future = executor.submit(
                    claude.get_response,
                    prompt,
                    empties[i],
                    chat=False,
                    model_name=text_models[model],
                    parent=containers[i]
                )
                futures.append(future)
        for t in executor._threads:
            add_script_run_ctx(t)

    # for future in as_completed(futures):
    #     future.result()