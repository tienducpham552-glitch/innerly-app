import streamlit as st
import time
import random
import pandas as pd
from datetime import datetime, timedelta
import google.generativeai as genai

# --- 1. CẤU HÌNH TRANG (PHẢI ĐỂ DÒNG ĐẦU TIÊN) ---
st.set_page_config(page_title="Innerly Studio Final", page_icon="🧸", layout="wide")

# --- 2. CẤU HÌNH API GOOGLE GEMINI ---
# BƯỚC QUAN TRỌNG: Dán API Key của bạn vào giữa 2 dấu ngoặc kép bên dưới để chạy trên máy tính.
# Lấy Key tại: https://aistudio.google.com/app/apikey
MY_LOCAL_KEY = "AIzaSyCnKVAyjJYT73lZVQqF6RMlGkxila7_SP0"  

# Logic tự động nhận diện Key (Ưu tiên Secrets trên Cloud, nếu không có thì dùng Key Local)
api_key = st.secrets.get("GEMINI_API_KEY", MY_LOCAL_KEY)

if api_key:
    genai.configure(api_key=api_key)

def get_ai_response(prompt_text):
    if not api_key:
        return "⚠️ Chưa có API Key! Hãy mở file code, tìm dòng 'MY_LOCAL_KEY' và dán key của bạn vào nhé."
    try:
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content(prompt_text)
        return response.text
    except Exception as e:
        return f"Innerly đang mất kết nối. Lỗi: {str(e)}"

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
    .card-icon { font-size: 60px; margin-bottom: 15px; }
    .card-title { font-size: 20px; font-weight: 700; color: #333; margin-bottom: 10px; }
    .card-text { font-size: 15px; color: #555; font-style: italic; }
    
    .stButton>button { border-radius: 50px; border: none; box-shadow: 0 4px 10px rgba(0,0,0,0.1); }
    
    .level-badge {
        padding: 10px; border-radius: 15px;
        background: linear-gradient(45deg, #85FFBD 0%, #FFFB7D 100%);
        color: #2c3e50; font-weight: bold; text-align: center;
        margin-bottom: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
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

# --- 5. KHỞI TẠO STATE ---
if "flipped" not in st.session_state: st.session_state.flipped = {}
if "chat_history" not in st.session_state: st.session_state.chat_history = []
if "mood_log" not in st.session_state: st.session_state.mood_log = [] 
if "xp" not in st.session_state: st.session_state.xp = 0 

def get_tree_status(xp):
    if xp < 20: return "Mầm non 🌱", "Cây đang lớn..."
    elif xp < 50: return "Cây con 🌿", "Thân cây cứng cáp!"
    else: return "Cây to 🌳", "Tán lá rộng che chở."

# --- 6. SIDEBAR ---
with st.sidebar:
    st.title("Innerly Studio")
    
    # Gamification
    icon, msg = get_tree_status(st.session_state.xp)
    st.markdown(f'<div class="level-badge"><h2>{icon}</h2>{st.session_state.xp} XP - {msg}</div>', unsafe_allow_html=True)
    st.progress(min(st.session_state.xp % 50 / 50, 1.0))
    
    st.divider()
    user_name = st.text_input("Tên bạn:", "Bạn")
    user_gender = st.radio("Chế độ:", ["Nữ 🌸", "Nam 🧢"], horizontal=True)
    
    st.divider()
    st.subheader("Cảm xúc hôm nay?")
    moods = {"Vui 🤩": 10, "Bình yên 🌿": 8, "Ổn 😐": 5, "Buồn ☁️": 3, "Mệt 🔋": 1}
    curr_mood = st.select_slider("", options=list(moods.keys()), value="Bình yên 🌿")
    
    if st.button("Lưu (+5 XP)"):
        st.session_state.mood_log.append({"Time": datetime.now().strftime("%H:%M"), "Score": moods[curr_mood]})
        st.session_state.xp += 5
        st.toast("Đã lưu!")

    st.divider()
    menu = st.radio("Menu:", ["Rút Thẻ", "Chat AI", "Hộp Thả Trôi", "Biểu Đồ"])
    
    # Nhạc
    sound = st.selectbox("Âm thanh:", ["Tắt", "Mưa 🌧️", "Piano 🎹", "Lofi ☕"])
    links = {
        "Mưa 🌧️": "https://www.youtube.com/embed/mPZkdNFkNps?autoplay=1&loop=1",
        "Piano 🎹": "https://www.youtube.com/embed/4oStW8P_Syo?autoplay=1&loop=1",
        "Lofi ☕": "https://www.youtube.com/embed/jfKfPfyJRdk?autoplay=1&loop=1"
    }
    if sound != "Tắt":
        st.markdown(f'<iframe width="0" height="0" src="{links[sound]}" allow="autoplay"></iframe>', unsafe_allow_html=True)

# --- THEME MÀU SẮC ---
bg_color = "linear-gradient(120deg, #d4fc79 0%, #96e6a1 100%)" if moods[curr_mood] > 5 else "linear-gradient(120deg, #a1c4fd 0%, #c2e9fb 100%)"
st.markdown(f"<style>.stApp {{ background-image: {bg_color}; background-attachment: fixed; }}</style>", unsafe_allow_html=True)

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
                        st.caption(f"📌 {card['quote']}")
                        if st.button("Úp lại ↩️", key=f"b_{ckey}"):
                            st.session_state.flipped[ckey] = False
                            st.rerun()

elif menu == "Chat AI":
    st.header("Tâm sự cùng Innerly 🧸")
    for msg in st.session_state.chat_history:
        st.chat_message(msg["role"]).write(msg["content"])
        
    if prompt := st.chat_input("Kể cho mình nghe đi..."):
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        st.chat_message("user").write(prompt)
        
        with st.chat_message("assistant"):
            with st.spinner("Đang lắng nghe..."):
                full_prompt = f"Bạn là Innerly, AI chữa lành. User: {user_name}. Tâm trạng: {curr_mood}. User nói: {prompt}"
                res = get_ai_response(full_prompt)
                st.write(res)
                st.session_state.chat_history.append({"role": "assistant", "content": res})

elif menu == "Hộp Thả Trôi":
    st.header("Hộp Thả Trôi Nỗi Buồn 🗑️")
    txt = st.text_area("Viết nỗi buồn vào đây:", height=200)
    if st.button("🌬️ Thả trôi (+10 XP)"):
        if txt:
            ph = st.empty()
            for i in range(len(txt), -1, -5):
                ph.code(txt[:i] + " ...👋")
                time.sleep(0.05)
            ph.empty()
            st.balloons()
            st.success("Đã thả trôi nỗi buồn!")
            st.session_state.xp += 10
            time.sleep(1)
            st.rerun()

elif menu == "Biểu Đồ":
    st.header("Biểu đồ cảm xúc 📈")
    if st.session_state.mood_log:
        df = pd.DataFrame(st.session_state.mood_log)
        st.line_chart(df, x="Time", y="Score")
        if st.button("AI Phân tích"):
             st.info(get_ai_response(f"Phân tích xu hướng cảm xúc này: {st.session_state.mood_log}"))
    else:
        st.warning("Chưa có dữ liệu. Hãy Check-in cảm xúc ở thanh bên trái nhé!")