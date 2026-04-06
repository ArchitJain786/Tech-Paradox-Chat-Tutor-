import html
from datetime import datetime

import streamlit as st
from google import genai
import speech_recognition as sr
import pyttsx3

from database import *
from pdf_export import export_chat_to_pdf

# -----------------------------
# STREAMLIT PAGE CONFIG
# -----------------------------
st.set_page_config(
    page_title="ChatTutor",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------------
# GEMINI CONFIG
# -----------------------------
# IMPORTANT:
# 1) Revoke the old exposed key
# 2) Paste your NEW key below
API_KEY = "AIzaSyDQtS-MYi57tqe29fhXRPYA5nP7wnhZJNM"
MODEL_NAME = "gemini-2.5-flash"

client = genai.Client(api_key=API_KEY)

# -----------------------------
# OPTIONAL VOICE SUPPORT
# -----------------------------
try:
    import pyaudio  # noqa: F401
    PYAUDIO_AVAILABLE = True
except ImportError:
    PYAUDIO_AVAILABLE = False

# -----------------------------
# SESSION STATE
# -----------------------------
if "current_session" not in st.session_state:
    st.session_state.current_session = None

if "messages" not in st.session_state:
    st.session_state.messages = []

if "show_notes" not in st.session_state:
    st.session_state.show_notes = False

if "speak_response" not in st.session_state:
    st.session_state.speak_response = False

# -----------------------------
# STYLES
# -----------------------------
st.markdown("""
<style>
    .user-wrap {
        display: flex;
        justify-content: flex-end;
        margin: 12px 0;
    }

    .user-bubble {
        background-color: #1976d2;
        color: white;
        padding: 12px 16px;
        border-radius: 18px;
        max-width: 70%;
        word-wrap: break-word;
        font-size: 15px;
    }

    .assistant-wrap {
        display: flex;
        justify-content: flex-start;
        margin: 12px 0;
    }

    .assistant-bubble {
        background-color: #f1f1f1;
        color: #222;
        padding: 12px 16px;
        border-radius: 18px;
        max-width: 70%;
        word-wrap: break-word;
        font-size: 15px;
    }

    .note-item {
        background-color: #fff8cc;
        padding: 10px 12px;
        border-left: 4px solid #ffc107;
        margin: 8px 0;
        border-radius: 4px;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------
# HELPERS
# -----------------------------
def get_system_prompt(subject: str = "") -> str:
    prompt = (
        "You are a helpful AI tutor chatbot. "
        "Answer clearly, correctly, and simply. "
        "Use easy language. "
        "When useful, explain step by step and give examples."
    )
    if subject:
        prompt += f" The current subject is {subject}."
    return prompt


def call_gemini(messages, subject=""):
    try:
        if not messages:
            return "Please ask a question."

        system_prompt = get_system_prompt(subject)

        conversation_lines = [system_prompt, "", "Conversation:"]
        for msg in messages:
            role = "User" if msg["role"] == "user" else "Assistant"
            conversation_lines.append(f"{role}: {msg['content']}")
        conversation_lines.append("Assistant:")

        prompt = "\n".join(conversation_lines)

        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt,
        )

        text = getattr(response, "text", None)
        if text and text.strip():
            return text.strip()

        return "I could not generate a response."
    except Exception as e:
        return f"Error: {str(e)}"


def display_messages():
    for msg in st.session_state.messages:
        safe_text = html.escape(msg["content"]).replace("\n", "<br>")
        if msg["role"] == "user":
            st.markdown(
                f"""
                <div class="user-wrap">
                    <div class="user-bubble">{safe_text}</div>
                </div>
                """,
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                f"""
                <div class="assistant-wrap">
                    <div class="assistant-bubble">{safe_text}</div>
                </div>
                """,
                unsafe_allow_html=True
            )


def get_speech_input():
    if not PYAUDIO_AVAILABLE:
        st.warning("PyAudio is not installed.")
        return None

    try:
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            recognizer.adjust_for_ambient_noise(source, duration=1)
            audio = recognizer.listen(source, timeout=10)
        return recognizer.recognize_google(audio)
    except Exception as e:
        st.error(f"Speech error: {str(e)}")
        return None


def speak_text(text):
    try:
        engine = pyttsx3.init()
        engine.setProperty("rate", 150)
        engine.say(text)
        engine.runAndWait()
    except Exception as e:
        st.error(f"Speech error: {str(e)}")


# -----------------------------
# SIDEBAR
# -----------------------------
with st.sidebar:
    st.title("💬 ChatTutor")

    if st.button("＋ New Chat", use_container_width=True):
        st.session_state.current_session = None
        st.session_state.messages = []
        st.rerun()

    st.divider()

    st.subheader("Chat History")
    sessions = get_all_sessions()

    if sessions:
        for session_id, title, subject, mode, created_at in sessions:
            col1, col2 = st.columns([4, 1])

            with col1:
                if st.button(title, key=f"session_{session_id}", use_container_width=True):
                    st.session_state.current_session = session_id
                    st.session_state.messages = get_session_messages(session_id)
                    st.rerun()

            with col2:
                if st.button("🗑️", key=f"delete_{session_id}"):
                    delete_session(session_id)
                    if st.session_state.current_session == session_id:
                        st.session_state.current_session = None
                        st.session_state.messages = []
                    st.rerun()
    else:
        st.info("No previous chats")

    st.divider()

    st.subheader("Settings")
    st.session_state.speak_response = st.checkbox(
        "🔊 Voice Response",
        value=st.session_state.speak_response
    )

# -----------------------------
# MAIN UI
# -----------------------------
if st.session_state.current_session is None:
    st.title("Simple Chat Tutor")

    subject = st.text_input("Subject (optional)", placeholder="Example: Biology, Python, Java")
    mode = "Chat"

    if st.button("Start Chat", use_container_width=True):
        title = f"{subject if subject else 'General Chat'} ({datetime.now().strftime('%H:%M')})"
        session_id = create_session(title, subject, mode)
        st.session_state.current_session = session_id
        st.session_state.messages = []
        st.rerun()

else:
    sessions = get_all_sessions()
    current = next((s for s in sessions if s[0] == st.session_state.current_session), None)

    if current:
        _, title, subject, mode, _ = current

        col1, col2, col3 = st.columns([2, 1, 1])

        with col1:
            st.title(f"💬 {title}")

        with col2:
            if st.button("📄 Export PDF", use_container_width=True):
                notes = get_notes(st.session_state.current_session)
                filename = f"chat_{st.session_state.current_session}.pdf"
                export_chat_to_pdf(filename, title, subject, st.session_state.messages, notes)
                st.success(f"Exported as {filename}")

        with col3:
            if st.button("📝 Notes", use_container_width=True):
                st.session_state.show_notes = not st.session_state.show_notes

        st.divider()

        display_messages()

        col1, col2 = st.columns([5, 1])

        with col1:
            user_input = st.text_input(
                "Message",
                placeholder="Ask your question here...",
                key="chat_input"
            )

        with col2:
            send = st.button("Send", use_container_width=True)

        if PYAUDIO_AVAILABLE:
            if st.button("🎤 Speak"):
                spoken_text = get_speech_input()
                if spoken_text:
                    user_input = spoken_text
                    send = True

        if send and user_input.strip():
            user_text = user_input.strip()

            user_msg = {"role": "user", "content": user_text}
            st.session_state.messages.append(user_msg)
            save_message(st.session_state.current_session, "user", user_text)

            with st.spinner("Thinking..."):
                bot_reply = call_gemini(st.session_state.messages, subject)

            assistant_msg = {"role": "assistant", "content": bot_reply}
            st.session_state.messages.append(assistant_msg)
            save_message(st.session_state.current_session, "assistant", bot_reply)

            if st.session_state.speak_response:
                speak_text(bot_reply)

            st.rerun()

        if st.session_state.show_notes:
            st.divider()
            st.subheader("Notes")

            note_input = st.text_area("Write a note", placeholder="Write your note here...")
            if st.button("Save Note"):
                if note_input.strip():
                    add_note(st.session_state.current_session, note_input.strip())
                    st.success("Note saved")
                    st.rerun()

            notes = get_notes(st.session_state.current_session)
            if notes:
                for note_id, content, created_at in notes:
                    col1, col2 = st.columns([5, 1])
                    with col1:
                        st.markdown(
                            f"<div class='note-item'>{html.escape(content)}</div>",
                            unsafe_allow_html=True
                        )
                    with col2:
                        if st.button("Delete", key=f"note_{note_id}"):
                            delete_note(note_id)
                            st.rerun()