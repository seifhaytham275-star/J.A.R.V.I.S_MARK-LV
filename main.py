import streamlit as st
import json
from pathlib import Path
from google import genai
from google.genai import types

st.set_page_config(
    page_title="J.A.R.V.I.S. Mobile Control Center",
    page_icon="🤖",
    layout="centered"
)

st.title("🤖 J.A.R.V.I.S. Mobile Bridge")
st.write("Welcome back, Seif. JARVIS is ready and fully bilingual (Arabic & English) with direct voice output.")

# Initialize session state for API key if not already present
if "api_key" not in st.session_state:
    st.session_state.api_key = ""
    # Try automatic loading from local config if available
    try:
        config_path = Path("config/api_keys.json")
        if config_path.exists():
            with open(config_path, "r", encoding="utf-8") as f:
                st.session_state.api_key = json.load(f).get("gemini_api_key", "")
    except Exception:
        pass

# Sidebar Settings
st.sidebar.title("⚙️ JARVIS Settings")

language_choice = st.sidebar.selectbox(
    "Default Response Language:",
    ["English", "Arabic (العربية)"]
)

voice_choice = st.sidebar.selectbox(
    "Voice Tone:",
    ["Puck (Deep/Powerful)", "Charon (Formal/Calm)", "Kore (Assistant)", "Fenrir (Firm)"]
)

# One-time API key input using session state
entered_api_key = st.sidebar.text_input(
    "Gemini API Key", 
    value=st.session_state.api_key, 
    type="password",
    help="Enter your API key once. It will be saved for this session."
)

if entered_api_key:
    st.session_state.api_key = entered_api_key

st.markdown("---")
st.subheader("💬 Chat & Commands")

system_instruction = (
    "You are JARVIS, Tony Stark's AI assistant. "
    "You are fully bilingual and can seamlessly understand and reply in both Arabic and English depending on what the user speaks or prefers. "
    "Be concise, direct, and professional."
)

user_input = st.text_input("Type your command in English or Arabic:")
uploaded_file = st.file_uploader("📸 Share screen or upload image for analysis:", type=["png", "jpg", "jpeg"])

if st.button("Execute / Send"):
    if not st.session_state.api_key:
        st.error("Please enter your Gemini API Key in the sidebar first.")
    elif not user_input and not uploaded_file:
        st.warning("Please type a command or upload an image.")
    else:
        try:
            with st.spinner("JARVIS is processing..."):
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
                
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=contents,
                    config=types.GenerateContentConfig(
                        system_instruction=system_instruction
                    )
                )
                
                reply_text = response.text
                st.success("JARVIS Response:")
                st.write(reply_text)
                
                # Text-to-speech for mobile browser
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
            st.error(f"An error occurred: {e}")

st.sidebar.markdown("---")
st.sidebar.info("💡 Your API key is saved for this session, so you only need to type it once!")
