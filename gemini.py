import streamlit as st

import vertexai
import vertexai.preview.generative_models as generative_models
from vertexai.generative_models import GenerativeModel
from vertexai.generative_models import (
    GenerativeModel,
    ResponseValidationError,
    FinishReason
)
from config import (
    chat_models,
    project_id,
    region
)

def get_stop_reason_name(stop_reason):
    for member in FinishReason:
        if member.value == stop_reason:
            return member.name
        
def get_chat_messages(client):
    messages = []
    for entry in client.history:
        message = {}
        if entry.role == "model":
            message['role'] = "assistant"
        else:
            message['role'] = "user"
        message['content'] = entry.parts[0].text
        messages.append(message)
    return messages

def get_response(prompt, empty, chat=True, model_name="", parent=None):
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
        "top_p": 1,
        "candidate_count": 1,
    }

    safety_settings = {
        generative_models.HarmCategory.HARM_CATEGORY_HATE_SPEECH: generative_models.HarmBlockThreshold.BLOCK_ONLY_HIGH,
        generative_models.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: generative_models.HarmBlockThreshold.BLOCK_ONLY_HIGH,
        generative_models.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: generative_models.HarmBlockThreshold.BLOCK_ONLY_HIGH,
        generative_models.HarmCategory.HARM_CATEGORY_HARASSMENT: generative_models.HarmBlockThreshold.BLOCK_ONLY_HIGH,
    }

    if chat:
        model_name = chat_models[st.session_state['model_name']]
    
    if chat and "gemini_chat_client" in st.session_state:
        chat_client = st.session_state["gemini_chat_client"]
    else:
        model = GenerativeModel(
            model_name,
            system_instruction=[system_message]
        )
        chat_client = model.start_chat()

    results = chat_client.send_message(
        [prompt],
        generation_config=generation_config,
        safety_settings=safety_settings,
        stream=True
    )

    response = ""

    try:
        for result in results:
            response += result.text
            empty.markdown(response, unsafe_allow_html=True)

    except ResponseValidationError as e:
        last_part = e.responses[-1].candidates[0].to_dict()
        warning = f"""
            <div class="warn_callout">
                A <span class="bold">ResponseValidationError</span> 
                occurred. Information about the part that generated the 
                error is below. The finish reason was <span 
                class="bold">{get_stop_reason_name(
                last_part['finish_reason'])}</span>.
            </div>
        """
        if chat:
            st.markdown(warning, unsafe_allow_html=True)
            st.json(last_part)
        else:
            parent.markdown(warning, unsafe_allow_html=True)
            parent.json(last_part, expanded=False)

    if chat:
        st.session_state["gemini_chat_client"] = chat_client
        st.session_state["messages"] = get_chat_messages(chat_client)
        
    return 
