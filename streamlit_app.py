import streamlit as st
import google.generativeai as genai

# --- CẤU HÌNH ---
st.set_page_config(page_title="Innerly Studio", page_icon="🧸")

# Lấy API Key từ Secrets
api_key = st.secrets.get("GEMINI_API_KEY", "")

if api_key:
    genai.configure(api_key=api_key)
else:
    st.error("⚠️ Chưa có API Key! Hãy kiểm tra lại phần Secrets.")

def get_ai_response(prompt):
    try:
        # ÉP CỨNG DÙNG MODEL FLASH 1.5 (MIỄN PHÍ & ỔN ĐỊNH)
        model = genai.GenerativeModel('gemini-1.5-flash')
        return model.generate_content(prompt).text
    except Exception as e:
        return f"Lỗi: {str(e)}"

# --- GIAO DIỆN CHAT ---
st.title("Tâm sự cùng Innerly 🧸")

if "history" not in st.session_state:
    st.session_state.history = []

for msg in st.session_state.history:
    st.chat_message(msg["role"]).write(msg["content"])

if prompt := st.chat_input("Kể cho mình nghe đi..."):
    st.session_state.history.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)
    with st.chat_message("assistant"):
        res = get_ai_response(prompt)
        st.write(res)
        st.session_state.history.append({"role": "assistant", "content": res})

