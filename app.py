import os
import io
import base64
import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import plotly.express as px
from datetime import datetime, date
from sqlalchemy import create_engine, text

# ---------------------------------------------------------
# 1. CẤU HÌNH TRANG & CSS GIAO DIỆN
# ---------------------------------------------------------
st.set_page_config(
    page_title="BỆNH VIỆN BƯU ĐIỆN - Hệ thống Quản trị Nhân sự & Điều hành",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .stApp { background-color: #f1f5f9 !important; }
    [data-testid="stVerticalBlockBorderWrapper"], form[key="login_form"] {
        background-color: #ffffff !important;
        border-radius: 16px !important;
        border: 1px solid #e2e8f0 !important;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.08), 0 8px 10px -6px rgba(0, 0, 0, 0.03) !important;
        padding: 30px 25px 25px 25px !important;
    }
    .hospital-title {
        color: #0066b2 !important; font-weight: 800 !important;
        font-size: 30px !important; text-align: center;
        margin-top: 15px; margin-bottom: 4px; letter-spacing: 0.5px;
    }
    .hospital-subtitle {
        color: #475569 !important; font-size: 16px !important;
        font-weight: 600 !important; text-align: center; margin-bottom: 25px;
    }
    .stTextInput > label, .stSelectbox > label {
        color: #0f172a !important; font-size: 15px !important;
        font-weight: 700 !important; margin-bottom: 4px !important;
    }
    .stTextInput > div > div > input {
        border-radius: 8px !important; border: 1.5px solid #cbd5e1 !important;
        background-color: #ffffff !important; color: #0f172a !important; height: 44px !important;
    }
    .stButton > button, div[data-testid="stFormSubmitButton"] > button {
        background: linear-gradient(180deg, #0070d2 0%, #0056a3 100%) !important;
        color: #ffffff !important; font-weight: 800 !important;
        font-size: 16px !important; border-radius: 8px !important;
        border: 1px solid #004080 !important; height: 44px !important;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.12) !important; width: 100% !important;
    }
    .stButton > button p, div[data-testid="stFormSubmitButton"] > button p {
        color: #ffffff !important; font-weight: 800 !important; font-size: 16px !important;
    }
    .card-box {
        padding: 20px; border-radius: 10px; color: white; margin-bottom: 15px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1); min-height: 130px;
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
    
    [data-testid="stSidebar"] { background-color: #2b303b !important; }
    [data-testid="stSidebar"] * { color: #d1d5db !important; }
</style>
""", unsafe_allow_html=True)

if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'db_initialized' not in st.session_state:
    st.session_state['db_initialized'] = False
if 'user_info' not in st.session_state:
    st.session_state['user_info'] = {"fullname": "Đoàn Danh Hiển", "role": "Quản trị viên Hệ thống"}

# ---------------------------------------------------------
# 2. DATABASE NEON
# ---------------------------------------------------------
@st.cache_resource
def get_db_engine():
    try:
        if "DATABASE_URL" in st.secrets:
            raw_url = st.secrets["DATABASE_URL"].strip()
            if raw_url.startswith("postgres://"):
                raw_url = raw_url.replace("postgres://", "postgresql://", 1)
            return create_engine(raw_url, pool_pre_ping=True, pool_recycle=300)
        elif "postgres" in st.secrets:
            pg = st.secrets["postgres"]
            db_url = f"postgresql://{pg['user']}:{pg['password']}@{pg['host']}:{pg['port']}/{pg['database']}?sslmode=require"
            return create_engine(db_url, pool_pre_ping=True, pool_recycle=300)
        return None
    except Exception as e:
        st.error(f"Lỗi khởi tạo Engine DB: {e}")
        return None

engine = get_db_engine()

def init_db_structure():
    if not engine or st.session_state['db_initialized']:
        return
    try:
        with engine.begin() as conn:
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS can_bo (
                    id SERIAL PRIMARY KEY,
                    ma_can_bo VARCHAR(50) UNIQUE,
                    ho_ten VARCHAR(255) NOT NULL,
                    ngay_sinh DATE,
                    so_cccd VARCHAR(50),
                    chuc_danh VARCHAR(255),
                    khoa_phong VARCHAR(255),
                    trinh_do VARCHAR(255),
                    so_dien_thoai VARCHAR(50),
                    email VARCHAR(255)
                );
                CREATE UNIQUE INDEX IF NOT EXISTS idx_can_bo_ma_unique ON can_bo (ma_can_bo);
            """))
            st.session_state['db_initialized'] = True
    except Exception as e:
        print(f"Khởi tạo DB warning: {e}")

init_db_structure()

@st.cache_data(ttl=1)
def load_data_from_db():
    if not engine:
        return pd.DataFrame()
    try:
        with engine.connect() as conn:
            query = text("SELECT id, ma_can_bo, ho_ten, ngay_sinh, so_cccd, chuc_danh, khoa_phong, trinh_do, so_dien_thoai, email FROM can_bo ORDER BY id DESC")
            return pd.read_sql(query, conn)
    except Exception as e:
        st.error(f"Lỗi đọc dữ liệu: {e}")
        return pd.DataFrame()

# ---------------------------------------------------------
# 3. TRANG ĐĂNG NHẬP
# ---------------------------------------------------------
def render_login():
    st.markdown("<br>", unsafe_allow_html=True)
    col_l, col_center, col_r = st.columns([1.5, 2.2, 1.5])
    with col_center:
        with st.form(key="login_form", clear_on_submit=False):
            logo_path = os.path.join(os.path.dirname(__file__), "logo.png") if '__file__' in globals() else "logo.png"
            if os.path.exists(logo_path):
                with open(logo_path, "rb") as f:
                    encoded_img = base64.b64encode(f.read()).decode("utf-8")
                st.markdown(
                    f"""
                    <div style="display: flex; justify-content: center; align-items: center; margin-bottom: 10px;">
                        <img src="data:image/png;base64,{encoded_img}" width="220" style="object-fit: contain;">
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            else:
                st.image("logo.png", width=220)
            st.markdown("<div class='hospital-title'>BỆNH VIỆN BƯU ĐIỆN</div>", unsafe_allow_html=True)
            st.markdown("<div class='hospital-subtitle'>Hệ thống Quản trị Nhân sự & Điều hành</div>", unsafe_allow_html=True)
            username = st.text_input("Tên đăng nhập / Username:", placeholder="Nhập tên đăng nhập...")
            password = st.text_input("Mật khẩu / Password:", type="password", placeholder="Nhập mật khẩu...")
            st.markdown("<br>", unsafe_allow_html=True)
            b_col1, b_col2 = st.columns(2)
            with b_col1:
                submit_login = st.form_submit_button("🔑 Đăng nhập", use_container_width=True)
            with b_col2:
                submit_exit = st.form_submit_button("✕ Thoát", use_container_width=True)
            if submit_login:
                if username == "admin" and password == "admin123":
                    st.session_state['logged_in'] = True
                    st.success("Đăng nhập thành công!")
                    st.rerun()
                else:
                    st.error("❌ Tên đăng nhập hoặc mật khẩu chưa đúng!")
            if submit_exit:
                st.info("Đã đóng phiên đăng nhập.")

# ---------------------------------------------------------
# 4. DASHBOARD TRANG CHỦ
# ---------------------------------------------------------
def render_dashboard_home():
    st.markdown("<br>", unsafe_allow_html=True)
    df_db = load_data_from_db()
    total_staff = len(df_db)
    st.info(f"📊 **Tổng số lượng cán bộ, nhân viên hiện có trong cơ sở dữ liệu hệ thống:** **{total_staff}** nhân sự.")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"<div class='card-box card-red'><div class='card-title'>👨‍⚕️ HỒ SƠ CÁN BỘ CNV</div><div class='card-desc'>Tổng số: <b>{total_staff}</b> hồ sơ đang quản lý và cập nhật toàn viện.</div><div class='card-link'>XEM CHI TIẾT ➔</div></div>", unsafe_allow_html=True)
        st.markdown("<div class='card-box card-dark'><div class='card-title'>📜 HỢP ĐỒNG LAO ĐỘNG</div><div class='card-desc'>Theo dõi hợp đồng xác định thời hạn, không xác định thời hạn và lịch sử ký.</div><div class='card-link'>QUẢN LÝ HỒ SƠ ➔</div></div>", unsafe_allow_html=True)
    with col2:
        st.markdown("<div class='card-box card-green'><div class='card-title'>📊 BÁO CÁO & THỐNG KÊ</div><div class='card-desc'>Truy xuất dữ liệu báo cáo BYT, BVT và biến động nhân sự theo thời gian thực.</div><div class='card-link'>XEM BÁO CÁO ➔</div></div>", unsafe_allow_html=True)
        st.markdown("<div class='card-box card-orange'><div class='card-title'>📈 NÂNG BẬC LƯƠNG & NGẠCH</div><div class='card-desc'>Quản lý nâng lương, ngạch viên chức và cảnh báo danh sách đủ điều kiện nâng lương.</div><div class='card-link'>XEM DANH SÁCH ➔</div></div>", unsafe_allow_html=True)
    with col3:
        st.markdown("<div class='card-box card-blue'><div class='card-title'>🏥 GPHN & ĐÀO TẠO CME</div><div class='card-desc'>Quản lý Chứng chỉ hành nghề và tiến độ tích lũy 48 tiết CME của Bác sĩ / Điều dưỡng.</div><div class='card-link'>XEM CHI TIẾT ➔</div></div>", unsafe_allow_html=True)
        st.markdown("<div class='card-box card-teal'><div class='card-title'>🩺 QUẢN LÝ BHOI & SỨC KHỎE</div><div class='card-desc'>Theo dõi chế độ bảo hiểm sở hữu, đóng xem và đợt khám sức khỏe định kỳ.</div><div class='card-link'>CHI TIẾT ➔</div></div>", unsafe_allow_html=True)

    st.markdown("---")
    col_dash1, col_dash2, col_dash3 = st.columns([1.1, 1, 1], gap="medium")
    
    with col_dash1:
        st.markdown("##### 📌 **Cảnh báo tự động**")
        def render_alert_card(title, desc, count, color_border):
            st.markdown(f"""
                <div style="display: flex; align-items: center; justify-content: space-between; background-color: #ffffff; padding: 10px 12px; border-radius: 8px; margin-bottom: 8px; border-left: 5px solid {color_border}; box-shadow: 0 1px 3px rgba(0,0,0,0.05);">
                    <div>
                        <div style="font-weight: 600; font-size: 13.5px; color: #333;">{title}</div>
                        <div style="font-size: 11.5px; color: #666; margin-top: 2px;">{desc}</div>
                    </div>
                    <div style="background-color: #fff5f5; color: {color_border}; font-weight: bold; font-size: 14px; padding: 4px 10px; border-radius: 6px; border: 1px solid {color_border}33;">
                        {count}
                    </div>
                </div>
            """, unsafe_allow_html=True)

        render_alert_card("⏰ Sắp hết hạn HĐLĐ", "Cần ký lại / gia hạn trong 30 ngày", "12", "#ff4d4f")
        render_alert_card("💰 Đến hạn nâng bậc lương", "Đủ thời hạn xét nâng ngạch, bậc", "08", "#fa8c16")
        render_alert_card("⚠️ Cảnh báo thiếu giờ CME", "Chưa tích lũy đủ 48 tiết / 2 năm", "25", "#1890ff")
        render_alert_card("📜 GPHN cần cập nhật", "Bổ sung thông tin chứng chỉ mới", "04", "#52c41a")

    with col_dash2:
        st.markdown("##### 📊 **Nhân sự theo Trình độ**")
        df_trinh_do = pd.DataFrame({
            'Trình độ': ['Tiến sĩ/CKI', 'Thạc sĩ/CKI', 'Đại học', 'Cao đẳng', 'Trung cấp/Khác'],
            'Số lượng': [25, 142, 450, 180, 80]
        })
        fig_td = px.bar(
            df_trinh_do, x='Trình độ', y='Số lượng', text='Số lượng', color='Trình độ',
            color_discrete_sequence=['#fa8c16', '#5c6bc0', '#26a69a', '#9ccc65', '#ab47bc']
        )
        fig_td.update_traces(textposition='outside', textfont_size=11)
        fig_td.update_layout(
            margin=dict(t=10, b=10, l=10, r=10), height=260, showlegend=False,
            xaxis=dict(title='', tickfont=dict(size=10)),
            yaxis=dict(title='', showgrid=True, gridcolor='#f0f0f0')
        )
        st.plotly_chart(fig_td, use_container_width=True, config={'displayModeBar': False})

    with col_dash3:
        st.markdown("##### 🍩 **Phân loại Hợp đồng**")
        df_hd = pd.DataFrame({
            'Loại hợp đồng': ['Không xác định thời hạn', 'Xác định thời hạn (1-3 năm)', 'Thử việc / Ngắn hạn'],
            'Số lượng': [520, 310, 47]
        })
        fig_hd = px.pie(
            df_hd, names='Loại hợp đồng', values='Số lượng', hole=0.55,
            color_discrete_sequence=['#1890ff', '#fa8c16', '#00b96b']
        )
        fig_hd.update_traces(textposition='inside', textinfo='percent+value')
        fig_hd.update_layout(
            margin=dict(t=10, b=10, l=10, r=10), height=260,
            legend=dict(orientation="h", yanchor="bottom", y=-0.3, xanchor="center", x=0.5, font=dict(size=10))
        )
        st.plotly_chart(fig_hd, use_container_width=True, config={'displayModeBar': False})

# ---------------------------------------------------------
# 5. QUẢN LÝ CÁN BỘ CNV
# ---------------------------------------------------------
def render_quan_ly_can_bo():
    st.markdown("---")
    st.subheader("📁 QUẢN LÝ CÁN BỘ CNV BỆNH VIỆN BƯU ĐIỆN")
    if not engine:
        st.error("Chưa kết nối được Cơ sở dữ liệu Neon.")
        return
        
    df = load_data_from_db()
    st.success(f"📋 **Tổng số nhân sự hiện có trong CSDL:** **{len(df)}** cán bộ, nhân viên.")
    st.dataframe(df, use_container_width=True, hide_index=True)

# ---------------------------------------------------------
# 6. SIDEBAR & ĐIỀU HƯỚNG ROUTING
# ---------------------------------------------------------
def render_dashboard():
    st.sidebar.markdown(
        f"""
        <div style="text-align: center; padding-bottom: 10px;">
            <h3 style="color: #4da6ff; margin-bottom: 2px;">DANH MỤC CHỨC NĂNG</h3>
            <p style="font-size: 13px; color: #a0aec0;">👤 Xin chào: <b>{st.session_state.user_info['fullname']}</b></p>
        </div>
        """,
        unsafe_allow_html=True
    )

    if st.sidebar.button("🚪 Đăng xuất", use_container_width=True):
        st.session_state['logged_in'] = False
        st.rerun()

    menu_options = [
        "📌 Trang chủ / Dashboard", 
        "📑 Thông báo & Văn bản", 
        "📇 Hồ sơ Cán bộ CNV", 
        "🎓 Phân loại Trình độ", 
        "📝 Hợp đồng Lao động", 
        "🏛️ Hồ sơ Đảng viên", 
        "📜 Giấy phép hành nghề (GPHN)", 
        "📚 Theo dõi Đào tạo CME", 
        "📈 Nâng bậc lương & Ngạch", 
        "🔄 Bố trí & Điều chuyển", 
        "📑 Quản lý BHXH", 
        "🏥 Quản lý BHOI & Sức khỏe", 
        "⏰ Quản lý Chấm công & Ngày nghỉ", 
        "📊 Báo cáo - Thống kê", 
        "⚙️ Cấu hình Hệ thống"
    ]

    st.sidebar.markdown("---")
    menu_choice = st.sidebar.radio("Điều hướng chức năng:", options=menu_options, index=0)

    if "Trang chủ / Dashboard" in menu_choice:
        render_dashboard_home()
    elif "Hồ sơ Cán bộ CNV" in menu_choice:
        render_quan_ly_can_bo()
    else:
        st.title(f"{menu_choice}")
        st.info("Chức năng đang trong quá trình đồng bộ dữ liệu...")

# ---------------------------------------------------------
# 7. CHẠY APP
# ---------------------------------------------------------
if not st.session_state['logged_in']:
    render_login()
else:
    render_dashboard()
