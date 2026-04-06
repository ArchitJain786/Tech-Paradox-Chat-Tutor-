import streamlit as st
import google.generativeai as genai
from dotenv import load_dotenv
import os
import speech_recognition as sr
import pyttsx3
from database import *
from pdf_export import export_chat_to_pdf
from datetime import datetime

# Check for pyaudio
try:
    import pyaudio
    PYAUDIO_AVAILABLE = True
except ImportError:
    PYAUDIO_AVAILABLE = False

load_dotenv()

# Page config
st.set_page_config(
    page_title="Teacher ChatBot",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Modern CSS styling
st.markdown("""
<style>
    * {
        margin: 0;
        padding: 0;
    }
    
    body {
        background-color: #ffffff;
    }
    
    .main-container {
        max-width: 900px;
        margin: 0 auto;
    }
    
    .user-message {
        display: flex;
        justify-content: flex-end;
        margin: 12px 0;
    }
    
    .user-message-content {
        background-color: #1976d2;
        color: white;
        padding: 12px 16px;
        border-radius: 18px;
        max-width: 70%;
        word-wrap: break-word;
        font-size: 14px;
    }
    
    .assistant-message {
        display: flex;
        justify-content: flex-start;
        margin: 12px 0;
    }
    
    .assistant-message-content {
        background-color: #f0f0f0;
        color: #333;
        padding: 12px 16px;
        border-radius: 18px;
        max-width: 70%;
        word-wrap: break-word;
        font-size: 14px;
    }
    
    .chat-container {
        height: 500px;
        overflow-y: auto;
        padding: 15px;
        background-color: #ffffff;
        border-radius: 8px;
    }
    
    .input-area {
        display: flex;
        gap: 10px;
        margin-top: 15px;
        align-items: flex-end;
    }
    
    .stTextInput input {
        border-radius: 24px !important;
        border: 1px solid #ddd !important;
        padding: 10px 16px !important;
    }
    
    .stButton button {
        border-radius: 24px !important;
        padding: 8px 20px !important;
        background-color: #1976d2 !important;
        color: white !important;
        border: none !important;
    }
    
    .note-item {
        background-color: #fffacd;
        padding: 10px 12px;
        border-left: 3px solid #ffc107;
        margin: 8px 0;
        border-radius: 4px;
    }
    
    .progress-bar {
        height: 20px;
        background-color: #e0e0e0;
        border-radius: 10px;
        overflow: hidden;
        margin: 10px 0;
    }
    
    .progress-fill {
        height: 100%;
        background: linear-gradient(90deg, #4caf50, #45a049);
        transition: width 0.3s ease;
    }
</style>
""", unsafe_allow_html=True)

# Session state initialization
if "current_session" not in st.session_state:
    st.session_state.current_session = None
if "messages" not in st.session_state:
    st.session_state.messages = []
if "api_key" not in st.session_state:
    st.session_state.api_key = os.getenv("GOOGLE_GEMINI_API_KEY", "")
if "speak_response" not in st.session_state:
    st.session_state.speak_response = False

def get_system_prompt(mode="teach"):
    """Get system prompt based on teaching mode"""
    base_prompt = """You are an expert, patient teacher. Help students learn effectively.
- Explain clearly and simply
- Use real-world examples
- Break down complex topics
- Be encouraging and supportive"""
    
    if mode == "quiz":
        return base_prompt + "\n\nYou are in QUIZ MODE. Ask ONE question at a time and evaluate answers."
    elif mode == "explain":
        return base_prompt + "\n\nYou are in EXPLAIN MODE. Provide detailed explanations with examples."
    return base_prompt

def call_gemini(messages, system_prompt):
    """Call Google Gemini API"""
    if not st.session_state.api_key:
        return "Please add your Google Gemini API key in the settings."
    
    try:
        genai.configure(api_key=st.session_state.api_key)
        model = genai.GenerativeModel(model_name="gemini-1.5-flash")
        
        # Prepare messages with system instruction
        formatted_messages = []
        
        # Add system instruction as first user-model exchange
        formatted_messages.append({
            "role": "user",
            "parts": [system_prompt]
        })
        formatted_messages.append({
            "role": "model",
            "parts": ["I understand. I will follow these instructions."]
        })
        
        # Add chat history
        for msg in messages:
            if msg["role"] == "user":
                formatted_messages.append({"role": "user", "parts": [msg["content"]]})
            else:
                formatted_messages.append({"role": "model", "parts": [msg["content"]]})
        
        # Start chat and get response
        chat = model.start_chat(history=formatted_messages[:-1])
        response = chat.send_message(
            formatted_messages[-1]["parts"][0] if formatted_messages else "Hello",
            generation_config=genai.types.GenerationConfig(temperature=0.7, max_output_tokens=1000)
        )
        
        return response.text
    except Exception as e:
        return f"Error: {str(e)}"

def get_speech_input():
    """Get speech input"""
    if not PYAUDIO_AVAILABLE:
        st.warning("PyAudio not installed. Use text input instead.")
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
    """Text to speech"""
    try:
        engine = pyttsx3.init()
        engine.setProperty('rate', 150)
        engine.say(text)
        engine.runAndWait()
    except Exception as e:
        st.error(f"Speech error: {str(e)}")

def display_messages():
    """Display chat messages"""
    container = st.container()
    with container:
        for msg in st.session_state.messages:
            if msg["role"] == "user":
                st.markdown(f'<div style="display: flex; justify-content: flex-end; margin: 12px 0;"><div style="background-color: #1976d2; color: white; padding: 12px 16px; border-radius: 18px; max-width: 70%;">{msg["content"]}</div></div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div style="display: flex; justify-content: flex-start; margin: 12px 0;"><div style="background-color: #f0f0f0; color: #333; padding: 12px 16px; border-radius: 18px; max-width: 70%;">{msg["content"]}</div></div>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.title("💬 ChatTutor")
    
    # API Key
    api_key = st.text_input("API Key", value=st.session_state.api_key, type="password", key="api_key_input")
    if api_key:
        st.session_state.api_key = api_key
    
    st.divider()
    
    # New Chat
    if st.button("+ New Chat", use_container_width=True):
        st.session_state.current_session = None
        st.session_state.messages = []
        st.rerun()
    
    st.divider()
    
    # Chat History
    st.subheader("Chat History")
    sessions = get_all_sessions()
    
    if sessions:
        for session_id, title, subject, mode, created_at in sessions:
            col1, col2 = st.columns([4, 1])
            with col1:
                if st.button(f"📖 {title}", use_container_width=True, key=f"session_{session_id}"):
                    st.session_state.current_session = session_id
                    st.session_state.messages = get_session_messages(session_id)
                    st.rerun()
            with col2:
                if st.button("🗑️", key=f"del_{session_id}", help="Delete"):
                    delete_session(session_id)
                    if st.session_state.current_session == session_id:
                        st.session_state.current_session = None
                    st.rerun()
    else:
        st.info("No chats yet. Create a new one!")
    
    st.divider()
    
    # Settings
    st.subheader("⚙️ Settings")
    st.session_state.speak_response = st.checkbox("🔊 Voice Response", value=st.session_state.speak_response)

# Main content
if st.session_state.current_session is None:
    # New chat dialog
    col1, col2 = st.columns(2)
    with col1:
        mode = st.radio("Mode", ["Interactive Q&A", "Explanations", "Quiz"], horizontal=True)
    with col2:
        subject = st.text_input("Subject (optional)", placeholder="e.g., Python, Biology...")
    
    if st.button("Start Chat", use_container_width=True):
        chat_name = f"{mode} - {subject if subject else 'General'} ({datetime.now().strftime('%H:%M')})"
        session_id = create_session(chat_name, subject, mode)
        st.session_state.current_session = session_id
        st.rerun()
else:
    # Active chat
    session = get_all_sessions()
    current = next((s for s in session if s[0] == st.session_state.current_session), None)
    
    if current:
        _, title, subject, mode, _ = current
        
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            st.title(f"📚 {title}")
        with col2:
            if st.button("📥 Export PDF", use_container_width=True):
                notes = get_notes(st.session_state.current_session)
                filename = f"chat_{st.session_state.current_session}.pdf"
                export_chat_to_pdf(filename, title, subject, st.session_state.messages, notes)
                st.success(f"Exported to {filename}")
        with col3:
            if st.button("📋 Notes", use_container_width=True):
                st.session_state.show_notes = not st.session_state.get("show_notes", False)
        
        st.divider()
        
        # Chat display
        display_messages()
        
        # Input area
        col1, col2 = st.columns([5, 1])
        with col1:
            user_input = st.text_input("Message...", placeholder="Ask something...", key="chat_input")
        with col2:
            send = st.button("Send", use_container_width=True)
        
        # Speech option
        if PYAUDIO_AVAILABLE:
            if st.button("🎤 Speak"):
                user_input = get_speech_input()
                if user_input:
                    send = True
        
        # Process input
        if send and user_input:
            # Save user message
            st.session_state.messages.append({"role": "user", "content": user_input})
            save_message(st.session_state.current_session, "user", user_input)
            
            # Get response
            system_prompt = get_system_prompt({"Interactive Q&A": "teach", "Explanations": "explain", "Quiz": "quiz"}.get(mode, "teach"))
            if subject:
                system_prompt += f"\n\nStudent is learning: {subject}"
            
            with st.spinner("🤔 Thinking..."):
                response = call_gemini(st.session_state.messages, system_prompt)
            
            # Save assistant message
            st.session_state.messages.append({"role": "assistant", "content": response})
            save_message(st.session_state.current_session, "assistant", response)
            
            # Speak response
            if st.session_state.speak_response:
                speak_text(response)
            
            st.rerun()
        
        # Notes section
        if st.session_state.get("show_notes", False):
            st.divider()
            st.subheader("📝 Notes")
            
            note_input = st.text_area("Add a note...", placeholder="Take notes while learning...")
            if st.button("Save Note"):
                add_note(st.session_state.current_session, note_input)
                st.success("Note saved!")
            
            notes = get_notes(st.session_state.current_session)
            if notes:
                st.subheader("Your Notes")
                for note_id, content, created_at in notes:
                    col1, col2 = st.columns([5, 1])
                    with col1:
                        st.markdown(f"<div class='note-item'>{content}</div>", unsafe_allow_html=True)
                    with col2:
                        if st.button("Delete", key=f"note_{note_id}"):
                            delete_note(note_id)
                            st.rerun()
        
        # Progress
        progress = get_progress(st.session_state.current_session)
        if progress["total"] > 0:
            st.divider()
            st.subheader("📊 Progress")
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Correct Answers", f"{progress['correct']}/{progress['total']}")
            with col2:
                st.metric("Score", f"{progress['score']:.1f}%")
