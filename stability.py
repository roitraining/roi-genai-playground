from config import image_models, secrets
import streamlit as st
import requests


def generate_image(prompt, empty, model_name="sd3-large-turbo", parent=None):
    sd3_endpoint = "https://api.stability.ai/v2beta/stable-image/generate/sd3"
    api_key = secrets['stability_api_key']
    response = requests.post(
        sd3_endpoint,
        headers = {
            "authorization": f"Bearer {api_key}",
            "accept": "image/*",
        },
        data={
            "prompt": prompt,
            "model": model_name,
            "mode": "text-to-image",
            "aspect_ratio": "1:1",
            "output_format": "jpeg"
        },
        files={"none": ""}
    )
    if not response.ok:
        empty.markdown(
            f"""
            <div class="warn_callout">
                <p class="bold">
                    An error occurred. 
                </p>
                <p>{response.text}</p>
            </div>
            """,
            unsafe_allow_html=True
        )
        return

    finish_reason = response.headers.get("finish_reason", "")
    if finish_reason == "CONTENT_FILTERED":
        empty.markdown(
            f"""
            <div class="warn_callout">
                <p class="bold">
                    An error occurred. 
                </p>
                <p>Content filtered by the model.</p>
            </div>
            """,
            unsafe_allow_html=True
        )
        return

    image = response.content
    empty.image(image)
    return
