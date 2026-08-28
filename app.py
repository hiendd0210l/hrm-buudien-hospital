import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, text

# --- CẤU HÌNH GIAO DIỆN STREAMLIT ---
st.set_page_config(
    page_title="Quản lý Cán bộ NV - Bệnh viện Bưu Điện",
    page_icon="🏥",
    layout="wide"
)

# --- KẾT NỐI CƠ SỞ DỮ LIỆU ---
# (Thay đổi chuỗi kết nối tùy theo cấu hình cơ sở dữ liệu thực tế của bạn)
DB_USER = "root"
DB_PASSWORD = ""
DB_HOST = "localhost"
DB_PORT = "3306"
DB_NAME = "quan_ly_can_bo"

DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
engine = create_engine(DATABASE_URL)

@st.cache_data(ttl=60)
def load_data():
    try:
        query = "SELECT * FROM can_bo;"
        df = pd.read_sql(query, con=engine)
        return df
    except Exception as e:
        # Nếu chưa có bảng hoặc lỗi kết nối, trả về DataFrame rỗng
        return pd.DataFrame()

# --- TIÊU ĐỀ TRANG ---
st.markdown("### **Xin chào, Đoàn Danh Hiển**")
st.markdown("<p style='color: gray; font-size: 14px;'>Quản trị viên Hệ thống — Bệnh viện Bưu điện</p>", unsafe_allow_html=True)
st.markdown("---")

st.markdown("#### 📁 **QUẢN LÝ CÁN BỘ CNV BỆNH VIỆN BƯU ĐIỆN**")

# --- KHỞI TẠO CÁC TAB CHỨC NĂNG ---
tab1, tab2, tab3 = st.tabs(["📋 Danh sách & Xóa", "➕ Thêm / Sửa Nhân sự", "📊 Thống kê & Báo cáo"])

# Tải dữ liệu hiện tại
df = load_data()

# ==========================================
# TAB 1: DANH SÁCH & XÓA
# ==========================================
with tab1:
    col_t1, col_t2, col_t3 = st.columns([3, 1.2, 1.2])
    col_t1.markdown("##### **Danh sách cán bộ nhân viên hiện có**")
    
    if col_t2.button("🔄 Tải lại dữ liệu", use_container_width=True):
        st.cache_data.clear()
        if "select_target_del" in st.session_state:
            del st.session_state["select_target_del"]
        st.toast("🔄 Đã làm mới dữ liệu từ CSDL thành công!")
        st.rerun()

    if col_t3.button("🧹 Xóa hết dữ liệu", use_container_width=True):
        try:
            with engine.connect() as conn:
                conn.execute(text("DELETE FROM can_bo;"))
                conn.commit()
            st.cache_data.clear()
            if "select_target_del" in st.session_state:
                del st.session_state["select_target_del"]
            st.success("Đã làm sạch toàn bộ CSDL!")
            st.rerun()
        except Exception as e_clean:
            st.error(f"Lỗi khi làm sạch CSDL: {e_clean}")

    if df.empty:
        st.info("Chưa có dữ liệu nhân sự trong CSDL. Bạn có thể chuyển sang tab 'Thêm / Sửa Nhân sự' để cập nhật.")
    else:
        display_df = df.drop(columns=['id']).copy() if 'id' in df.columns else df.copy()
        display_df.columns = [
            'Mã Cán bộ', 'Họ và Tên', 'Ngày sinh', 'Số CCCD', 
            'Chức danh', 'Khoa / Phòng', 'Trình độ', 'Số điện thoại', 'Email'
        ]
        st.dataframe(display_df, use_container_width=True, hide_index=True)
        
        st.markdown("---")
        st.markdown("##### 🗑️ **Xóa dữ liệu cá nhân**")
        col_del1, col_del2, col_del3 = st.columns([2.5, 1, 1])
        
        # Tạo danh sách lựa chọn với dòng mặc định ở đầu tiên
        options_list = ["-- Chọn nhân sự muốn xóa --"]
        options_map = {"-- Chọn nhân sự muốn xóa --": None}
        
        for _, row in df.iterrows():
            mcb = str(row['ma_can_bo']) if pd.notna(row['ma_can_bo']) else "N/A"
            hoten = str(row['ho_ten']) if pd.notna(row['ho_ten']) else "N/A"
            khoa = str(row['khoa_phong']) if pd.notna(row['khoa_phong']) else "Chưa phân khoa"
            label = f"{mcb} - {hoten} ({khoa})"
            options_list.append(label)
            options_map[label] = row['id']

        # Đảm bảo session_state khởi tạo hợp lệ
        if "select_target_del" not in st.session_state:
            st.session_state["select_target_del"] = "-- Chọn nhân sự muốn xóa --"

        selected_del_label = col_del1.selectbox(
            "Chọn nhân sự muốn xóa:", 
            options_list, 
            key="select_target_del"
        )
        
        target_id = options_map.get(selected_del_label, None)

        if col_del2.button("🗑️ Xóa nhân sự", use_container_width=True):
            if target_id is None:
                st.warning("⚠️ Vui lòng chọn một nhân sự cụ thể trong danh sách để xóa!")
            else:
                with engine.connect() as conn:
                    conn.execute(text("DELETE FROM can_bo WHERE id = :id"), {"id": target_id})
                    conn.commit()
                st.cache_data.clear()
                st.session_state["select_target_del"] = "-- Chọn nhân sự muốn xóa --"
                st.success(f"Đã xóa thành công [{selected_del_label}]!")
                st.rerun()

        # Xử lý nút Hủy thao tác cập nhật lại ngay lập tức
        if col_del3.button("❌ Hủy thao tác", use_container_width=True):
            st.session_state["select_target_del"] = "-- Chọn nhân sự muốn xóa --"
            st.toast("Đã hủy thao tác chọn nhân sự.")
            st.rerun()

# ==========================================
# TAB 2: THÊM / SỬA NHÂN SỰ
# ==========================================
with tab2:
    st.markdown("##### ➕ **Thêm mới cán bộ nhân viên**")
    with st.form("form_them_cb"):
        col_f1, col_f2, col_f3 = st.columns(3)
        with col_f1:
            ma_cb = st.text_input("Mã Cán bộ (*)")
            ho_ten = st.text_input("Họ và Tên (*)")
            ngay_sinh = st.date_input("Ngày sinh")
        with col_f2:
            so_cccd = st.text_input("Số CCCD")
            chuc_danh = st.text_input("Chức danh")
            khoa_phong = st.text_input("Khoa / Phòng")
        with col_f3:
            trinh_do = st.text_input("Trình độ")
            sdt = st.text_input("Số điện thoại")
            email = st.text_input("Email")
            
        submitted = st.form_submit_button("💾 Lưu thông tin nhân sự", use_container_width=True)
        if submitted:
            if not ma_cb or not ho_ten:
                st.error("Vui lòng điền đầy đủ Mã Cán bộ và Họ và Tên!")
            else:
                try:
                    with engine.connect() as conn:
                        query_insert = text("""
                            INSERT INTO can_bo (ma_can_bo, ho_ten, ngay_sinh, so_cccd, chuc_danh, khoa_phong, trinh_do, so_dien_thoai, email)
                            VALUES (:ma_cb, :ho_ten, :ngay_sinh, :so_cccd, :chuc_danh, :khoa_phong, :trinh_do, :sdt, :email)
                        """)
                        conn.execute(query_insert, {
                            "ma_cb": ma_cb, "ho_ten": ho_ten, "ngay_sinh": str(ngay_sinh),
                            "so_cccd": so_cccd, "chuc_danh": chuc_danh, "khoa_phong": khoa_phong,
                            "trinh_do": trinh_do, "sdt": sdt, "email": email
                        })
                        conn.commit()
                    st.cache_data.clear()
                    st.success("Thêm mới cán bộ thành công!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Lỗi khi thêm dữ liệu: {e}")

# ==========================================
# TAB 3: THỐNG KÊ & BÁO CÁO
# ==========================================
with tab3:
    st.markdown("##### 📊 **Thống kê tổng quan nhân sự**")
    if df.empty:
        st.info("Chưa có dữ liệu để thống kê.")
    else:
        col_st1, col_st2 = st.columns(2)
        with col_st1:
            st.metric(label="Tổng số cán bộ nhân viên", value=len(df))
        with col_st2:
            if 'khoa_phong' in df.columns:
                st.metric(label="Tổng số Khoa / Phòng", value=df['khoa_phong'].nunique())
        
        if 'khoa_phong' in df.columns:
            st.markdown("##### 🏥 **Phân bổ nhân sự theo Khoa / Phòng**")
            khoa_counts = df['khoa_phong'].value_comst = df['khoa_phong'].value_counts().reset_index()
            khoa_counts.columns = ['Khoa / Phòng', 'Số lượng']
            st.dataframe(khoa_counts, use_container_width=True, hide_index=True)
