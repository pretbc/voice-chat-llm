import base64
import uuid
import os
import time
import streamlit as st
import soundfile as sf
import whisper

from langchain_core.messages import HumanMessage, AIMessage
from langchain_ollama import ChatOllama

from src.audio_processing import transcribe_audio, text_to_speach
from src.auth import authenticate_user, auth_token
from src.webRTC import WebRTCHandler
from src.chat import ChatAssistant, END
from typing import Literal

CONVERSATION_ITERATIONS = 15
SPINNER_MSG = "Mów teraz. Nagrywanie odpowiedzi..."

MAX_ATTEMPTS = 3  # Set your maximum attempts here
COOLDOWN_PERIOD = 60  # Cooldown period in seconds (1 minute)

# Initialize session state variables
if 'login_attempts' not in st.session_state:
    st.session_state.login_attempts = 0
if 'cooldown_start' not in st.session_state:
    st.session_state.cooldown_start = None

authenticator = authenticate_user()

if 'is_running' not in st.session_state:
    st.session_state.is_running = True


@st.cache_resource(show_spinner=True)
def load_whisper_model():
    return whisper.load_model("small")


def play_audio_autoplay(file_path, audio_placeholder):
    with open(file_path, "rb") as f:
        data = f.read()
    b64 = base64.b64encode(data).decode()

    unique_id = str(uuid.uuid4())
    audio_html = f"""
    <audio id="{unique_id}" controls autoplay>
        <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
    </audio>
    """
    audio_placeholder.empty()
    time.sleep(.1)
    audio_placeholder.markdown(audio_html, unsafe_allow_html=True)


def update_chat(chat_placeholder, messages):
    with chat_placeholder.container():
        for message in messages:
            role: Literal['user', 'assistant'] = 'user' if isinstance(message, HumanMessage) else 'assistant'
            with st.chat_message(role):
                st.write(message.content)


def user_respond(msg_placeholder, webrtc_ctx: WebRTCHandler):
    webrtc_ctx.clear_audio_buffer()
    webrtc_ctx.mute_audio(False)

    with msg_placeholder.container():
        with st.spinner(SPINNER_MSG):
            time.sleep(6)

    webrtc_ctx.mute_audio(True)
    with msg_placeholder.container():
        with st.spinner("Przetwarzanie..."):
            text = transcribe_audio(webrtc_ctx.audio_data, load_whisper_model(), sample_rate=webrtc_ctx.sample_rate)

    return text


def play_voice_chat(respond: AIMessage, audio_placeholder):
    audio_file = text_to_speach(respond.content)
    audio_data, sample_rate = sf.read(audio_file)
    audio_duration = len(audio_data) / sample_rate

    play_audio_autoplay(audio_file, audio_placeholder)
    os.unlink(audio_file)

    time.sleep(audio_duration + 1)  # Wait for the actual duration of the audio
    audio_placeholder.empty()


def login():
    try:
        authenticator.login()
    except AttributeError:
        st.error("Authentication failed due to missing or invalid configuration.")
    else:
        if st.session_state['authentication_status'] or auth_token():
            if not st.session_state['authentication_status']:
                st.session_state['authentication_status'] = True
            st.session_state.login_attempts = 0
            st.session_state.cooldown_start = None  # Reset cooldown
            main()
        elif st.session_state['authentication_status'] is False:
            st.session_state.login_attempts += 1
            if st.session_state.login_attempts >= MAX_ATTEMPTS:
                if st.session_state.cooldown_start is None:
                    st.session_state.cooldown_start = time.time()
                elapsed_time = time.time() - st.session_state.cooldown_start

                if elapsed_time < COOLDOWN_PERIOD:
                    remaining_time = COOLDOWN_PERIOD - elapsed_time
                    countdown_placeholder = st.empty()
                    for remaining in range(int(remaining_time), 0, -1):
                        countdown_placeholder.error(
                            f'Maximum login attempts exceeded. Please wait {remaining} seconds before trying again.'
                        )
                        time.sleep(1)  # Sleep for a second to create a countdown effect

                    countdown_placeholder.success('You can try logging in again.')
                    st.session_state.login_attempts = 0  # Reset attempts after cooldown
                    st.session_state.cooldown_start = None  # Reset cooldown state
                else:
                    st.session_state.login_attempts = 0
                    st.session_state.cooldown_start = None
                    st.warning('You can try logging in again.')
            else:
                st.error('Username/password is incorrect')
        elif st.session_state['authentication_status'] is None:
            st.warning('Please enter your username and password')


def main():
    st.title("Voice Chat with AI Assistant")
    st.subheader(
        "Please allow the browser to access your microphone then press start button to begin the conversation."
    )
    st.subheader(f"The conversation will end after :orange[{CONVERSATION_ITERATIONS}] iterations.")
    st.subheader(
        f"User should wait for a :red[spinner] msg: :orange[\"{SPINNER_MSG}\"] to appear, before speaking.",
        divider="gray"
    )

    chat_placeholder = st.empty()
    audio_placeholder = st.empty()
    msg_placeholder = st.empty()

    load_whisper_model()
    chat_assistant = ChatAssistant(ChatOllama(model='gemma2', temperature=0.9))
    webrtc_handler = WebRTCHandler()

    while webrtc_handler.is_playing and st.session_state.is_running:
        webrtc_handler.mute_audio(True)
        ai_message_count = sum(1 for msg in chat_assistant.chat_history if isinstance(msg, HumanMessage))

        if not chat_assistant.chat_history:
            respond = chat_assistant.invoke()
        else:
            user_input = user_respond(msg_placeholder, webrtc_handler)
            respond = chat_assistant.invoke(user_input)

        if ai_message_count > CONVERSATION_ITERATIONS:
            respond = chat_assistant.invoke(END)
            st.session_state.is_running = False

        update_chat(chat_placeholder, chat_assistant.chat_history)
        play_voice_chat(respond, audio_placeholder)


if __name__ == "__main__":
    login()
