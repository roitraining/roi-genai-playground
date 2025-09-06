import streamlit as st
from config import chat_models
from config import load_secrets


@st.cache_resource
def get_openai_client():
    import openai
    secrets = load_secrets()
    openai.api_key = secrets["openai_api_key"]
    return openai

def get_response(prompt, 
                 response_container, 
                 chat=True, 
                 model_name="",
                 parent=None
                 ):
    
    openai = get_openai_client()
    
    messages = []

    prompt_message = {
        "role": "user",
        "content": prompt
    }

    system_message = {
        "role": "system",
        "content": f"""You are the ROI Generative AI Chatbot. You provide 
        responses that are clear, professional, detailed, and accurate. When 
        asked questions, you provide the answer first and then provide 
        additional information or context. When specifically prompted to do 
        step-by-step reasoning, you do so (as opposed to keeping explanation 
        until the end). Your responses should be kept to fewer than 2000 tokens
        ."""
    }

    welcome_message={
        "role": "assistant",
        "content": "Hi! I'm the ROI Chatbot. How can I help you?"
    }

    messages = [system_message, welcome_message]

    if chat and st.session_state['messages'] != []:
        messages = messages + st.session_state['messages']

    messages = messages + [prompt_message]

    if chat:
        model_name = chat_models[st.session_state['model_name']]

    stream = openai.chat.completions.create(
        model=model_name,
        messages=messages,
        temperature=0.5,
        max_tokens=2048,
        stream=True,
        top_p=1,
        n=1
    )

    response = ""

    try:
        for chunk in stream:
            if chunk.choices[0].delta.content is not None:
                response += chunk.choices[0].delta.content
                response_container.markdown(response, unsafe_allow_html=True)
        response_message = {
            "role": "assistant",
            "content": response
        }

        messages.append(response_message)

        if chat:
            st.session_state['messages'] = messages[2:]

    except Exception as e:
        warning = f"""
            <div class="warn_callout">
                An error occured
            </div>
        """
        if chat:
            st.markdown(warning, unsafe_allow_html=True)
            st.write(e)
        else:
            parent.markdown(warning, unsafe_allow_html=True)
            parent.write(e)
            
    return