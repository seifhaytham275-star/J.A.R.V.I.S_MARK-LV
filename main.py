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

st.title("🤖 J.A.R.V.I.S. Bilingual Mobile Bridge")
st.write("أهلاً بك يا سيف. جارفيس جاهز الآن باللغتين العربية والإنجليزية مع النطق الصوتي المباشر.")

# الشريط الجانبي للإعدادات واختيار الصوت واللغة
st.sidebar.title("⚙️ إعدادات جارفيس")

language_choice = st.sidebar.selectbox(
    "لغة التحدث الافتراضية:",
    ["العربية (Arabic)", "English"]
)

voice_choice = st.sidebar.selectbox(
    "اختر نبرة الصوت:",
    ["Puck (Deep/قوي)", "Charon (Formal/رسمي)", "Kore (Assistant/مساعد)", "Fenrir (Firm/حازم)"]
)

api_key = st.sidebar.text_input("Gemini API Key", type="password")

if not api_key:
    try:
        config_path = Path("config/api_keys.json")
        if config_path.exists():
            with open(config_path, "r", encoding="utf-8") as f:
                api_key = json.load(f).get("gemini_api_key", "")
    except Exception:
        pass

st.markdown("---")
st.subheader("💬 المحادثة والأوامر")

# تحديد لغة التوجيه للذكاء الاصطناعي بناءً على اختيار المستخدم
system_instruction = (
    "You are JARVIS, Tony Stark's AI assistant. "
    "You are fully bilingual and can seamlessly understand and reply in both Arabic and English depending on what the user speaks or prefers. "
    "Be concise, direct, and professional."
)

user_input = st.text_input("اكتب أمرك بالعربية أو الإنجليزية / Type your command:")
uploaded_file = st.file_uploader("📸 مشاركة شاشة أو صورة للتحليل / Upload screen or image:", type=["png", "jpg", "jpeg"])

if st.button("تنفيذ / Execute"):
    if not api_key:
        st.error("الرجاء إدخال مفتاح الـ API في الشريط الجانبي أولاً.")
    elif not user_input and not uploaded_file:
        st.warning("الرجاء كتابة أمر أو إرفاق صورة.")
    else:
        try:
            with st.spinner("جارفيس قيد التنفيذ / JARVIS is processing..."):
                client = genai.Client(api_key=api_key)
                
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
                
                # استدعاء النموذج مع توجيهات اللغتين
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=contents,
                    config=types.GenerateContentConfig(
                        system_instruction=system_instruction
                    )
                )
                
                reply_text = response.text
                st.success("رد جارفيس / JARVIS Response:")
                st.write(reply_text)
                
                # تشغيل الصوت تلقائياً عبر متصفح الموبايل (Web Speech API)
                # كود JavaScript خفيف ليقوم بقراءة الرد بصوت واضح
                lang_code = "ar-SA" if "العربية" in language_choice else "en-US"
                
                # تنظيف النص من الرموز لكي لا تقرأ خطأ
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
            st.error(f"حدث خطأ أثناء الاتصال: {e}")

st.sidebar.markdown("---")
st.sidebar.info("💡 جارفيس الآن يفهم العربي والإنجليزي تماماً، وينطق الإجابات صوتياً مباشرة من متصفح هاتفك!")
