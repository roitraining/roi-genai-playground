from openai import OpenAI
from config import image_models
import streamlit as st
import base64
import re

from config import load_secrets

# Cache the client for the lifetime of the Cloud Run instance.
@st.cache_resource
def _get_openai_client():
    secrets = load_secrets()  # if load_secrets() is cached, this is fast; otherwise runs once here
    return OpenAI(api_key=secrets['openai_api_key'])

def generate_image(prompt, empty, model_name="", parent=None):
    response = None
    error = None

    try:
        client = _get_openai_client()  # <-- cached; no per-request Secret Manager hit
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

        # Defensive: ensure payload exists before decoding
        if not getattr(response, "data", None):
            raise RuntimeError("Image API returned no data.")
        image = response.data[0]
        if not getattr(image, "b64_json", None):
            raise RuntimeError("No image payload (b64_json) in response.")
        empty.image(base64.b64decode(image.b64_json))

    except Exception as e:
        # Keep your original pattern but fall back to str(e) if needed
        msg_text = getattr(e, "message", None)
        if not msg_text:
            msg_text = str(e)
        match = re.search(r"'message': '([^']*)'", msg_text) or re.search(r"\"message\":\s*\"([^\"]+)\"", msg_text)
        error_message = match.group(1) if match else msg_text

        warning = f"""
            <div class="warn_callout">
                <p class="bold">An error occurred.</p>
                <p>{error_message}</p>
            </div>
        """
        empty.markdown(warning, unsafe_allow_html=True)
        error = error_message

    return response, error
