import streamlit as st

st.set_page_config(
    page_title='ROI GenAI Playground',
    page_icon='./static/ROISquareLogo.png',
    layout="wide"
)

import time
import imagen, dall_e, stability
from config import (
    image_models, 
    google_image_models, 
    openai_image_models,
    stability_image_models,
)
from concurrent.futures import ThreadPoolExecutor, as_completed
from streamlit.runtime.scriptrunner import add_script_run_ctx

from config import load_markdown_files
md_dict = load_markdown_files()

st.markdown(md_dict['styles'], unsafe_allow_html=True)

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

stability_header_style = """
    background-color: #F4B400;
    color: white;
    display: flex;
    justify-content: center;
    align-items: center;
    height: 100%;
    border-radius: 5px;
    margin-bottom: 10px;
"""

results_style = """
    background-color: lightgray;
    color: white;
    display: flex;
    justify-content: center;
    align-items: center;
    height: 100%;
    border-radius: 5px;
    margin-bottom: 10px;
"""


def show_intro():
    """
    Displays the introduction section of the ROI Training GenAI Chat page.
    """
    st.image(
        "static/roilogo.png",
        width=200
    )
    st.title("Generative AI Playground - Image Generation")
    st.divider()

show_intro()
cols = [col for col in st.columns(3)]
containers = []
empties = []
for i, model in enumerate(image_models):
    container = cols[i % 3].container(border=True)
    header_style = ""
    if model in google_image_models:
        header_style = google_header_style
    if model in openai_image_models:
        header_style = openai_header_style
    if model in stability_image_models:
        header_style = stability_header_style
    container.markdown(
        f"<div style='{header_style}'>{model}</div>",
        unsafe_allow_html=True)
    empty = container.empty()
    containers.append(container)
    empties.append(empty)

last_prompt = st.session_state.get("prompt", None)
prompt = st.chat_input("What would you like to see?")
if prompt:
    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = []
        for i, model in enumerate(image_models):
            if model in google_image_models:
                future = executor.submit(
                    imagen.generate_image, 
                    prompt,
                    empties[i],
                    model_name=image_models[model],
                    parent = containers[i]
                )
                futures.append(future)
            if model in openai_image_models:
                future = executor.submit(
                    dall_e.generate_image, 
                    prompt,
                    empties[i],
                    model_name=image_models[model],
                    parent = containers[i]
                )
                futures.append(future)
            if model in stability_image_models:
                future = executor.submit(
                    stability.generate_image,
                    prompt,
                    empties[i],
                    model_name=image_models[model],
                    parent=containers[i]
                )
                futures.append(future)
        for t in executor._threads:
            add_script_run_ctx(t)
    prompt_reminder = f"""
        <div>
            <span class="bold">
                Results for prompt:
            </span> {prompt}
        </div>
    
    """
    st.markdown(prompt_reminder, unsafe_allow_html=True)
    # for future in as_completed(futures):
    #     st.write(future.result())