from config import secrets
from openai import OpenAI
from config import secrets, image_models
import streamlit as st
import base64
import re

def generate_image(prompt, empty, model_name="", parent=None):
    response = None
    error = None

    try:
        client = OpenAI(api_key=secrets['openai_api_key'])
        with empty:
            with st.spinner("Generating Image..."):
                response = client.images.generate(
                    model=model_name,
                    prompt=prompt,
                    n=1,
                    size="1024x1024",
                    quality="standard",
                    response_format="b64_json"
                )
        image = response.data[0]
        empty.image(base64.b64decode(image.b64_json))

    except Exception as e:
        match = re.search(r"'message': '([^']*)'", e.message)
        if match:
            error_message = match.group(1)
        else:
            error_message = e.message
        warning = f"""
            <div class="warn_callout">
                <p class="bold">
                    An error occurred. 
                </p>
                <p>{error_message}</p>
            </div>
        """
        empty.markdown(warning, unsafe_allow_html=True)
        
    return response, error
