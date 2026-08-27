import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine, text

# ---------------------------------------------------------
# 1. CẤU HÌNH TRANG STREAMLIT
# ---------------------------------------------------------
st.set_page_config(
    page_title="HRM Bệnh viện Bưu điện",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------------------------------------------------
# 2. KẾT NỐI DATABASE NEON POSTGRESQL
# ---------------------------------------------------------
@st.cache_resource
def get_db_engine():
    try:
        if "host" not in st.secrets:
            st.warning("⚠️ Chưa cấu hình Secrets trên Streamlit Cloud. Vui lòng kiểm tra lại phần Settings -> Secrets.")
            return None
            
        user = st.secrets["user"]
        password = st.secrets["password"]
        host = st.secrets["host"]
        port = st.secrets["port"]
        database = st.secrets["database"]
        
        # Chuỗi kết nối chuẩn SQLAlchemy cho Neon PostgreSQL (yêu cầu SSL)
        db_url = f"postgresql://{user}:{password}@{host}:{port}/{database}?sslmode=require"
        engine = create_engine(db_url)
        return engine
    except Exception as e:
        st.error(f"Lỗi kết nối CSDL Neon: {e}")
        return None

engine = get_db_engine()

# Khởi tạo bảng dữ liệu trên Neon DB nếu chưa tồn tại
def init_db():
    if engine:
        try:
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
        except Exception as e:
            st.error(f"Lỗi khởi tạo bảng CSDL: {e}")

init_db()

# ---------------------------------------------------------
# 3. THANH MENU BÊN TRÁI (SIDEBAR)
# ---------------------------------------------------------
st.sidebar.title("🏥 HRM BƯU ĐIỆN")
st.sidebar.caption("Hệ thống Quản trị Nhân sự Y tế 4.0")

menu = st.sidebar.radio(
    "Danh mục quản lý", 
    ["Dashboard & Cảnh báo", "Hồ sơ Cán bộ", "Báo cáo & Thống kê"]
)

st.sidebar.markdown("---")
st.sidebar.info("💡 **Hỗ trợ:** Kết nối dữ liệu thời gian thực với Neon Console Database.")

# ---------------------------------------------------------
# TAB 1: DASHBOARD & CẢNH BÁO
# ---------------------------------------------------------
if menu == "Dashboard & Cảnh báo":
    st.title("📊 TỔNG QUAN NHÂN SỰ BỆNH VIỆN BƯU ĐIỆN")
    
    # Đếm tổng số cán bộ từ DB thực tế
    total_cb = 0
    if engine:
        try:
            with engine.connect() as conn:
                res = conn.execute(text("SELECT COUNT(*) FROM can_bo")).fetchone()
                total_cb = res[0] if res else 0
        except:
            total_cb = 0

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Tổng cán bộ (Đã nhập)", f"{total_cb} Cán bộ", "+12 tháng này")
    col2.metric("Bác sĩ / Dược sĩ", "450", "30% Tổng số quy hoạch")
    col3.metric("Cảnh báo nâng lương", "28 Cán bộ", "⚡ Cần xử lý", delta_color="inverse")
    col4.metric("Sắp đến tuổi nghỉ hưu", "5 Cán bộ", "Trong 6 tháng")
    
    st.markdown("---")
    st.subheader("⚠️ Cảnh báo Hệ thống Tự động (Phụ lục 02)")
    
    st.warning("🔔 **Thông báo:** Có 8 cán bộ quá hạn giữ chức vụ bổ nhiệm & 12 cán bộ sắp hết hạn Hợp đồng lao động!")
    
    # Bảng mẫu danh sách cảnh báo
    data_canh_bao = {
        "Mã CB": ["CB001", "CB045", "CB112", "CB090"],
        "Họ và Tên": ["BS. Nguyễn Văn A", "ThS. Trần Thị B", "CN. Lê Văn C", "BSCKII. Phạm Hoàng D"],
        "Khoa / Phòng": ["Khoa Cấp Cứu", "Khoa Dược", "Phòng TCKT", "Khoa Ngoại Tổng Hợp"],
        "Loại Cảnh báo": ["Quá hạn nâng lương", "Sắp hết hạn HĐLĐ", "Sắp nghỉ hưu", "Quá hạn bổ nhiệm"],
        "Hạn xử lý": ["15/09/2026", "20/09/2026", "01/10/2026", "05/10/2026"]
    }
    st.table(pd.DataFrame(data_canh_bao))

# ---------------------------------------------------------
# TAB 2: QUẢN LÝ HỒ SƠ CÁN BỘ
# ---------------------------------------------------------
elif menu == "Hồ sơ Cán bộ":
    st.title("📁 QUẢN LÝ HỒ SƠ CÁN BỘ Y TẾ")
    
    tab_danh_sach, tab_them_moi = st.tabs(["📋 Danh sách Cán bộ", "➕ Thêm Cán bộ Mới"])
    
    # --- 2.1 Xem & Tìm kiếm Cán bộ ---
    with tab_danh_sach:
        st.subheader("Danh sách Cán bộ Y tế trong CSDL")
        
        if engine:
            try:
                df_can_bo = pd.read_sql("SELECT * FROM can_bo ORDER BY ma_cb ASC", engine)
                
                col_s1, col_s2 = st.columns([3, 1])
                tu_khoa = col_s1.text_input("🔍 Tìm kiếm theo Họ tên hoặc Mã Cán bộ:")
                
                if tu_khoa:
                    df_can_bo = df_can_bo[
                        df_can_bo['ho_ten'].astype(str).str.contains(tu_khoa, case=False, na=False) |
                        df_can_bo['ma_cb'].astype(str).str.contains(tu_khoa, case=False, na=False)
                    ]
                
                if df_can_bo.empty:
                    st.info("Chưa có dữ liệu cán bộ. Bạn hãy chuyển sang tab 'Thêm Cán bộ Mới' để nhập dữ liệu.")
                else:
                    # Hiển thị bảng
                    st.dataframe(
                        df_can_bo.rename(columns={
                            "ma_cb": "Mã CB",
                            "ho_ten": "Họ và Tên",
                            "chuc_danh": "Chức danh",
                            "khoa_phong": "Khoa / Phòng",
                            "loai_nhan_su": "Loại Nhân sự",
                            "so_dienthoai": "Số điện thoại",
                            "trang_thai": "Trạng thái"
                        }),
                        use_container_width=True
                    )
                    
                    # Nút Xuất CSV/Excel
                    csv_data = df_can_bo.to_csv(index=False).encode('utf-8-sig')
                    st.download_button(
                        label="📥 Tải về danh sách Cán bộ (File CSV)",
                        data=csv_data,
                        file_name="danh_sach_can_bo_buu_dien.csv",
                        mime="text/csv"
                    )
            except Exception as e:
                st.error(f"Lỗi truy vấn dữ liệu từ CSDL: {e}")

    # --- 2.2 Thêm Cán bộ Mới ---
    with tab_them_moi:
        st.subheader("Nhập thông tin Hồ sơ Nhân sự mới")
        with st.form("form_them_can_bo", clear_on_submit=True):
            col_a, col_b = st.columns(2)
            ma_cb = col_a.text_input("Mã Cán bộ (Ví dụ: CB001)*")
            ho_ten = col_b.text_input("Họ và Tên Cán bộ*")
            
            chuc_danh = col_a.selectbox(
                "Chức danh / Trình độ", 
                ["BS CKI", "BS CKII", "Thạc sĩ", "Tiến sĩ", "Cử nhân Điều dưỡng", "Dược sĩ CKI", "Cử nhân Khác"]
            )
            khoa_phong = col_b.selectbox(
                "Khoa / Phòng công tác", 
                ["Khoa Cấp Cứu", "Khoa Dược", "Phòng TCKT", "Khoa Ngoại Tổng Hợp", "Khoa Khám Bệnh", "Khoa Hồi Sức Tích Cực", "Phòng Tổ Chức Cán Bộ"]
            )
            
            loai_nhan_su = col_a.selectbox(
                "Phân loại Nhân sự", 
                ["Bác sĩ", "Dược sĩ", "Điều dưỡng", "Hành chính", "Kỹ thuật viên"]
            )
            so_dienthoai = col_b.text_input("Số điện thoại liên hệ")
            
            btn_submit = st.form_submit_button("💾 Lưu vào CSDL Neon")
            
            if btn_submit:
                if not ma_cb or not ho_ten:
                    st.error("❌ Vui lòng điền đầy đủ Mã Cán bộ và Họ tên!")
                elif engine:
                    try:
                        with engine.connect() as conn:
                            conn.execute(
                                text("""
                                    INSERT INTO can_bo (ma_cb, ho_ten, chuc_danh, khoa_phong, loai_nhan_su, so_dienthoai)
                                    VALUES (:ma_cb, :ho_ten, :chuc_danh, :khoa_phong, :loai_nhan_su, :so_dienthoai)
                                """),
                                {
                                    "ma_cb": ma_cb.strip(),
                                    "ho_ten": ho_ten.strip(),
                                    "chuc_danh": chuc_danh,
                                    "khoa_phong": khoa_phong,
                                    "loai_nhan_su": loai_nhan_su,
                                    "so_dienthoai": so_dienthoai.strip()
                                }
                            )
                            conn.commit()
                        st.success(f"✅ Thêm thành công cán bộ **{ho_ten}** ({ma_cb}) vào Database Neon!")
                        st.rerun()
                    except Exception as err:
                        st.error(f"❌ Lỗi khi lưu dữ liệu (Mã Cán bộ '{ma_cb}' có thể đã tồn tại): {err}")

# ---------------------------------------------------------
# TAB 3: BÁO CÁO & THỐNG KÊ
# ---------------------------------------------------------
elif menu == "Báo cáo & Thống kê":
    st.title("📈 BÁO CÁO & THỐNG KÊ NHÂN SỰ")
    
    if engine:
        try:
            df = pd.read_sql("SELECT * FROM can_bo", engine)
            
            if df.empty:
                st.info("💡 Chưa có dữ liệu thực tế trong CSDL. Vui lòng vào tab **'Hồ sơ Cán bộ'** để thêm thông tin nhân sự.")
            else:
                st.subheader("📊 Biểu đồ Phân tích Nhân sự Thời gian thực")
                
                col_chart1, col_chart2 = st.columns(2)
                
                with col_chart1:
                    st.markdown("##### Cơ cấu Nhân sự theo Khoa / Phòng")
                    fig_khoa = px.pie(
                        df, 
                        names='khoa_phong', 
                        title='Tỷ lệ Cán bộ theo Khoa/Phòng',
                        hole=0.4,
                        color_discrete_sequence=px.colors.qualitative.Pastel
                    )
                    st.plotly_chart(fig_khoa, use_container_width=True)
                    
                with col_chart2:
                    st.markdown("##### Phân bổ Trình độ & Phân loại Nhân sự")
                    fig_trinh_do = px.bar(
                        df, 
                        x='chuc_danh', 
                        color='loai_nhan_su',
                        title='Số lượng theo Trình độ chuyên môn',
                        barmode='stack',
                        color_discrete_sequence=px.colors.qualitative.Set2
                    )
                    st.plotly_chart(fig_trinh_do, use_container_width=True)
                
                st.markdown("---")
                st.subheader("📋 Bảng tổng hợp theo Loại Nhân sự")
                df_summary = df.groupby(['loai_nhan_su', 'chuc_danh']).size().reset_index(name='Số lượng')
                st.dataframe(df_summary, use_container_width=True)
                
        except Exception as e:
            st.error(f"Lỗi tải dữ liệu báo cáo: {e}")
