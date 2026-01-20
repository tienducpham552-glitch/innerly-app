import streamlit as st
import time
import random
import pandas as pd
from datetime import datetime, timedelta
import google.generativeai as genai

# --- 1. CẤU HÌNH TRANG ---
st.set_page_config(page_title="Innerly Studio Debug", page_icon="🐞", layout="wide")

# --- 2. CẤU HÌNH API ---
# Lấy Key từ Secrets
api_key = st.secrets.get("GEMINI_API_KEY", "")

if api_key:
    genai.configure(api_key=api_key)

# --- HÀM XỬ LÝ AI (CHẾ ĐỘ DÒ LỖI) ---
def get_ai_response(prompt_text):
    if not api_key:
        return "⚠️ Chưa có API Key! Hãy vào Settings -> Secrets để dán Key vào."
    
    # Thử Model mới nhất (Flash)
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt_text)
        return response.text
    except Exception as e_flash:
        # Nếu Flash lỗi, thử Model cũ (Pro)
        try:
            model = genai.GenerativeModel('gemini-pro')
            response = model.generate_content(prompt_text)
            return response.text
        except Exception as e_pro:
            # NẾU CẢ 2 ĐỀU LỖI -> IN RA MÀN HÌNH ĐỂ SỬA
            return f"🚨 BẮT ĐƯỢC LỖI RỒI (Chụp ảnh gửi mình đoạn này nhé):\n\n❌ Lỗi 1 (Flash): {str(e_flash)}\n\n❌ Lỗi 2 (Pro): {str(e_pro)}"

# --- 3. CSS GIAO DIỆN ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Quicksand:wght@400;500;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Quicksand', sans-serif; }
    [data-testid="stSidebar"] { background-color: rgba(255, 255, 255, 0.95); border-right: 1px solid #eee; }
    .card-inner {
        background: rgba(255, 255, 255, 0.9);
        border-radius: 20px; padding: 20px; text-align: center;
        box-shadow: 0 8px 32px rgba(0,0,0,0.1); border: 2px solid white;
        min-height: 400px; display: flex; flex-direction: column; justify-content: center;
    }
    .card-title { font-size: 20px; font-weight: 700; color: #333; margin-bottom: 10px; }
    .stButton>button { border-radius: 50px; border: none; box-shadow: 0 4px 10px rgba(0,0,0,0.1); }
</style>
""", unsafe_allow_html=True)

# --- 4. DỮ LIỆU ---
DATA_NU = {
    "Cảm xúc": [
        {"id": 101, "icon": "🌧️", "title": "Buồn không tên", "front": "Tự nhiên thấy buồn.", "back": "• Nghe nhạc không lời\n• Cho phép buồn 15 phút", "quote": "Cảm xúc như cơn mưa."},
        {"id": 102, "icon": "😶‍🌫️", "title": "Overthinking", "front": "Suy nghĩ dồn dập.", "back": "• Viết hết ra giấy\n• Tập trung vào hơi thở", "quote": "Đừng để suy nghĩ làm đau bạn."},
    ]
}
DATA_NAM = {
    "Tâm trí": [
        {"id": 301, "icon": "🌪️", "title": "Rối bời", "front": "Quá nhiều việc.", "back": "• Làm việc nhỏ nhất trước\n• Tắt điện thoại 30p", "quote": "Gỡ từng nút thắt."},
        {"id": 302, "icon": "👺", "title": "Tự ti", "front": "Thấy mình kém cỏi.", "back": "• Nhìn lại thành quả cũ\n• Bạn giỏi hơn bạn nghĩ", "quote": "Tin vào chính mình."},
    ]
}

# --- 5. LOGIC CHÍNH ---
if "flipped" not in st.session_state: st.session_state.flipped = {}
if "chat_history" not in st.session_state: st.session_state.chat_history = []
if "mood_log" not in st.session_state: st.session_state.mood_log = [] 
if "xp" not in st.session_state: st.session_state.xp = 0 

with st.sidebar:
    st.title("Innerly Studio")
    st.markdown(f"**XP hiện tại: {st.session_state.xp}**")
    st.progress(min(st.session_state.xp % 50 / 50, 1.0))
    st.divider()
    user_name = st.text_input("Tên bạn:", "Bạn")
    user_gender = st.radio("Chế độ:", ["Nữ 🌸", "Nam 🧢"], horizontal=True)
    st.divider()
    menu = st.radio("Menu:", ["Rút Thẻ", "Chat AI (Test Lỗi)", "Hộp Thả Trôi"])

# --- NỘI DUNG CHÍNH ---
data = DATA_NU if "Nữ" in user_gender else DATA_NAM

if menu == "Rút Thẻ":
    st.header(f"Thông điệp cho {user_name} 🌿")
    tabs = st.tabs(list(data.keys()))
    for i, (cat, cards) in enumerate(data.items()):
        with tabs[i]:
            cols = st.columns(2)
            for idx, card in enumerate(cards):
                ckey = f"{user_gender}_{card['id']}"
                with cols[idx % 2]:
                    if not st.session_state.flipped.get(ckey, False):
                        st.info(f"**{card['title']}**")
                        st.write(f"_{card['front']}_")
                        if st.button("Lật thẻ 🌀", key=f"f_{ckey}"):
                            st.session_state.flipped[ckey] = True
                            st.rerun()
                    else:
                        st.success(f"**Lời khuyên:**")
                        st.write(card['back'])
                        if st.button("Úp lại ↩️", key=f"b_{ckey}"):
                            st.session_state.flipped[ckey] = False
                            st.rerun()

elif menu == "Chat AI (Test Lỗi)":
    st.header("Kiểm tra kết nối AI 🐞")
    st.caption("Hãy chat một câu bất kỳ để xem lỗi chi tiết:")
    
    for msg in st.session_state.chat_history:
        st.chat_message(msg["role"]).write(msg["content"])
        
    if prompt := st.chat_input("Alo..."):
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        st.chat_message("user").write(prompt)
        with st.chat_message("assistant"):
            with st.spinner("Đang kiểm tra lỗi..."):
                res = get_ai_response(prompt)
                st.code(res, language="text") # Hiển thị lỗi dạng code cho dễ đọc
                st.session_state.chat_history.append({"role": "assistant", "content": res})

elif menu == "Hộp Thả Trôi":
    st.header("Hộp Thả Trôi 🗑️")
    txt = st.text_area("Viết nỗi buồn vào đây:", height=200)
    if st.button("🌬️ Thả trôi"):
        if txt:
            st.balloons()
            st.success("Đã thả trôi!")
            st.session_state.xp += 10
