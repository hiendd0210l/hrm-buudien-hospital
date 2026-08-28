import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine, text

# ---------------------------------------------------------
# 1. CẤU HÌNH TRANG & CSS TÙY CHỈNH (THEO THIẾT KẾ MỚI)
# ---------------------------------------------------------
st.set_page_config(
    page_title="DANH MỤC CHỨC NĂNG - BỆNH VIỆN BƯU ĐIỆN",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS tái tạo giao diện thẻ màu & hiệu ứng đẹp mắt
st.markdown("""
<style>
    /* Gradient & khung thẻ màu */
    .card-box {
        padding: 20px;
        border-radius: 10px;
        color: white;
        margin-bottom: 15px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        position: relative;
        min-height: 130px;
    }
    .card-red { background: linear-gradient(135deg, #e53935, #d32f2f); }
    .card-green { background: linear-gradient(135deg, #00b074, #008a5b); }
    .card-blue { background: linear-gradient(135deg, #29b6f6, #0288d1); }
    .card-dark { background: linear-gradient(135deg, #37474f, #263238); }
    .card-orange { background: linear-gradient(135deg, #ff9200, #e67e00); }
    .card-teal { background: linear-gradient(135deg, #00a896, #028090); }
    
    .card-title { font-size: 16px; font-weight: bold; margin-bottom: 5px; text-transform: uppercase; }
    .card-desc { font-size: 12px; opacity: 0.9; margin-bottom: 10px; }
    .card-link { font-size: 11px; font-weight: bold; text-align: right; text-transform: uppercase; cursor: pointer; }

    /* Badge hình tròn ở khung Cảnh báo */
    .badge-circle {
        background-color: #ffffff;
        border: 2px solid;
        border-radius: 50%;
        width: 32px;
        height: 32px;
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
        background-color: #f8f9fa;
        padding: 12px 15px;
        border-radius: 8px;
        margin-bottom: 10px;
        border-left: 4px solid #00b074;
    }
</style>
""", unsafe_allow_html=True)

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
# 3. SIDEBAR - DANH MỤC CHỨC NĂNG (ĐẦY ĐỦ NHƯ THIẾT KẾ)
# ---------------------------------------------------------
st.sidebar.title("DANH MỤC CHỨC NĂNG")
st.sidebar.caption("👤 **Xin chào:** Đoàn Danh Hiển")

# Nút Đăng xuất mẫu
st.sidebar.button("🔒 Đăng xuất", use_container_width=True)

st.sidebar.markdown("---")
st.sidebar.caption("Điều hướng chức năng")

# Tất cả 16 danh mục đúng theo giao diện mẫu
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

# ---------------------------------------------------------
# CỦA SỔ CHÍNH - HEADER NGUỜI DÙNG
# ---------------------------------------------------------
def render_header():
    col_user_img, col_user_info = st.columns([1, 11])
    with col_user_img:
        st.image("https://cdn-icons-png.flaticon.com/512/3135/3135715.png", width=70)
    with col_user_info:
        st.title("Xin chào, Đoàn Danh Hiển")
        st.caption("Quản trị viên Hệ thống — Bệnh viện Bưu điện")

# ---------------------------------------------------------
# MAN HINH 1: TRANG CHỦ / DASHBOARD (CHÍNH THEO THIẾT KẾ)
# ---------------------------------------------------------
if menu == "📌 Trang chủ / Dashboard":
    render_header()
    st.markdown("<br>", unsafe_allow_html=True)
    
    # --- KHỐI 6 THẺ CHỨC NĂNG CHÍNH (GRID 3x2) ---
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="card-box card-red">
            <div class="card-title">👨‍⚕️ HỒ SƠ CÁN BỘ CNV</div>
            <div class="card-desc">Theo dõi, cập nhật và quản lý toàn bộ danh sách hồ sơ 877 nhân sự toàn bệnh viện.</div>
            <div class="card-link">XEM CHI TIẾT ➔</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="card-box card-dark">
            <div class="card-title">📜 HỢP ĐỒNG LAO ĐỘNG</div>
            <div class="card-desc">Theo dõi hợp đồng xác định thời hạn, không xác định thời hạn và lịch sử ký.</div>
            <div class="card-link">QUẢN LÝ HỒ SƠ ➔</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="card-box card-green">
            <div class="card-title">📊 BÁO CÁO & THỐNG KÊ</div>
            <div class="card-desc">Truy xuất dữ liệu báo cáo BYT, BVT và biến động nhân sự theo thời gian thực.</div>
            <div class="card-link">XEM BÁO CÁO ➔</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="card-box card-orange">
            <div class="card-title">📈 NÂNG BẬC LƯƠNG & NGẠCH</div>
            <div class="card-desc">Quản lý nâng lương, ngạch viên chức và cảnh báo danh sách đủ điều kiện nâng lương.</div>
            <div class="card-link">XEM DANH SÁCH ➔</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div class="card-box card-blue">
            <div class="card-title">🏥 GPHN & ĐÀO TẠO CME</div>
            <div class="card-desc">Quản lý Chứng chỉ hành nghề và tiến độ tích lũy 48 tiết CME của Bác sĩ / Điều dưỡng.</div>
            <div class="card-link">XEM CHI TIẾT ➔</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="card-box card-teal">
            <div class="card-title">🩺 QUẢN LÝ BHOI & SỨC KHỎE</div>
            <div class="card-desc">Theo dõi chế độ bảo hiểm sở hữu, đóng xem và đợt khám sức khỏe định kỳ.</div>
            <div class="card-link">CHI TIẾT ➔</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # --- KHỐI BÊN DƯỚI: CẢNH BÁO + 2 BIỂU ĐỒ (3 CỘT) ---
    c_left, c_mid, c_right = st.columns([1.2, 1.4, 1.4])

    # 1. Cột Cảnh báo tự động
    with c_left:
        st.subheader("📌 Cảnh báo tự động")
        
        st.markdown("""
        <div class="alert-item">
            <span class="badge-circle badge-red">12</span>
            <b>⏳ Sắp hết hạn HĐLĐ</b><br>
            <small style="color: gray;">Cần tái ký / gia hạn trong 30 ngày</small>
        </div>
        <div class="alert-item">
            <span class="badge-circle badge-orange">08</span>
            <b>💰 Đến hạn nâng bậc lương</b><br>
            <small style="color: gray;">Đủ thời hạn nâng lương ngạch, bậc</small>
        </div>
        <div class="alert-item">
            <span class="badge-circle badge-blue">25</span>
            <b>⚠️ Cảnh báo thiếu giờ CME</b><br>
            <small style="color: gray;">Chưa tích lũy đủ 48 tiết / 2 năm</small>
        </div>
        <div class="alert-item">
            <span class="badge-circle badge-green">04</span>
            <b>📜 GPHN cần cập nhật</b><br>
            <small style="color: gray;">Bổ sung thông tin chứng chỉ mới</small>
        </div>
        """, unsafe_allow_html=True)

    # 2. Cột Biểu đồ Trình độ (Bar Chart)
    with c_mid:
        st.subheader("📊 Nhân sự theo Trình độ")
        data_trinh_do = pd.DataFrame({
            "Trình độ": ["Tiến sĩ / CKI", "Thạc sĩ / CKI", "Đại học", "Cao đẳng", "Trung cấp / Khác"],
            "Số lượng": [25, 142, 450, 180, 80]
        })
        fig_bar = px.bar(
            data_trinh_do, 
            x="Trình độ", 
            y="Số lượng", 
            text="Số lượng",
            color="Trình độ",
            color_discrete_sequence=['#ff9200', '#5c6bc0', '#26a69a', '#9ccc65', '#ec407a']
        )
        fig_bar.update_layout(showlegend=False, margin=dict(l=10, r=10, t=20, b=20), height=320)
        st.plotly_chart(fig_bar, use_container_width=True)

    # 3. Cột Biểu đồ Phân loại Hợp đồng (Donut Chart)
    with c_right:
        st.subheader("🍩 Phân loại Hợp đồng")
        data_hd = pd.DataFrame({
            "Loại HĐ": ["Không xác định thời hạn", "Xác định thời hạn (1-3 năm)", "Thử việc / Ngắn hạn"],
            "Số lượng": [520, 310, 47]
        })
        fig_donut = px.pie(
            data_hd, 
            names="Loại HĐ", 
            values="Số lượng", 
            hole=0.5,
            color_discrete_sequence=['#0288d1', '#ff9200', '#00b074']
        )
        fig_donut.update_layout(
            legend=dict(orientation="h", yanchor="bottom", y=-0.3, xanchor="center", x=0.5),
            margin=dict(l=10, r=10, t=20, b=20),
            height=320
        )
        st.plotly_chart(fig_donut, use_container_width=True)

# ---------------------------------------------------------
# MAN HINH 2: HỒ SƠ CÁN BỘ CNV (CHỨC NĂNG THỰC TẾ CSDL)
# ---------------------------------------------------------
elif menu == "👤 Hồ sơ Cán bộ CNV":
    render_header()
    st.markdown("---")
    st.subheader("📁 QUẢN LÝ CÁN BỘ CNV BỆNH VIỆN BƯU ĐIỆN")
    
    tab_list, tab_add = st.tabs(["📋 Danh sách Nhân sự (Neon DB)", "➕ Thêm Nhân sự Mới"])
    
    with tab_list:
        if engine:
            try:
                df = pd.read_sql("SELECT * FROM can_bo ORDER BY ma_cb ASC", engine)
                if df.empty:
                    st.info("Chưa có dữ liệu nhân sự. Bạn hãy qua tab 'Thêm Nhân sự Mới' để khởi tạo.")
                else:
                    st.dataframe(df, use_container_width=True)
            except Exception as e:
                st.error(f"Lỗi tải dữ liệu: {e}")
                
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

# ---------------------------------------------------------
# MẶC ĐỊNH CHO CÁC MỤC CÒN LẠI (GIAO DIỆN CHỜ PHOI)
# ---------------------------------------------------------
else:
    render_header()
    st.markdown("---")
    st.info(f"⚙️ Chức năng **{menu}** đang được đồng bộ dữ liệu. Giao diện đã sẵn sàng!")
