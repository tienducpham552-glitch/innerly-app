import streamlit as st
import google.generativeai as genai

# --- Cấu hình trang ---
st.set_page_config(page_title="Innerly Studio", page_icon="🧸")

# Lấy API Key từ Secrets
api_key = st.secrets.get("GEMINI_API_KEY", "")

if api_key:
    genai.configure(api_key=api_key)
else:
    st.error("⚠️ Chưa có API Key trong phần Secrets!")

def get_ai_response(prompt):
    try:
        # Sử dụng model ổn định nhất
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Innerly đang gặp chút lỗi: {str(e)}"

# --- Giao diện chính ---
st.title("Tâm sự cùng Innerly 🧸")

if "history" not in st.session_state:
    st.session_state.history = []

for msg in st.session_state.history:
    st.chat_message(msg["role"]).write(msg["content"])

if prompt := st.chat_input("Hãy chia sẻ cùng mình..."):
    st.session_state.history.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)
    with st.chat_message("assistant"):
        res = get_ai_response(prompt)
        st.write(res)
        st.session_state.history.append({"role": "assistant", "content": res})
