import streamlit as st
import sys
import subprocess

# --- 1. TỰ ĐỘNG CÀI ĐẶT (CỐ GẮNG ÉP MÁY CHỦ CẬP NHẬT) ---
try:
    import google.generativeai as genai
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "google-generativeai"])
    import google.generativeai as genai

# --- 2. CẤU HÌNH TRANG ---
st.set_page_config(page_title="Innerly Studio", page_icon="🧸", layout="wide")

# Lấy phiên bản thư viện hiện tại để hiển thị
try:
    lib_version = genai.__version__
except:
    lib_version = "Quá cũ (Không xác định)"

# Lấy API Key
api_key = st.secrets.get("GEMINI_API_KEY", "")
if api_key:
    genai.configure(api_key=api_key)

def get_ai_response(prompt):
    if not api_key:
        return "⚠️ Chưa nhập Key! Vào Settings -> Secrets để điền nhé."
    
    # CHIẾN THUẬT THÔNG MINH: Thử cái mới, nếu lỗi thì dùng cái cũ
    try:
        # Ưu tiên dùng Flash (Mới, Nhanh)
        model = genai.GenerativeModel('gemini-1.5-flash')
        return model.generate_content(prompt).text
    except Exception as e_flash:
        try:
            # Nếu Flash lỗi, tự động chuyển sang Pro (Cũ nhưng ổn định)
            model = genai.GenerativeModel('gemini-pro')
            return f"Run with Pro: {model.generate_content(prompt).text}"
        except Exception as e_pro:
            return f"❌ Lỗi toàn tập:\nFlash: {str(e_flash)}\nPro: {str(e_pro)}"

# --- 3. GIAO DIỆN ---
st.markdown("""<style>
    @import url('https://fonts.googleapis.com/css2?family=Quicksand:wght@500;700&display=swap');
    * { font-family: 'Quicksand', sans-serif; }
    .stApp { background: linear-gradient(120deg, #a1c4fd 0%, #c2e9fb 100%); }
    .debug-box { background: #333; color: #0f0; padding: 10px; border-radius: 5px; font-family: monospace; font-size: 12px; margin-bottom: 20px;}
</style>""", unsafe_allow_html=True)

with st.sidebar:
    st.title("Innerly Studio 🧸")
    st.markdown(f"**Trạng thái hệ thống:**")
    st.code(f"Phiên bản GenAI: {lib_version}") # Hiện phiên bản để kiểm tra
    menu = st.radio("Menu", ["Chat AI", "Rút Thẻ"])

if menu == "Chat AI":
    st.header("Tâm sự cùng Innerly")
    
    # Hiển thị cảnh báo nếu phiên bản quá cũ
    if str(lib_version).startswith("0.3") or str(lib_version).startswith("0.4"):
        st.warning(f"⚠️ Máy chủ đang dùng phiên bản cũ ({lib_version}). Innerly sẽ tự động chuyển sang chế độ tương thích (Gemini Pro).")

    if "history" not in st.session_state: st.session_state.history = []
    
    for msg in st.session_state.history:
        st.chat_message(msg["role"]).write(msg["content"])
        
    if prompt := st.chat_input("Bạn đang nghĩ gì..."):
        st.session_state.history.append({"role": "user", "content": prompt})
        st.chat_message("user").write(prompt)
        with st.chat_message("assistant"):
            with st.spinner("Innerly đang suy nghĩ..."):
                res = get_ai_response(prompt)
                st.write(res)
                st.session_state.history.append({"role": "assistant", "content": res})

elif menu == "Rút Thẻ":
    st.header("Thông điệp chữa lành 🌿")
    st.info("Tính năng đang bảo trì để nâng cấp.")
