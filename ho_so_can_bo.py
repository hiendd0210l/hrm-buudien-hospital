import streamlit as st
import pandas as pd
from datetime import datetime, date
from sqlalchemy import text
import io

@st.cache_data(ttl=1)
def load_data_from_db(engine):
    if not engine:
        return pd.DataFrame()
    try:
        with engine.connect() as conn:
            query = text("SELECT id, ma_can_bo, ho_ten, ngay_sinh, so_cccd, chuc_danh, khoa_phong, trinh_do, so_dien_thoai, email FROM can_bo ORDER BY id DESC")
            return pd.read_sql(query, conn)
    except Exception as e:
        st.error(f"Lỗi đọc dữ liệu: {e}")
        return pd.DataFrame()

def render_quan_ly_can_bo(engine):
    st.markdown("---")
    st.subheader("📁 QUẢN LÝ CÁN BỘ CNV BỆNH VIỆN BƯU ĐIỆN")
    if not engine:
        st.error("Chưa kết nối được Cơ sở dữ liệu Neon.")
        return
        
    df = load_data_from_db(engine)
    st.success(f"📋 **Tổng số nhân sự hiện có trong CSDL:** **{len(df)}** cán bộ, nhân viên.")
    
    tab1, tab2, tab3 = st.tabs(["📋 Danh sách & Xóa", "➕ Thêm / ✏️ Sửa Nhân sự", "📤 Xuất Data Excel"])
    
    with tab1:
        if df.empty:
            st.info("Chưa có dữ liệu nhân sự trong CSDL.")
        else:
            st.dataframe(df, use_container_width=True, hide_index=True)

    with tab2:
        st.info("Form thêm mới và chỉnh sửa nhân sự...")

    with tab3:
        st.info("Chức năng xuất dữ liệu Excel...")
