import streamlit as st
import google.generativeai as genai
import time
import random

# --- 1. CẤU HÌNH ---
st.set_page_config(page_title="Innerly Studio", page_icon="🧸", layout="wide")

# Lấy API Key
api_key = st.secrets.get("GEMINI_API_KEY", "")
if api_key:
    genai.configure(api_key=api_key)

# --- 2. HÀM TỰ ĐỘNG QUÉT MODEL (QUAN TRỌNG) ---
@st.cache_data # Lưu lại để không phải quét nhiều lần
def get_available_models():
    if not api_key: return []
    try:
        # Hỏi Google xem có những model nào
        models = genai.list_models()
        # Chỉ lấy những model biết chat (generateContent)
        valid_models = [m.name for m in models if 'generateContent' in m.supported_generation_methods]
        return valid_models
    except Exception as e:
        return []

# --- 3. XỬ LÝ AI ---
def get_ai_response(model_name, prompt):
    if not api_key:
        return "⚠️ Chưa có API Key! Vào Settings -> Secrets để điền nhé."
    try:
        # Dùng đúng cái model mà người dùng chọn
        model = genai.GenerativeModel(model_name)
        return model.generate_content(prompt).text
    except Exception as e:
        return f"Lỗi: {str(e)}"

# --- 4. GIAO DIỆN ---
st.markdown("""<style>
    @import url('https://fonts.googleapis.com/css2?family=Quicksand:wght@500;700&display=swap');
    * { font-family: 'Quicksand', sans-serif; }
    .stApp { background: linear-gradient(120deg, #a1c4fd 0%, #c2e9fb 100%); }
</style>""", unsafe_allow_html=True)

with st.sidebar:
    st.title("Innerly Studio 🧸")
    
    # --- KHU VỰC CHỌN MODEL ---
    st.divider()
    st.markdown("### ⚙️ Cấu hình AI")
    if not api_key:
        st.error("Chưa nhập API Key!")
        my_model = None
    else:
        # Tự động lấy danh sách
        available_models = get_available_models()
        
        if not available_models:
            st.error("🚫 Key đúng nhưng không tìm thấy Model nào! Có thể Project trên Google chưa bật API.")
            my_model = "gemini-pro" # Fallback
        else:
            # Ưu tiên chọn Flash nếu có, không thì chọn cái đầu tiên
            default_idx = 0
            for i, m in enumerate(available_models):
                if "flash" in m:
                    default_idx = i
                    break
            
            my_model = st.selectbox("Chọn Model hoạt động:", available_models, index=default_idx)
            st.success(f"Đang dùng: {my_model}")
    
    st.divider()
    menu = st.radio("Menu", ["Chat AI", "Rút Thẻ", "Thả Trôi"])

# --- CÁC MÀN HÌNH CHÍNH ---
if menu == "Chat AI":
    st.header("Tâm sự cùng Innerly")
    if "history" not in st.session_state: st.session_state.history = []
    
    for msg in st.session_state.history:
        st.chat_message(msg["role"]).write(msg["content"])
        
    if prompt := st.chat_input("Bạn đang nghĩ gì..."):
        st.session_state.history.append({"role": "user", "content": prompt})
        st.chat_message("user").write(prompt)
        with st.chat_message("assistant"):
            if my_model:
                with st.spinner(f"Innerly ({my_model}) đang nghĩ..."):
                    res = get_ai_response(my_model, prompt)
                    st.write(res)
                    st.session_state.history.append({"role": "assistant", "content": res})
            else:
                st.error("Không có model nào để trả lời.")

elif menu == "Rút Thẻ":
    st.header("Thông điệp chữa lành 🌿")
    st.info("Tính năng đang bảo trì.")

elif menu == "Thả Trôi":
    st.header("Hộp thả trôi 🗑️")
    if st.text_area("Viết nỗi buồn vào đây:") and st.button("🌬️ Thổi bay"):
        st.balloons()
        st.success("Đã bay đi rồi!")

