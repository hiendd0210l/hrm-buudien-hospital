import streamlit as st
from streamlit_option_menu import option_menu
import pandas as pd

# 1. Cấu hình trang chuẩn phong cách Bệnh viện Bưu điện
st.set_page_config(
    page_title="HRM - Bệnh viện Bưu điện",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Thanh điều hướng Sidebar chuẩn Phụ lục 01 & 02
with st.sidebar:
    st.title("🏥 HRM BƯU ĐIỆN")
    st.caption("Hệ thống Quản trị Nhân sự Y tế 4.0")
    
    selected_menu = option_menu(
        menu_title=None,
        options=[
            "Dashboard & Cảnh báo", 
            "Hồ sơ Cán bộ", 
            "Chấm công & Phê duyệt", 
            "Quản lý Sức khỏe", 
            "Báo cáo & Thống kê", 
            "Nguồn lực Y tế",
            "Ứng dụng Mobile / PWA"
        ],
        icons=["speedometer2", "person-badge", "calendar-check", "heart-pulse", "bar-chart-line", "hospital", "phone"],
        default_index=0
    )

# 3. Phân hệ Dashboard & Cảnh báo Tự động
if selected_menu == "Dashboard & Cảnh báo":
    st.title("🏥 TỔNG QUAN NHÂN SỰ BỆNH VIỆN BƯU ĐIỆN")
    st.markdown("---")
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Tổng cán bộ, NVYT", "1,500", "+12 tháng này")
    col2.metric("Bác sĩ / Dược sĩ", "450", "30% Tổng số")
    col3.metric("Cảnh báo nâng lương", "28 Cán bộ", "Cần xử lý", delta_color="inverse")
    col4.metric("Sắp đến tuổi nghỉ hưu", "5 Cán bộ", "Trong 6 tháng", delta_color="off")
    
    st.subheader("⚠️ Cảnh báo Hệ thống Tự động (Phụ lục 02 - Mục II)")
    st.warning("🔔 Có **8 cán bộ** quá hạn giữ chức vụ bổ nhiệm & **12 cán bộ** sắp hết hạn Hợp đồng lao động!")
    
    df_alert = pd.DataFrame({
        "Mã CB": ["CB001", "CB045", "CB112", "CB890"],
        "Họ và Tên": ["BS. Nguyễn Văn A", "ThS. Trần Thị B", "CN. Lê Văn C", "BSCKII. Phạm Hoàng D"],
        "Khoa / Phòng": ["Khoa Cấp Cứu", "Khoa Dược", "Phòng TCKT", "Khoa Ngoại Tổng Hợp"],
        "Loại Cảnh báo": ["Quá hạn nâng lương", "Sắp hết hạn HĐLD", "Sắp nghỉ hưu", "Quá hạn bổ nhiệm"],
        "Hạn xử lý": ["15/09/2026", "20/09/2026", "01/10/2026", "05/10/2026"]
    })
    st.dataframe(df_alert, use_container_width=True)

# 4. Phân hệ Quản lý Hồ sơ & In Mẫu SYLL
elif selected_menu == "Hồ sơ Cán bộ":
    st.title("📋 QUẢN LÝ HỒ SƠ CÁN BỘ (1,500 NHÂN SỰ)")
    
    tab1, tab2, tab3 = st.tabs(["Danh sách & Tra cứu", "Thêm mới / Cập nhật", "In mẫu SYLL & Kê khai"])
    
    with tab1:
        st.text_input("🔍 Tìm kiếm theo Tên, Mã cán bộ, Số CCCD hoặc Khoa phòng...")
        df_cb = pd.DataFrame({
            "Mã CB": ["BV001", "BV002", "BV003"],
            "Họ Tên": ["Nguyễn Văn An", "Trần Thị Bình", "Lê Hoàng Cường"],
            "Chức vụ": ["Trưởng khoa Cấp cứu", "Phó Trưởng khoa Dược", "Điều dưỡng trưởng"],
            "Trình độ": ["Bác sĩ CKII", "Thạc sĩ Dược", "Cử nhân Điều dưỡng"],
            "Trạng thái": ["Chính thức", "Chính thức", "Hợp đồng"]
        })
        st.dataframe(df_cb, use_container_width=True)
        
    with tab3:
        st.subheader("📄 In Mẫu Sơ Yếu Lý Lịch Chuẩn Quy Định")
        col_a, col_b = st.columns(2)
        with col_a:
            cb_select = st.selectbox("Chọn Cán bộ xuất hồ sơ:", ["BV001 - Nguyễn Văn An", "BV002 - Trần Thị Bình"])
            mau_in = st.selectbox("Chọn Mẫu biểu cần in:", [
                "Mẫu BNV (Bộ Nội vụ)", 
                "Mẫu HS-02 (Viên chức)", 
                "Mẫu TCTW-98 (Đảng viên)", 
                "Mẫu SYLL Hợp nhất Bệnh viện",
                "Kê khai tài sản (NĐ 130/2020/NĐ-CP)"
            ])
        with col_b:
            st.write(" ")
            if st.button("📥 Xuất File Word (.docx) theo Form"):
                st.success(f"Đã tạo thành công {mau_in} cho {cb_select}!")
