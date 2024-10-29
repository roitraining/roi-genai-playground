import streamlit as st

import vertexai
from vertexai.language_models import (
    ChatModel, 
    TextGenerationModel,
    CodeGenerationModel,
    CodeChatModel
)
from config import (
    chat_models,
    text_models,
    codey_models,
    project_id,
    region
)

class RequestBlocked(Exception):
    def __init__(self, message):
        self.message = message

def get_chat_messages(client):
    messages = []
    for entry in client.message_history:
        message = {}
        if entry.author == "bot":
            message['role'] = "assistant"
        else:
            message['role'] = "user"
        message['content'] = entry.content
        messages.append(message)
    return messages

def get_response(prompt, response_container):
    vertexai.init(project=project_id, location=region)

    system_message = """
        You are the ROI Generative AI Chatbot. You provide responses
        that are clear, professional, detailed, and accurate. When asked
        questions, you provide the answer first and then provide additional
        information or context. When specifically prompted to do step-by-step
        reasoning, you do so (as opposed to keeping explanation until the end).
        Your responses should be kept to fewer than 2000 tokens.
    """

    generation_config = {
        "max_output_tokens": 2048,
        "temperature": 0.5,
        "top_p": 1
    }

    if "non_gemini_chat_client" in st.session_state:
        chat = st.session_state["non_gemini_chat_client"]
    else:
        model_name = chat_models[st.session_state['model_name']]
        if is_codey(model_name, is_chat=True):
            del generation_config["top_p"]
            model = CodeChatModel.from_pretrained(model_name)
        else:
            model = ChatModel.from_pretrained(model_name)
        chat = model.start_chat(
            context = system_message
        )

    results = chat.send_message_streaming(
        prompt,
        **generation_config
    )

    response = ""

    try:
        for result in results:
            if (result._prediction_response.predictions[0]['safetyAttributes'][0]['blocked']):
                raise RequestBlocked('Blocked content detected')
            response += result.text
            response_container.markdown(response, unsafe_allow_html=True)

    except RequestBlocked as e:
        st.markdown(f"""
            <div class="warn_callout">
                This response was cut off due to blocked content.
            </div>
        """, unsafe_allow_html=True)

    except Exception as e:
        st.write(e)
    st.session_state["non_gemini_chat_client"] = chat
    st.session_state["messages"] = get_chat_messages(chat)

    return

# need to handle chat too
def is_codey(model_name, is_chat=False):
    if is_chat:
        models = chat_models
    else:
        models = text_models

    for key, value in models.items():
        if model_name == value and key in codey_models:
            return True
        
    return False

def get_text_response(prompt, response_container, model_name, parent=None):
    vertexai.init(project=project_id, location=region)

    system_message = """
        You are the ROI Generative AI Chatbot. You provide responses
        that are clear, professional, detailed, and accurate. When asked
        questions, you provide the answer first and then provide additional
        information or context. When specifically prompted to do step-by-step
        reasoning, you do so (as opposed to keeping explanation until the end).
        Your responses should be kept to fewer than 2000 tokens.
    """

    generation_config = {
        "max_output_tokens": 2048,
        "temperature": 0.5,
    }

    if is_codey(model_name):
        model = CodeGenerationModel.from_pretrained(model_name)
    else:
        model = TextGenerationModel.from_pretrained(model_name)

    results = model.predict_streaming(
        prompt,
        **generation_config
    )

    response = ""
    try:
        for result in results:
            blocked = result._prediction_response.predictions[0]['safetyAttributes']["blocked"]
            if (blocked):
                raise RequestBlocked('Blocked content detected')
            response += result.text
            response_container.markdown(response, unsafe_allow_html=True)

    except RequestBlocked as e:
        parent.markdown(f"""
            <div class="warn_callout">
                This response was cut off due to blocked content.
            </div>
        """, unsafe_allow_html=True)

    except Exception as e:
        parent.write(e)
        
    return
