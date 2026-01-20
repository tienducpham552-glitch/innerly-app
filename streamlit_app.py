import streamlit as st
import sys
import subprocess

st.set_page_config(page_title="Trạm Sửa Chữa Innerly", page_icon="🛠️")

st.title("🛠️ TRẠM CHẨN ĐOÁN & SỬA LỖI")

# --- 1. KIỂM TRA PHIÊN BẢN HIỆN TẠI ---
try:
    import google.generativeai as genai
    version = genai.__version__
except:
    version = "Không xác định (Chưa cài)"

st.metric(label="Phiên bản Google GenAI trên máy chủ:", value=version)

if str(version).startswith("0.8"):
    st.success("✅ Phiên bản ĐÚNG (0.8.x)! Bạn có thể dán lại code app chính để dùng.")
else:
    st.error("❌ Phiên bản QUÁ CŨ! Cần cập nhật ngay.")

# --- 2. NÚT BẤM CƯỠNG CHẾ CÀI ĐẶT ---
st.write("---")
st.write("### 🚑 Giải pháp khẩn cấp")
if st.button("🚀 BẤM VÀO ĐÂY ĐỂ ÉP CẬP NHẬT (Force Install)", type="primary"):
    with st.status("Đang tiến hành cài đặt...", expanded=True) as status:
        st.write("1. Đang tải thư viện google-generativeai mới nhất...")
        try:
            # Chạy lệnh pip install trực tiếp
            result = subprocess.run(
                [sys.executable, "-m", "pip", "install", "--upgrade", "google-generativeai>=0.8.3"],
                capture_output=True, text=True
            )
            st.code(result.stdout) # Hiện nhật ký cài đặt
            
            if result.returncode == 0:
                st.success("✅ CÀI ĐẶT THÀNH CÔNG!")
                st.balloons()
                st.warning("⚠️ QUAN TRỌNG: Hãy tải lại trang (F5) ngay bây giờ để áp dụng!")
            else:
                st.error("❌ Cài đặt thất bại.")
                st.code(result.stderr)
        except Exception as e:
            st.error(f"Lỗi hệ thống: {e}")
        status.update(label="Hoàn tất quy trình!", state="complete")

# --- 3. TEST KẾT NỐI ---
st.write("---")
st.write("### 🔍 Kiểm tra kết nối Model")
api_key = st.secrets.get("GEMINI_API_KEY", "")
if not api_key:
    st.info("Chưa nhập API Key trong Secrets.")
else:
    if st.button("Kiểm tra danh sách Model"):
        try:
            genai.configure(api_key=api_key)
            models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
            st.success(f"Kết nối tốt! Tìm thấy {len(models)} model:")
            st.json(models)
        except Exception as e:
            st.error(f"Vẫn lỗi kết nối: {e}")
