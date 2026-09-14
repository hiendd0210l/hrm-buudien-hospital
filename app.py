import os
import base64
import streamlit as st
from sqlalchemy import create_engine, text

# Import các module từ thư mục modules/
from modules.dashboard import render_dashboard_home
from modules.ho_so_can_bo import render_quan_ly_can_bo
from modules.cham_cong import render_cham_cong

# ---------------------------------------------------------
# 1. CẤU HÌNH TRANG & CSS GIAO DIỆN CHUNG
# ---------------------------------------------------------
st.set_page_config(
    page_title="BỆNH VIỆN BƯU ĐIỆN - Hệ thống Quản trị Nhân sự",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'user_info' not in st.session_state:
    st.session_state['user_info'] = {"fullname": "Đoàn Danh Hiển", "role": "Quản trị viên Hệ thống"}

# ---------------------------------------------------------
# 2. DATABASE ENGINE
# ---------------------------------------------------------
@st.cache_resource
def get_db_engine():
    try:
        if "DATABASE_URL" in st.secrets:
            raw_url = st.secrets["DATABASE_URL"].strip().replace("postgres://", "postgresql://", 1)
            return create_engine(raw_url, pool_pre_ping=True, pool_recycle=300)
        return None
    except Exception as e:
        st.error(f"Lỗi khởi tạo Engine DB: {e}")
        return None

engine = get_db_engine()

# ---------------------------------------------------------
# 3. TRANG ĐĂNG NHẬP
# ---------------------------------------------------------
def render_login():
    st.markdown("## 🏥 BỆNH VIỆN BƯU ĐIỆN")
    with st.form("login_form"):
        username = st.text_input("Tên đăng nhập:")
        password = st.text_input("Mật khẩu:", type="password")
        if st.form_submit_button("🔑 Đăng nhập"):
            if username == "admin" and password == "admin123":
                st.session_state['logged_in'] = True
                st.rerun()
            else:
                st.error("Tài khoản hoặc mật khẩu không đúng!")

# ---------------------------------------------------------
# 4. SIDEBAR & ĐIỀU HƯỚNG (ROUTING MODULES)
# ---------------------------------------------------------
def render_dashboard():
    st.sidebar.title("DANH MỤC CHỨC NĂNG")
    st.sidebar.write(f"👤 **{st.session_state.user_info['fullname']}**")

    if st.sidebar.button("🚪 Đăng xuất", use_container_width=True):
        st.session_state['logged_in'] = False
        st.rerun()

    menu_options = [
        "📌 Trang chủ / Dashboard", 
        "📇 Hồ sơ Cán bộ CNV", 
        "📝 Hợp đồng Lao động", 
        "📜 Giấy phép hành nghề & CME", 
        "⏰ Quản lý Chấm công & Ngày nghỉ", 
        "⚙️ Cấu hình Hệ thống"
    ]

    st.sidebar.markdown("---")
    menu_choice = st.sidebar.radio("Điều hướng:", options=menu_options)

    # ĐIỀU HƯỚNG GỌI CÁC MODULE
    if "Trang chủ" in menu_choice:
        render_dashboard_home(engine)
    elif "Hồ sơ Cán bộ" in menu_choice:
        render_quan_ly_can_bo(engine)
    elif "Chấm công" in menu_choice:
        render_cham_cong(engine)
    elif "Hợp đồng" in menu_choice:
        try:
            from modules.hop_dong import render_hop_dong
            render_hop_dong(engine)
        except ModuleNotFoundError:
            st.title("📝 Hợp đồng Lao động")
            st.info("Chức năng đang được bổ sung file `modules/hop_dong.py`...")
    else:
        st.title(menu_choice)
        st.info("Chức năng đang phát triển...")

# ---------------------------------------------------------
# 5. CHẠY APP
# ---------------------------------------------------------
if not st.session_state['logged_in']:
    render_login()
else:
    render_dashboard()
