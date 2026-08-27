import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine, text

# ---------------------------------------------------------
# 1. KẾT NỐI DATABASE NEON POSTGRESQL
# ---------------------------------------------------------
@st.cache_resource
def get_db_engine():
    # Lấy thông tin kết nối từ st.secrets
    try:
        db_config = st.secrets["postgres"]
        db_url = f"postgresql://{db_config['user']}:{db_config['password']}@{db_config['host']}:{db_config['port']}/{db_config['database']}?sslmode=require"
        engine = create_engine(db_url)
        return engine
    except Exception as e:
        st.error(f"Lỗi kết nối CSDL: {e}")
        return None

engine = get_db_engine()

# Khởi tạo bảng mẫu trong Database nếu chưa có
def init_db():
    if engine:
        with engine.connect() as conn:
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS can_bo (
                    ma_cb VARCHAR(20) PRIMARY KEY,
                    ho_ten VARCHAR(100) NOT NULL,
                    chuc_danh VARCHAR(50),
                    khoa_phong VARCHAR(100),
                    loai_nhan_su VARCHAR(50),
                    so_dienthoai VARCHAR(15),
                    trang_thai VARCHAR(20) DEFAULT 'Đang làm việc'
                );
            """))
            conn.commit()

init_db()

# ---------------------------------------------------------
# 2. CẤU HÌNH GIAO DIỆN STREAMLIT
# ---------------------------------------------------------
st.set_page_config(page_title="HRM Bệnh viện Bưu điện", layout="wide")

st.sidebar.title("🏥 HRM BƯU ĐIỆN")
menu = st.sidebar.radio(
    "Danh mục quản lý", 
    ["Dashboard & Cảnh báo", "Hồ sơ Cán bộ", "Báo cáo & Thống kê"]
)

# ---------------------------------------------------------
# TAB 1: DASHBOARD & CẢNH BÁO
# ---------------------------------------------------------
if menu == "Dashboard & Cảnh báo":
    st.header("📊 TỔNG QUAN NHÂN SỰ BỆNH VIỆN BƯU ĐIỆN")
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Tổng cán bộ, NVYT", "1,500", "+12 tháng này")
    col2.metric("Bác sĩ / Dược sĩ", "450", "30% Tổng số")
    col3.metric("Cảnh báo nâng lương", "28 Cán bộ", "Cần xử lý")
    col4.metric("Sắp đến tuổi nghỉ hưu", "5 Cán bộ", "Trong 6 tháng")
    
    st.subheader("⚠️ Cảnh báo Hệ thống Tự động")
    st.warning("🔔 Có 8 cán bộ quá hạn giữ chức vụ bổ nhiệm & 12 cán bộ sắp hết hạn HĐLĐ!")

# ---------------------------------------------------------
# TAB 2: QUẢN LÝ HỒ SƠ CÁN BỘ
# ---------------------------------------------------------
elif menu == "Hồ sơ Cán bộ":
    st.header("📁 QUẢN LÝ HỒ SƠ CÁN BỘ Y TẾ")
    
    tab_danh_sach, tab_them_moi = st.tabs(["📋 Danh sách Cán bộ", "➕ Thêm Cán bộ Mới"])
    
    # 2.1 Hiển thị & Tìm kiếm
    with tab_danh_sach:
        col_search1, col_search2 = st.columns([3, 1])
        tu_khoa = col_search1.text_input("🔍 Tìm kiếm theo Họ tên hoặc Mã Cán bộ:")
        
        if engine:
            query = "SELECT * FROM can_bo"
            df_can_bo = pd.read_sql(query, engine)
            
            if tu_khoa:
                df_can_bo = df_can_bo[
                    df_can_bo['ho_ten'].str.contains(tu_khoa, case=False, na=False) |
                    df_can_bo['ma_cb'].str.contains(tu_khoa, case=False, na=False)
                ]
            
            st.dataframe(df_can_bo, use_container_width=True)
            
            # Export dữ liệu Excel
            csv = df_can_bo.to_csv(index=False).encode('utf-8-sig')
            st.download_button("📥 Tải xuống danh sách (CSV)", csv, "danh_sach_can_bo.csv", "text/csv")

    # 2.2 Thêm mới Cán bộ
    with tab_them_moi:
        with st.form("form_them_can_bo", clear_on_submit=True):
            st.subheader("Nhập thông tin nhân sự mới")
            c1, c2 = st.columns(2)
            ma_cb = c1.text_input("Mã Cán bộ (Ví dụ: CB001)*")
            ho_ten = c2.text_input("Họ và Tên*")
            
            chuc_danh = c1.selectbox("Chức danh / Trình độ", ["BS CKI", "BS CKII", "Thạc sĩ", "Tiến sĩ", "Cử nhân", "Khác"])
            khoa_phong = c2.selectbox("Khoa / Phòng", ["Khoa Cấp Cứu", "Khoa Dược", "Phòng TCKT", "Khoa Ngoại Tổng Hợp", "Khoa Khám Bệnh"])
            
            loai_nhan_su = c1.selectbox("Loại nhân sự", ["Bác sĩ", "Dược sĩ", "Điều dưỡng", "Hành chính", "Kỹ thuật viên"])
            so_dienthoai = c2.text_input("Số điện thoại")
            
            btn_submit = st.form_submit_button("Lưu Hồ Sơ")
            
            if btn_submit:
                if not ma_cb or not ho_ten:
                    st.error("Vui lòng điền đầy đủ thông tin bắt buộc (*)")
                elif engine:
                    try:
                        with engine.connect() as conn:
                            conn.execute(
                                text("""
                                    INSERT INTO can_bo (ma_cb, ho_ten, chuc_danh, khoa_phong, loai_nhan_su, so_dienthoai)
                                    VALUES (:ma_cb, :ho_ten, :chuc_danh, :khoa_phong, :loai_nhan_su, :so_dienthoai)
                                """),
                                {
                                    "ma_cb": ma_cb, "ho_ten": ho_ten, "chuc_danh": chuc_danh,
                                    "khoa_phong": khoa_phong, "loai_nhan_su": loai_nhan_su, "so_dienthoai": so_dienthoai
                                }
                            )
                            conn.commit()
                        st.success(f"Thêm thành công cán bộ {ho_ten} ({ma_cb}) vào Database Neon!")
                    except Exception as err:
                        st.error(f"Lỗi khi lưu dữ liệu (Có thể trùng Mã Cán bộ): {err}")

# ---------------------------------------------------------
# TAB 3: BÁO CÁO & THỐNG KÊ
# ---------------------------------------------------------
elif menu == "Báo cáo & Thống kê":
    st.header("📈 BÁO CÁO & THỐNG KÊ NHÂN SỰ")
    
    if engine:
        df = pd.read_sql("SELECT * FROM can_bo", engine)
        
        if df.empty:
            st.info("Chưa có dữ liệu trong Database. Vui lòng thêm cán bộ ở mục 'Hồ sơ Cán bộ'.")
        else:
            col_chart1, col_chart2 = st.columns(2)
            
            with col_chart1:
                st.subheader("Cơ cấu Nhân sự theo Khoa / Phòng")
                fig_khoa = px.pie(df, names='khoa_phong', title='Tỷ lệ nhân sự theo Khoa/Phòng', hole=0.4)
                st.plotly_chart(fig_khoa, use_container_width=True)
                
            with col_chart2:
                st.subheader("Phân bổ Trình độ / Chức danh")
                fig_trinh_do = px.bar(df, x='chuc_danh', color='loai_nhan_su', title='Số lượng theo Trình độ & Loại nhân sự')
                st.plotly_chart(fig_trinh_do, use_container_width=True)
