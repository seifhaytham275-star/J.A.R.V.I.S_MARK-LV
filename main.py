import streamlit as st
import json
from pathlib import Path
from google import genai
from google.genai import types

st.set_page_config(
    page_title="J.A.R.V.I.S. Mark LV",
    page_icon="⚡",
    layout="centered"
)

# Ultra-Modern Clean Dark UI (Custom CSS Injection)
st.markdown("""
    <style>
    /* Global Theme */
    .stApp {
        background-color: #080a0f;
        color: #e2e8f0;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }
    
    /* Hide Streamlit elements */
    header {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Sleek Sidebar */
    section[data-testid="stSidebar"] {
        background-color: #0f172a;
        border-right: 1px solid #1e293b;
    }
    
    /* Modern Input Fields */
    .stTextInput>div>div>input {
        background-color: #111827 !important;
        color: #f8fafc !important;
        border: 1px solid #374151 !important;
        border-radius: 10px !important;
        padding: 10px 14px !important;
    }
    .stTextInput>div>div>input:focus {
        border-color: #3b82f6 !important;
        box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.2) !important;
    }
    
    /* Modern Selectbox */
    .stSelectbox>div>div>div {
        background-color: #111827 !important;
        color: #f8fafc !important;
        border: 1px solid #374151 !important;
        border-radius: 10px !important;
    }

    /* Clean Compact File Uploader */
    section[data-testid="stFileUploadDropzone"] {
        background-color: #111827 !important;
        border: 1px dashed #374151 !important;
        border-radius: 10px !important;
        padding: 10px !important;
    }
    
    /* Modern Action Button */
    .stButton>button {
        background: linear-gradient(135deg, #1e293b, #0f172a) !important;
        color: #f8fafc !important;
        border: 1px solid #334155 !important;
        border-radius: 10px !important;
        font-weight: 600 !important;
        padding: 8px 16px !important;
        width: 100% !important;
        transition: all 0.2s ease;
    }
    .stButton>button:hover {
        background: linear-gradient(135deg, #334155, #1e293b) !important;
        border-color: #64748b !important;
    }

    /* Chat Messages Styling */
    div[data-testid="stChatMessage"] {
        background-color: #111827;
        border: 1px solid #1f2937;
        border-radius: 12px;
        padding: 12px;
        margin-bottom: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# Minimal Modern Header
st.markdown("""
    <div style='text-align: center; padding: 1rem 0;'>
        <h1 style='color: #f8fafc; font-weight: 700; letter-spacing: -0.5px; margin-bottom: 0;'>J.A.R.V.I.S. Mark LV</h1>
        <p style='color: #64748b; font-size: 0.9rem; margin-top: 4px;'>Neural Cloud Interface</p>
    </div>
""", unsafe_allow_html=True)

# Initialize session state for API key and Chat History
if "api_key" not in st.session_state:
    st.session_state.api_key = ""
    try:
        config_path = Path("config/api_keys.json")
        if config_path.exists():
            with open(config_path, "r", encoding="utf-8") as f:
                st.session_state.api_key = json.load(f).get("gemini_api_key", "")
    except Exception:
        pass

if "messages" not in st.session_state:
    st.session_state.messages = []

# Modern Minimal Sidebar
with st.sidebar:
    st.markdown("<h3 style='color: #f8fafc;'>System Preferences</h3>", unsafe_allow_html=True)
    
    language_choice = st.selectbox(
        "Response Language",
        ["English", "Arabic (العربية)"]
    )

    voice_choice = st.selectbox(
        "Voice Tone",
        ["Puck", "Charon", "Kore", "Fenrir"]
    )

    entered_api_key = st.text_input(
        "Gemini API Key", 
        value=st.session_state.api_key, 
        type="password"
    )

    if entered_api_key:
        st.session_state.api_key = entered_api_key
        
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("Clear Conversation"):
        st.session_state.messages = []
        st.rerun()

st.markdown("---")

# Display historical chat messages in clean cards
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Clean Chat Input & Optional Attachment
user_input = st.chat_input("Message JARVIS...")
uploaded_file = st.file_uploader("Attach file / screen capture (optional):", type=["png", "jpg", "jpeg"])

if user_input or uploaded_file:
    if not st.session_state.api_key:
        st.error("Please configure your Gemini API Key in the sidebar.")
    else:
        prompt_text = user_input if user_input else "Analyze this attachment:"
        
        st.session_state.messages.append({"role": "user", "content": prompt_text})
        with st.chat_message("user"):
            st.markdown(prompt_text)
            if uploaded_file:
                st.image(uploaded_file, use_column_width=True)

        with st.spinner("Processing..."):
            try:
                client = genai.Client(api_key=st.session_state.api_key)
                
                contents = [prompt_text]
                if uploaded_file:
                    bytes_data = uploaded_file.getvalue()
                    contents.append(
                        types.Part.from_bytes(
                            data=bytes_data,
                            mime_type=uploaded_file.type
                        )
                    )
                
                system_instruction = (
                    "You are JARVIS, Tony Stark's AI assistant. "
                    "You are fully bilingual and can seamlessly understand and reply in both Arabic and English depending on what the user speaks or prefers. "
                    "Be concise, direct, and professional."
                )

                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=contents,
                    config=types.GenerateContentConfig(
                        system_instruction=system_instruction
                    )
                )
                
                reply_text = response.text
                
                st.session_state.messages.append({"role": "assistant", "content": reply_text})
                with st.chat_message("assistant"):
                    st.markdown(reply_text)
                
                # Text-to-speech execution
                lang_code = "ar-SA" if "Arabic" in language_choice else "en-US"
                clean_reply = reply_text.replace('"', '').replace("'", "").replace("\n", " ")
                
                sound_html = f"""
                <script>
                function speakText() {{
                    if ('speechSynthesis' in window) {{
                        let utterance = new SpeechSynthesisUtterance("{clean_reply}");
                        utterance.lang = "{lang_code}";
                        window.speechSynthesis.speak(utterance);
                    }}
                }}
                speakText();
                </script>
                """
                st.components.v1.html(sound_html, height=0)
                
            except Exception as e:
                st.error(f"Error: {e}")
