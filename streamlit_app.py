import streamlit as st
import google.generativeai as genai
import pandas as pd
import time
import random
from datetime import datetime

# --- 1. CẤU HÌNH TRANG ---
st.set_page_config(page_title="Innerly Studio", page_icon="🧸", layout="wide")

# --- 2. CẤU HÌNH API ---
# Tự động lấy Key từ Secrets
api_key = st.secrets.get("GEMINI_API_KEY", "")

if api_key:
    genai.configure(api_key=api_key)

def get_ai_response(prompt_text):
    if not api_key:
        return "⚠️ Chưa có API Key! Bạn hãy vào Settings -> Secrets để dán Key vào nhé."
    try:
        # Bây giờ đã dùng được bản Flash xịn xò
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt_text)
        return response.text
    except Exception as e:
        return f"Innerly đang mất kết nối một chút. Lỗi: {str(e)}"

# --- 3. CSS GIAO DIỆN ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Quicksand:wght@400;500;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Quicksand', sans-serif; }
    
    [data-testid="stSidebar"] { background-color: rgba(255, 255, 255, 0.95); border-right: 1px solid #eee; }
    
    .card-inner {
        position: relative; width: 100%; min-height: 400px;
        text-align: center; border-radius: 20px;
        background: rgba(255, 255, 255, 0.9);
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
        border: 2px solid white;
        display: flex; flex-direction: column;
        justify-content: center; align-items: center;
        padding: 20px; transition: transform 0.6s;
    }
    .card-title { font-size: 20px; font-weight: 700; color: #333; margin-bottom: 10px; }
    
    .stButton>button { border-radius: 50px; border: none; box-shadow: 0 4px 10px rgba(0,0,0,0.1); }
</style>
""", unsafe_allow_html=True)

# --- 4. DỮ LIỆU THẺ BÀI ---
DATA_NU = {
    "Cảm xúc": [
        {"id": 101, "icon": "🌧️", "title": "Buồn không tên", "front": "Tự nhiên thấy buồn.", "back": "• Nghe nhạc không lời\n• Cho phép buồn 15 phút", "quote": "Cảm xúc như cơn mưa, rồi sẽ tạnh."},
        {"id": 102, "icon": "😶‍🌫️", "title": "Overthinking", "front": "Suy nghĩ dồn dập.", "back": "• Viết hết ra giấy\n• Tập trung vào hơi thở", "quote": "Đừng để suy nghĩ làm bạn đau."},
    ],
    "Áp lực": [
        {"id": 201, "icon": "🔋", "title": "Kiệt sức", "front": "Không muốn làm gì.", "back": "• Ngủ một giấc sâu\n• Ăn món ngon", "quote": "Nghỉ ngơi là sạc pin."},
        {"id": 202, "icon": "👀", "title": "Sợ phán xét", "front": "Sợ người khác nghĩ gì.", "back": "• Sống cho mình\n• Mặc bộ đồ mình thích", "quote": "Đời mình mình lái."},
    ]
}

DATA_NAM = {
    "Tâm trí": [
        {"id": 301, "icon": "🌪️", "title": "Rối bời", "front": "Quá nhiều việc.", "back": "• Làm việc nhỏ nhất trước\n• Tắt điện thoại 30p", "quote": "Gỡ từng nút thắt."},
        {"id": 302, "icon": "👺", "title": "Tự ti", "front": "Thấy mình kém cỏi.", "back": "• Nhìn lại thành quả cũ\n• Bạn giỏi hơn bạn nghĩ", "quote": "Tin vào chính mình."},
    ],
    "Sự nghiệp": [
        {"id": 401, "icon": "💸", "title": "Áp lực tiền", "front": "Lo lắng tương lai.", "back": "• Lập kế hoạch chi tiêu\n• Học thêm kỹ năng", "quote": "Tiền là công cụ."},
        {"id": 402, "icon": "🤬", "title": "Nóng giận", "front": "Muốn đập phá.", "back": "• Rửa mặt nước lạnh\n• Chạy bộ ngay", "quote": "Tĩnh lặng là bản lĩnh."},
    ]
}

# --- 5. LOGIC CHÍNH ---
if "flipped" not in st.session_state: st.session_state.flipped = {}
if "chat_history" not in st.session_state: st.session_state.chat_history = []
if "xp" not in st.session_state: st.session_state.xp = 0 

with st.sidebar:
    st.title("Innerly Studio")
    st.markdown(f"**XP tích lũy: {st.session_state.xp}**")
    st.progress(min(st.session_state.xp % 50 / 50, 1.0))
    st.divider()
    
    user_name = st.text_input("Tên bạn:", "Bạn")
    user_gender = st.radio("Chế độ:", ["Nữ 🌸", "Nam 🧢"], horizontal=True)
    
    st.divider()
    menu = st.radio("Menu:", ["Chat AI", "Rút Thẻ", "Hộp Thả Trôi"])
    
    # Nhạc nền
    sound = st.selectbox("Âm thanh:", ["Tắt", "Mưa 🌧️", "Piano 🎹", "Lofi ☕"])
    links = {
        "Mưa 🌧️": "https://www.youtube.com/embed/mPZkdNFkNps?autoplay=1&loop=1",
        "Piano 🎹": "https://www.youtube.com/embed/4oStW8P_Syo?autoplay=1&loop=1",
        "Lofi ☕": "https://www.youtube.com/embed/jfKfPfyJRdk?autoplay=1&loop=1"
    }
    if sound != "Tắt":
        st.markdown(f'<iframe width="0" height="0" src="{links[sound]}" allow="autoplay"></iframe>', unsafe_allow_html=True)

# Màu nền
bg_color = "linear-gradient(120deg, #a1c4fd 0%, #c2e9fb 100%)"
st.markdown(f"<style>.stApp {{ background-image: {bg_color}; background-attachment: fixed; }}</style>", unsafe_allow_html=True)

data = DATA_NU if "Nữ" in user_gender else DATA_NAM

# --- CÁC MÀN HÌNH ---
if menu == "Chat AI":
    st.header("Tâm sự cùng Innerly 🧸")
    for msg in st.session_state.chat_history:
        st.chat_message(msg["role"]).write(msg["content"])
        
    if prompt := st.chat_input("Kể cho mình nghe đi..."):
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        st.chat_message("user").write(prompt)
        
        with st.chat_message("assistant"):
            with st.spinner("Innerly đang lắng nghe..."):
                res = get_ai_response(f"Bạn tên là Innerly. User tên {user_name}. User nói: {prompt}")
                st.write(res)
                st.session_state.chat_history.append({"role": "assistant", "content": res})

elif menu == "Rút Thẻ":
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
                        st.caption(f"📌 {card['quote']}")
                        if st.button("Úp lại ↩️", key=f"b_{ckey}"):
                            st.session_state.flipped[ckey] = False
                            st.rerun()

elif menu == "Hộp Thả Trôi":
    st.header("Hộp Thả Trôi Nỗi Buồn 🗑️")
    txt = st.text_area("Viết nỗi buồn vào đây:", height=200)
    if st.button("🌬️ Thả trôi (+10 XP)"):
        if txt:
            st.balloons()
            st.success("Đã thả trôi nỗi buồn!")
            st.session_state.xp += 10
            time.sleep(1)
            st.rerun()

