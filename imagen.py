from vertexai.preview.vision_models import ImageGenerationModel
from config import image_models
import streamlit as st

def generate_image(prompt, empty, model_name="", parent=None):
    response = None
    error = None
    
    try:
        model = ImageGenerationModel.from_pretrained(model_name)
        with empty:
            with st.spinner("Generating Image..."):
                response = model.generate_images(
                    prompt=prompt,
                    number_of_images=1,
                    guidance_scale=21,
                    safety_filter_level="block_few",
                    #person_generation="allow_adult",
                    aspect_ratio="1:1",
                )
        if response is None:
            return
        image = response.images[0]
        empty.image(image._image_bytes)

    except Exception as e:
        warning = f"""
            <div class="warn_callout">
                <p class="bold">
                    An error occurred. 
                </p>
                <p>{e.message}</p>
            </div>
        """
        empty.markdown(warning, unsafe_allow_html=True)
        
    return response, error
