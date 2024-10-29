import streamlit as st
from config import secrets, chat_models, project_id, region
from anthropic import AnthropicVertex

# turns out that Claude models aren't all available in central
region = "us-east5"
client = AnthropicVertex(region=region, project_id=project_id)

class ClaudeError(Exception):
    def __init__(self, message):
        self.message = message

def get_response(prompt, 
                 response_container,
                 chat=True,
                 model_name="",
                 parent=None):
    messages = []
    prompt_message = {
        "role": "user",
        "content": prompt
    }
    system_message = f"""
        You are the ROI Generative AI Chatbot. You provide responses
        that are clear, professional, detailed, and accurate. When asked
        questions, you provide the answer first and then provide additional
        information or context. When specifically prompted to do step-by-step
        reasoning, you do so (as opposed to keeping explanation until the end).
        Your responses should be kept to fewer than 2000 tokens."""

    if chat:
        if st.session_state['messages'] != []:
            messages = messages + st.session_state['messages']

    messages = messages + [prompt_message]

    if chat:
        model_name = chat_models[st.session_state['model_name']]

    stream = client.messages.create(
        model=model_name,
        max_tokens=2048,
        system=system_message,
        messages= messages,
        stream=True
    )

    response = ""
    try:
        for event in stream:
            if event.type == "content_block_delta":
                response += event.delta.text
                response_container.markdown(response, unsafe_allow_html=True)
            if event.type == "error":
                raise ClaudeError(event)

        response_message = {
            "role": "assistant",
            "content": response
        }
        messages.append(response_message)
        if chat:
            st.session_state['messages'] = messages

    except ClaudeError as e:
        warning = f"""
            <div class="warn_callout">
                Claude reported and error.
            </div>
        """
        if chat:
            st.markdown(warning, unsafe_allow_html=True)
            st.json(event)
        else:
            parent.markdown(warning, unsafe_allow_html=True)
            parent.json(event)

    except Exception as e:
        warning = f"""
            <div class="warn_callout">
                An error occured.
            </div>
        """
        if chat:
            st.markdown(warning, unsafe_allow_html=True)
            st.json(event)
        else:
            parent.markdown(warning, unsafe_allow_html=True)
            parent.json(event)
    
    return