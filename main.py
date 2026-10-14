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

# Clean, professional, and minimalist dark theme styling (No logos, pure focus on chat)
st.markdown("""
    <style>
    .stApp {
        background-color: #0d1117;
        color: #e6edf3;
    }
    header {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Sleek Sidebar */
    section[data-testid="stSidebar"] {
        background-color: #161b22;
        border-right: 1px solid #30363d;
    }
    
    /* Clean Input Fields */
    .stTextInput>div>div>input {
        background-color: #21262d !important;
        color: #f0f6fc !important;
        border: 1px solid #30363d !important;
        border-radius: 6px !important;
    }
    .stSelectbox>div>div>div {
        background-color: #21262d !important;
        color: #f0f6fc !important;
        border: 1px solid #30363d !important;
        border-radius: 6px !important;
    }

    /* Minimalist Button */
    .stButton>button {
        background-color: #21262d !important;
        color: #c9d1d9 !important;
        border: 1px solid #30363d !important;
        border-radius: 6px !important;
        font-weight: 500 !important;
        width: 100% !important;
        transition: 0.2s;
    }
    .stButton>button:hover {
        background-color: #30363d !important;
        color: #ffffff !important;
        border-color: #8b949e !important;
    }
    </style>
""", unsafe_allow_html=True)

# Title updated cleanly to Mark LV without extra logos
st.title("J.A.R.V.I.S. Mark LV")
st.caption("Secure Mobile Interface")

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

# Sidebar settings (Clean & Minimal)
with st.sidebar:
    st.markdown("### Settings")
    
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
        
    st.markdown("---")
    if st.button("Clear Conversation"):
        st.session_state.messages = []
        st.rerun()

st.markdown("---")

# Display historical chat messages in an elegant chat container
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input bar at the bottom
user_input = st.chat_input("Type a message...")
uploaded_file = st.file_uploader("Attach image / screen (Optional):", type=["png", "jpg", "jpeg"])

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
