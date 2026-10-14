import streamlit as st
import json
from pathlib import Path
from google import genai
from google.genai import types

st.set_page_config(
    page_title="J.A.R.V.I.S. Command Interface",
    page_icon="⚡",
    layout="centered"
)

# Custom Cyberpunk / Jarvis Dark Theme Styling
st.markdown("""
    <style>
    .main {
        background-color: #0e1117;
        color: #c9d1d9;
    }
    .stTextInput>div>div>input {
        background-color: #161b22;
        color: #58a6ff;
        border: 1px solid #30363d;
        border-radius: 8px;
    }
    .stSelectbox>div>div>div {
        background-color: #161b22;
        color: #58a6ff;
        border: 1px solid #30363d;
        border-radius: 8px;
    }
    .stButton>button {
        background: linear-gradient(45deg, #1f6feb, #238636);
        color: white;
        border: none;
        border-radius: 8px;
        font-weight: bold;
        width: 100%;
        transition: 0.3s;
    }
    .stButton>button:hover {
        opacity: 0.85;
    }
    </style>
""", unsafe_allow_html=True)

st.title("⚡ J.A.R.V.I.S. Core Interface")
st.caption("Advanced AI Mobile Bridge — Bilingual & Voice Enabled")

# Initialize session state for API key
if "api_key" not in st.session_state:
    st.session_state.api_key = ""
    try:
        config_path = Path("config/api_keys.json")
        if config_path.exists():
            with open(config_path, "r", encoding="utf-8") as f:
                st.session_state.api_key = json.load(f).get("gemini_api_key", "")
    except Exception:
        pass

# Sidebar Settings
with st.sidebar:
    st.markdown("### ⚙️ System Controls")
    
    language_choice = st.selectbox(
        "Response Language",
        ["English", "Arabic (العربية)"]
    )

    voice_choice = st.selectbox(
        "Voice Tone",
        ["Puck (Deep/Powerful)", "Charon (Formal/Calm)", "Kore (Assistant)", "Fenrir (Firm)"]
    )

    entered_api_key = st.text_input(
        "Gemini API Key", 
        value=st.session_state.api_key, 
        type="password",
        help="Saved for this session."
    )

    if entered_api_key:
        st.session_state.api_key = entered_api_key
        
    st.markdown("---")
    st.info("System Status: **ONLINE** 🟢\nCloud Node: Active")

# Main Interface
st.markdown("---")

user_input = st.text_input("💬 Command JARVIS (Arabic / English):", placeholder="Type your instruction or question here...")
uploaded_file = st.file_uploader("📸 Share screen or upload image for analysis:", type=["png", "jpg", "jpeg"])

if st.button("🚀 EXECUTE COMMAND"):
    if not st.session_state.api_key:
        st.error("⚠️ Please configure your Gemini API Key in the sidebar.")
    elif not user_input and not uploaded_file:
        st.warning("⚠️ Please provide a text command or an image input.")
    else:
        with st.spinner("Processing protocol..."):
            try:
                client = genai.Client(api_key=st.session_state.api_key)
                
                contents = []
                if user_input:
                    contents.append(user_input)
                
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
                
                st.markdown("### 📋 Response Output:")
                st.success(reply_text)
                
                # Text-to-speech injection
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
                st.error(f"❌ Execution failed: {e}")
