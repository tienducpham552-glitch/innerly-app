import streamlit as st
import google.generativeai as genai
import pandas as pd
import time
from datetime import datetime

# 1. CẤU HÌNH
st.set_page_config(page_title="Innerly Studio", page_icon="🧸", layout="wide")

# 2. API KEY (Tự động lấy từ Secrets)
api_key = st.secrets.get("GEMINI_API_KEY", "")
if api_key:
    genai.configure(api_key=api_key)

def get_ai_response(prompt):
    if not api_key:
        return "⚠️ Chưa nhập Key! Bạn hãy vào Settings -> Secrets để điền nhé."
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        return model.generate_content(prompt).text
    except Exception as e:
        return f"Lỗi kết nối: {str(e)}"

# 3. GIAO DIỆN
st.markdown("""<style>
    @import url('https://fonts.googleapis.com/css2?family=Quicksand:wght@500;700&display=swap');
    * { font-family: 'Quicksand', sans-serif; }
    .stApp { background: linear-gradient(120deg, #a1c4fd 0%, #c2e9fb 100%); }
    .card { background: rgba(255,255,255,0.9); padding: 20px; border-radius: 15px; text-align: center; margin-bottom: 10px; }
</style>""", unsafe_allow_html=True)

with st.sidebar:
    st.title("Innerly Studio 🧸")
    menu = st.radio("Menu", ["Chat AI", "Rút Thẻ", "Thả Trôi"])

if menu == "Chat AI":
    st.header("Tâm sự cùng Innerly")
    if "history" not in st.session_state: st.session_state.history = []
    
    for msg in st.session_state.history:
        st.chat_message(msg["role"]).write(msg["content"])
        
    if prompt := st.chat_input("Bạn đang nghĩ gì..."):
        st.session_state.history.append({"role": "user", "content": prompt})
        st.chat_message("user").write(prompt)
        with st.chat_message("assistant"):
            res = get_ai_response(prompt)
            st.write(res)
            st.session_state.history.append({"role": "assistant", "content": res})

elif menu == "Rút Thẻ":
    st.header("Thông điệp chữa lành 🌿")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="card"><h3>🌧️ Buồn</h3><p>Cho phép mình buồn 15 phút thôi nhé.</p></div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="card"><h3>🔋 Mệt</h3><p>Ngủ một giấc thật sâu để sạc lại pin.</p></div>', unsafe_allow_html=True)

elif menu == "Thả Trôi":
    st.header("Hộp thả trôi nỗi buồn 🗑️")
    if st.text_area("Viết nỗi buồn vào đây:") and st.button("🌬️ Thổi bay"):
        st.balloons()
        st.success("Nỗi buồn đã bay đi rồi!")
