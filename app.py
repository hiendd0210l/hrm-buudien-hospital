import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine, text

# ---------------------------------------------------------
# 1. CẤU HÌNH TRANG & CSS NỔI BẬT & THU GỌN FORM
# ---------------------------------------------------------
st.set_page_config(
    page_title="BỆNH VIỆN BƯU ĐIỆN - Hệ thống Quản trị Nhân sự & Điều hành",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    /* Nền trang xám rất nhạt để tôn form đăng nhập */
    .stApp {
        background-color: #f1f5f9 !important;
    }

    /* Tiêu đề chính BỆNH VIỆN BƯU ĐIỆN */
    .hospital-title {
        color: #005696 !important;
        font-weight: 800 !important;
        font-size: 26px !important;
        text-align: center;
        margin-top: 10px;
        margin-bottom: 2px;
        letter-spacing: 0.5px;
    }

    /* Dòng phụ đề */
    .hospital-subtitle {
        color: #475569 !important;
        font-size: 14px !important;
        font-weight: 600 !important;
        text-align: center;
        margin-bottom: 20px;
    }

    /* Khung Form Đăng Nhập: Thu gọn chiều ngang & Tô màu đậm nét */
    .login-card {
        background-color: #ffffff !important;
        border: 1px solid #cbd5e1 !important;
        border-radius: 12px !important;
        padding: 30px 25px !important;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1), 0 8px 10px -6px rgba(0, 0, 0, 0.1) !important;
        max-width: 480px;
        margin: 0 auto;
    }

    /* Nhãn Ô Nhập (Label) Đậm Nét */
    .stTextInput > label {
        color: #0f172a !important;
        font-size: 14px !important;
        font-weight: 700 !important;
        margin-bottom: 6px !important;
    }

    /* Khung Ô Nhập Liệu Rõ Ràng */
    .stTextInput > div > div > input {
        border-radius: 6px !important;
        border: 1.5px solid #94a3b8 !important;
        background-color: #ffffff !important;
        color: #0f172a !important;
        font-size: 15px !important;
        height: 44px !important;
    }
    .stTextInput > div > div > input:focus {
        border-color: #0077ba !important;
        box-shadow: 0 0 0 3px rgba(0, 119, 186, 0.2) !important;
    }

    /* Nút Đăng nhập Màu Xanh Lam Đậm */
    div.stButton > button[key="btn_login"] {
        background-color: #0077ba !important;
        color: #ffffff !important;
        font-weight: 700 !important;
        font-size: 15px !important;
        border-radius: 6px !important;
        border: none !important;
        height: 44px !important;
        box-shadow: 0 2px 4px rgba(0,119,186,0.3) !important;
    }
    div.stButton > button[key="btn_login"]:hover {
        background-color: #005c91 !important;
    }

    /* Nút Thoát Màu Đỏ Nổi Bật */
    div.stButton > button[key="btn_exit"] {
        background-color: #ef4444 !important;
        color: #ffffff !important;
        font-weight: 700 !important;
        font-size: 15px !important;
        border-radius: 6px !important;
        border: none !important;
        height: 44px !important;
        box-shadow: 0 2px 4px rgba(239, 68, 68, 0.3) !important;
    }
    div.stButton > button[key="btn_exit"]:hover {
        background-color: #dc2626 !important;
    }

    /* CSS Giao diện Dashboard */
    .card-box {
        padding: 20px;
        border-radius: 10px;
        color: white;
        margin-bottom: 15px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        min-height: 130px;
    }
    .card-red { background: linear-gradient(135deg, #e53935, #d32f2f); }
    .card-green { background: linear-gradient(135deg, #00b074, #008a5b); }
    .card-blue { background: linear-gradient(135deg, #29b6f6, #0288d1); }
    .card-dark { background: linear-gradient(135deg, #37474f, #263238); }
    .card-orange { background: linear-gradient(135deg, #ff9200, #e67e00); }
    .card-teal { background: linear-gradient(135deg, #00a896, #028090); }

    .card-title { font-size: 15px; font-weight: bold; margin-bottom: 5px; text-transform: uppercase; }
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
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
</style>
""", unsafe_allow_html=True)

if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

# ---------------------------------------------------------
# 2. KẾT NỐI DATABASE
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
    except Exception:
        return None

engine = get_db_engine()

# ---------------------------------------------------------
# 3. TRANG ĐĂNG NHẬP (THU GỌN & RÕ NÉT)
# ---------------------------------------------------------
def render_login():
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # Căn giữa và thu hẹp tỷ lệ cột (1.8 - 1.4 - 1.8)
    col_l, col_center, col_r = st.columns([1.8, 1.4, 1.8])

    with col_center:
        # Logo VNPT Bệnh viện Bưu điện vẽ SVG sắc nét
        st.markdown("""
<div style="text-align: center; margin-bottom: 15px;">
    <svg width="110" height="110" viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg">
        <circle cx="100" cy="100" r="95" fill="#0066b2"/>
        <circle cx="100" cy="100" r="72" fill="#ffffff"/>
        <path id="text-path" d="M 35 100 A 65 65 0 0 1 165 100" fill="none"/>
        <text fill="#0066b2" font-size="13" font-weight="bold" font-family="Arial">
            <textPath href="#text-path" startOffset="50%" text-anchor="middle">
                BỆNH VIỆN BƯU ĐIỆN
            </textPath>
        </text>
        <polygon points="32,95 35,102 28,98 36,98 29,102" fill="#ffffff"/>
        <polygon points="168,95 171,102 164,98 172,98 165,102" fill="#ffffff"/>
        <rect x="88" y="55" width="24" height="60" fill="#e51c23" rx="2"/>
        <rect x="70" y="73" width="60" height="24" fill="#e51c23" rx="2"/>
        <path d="M 60 115 C 75 135, 100 138, 100 138 C 100 138, 125 135, 140 115 C 120 128, 100 128, 100 128 C 100 128, 80 128, 60 115 Z" fill="#4caf50"/>
        <path d="M 40 130 Q 100 165 160 130 A 95 95 0 0 1 40 130 Z" fill="#0066b2"/>
        <text x="100" y="162" fill="#ffffff" font-size="18" font-weight="900" font-family="Arial" text-anchor="middle">VNPT</text>
    </svg>
</div>
""", unsafe_allow_html=True)

        st.markdown("<div class='hospital-title'>BỆNH VIỆN BƯU ĐIỆN</div>", unsafe_allow_html=True)
        st.markdown("<div class='hospital-subtitle'>Hệ thống Quản trị Nhân sự & Điều hành</div>", unsafe_allow_html=True)

        st.markdown("<div class='login-card'>", unsafe_allow_html=True)
        
        username = st.text_input("Tên đăng nhập / Username:", placeholder="Nhập tên đăng nhập...")
        password = st.text_input("Mật khẩu / Password:", type="password", placeholder="Nhập mật khẩu...")

        st.markdown("<br>", unsafe_allow_html=True)
        b_col1, b_col2 = st.columns(2)

        with b_col1:
            if st.button("🔑 Đăng nhập", key="btn_login", use_container_width=True):
                if username == "admin" and password == "admin123":
                    st.session_state['logged_in'] = True
                    st.success("Đăng nhập thành công!")
                    st.rerun()
                else:
                    st.error("❌ Tên đăng nhập hoặc mật khẩu chưa đúng!")

        with b_col2:
            if st.button("✕ Thoát", key="btn_exit", use_container_width=True):
                st.info("Đã đóng phiên đăng nhập.")

        st.markdown("</div>", unsafe_allow_html=True)

# ---------------------------------------------------------
# 4. GIAO DIỆN DASHBOARD
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
# 5. CHẠY ỨNG DỤNG
# ---------------------------------------------------------
if not st.session_state['logged_in']:
    render_login()
else:
    render_dashboard()
