import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine, text

# ---------------------------------------------------------
# 1. CẤU HÌNH TRANG & CSS TÙY CHỈNH
# ---------------------------------------------------------
st.set_page_config(
    page_title="BỆNH VIỆN BƯU ĐIỆN - Hệ thống Quản trị Nhân sự & Điều hành",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS chuyên nghiệp cho màn hình đăng nhập & Dashboard
st.markdown("""
<style>
    /* Gradient nền chính cho toàn bộ trang đăng nhập */
    .stApp {
        background: linear-gradient(135deg, #eef2f7 0%, #e3edf7 100%);
    }

    /* Khung Card Login trung tâm */
    .login-container {
        max-width: 450px;
        margin: 30px auto 0 auto;
        background: #ffffff;
        padding: 35px 30px 30px 30px;
        border-radius: 16px;
        box-shadow: 0 10px 30px rgba(0, 82, 204, 0.12);
        border: 1px solid #e1e8f0;
        text-align: center;
    }

    /* Khung hiển thị Logo nổi bật */
    .logo-wrapper {
        background: #ffffff;
        width: 110px;
        height: 110px;
        margin: -85px auto 15px auto;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0 6px 16px rgba(0, 82, 204, 0.18);
        border: 4px solid #ffffff;
    }

    .logo-wrapper img {
        width: 85px;
        height: auto;
    }

    /* Tiêu đề trang đăng nhập */
    .brand-title {
        color: #003b95;
        font-weight: 800;
        font-size: 22px;
        letter-spacing: 0.5px;
        margin-bottom: 4px;
        text-transform: uppercase;
    }

    .brand-subtitle {
        color: #5a6e85;
        font-size: 13px;
        font-weight: 500;
        margin-bottom: 25px;
    }

    /* Tùy chỉnh nhãn & ô nhập liệu */
    .stTextInput > label {
        color: #2c3e50 !important;
        font-weight: 600 !important;
        font-size: 13px !important;
    }

    .stTextInput > div > div > input {
        border-radius: 8px !important;
        border: 1px solid #cbd5e1 !important;
        padding: 10px 14px !important;
        font-size: 14px !important;
    }

    .stTextInput > div > div > input:focus {
        border-color: #0052cc !important;
        box-shadow: 0 0 0 3px rgba(0, 82, 204, 0.15) !important;
    }

    /* Style nút Đăng nhập & Thoát */
    div.stButton > button[key="btn_login"] {
        background: linear-gradient(135deg, #0052cc 0%, #0066ff 100%) !important;
        color: #ffffff !important;
        font-weight: 700 !important;
        font-size: 14px !important;
        border-radius: 8px !important;
        border: none !important;
        padding: 10px 0 !important;
        box-shadow: 0 4px 12px rgba(0, 82, 204, 0.25) !important;
        transition: all 0.2s ease !important;
    }

    div.stButton > button[key="btn_login"]:hover {
        transform: translateY(-1px);
        box-shadow: 0 6px 16px rgba(0, 82, 204, 0.35) !important;
    }

    div.stButton > button[key="btn_exit"] {
        background: #f1f5f9 !important;
        color: #475569 !important;
        font-weight: 600 !important;
        font-size: 14px !important;
        border-radius: 8px !important;
        border: 1px solid #cbd5e1 !important;
        padding: 10px 0 !important;
        transition: all 0.2s ease !important;
    }

    div.stButton > button[key="btn_exit"]:hover {
        background: #e2e8f0 !important;
        color: #1e293b !important;
    }

    /* Custom CSS Dashboard Card */
    .card-box {
        padding: 20px;
        border-radius: 12px;
        color: white;
        margin-bottom: 15px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
        min-height: 130px;
    }
    .card-red { background: linear-gradient(135deg, #e53935, #d32f2f); }
    .card-green { background: linear-gradient(135deg, #00b074, #008a5b); }
    .card-blue { background: linear-gradient(135deg, #29b6f6, #0288d1); }
    .card-dark { background: linear-gradient(135deg, #37474f, #263238); }
    .card-orange { background: linear-gradient(135deg, #ff9200, #e67e00); }
    .card-teal { background: linear-gradient(135deg, #00a896, #028090); }

    .card-title { font-size: 15px; font-weight: bold; margin-bottom: 6px; text-transform: uppercase; }
    .card-desc { font-size: 12px; opacity: 0.9; margin-bottom: 10px; }
    .card-link { font-size: 11px; font-weight: bold; text-align: right; text-transform: uppercase; }

    .badge-circle {
        background-color: #ffffff;
        border: 2px solid;
        border-radius: 50%;
        width: 30px;
        height: 30px;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        font-weight: bold;
        float: right;
    }
    .badge-red { border-color: #ff4d4f; color: #ff4d4f; }
    .badge-orange { border-color: #ff9200; color: #ff9200; }
    .badge-blue { border-color: #29b6f6; color: #29b6f6; }
    .badge-green { border-color: #00b074; color: #00b074; }

    .alert-item {
        background-color: #ffffff;
        padding: 12px 15px;
        border-radius: 8px;
        margin-bottom: 10px;
        border-left: 4px solid #00b074;
        box-shadow: 0 2px 6px rgba(0,0,0,0.04);
    }
</style>
""", unsafe_allow_html=True)

# Khởi tạo session lưu trạng thái đăng nhập
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

# ---------------------------------------------------------
# 2. KẾT NỐI DATABASE NEON POSTGRESQL
# ---------------------------------------------------------
@st.cache_resource
def get_db_engine():
    try:
        if "DATABASE_URL" in st.secrets:
            raw_url = st.secrets["DATABASE_URL"].strip()
            if raw_url.startswith("postgres://"):
                raw_url = raw_url.replace("postgres://", "postgresql://", 1)
            return create_engine(raw_url, pool_pre_ping=True)
        elif "postgres" in st.secrets:
            pg = st.secrets["postgres"]
            db_url = f"postgresql://{pg['user']}:{pg['password']}@{pg['host']}:{pg['port']}/{pg['database']}?sslmode=require"
            return create_engine(db_url, pool_pre_ping=True)
        return None
    except Exception as e:
        st.error(f"Lỗi kết nối CSDL: {e}")
        return None

engine = get_db_engine()

# ---------------------------------------------------------
# 3. MÀN HÌNH ĐĂNG NHẬP SANG TRỌNG & NỔI BẬT LOGO
# ---------------------------------------------------------
def render_login():
    st.markdown("<br><br>", unsafe_allow_html=True)
    col_l, col_main, col_r = st.columns([1, 1.2, 1])

    with col_main:
        # Khung Logo Nổi bật đặt đè lên Card
        st.markdown("""
        <div class="logo-wrapper">
            <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/c/c3/VNPT_Logo.svg/1200px-VNPT_Logo.svg.png" alt="VNPT Logo">
        </div>
        """, unsafe_allow_html=True)

        # Khung Form Đăng nhập
        with st.container():
            st.markdown("<div class='login-container'>", unsafe_allow_html=True)
            st.markdown("<div class='brand-title'>BỆNH VIỆN BƯU ĐIỆN</div>", unsafe_allow_html=True)
            st.markdown("<div class='brand-subtitle'>Hệ thống Quản trị Nhân sự & Điều hành</div>", unsafe_allow_html=True)

            username = st.text_input("Tên đăng nhập / Username", placeholder="Tên tài khoản...")
            password = st.text_input("Mật khẩu / Password", type="password", placeholder="••••••••")

            st.markdown("<br>", unsafe_allow_html=True)
            btn_col1, btn_col2 = st.columns([1.5, 1])

            with btn_col1:
                if st.button("🔑 ĐĂNG NHẬP", key="btn_login", use_container_width=True):
                    if username == "admin" and password == "admin123":
                        st.session_state['logged_in'] = True
                        st.success("Đăng nhập thành công!")
                        st.rerun()
                    else:
                        st.error("❌ Tên đăng nhập hoặc mật khẩu sai!")

            with btn_col2:
                if st.button("✕ Thoát", key="btn_exit", use_container_width=True):
                    st.info("Phiên làm việc tạm dừng.")

            st.markdown("</div>", unsafe_allow_html=True)

# ---------------------------------------------------------
# 4. GIAO DIỆN CHÍNH (SAU KHI ĐĂNG NHẬP)
# ---------------------------------------------------------
def render_dashboard():
    st.sidebar.title("DANH MỤC CHỨC NĂNG")
    st.sidebar.caption("👤 **Xin chào:** Đoàn Danh Hiển")

    if st.sidebar.button("🔒 Đăng xuất", use_container_width=True):
        st.session_state['logged_in'] = False
        st.rerun()

    st.sidebar.markdown("---")
    st.sidebar.caption("Điều hướng chức năng")

    menu = st.sidebar.radio(
        "",
        [
            "📌 Trang chủ / Dashboard",
            "📑 Thông báo & Văn bản",
            "👤 Hồ sơ Cán bộ CNV",
            "🎓 Phân loại Trình độ",
            "📝 Hợp đồng Lao động",
            "🏛️ Hồ sơ Đảng viên",
            "📜 Giấy phép hành nghề (GPHN)",
            "📚 Theo dõi Đào tạo CME",
            "📈 Nâng bậc lương & Ngạch",
            "🔄 Bố trí & Điều chuyển",
            "🏥 Quản lý BHXH",
            "🩺 Quản lý BHOI & Sức khỏe",
            "⏱️ Báo cáo - Thống kê",
            "📊 Thống kê Tiến độ Đào tạo MS",
            "⚙️ Cấu hình Hệ thống"
        ]
    )

    # Header người dùng
    col_user_img, col_user_info = st.columns([1, 11])
    with col_user_img:
        st.image("https://cdn-icons-png.flaticon.com/512/3135/3135715.png", width=70)
    with col_user_info:
        st.title("Xin chào, Đoàn Danh Hiển")
        st.caption("Quản trị viên Hệ thống — Bệnh viện Bưu điện")

    if menu == "📌 Trang chủ / Dashboard":
        st.markdown("<br>", unsafe_allow_html=True)

        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown("<div class='card-box card-red'><div class='card-title'>👨‍⚕️ HỒ SƠ CÁN BỘ CNV</div><div class='card-desc'>Theo dõi, cập nhật và quản lý toàn bộ danh sách hồ sơ 877 nhân sự toàn bệnh viện.</div><div class='card-link'>XEM CHI TIẾT ➔</div></div>", unsafe_allow_html=True)
            st.markdown("<div class='card-box card-dark'><div class='card-title'>📜 HỢP ĐỒNG LAO ĐỘNG</div><div class='card-desc'>Theo dõi hợp đồng xác định thời hạn, không xác định thời hạn và lịch sử ký.</div><div class='card-link'>QUẢN LÝ HỒ SƠ ➔</div></div>", unsafe_allow_html=True)

        with col2:
            st.markdown("<div class='card-box card-green'><div class='card-title'>📊 BÁO CÁO & THỐNG KÊ</div><div class='card-desc'>Truy xuất dữ liệu báo cáo BYT, BVT và biến động nhân sự theo thời gian thực.</div><div class='card-link'>XEM BÁO CÁO ➔</div></div>", unsafe_allow_html=True)
            st.markdown("<div class='card-box card-orange'><div class='card-title'>📈 NÂNG BẬC LƯƠNG & NGẠCH</div><div class='card-desc'>Quản lý nâng lương, ngạch viên chức và cảnh báo danh sách đủ điều kiện nâng lương.</div><div class='card-link'>XEM DANH SÁCH ➔</div></div>", unsafe_allow_html=True)

        with col3:
            st.markdown("<div class='card-box card-blue'><div class='card-title'>🏥 GPHN & ĐÀO TẠO CME</div><div class='card-desc'>Quản lý Chứng chỉ hành nghề và tiến độ tích lũy 48 tiết CME của Bác sĩ / Điều dưỡng.</div><div class='card-link'>XEM CHI TIẾT ➔</div></div>", unsafe_allow_html=True)
            st.markdown("<div class='card-box card-teal'><div class='card-title'>🩺 QUẢN LÝ BHOI & SỨC KHỎE</div><div class='card-desc'>Theo dõi chế độ bảo hiểm sở hữu, đóng xem và đợt khám sức khỏe định kỳ.</div><div class='card-link'>CHI TIẾT ➔</div></div>", unsafe_allow_html=True)

        st.markdown("---")

        c_left, c_mid, c_right = st.columns([1.2, 1.4, 1.4])
        with c_left:
            st.subheader("📌 Cảnh báo tự động")
            st.markdown("""
            <div class="alert-item"><span class="badge-circle badge-red">12</span><b>⏳ Sắp hết hạn HĐLĐ</b><br><small style="color: gray;">Cần tái ký / gia hạn trong 30 ngày</small></div>
            <div class="alert-item"><span class="badge-circle badge-orange">08</span><b>💰 Đến hạn nâng bậc lương</b><br><small style="color: gray;">Đủ thời hạn nâng lương ngạch, bậc</small></div>
            <div class="alert-item"><span class="badge-circle badge-blue">25</span><b>⚠️ Cảnh báo thiếu giờ CME</b><br><small style="color: gray;">Chưa tích lũy đủ 48 tiết / 2 năm</small></div>
            <div class="alert-item"><span class="badge-circle badge-green">04</span><b>📜 GPHN cần cập nhật</b><br><small style="color: gray;">Bổ sung thông tin chứng chỉ mới</small></div>
            """, unsafe_allow_html=True)

        with c_mid:
            st.subheader("📊 Nhân sự theo Trình độ")
            data_trinh_do = pd.DataFrame({"Trình độ": ["Tiến sĩ / CKI", "Thạc sĩ / CKI", "Đại học", "Cao đẳng", "Trung cấp / Khác"], "Số lượng": [25, 142, 450, 180, 80]})
            fig_bar = px.bar(data_trinh_do, x="Trình độ", y="Số lượng", text="Số lượng", color="Trình độ", color_discrete_sequence=['#ff9200', '#5c6bc0', '#26a69a', '#9ccc65', '#ec407a'])
            fig_bar.update_layout(showlegend=False, margin=dict(l=10, r=10, t=20, b=20), height=320)
            st.plotly_chart(fig_bar, use_container_width=True)

        with c_right:
            st.subheader("🍩 Phân loại Hợp đồng")
            data_hd = pd.DataFrame({"Loại HĐ": ["Không xác định thời hạn", "Xác định thời hạn (1-3 năm)", "Thử việc / Ngắn hạn"], "Số lượng": [520, 310, 47]})
            fig_donut = px.pie(data_hd, names="Loại HĐ", values="Số lượng", hole=0.5, color_discrete_sequence=['#0288d1', '#ff9200', '#00b074'])
            fig_donut.update_layout(legend=dict(orientation="h", yanchor="bottom", y=-0.3, xanchor="center", x=0.5), margin=dict(l=10, r=10, t=20, b=20), height=320)
            st.plotly_chart(fig_donut, use_container_width=True)

    elif menu == "👤 Hồ sơ Cán bộ CNV":
        st.markdown("---")
        st.subheader("📁 QUẢN LÝ CÁN BỘ CNV BỆNH VIỆN BƯU ĐIỆN")
        tab_list, tab_add = st.tabs(["📋 Danh sách Nhân sự (Neon DB)", "➕ Thêm Nhân sự Mới"])

        with tab_list:
            if engine:
                try:
                    df = pd.read_sql("SELECT * FROM can_bo ORDER BY ma_cb ASC", engine)
                    if df.empty:
                        st.info("Chưa có dữ liệu nhân sự trong CSDL Neon.")
                    else:
                        st.dataframe(df, use_container_width=True)
                except Exception as e:
                    st.error(f"Lỗi truy vấn CSDL: {e}")

        with tab_add:
            with st.form("add_form"):
                col1, col2 = st.columns(2)
                ma_cb = col1.text_input("Mã Cán bộ*")
                ho_ten = col2.text_input("Họ và Tên*")
                chuc_danh = col1.selectbox("Chức danh", ["Bác sĩ", "Dược sĩ", "Điều dưỡng", "Hành chính"])
                khoa_phong = col2.text_input("Khoa / Phòng")

                if st.form_submit_button("Lưu Hồ Sơ"):
                    if engine and ma_cb and ho_ten:
                        try:
                            with engine.connect() as conn:
                                conn.execute(text("INSERT INTO can_bo (ma_cb, ho_ten, chuc_danh, khoa_phong) VALUES (:m, :h, :c, :k)"),
                                             {"m": ma_cb, "h": ho_ten, "c": chuc_danh, "k": khoa_phong})
                                conn.commit()
                            st.success("Đã thêm cán bộ thành công!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Lỗi: {e}")
    else:
        st.markdown("---")
        st.info(f"⚙️ Chức năng **{menu}** đang được đồng bộ dữ liệu.")

# ---------------------------------------------------------
# 5. ĐIỀU HƯỚNG MÀN HÌNH
# ---------------------------------------------------------
if not st.session_state['logged_in']:
    render_login()
else:
    render_dashboard()
