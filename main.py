import streamlit as st
import json
from pathlib import Path
from google import genai
from google.genai import types

st.set_page_config(
    page_title="J.A.R.V.I.S. Core Interface",
    page_icon="⚡",
    layout="centered"
)

# Complete Custom High-Tech Dark Theme
st.markdown("""
    <style>
    /* Main Background & Text Color */
    .stApp {
        background-color: #090c10;
        color: #e6edf3;
    }
    
    /* Hide Streamlit Header & Footer elements for clean view */
    header {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Sidebar Dark Styling */
    section[data-testid="stSidebar"] {
        background-color: #0d1117;
        border-right: 1px solid #21262d;
    }
    
    /* Custom Input Boxes */
    .stTextInput>div>div>input {
        background-color: #161b22 !important;
        color: #58a6ff !important;
        border: 1px solid #30363d !important;
        border-radius: 8px !important;
    }
    
    .stSelectbox>div>div>div {
        background-color: #161b22 !important;
        color: #58a6ff !important;
        border: 1px solid #30363d !important;
        border-radius: 8px !important;
    }

    /* File Uploader Dark Theme */
    section[data-testid="stFileUploadDropzone"] {
        background-color: #161b22 !important;
        border: 1px dashed #30363d !important;
        border-radius: 10px !important;
    }
    
    /* Futuristic Glow Button */
    .stButton>button {
        background: linear-gradient(135deg, #0052d4, #4364f7, #6fb1fc) !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 700 !important;
        letter-spacing: 1px !important;
        padding: 0.6rem 1rem !important;
        width: 100% !important;
        box-shadow: 0 4px 15px rgba(67, 100, 247, 0.4) !important;
        transition: all 0.3s ease !important;
    }
    
    .stButton>button:hover {
        box-shadow: 0 6px 20px rgba(67, 100, 247, 0.7) !important;
        transform: translateY(-1px) !important;
    }

    /* Response Box Styling */
    .jarvis-response-box {
        background-color: #161b22;
        border: 1px solid #30363d;
        border-left: 4px solid #58a6ff;
        border-radius: 8px;
        padding: 1.2rem;
        margin-top: 1rem;
        color: #e6edf3;
        font-size: 1rem;
        line-height: 1.6;
    }
    </style>
""", unsafe_allow_html=True)

st.title("⚡ J.A.R.V.I.S. Core Interface")
st.caption("Dark Node Architecture — Mobile & Voice Ready")

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

# Sidebar Settings Controls
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
                st.markdown(f'<div class="jarvis-response-box">{reply_text}</div>', unsafe_allow_html=True)
                
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
