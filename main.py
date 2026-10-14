Import json
import re
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components
from google import genai
from google.genai import types

# ---------------------------------------------------------------------------
# Page config (mobile first)
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="JARVIS",
    page_icon="⚡",
    layout="centered",
    initial_sidebar_state="collapsed",
)

MODEL = "gemini-2.5-flash"

SYSTEM_PROMPT = (
    "You are JARVIS, Tony Stark's AI assistant. "
    "You are fully bilingual and reply in Arabic or English, matching the user's language "
    "(or the preferred language if one is set). "
    "Be concise, direct, and professional. Keep answers short and easy to read on a phone."
)

# ---------------------------------------------------------------------------
# Styling
# ---------------------------------------------------------------------------
st.markdown(
    """
<style>
:root {
    --bg: #07090f;
    --surface: #0f1420;
    --surface-2: #151b2b;
    --border: rgba(255,255,255,0.07);
    --text: #e8edf6;
    --muted: #7b869c;
    --accent: #4f8cff;
    --accent-2: #8b5cf6;
}

.stApp {
    background:
        radial-gradient(1200px 500px at 50% -10%, rgba(79,140,255,0.12), transparent 60%),
        var(--bg);
    color: var(--text);
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Noto Sans Arabic", sans-serif;
}

/* Clean chrome, but keep the header so nothing breaks on mobile */
#MainMenu, footer, [data-testid="stToolbar"], [data-testid="stDecoration"],
[data-testid="stStatusWidget"] { display: none !important; }
header[data-testid="stHeader"] { background: transparent !important; height: 0 !important; }

/* Tight mobile layout */
.block-container {
    padding: 1rem 0.9rem 7rem 0.9rem !important;
    max-width: 720px !important;
}

/* Header */
.jv-title { font-size: 1.35rem; font-weight: 700; letter-spacing: -0.3px; line-height: 1.1; }
.jv-sub { font-size: 0.75rem; color: var(--muted); margin-top: 2px; display: flex; align-items: center; gap: 6px; }
.jv-dot { width: 7px; height: 7px; border-radius: 50%; background: #22c55e; box-shadow: 0 0 8px #22c55e; display: inline-block; }

/* Chat bubbles */
div[data-testid="stChatMessage"] {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 18px;
    padding: 0.7rem 0.8rem;
    margin-bottom: 0.6rem;
    gap: 0.6rem;
}
div[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) {
    background: linear-gradient(135deg, rgba(79,140,255,0.16), rgba(139,92,246,0.12));
    border-color: rgba(79,140,255,0.25);
}
div[data-testid="stChatMessage"] p,
div[data-testid="stChatMessage"] li {
    font-size: 0.98rem;
    line-height: 1.6;
    unicode-bidi: plaintext;
    text-align: start;
}
div[data-testid="stChatMessage"] img { border-radius: 12px; }

/* Chat input: floating pill */
div[data-testid="stChatInput"] {
    background: var(--surface-2) !important;
    border: 1px solid var(--border) !important;
    border-radius: 28px !important;
    padding: 2px 4px !important;
}
div[data-testid="stChatInput"] textarea {
    color: var(--text) !important;
    font-size: 16px !important; /* stops iOS zoom on focus */
}
div[data-testid="stChatInput"] button {
    background: linear-gradient(135deg, var(--accent), var(--accent-2)) !important;
    border-radius: 50% !important;
    border: none !important;
}
[data-testid="stBottom"] > div { background: transparent !important; }

/* Inputs / selects / uploader */
.stTextInput input, div[data-baseweb="select"] > div {
    background: var(--surface-2) !important;
    color: var(--text) !important;
    border: 1px solid var(--border) !important;
    border-radius: 12px !important;
    font-size: 16px !important;
}
section[data-testid="stFileUploaderDropzone"], [data-testid="stFileUploaderDropzone"] {
    background: var(--surface-2) !important;
    border: 1px dashed rgba(255,255,255,0.15) !important;
    border-radius: 14px !important;
}

/* Buttons */
.stButton > button, [data-testid="stPopover"] > button, [data-testid="stBaseButton-secondary"] {
    background: var(--surface-2) !important;
    color: var(--text) !important;
    border: 1px solid var(--border) !important;
    border-radius: 12px !important;
    min-height: 42px;
    font-weight: 600 !important;
    width: 100%;
}
.stButton > button:hover { border-color: var(--accent) !important; }

/* Expander / popover */
details, [data-testid="stExpander"] {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: 14px !important;
}

/* Empty state */
.jv-empty { text-align: center; color: var(--muted); padding: 3rem 1rem 1rem; }
.jv-empty .big { font-size: 2.6rem; margin-bottom: 0.4rem; }
.jv-empty b { color: var(--text); }
</style>
""",
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# State
# ---------------------------------------------------------------------------
if "api_key" not in st.session_state:
    key = ""
    try:
        key = st.secrets.get("gemini_api_key", "")  # works on Streamlit Cloud
    except Exception:
        pass
    if not key:
        try:
            cfg = Path("config/api_keys.json")
            if cfg.exists():
                key = json.loads(cfg.read_text(encoding="utf-8")).get("gemini_api_key", "")
        except Exception:
            pass
    st.session_state.api_key = key

st.session_state.setdefault("messages", [])
st.session_state.setdefault("uploader_id", 0)
st.session_state.setdefault("pending", False)

# ---------------------------------------------------------------------------
# Header + settings (inside the page, not the sidebar, so it works on phones)
# ---------------------------------------------------------------------------
head_l, head_r = st.columns([5, 1.4], vertical_alignment="center")
with head_l:
    st.markdown(
        "<div class='jv-title'>J.A.R.V.I.S.</div>"
        "<div class='jv-sub'><span class='jv-dot'></span>Online</div>",
        unsafe_allow_html=True,
    )
with head_r:
    settings = st.popover("⚙️", use_container_width=True)

with settings:
    language_choice = st.selectbox("Response language", ["English", "Arabic (العربية)"])
    speak_on = st.toggle("🔊 Speak replies", value=True)
    entered_key = st.text_input("Gemini API key", value=st.session_state.api_key, type="password")
    if entered_key:
        st.session_state.api_key = entered_key
    if st.button("🗑️ Clear conversation"):
        st.session_state.messages = []
        st.rerun()

is_arabic = "Arabic" in language_choice


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def speak_button(text: str, lang: str, key: str):
    """Small 'Listen' button. Needs a tap, because phones block auto-play audio."""
    clean = re.sub(r"[*_`#>~|]", "", text)
    clean = re.sub(r"\s+", " ", clean).strip()
    html = f"""
    <button id="b" style="
        background:#151b2b;color:#e8edf6;border:1px solid rgba(255,255,255,.1);
        border-radius:999px;padding:7px 14px;font-size:13px;font-family:-apple-system,Segoe UI,sans-serif;
        cursor:pointer;">🔊 Listen</button>
    <script>
      const t = {json.dumps(clean)};
      const b = document.getElementById('b');
      b.onclick = () => {{
        const s = window.speechSynthesis;
        if (!s) return;
        if (s.speaking) {{ s.cancel(); b.textContent = '🔊 Listen'; return; }}
        const u = new SpeechSynthesisUtterance(t);
        u.lang = {json.dumps("ar-SA" if lang == "ar" else "en-US")};
        u.onend = () => b.textContent = '🔊 Listen';
        b.textContent = '⏹ Stop';
        s.speak(u);
      }};
    </script>
    """
    components.html(html, height=44)


def build_contents(messages):
    """Send the whole conversation so JARVIS keeps context."""
    contents = []
    for i, m in enumerate(messages):
        role = "user" if m["role"] == "user" else "model"
        parts = [types.Part.from_text(text=m["content"])]
        # only attach images from the latest user turn to keep requests light
        if m.get("image") and i == len(messages) - 1:
            parts.append(types.Part.from_bytes(data=m["image"], mime_type=m["mime"]))
        contents.append(types.Content(role=role, parts=parts))
    return contents


# ---------------------------------------------------------------------------
# Chat history
# ---------------------------------------------------------------------------
if not st.session_state.messages:
    st.markdown(
        "<div class='jv-empty'><div class='big'>⚡</div>"
        "<b>How can I help?</b><br>Ask in English or Arabic · attach a screenshot with 📎</div>",
        unsafe_allow_html=True,
    )

last_idx = len(st.session_state.messages) - 1
for i, msg in enumerate(st.session_state.messages):
    with st.chat_message(msg["role"], avatar="🧑‍💻" if msg["role"] == "user" else "⚡"):
        if msg.get("image"):
            st.image(msg["image"], use_container_width=True)
        st.markdown(msg["content"])
        if msg["role"] == "assistant" and i == last_idx and speak_on:
            speak_button(msg["content"], "ar" if is_arabic else "en", f"sp{i}")

# ---------------------------------------------------------------------------
# Attachment (collapsed so it does not clutter the phone screen)
# ---------------------------------------------------------------------------
with st.expander("📎 Attach image"):
    uploaded_file = st.file_uploader(
        "Image",
        type=["png", "jpg", "jpeg"],
        label_visibility="collapsed",
        key=f"up_{st.session_state.uploader_id}",
    )
    if uploaded_file:
        st.caption("Attached. It will be sent with your next message.")

user_input = st.chat_input("Message JARVIS...")

# ---------------------------------------------------------------------------
# Send
# ---------------------------------------------------------------------------
if user_input:
    if not st.session_state.api_key:
        st.error("Add your Gemini API key in ⚙️ settings first.")
    else:
        entry = {"role": "user", "content": user_input}
        if uploaded_file:
            entry["image"] = uploaded_file.getvalue()
            entry["mime"] = uploaded_file.type
        st.session_state.messages.append(entry)
        st.session_state.uploader_id += 1  # resets the uploader
        st.session_state.pending = True
        st.rerun()

if st.session_state.pending:
    st.session_state.pending = False
    with st.chat_message("assistant", avatar="⚡"):
        with st.spinner("Thinking..."):
            try:
                client = genai.Client(api_key=st.session_state.api_key)
                lang_hint = (
                    "\nReply in Arabic." if is_arabic else "\nReply in the language the user writes in."
                )
                response = client.models.generate_content(
                    model=MODEL,
                    contents=build_contents(st.session_state.messages),
                    config=types.GenerateContentConfig(system_instruction=SYSTEM_PROMPT + lang_hint),
                )
                reply = response.text or "..."
                st.session_state.messages.append({"role": "assistant", "content": reply})
            except Exception as e:
                st.session_state.messages.append(
                    {"role": "assistant", "content": f"⚠️ Error: {e}"}
                )
    st.rerun()
