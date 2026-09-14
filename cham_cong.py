import streamlit as st
import pandas as pd
import datetime

def render_cham_cong(engine):
    st.title("⏰ Quản lý Chấm công & Ngày nghỉ - Lịch trực")
    
    # Tạo các Tab chức năng
    tab1, tab2, tab3 = st.tabs([
        "📅 Bảng Chấm công Tổng hợp", 
        "📝 Đăng ký Nghỉ phép / Lịch trực", 
        "📊 Thống kê Quỹ phép & Trực ca"
    ])
    
    # --- TAB 1: BẢNG CHẤM CÔNG TỔNG HỢP ---
    with tab1:
        st.subheader("Bảng theo dõi chấm công tháng")
        
        col_filters1, col_filters2, col_filters3 = st.columns([1, 1, 1])
        with col_filters1:
            thang = st.selectbox("Chọn Tháng:", range(1, 13), index=datetime.datetime.now().month - 1)
        with col_filters2:
            nam = st.selectbox("Chọn Năm:", [2025, 2026, 2027], index=1)
        with col_filters3:
            khoa_phong = st.selectbox("Khoa / Phòng:", ["Tất cả Khoa/Phòng", "Khoa Ngoại TH", "Khoa GMHS", "Khoa CĐHA", "Phòng TCCB"])

        # Dữ liệu mẫu chấm công
        df_chamcong = pd.DataFrame([
            {"Mã NV": "NV001", "Họ và tên": "BS. Nguyễn Văn An", "Khoa/Phòng": "Khoa Ngoại TH", "Công chuẩn": 22, "Công thực tế": 22, "Nghỉ phép (P)": 0, "Nghỉ ốm (Ô)": 0, "Trực đêm (T)": 4, "Tăng giờ (OT)": "8h"},
            {"Mã NV": "NV002", "Họ và tên": "ĐĐ. Lê Thị Bích", "Khoa/Phòng": "Khoa GMHS", "Công chuẩn": 22, "Công thực tế": 20, "Nghỉ phép (P)": 2, "Nghỉ ốm (Ô)": 0, "Trực đêm (T)": 6, "Tăng giờ (OT)": "0h"},
            {"Mã NV": "NV003", "Họ và tên": "KTV. Phạm Quốc Cường", "Khoa/Phòng": "Khoa CĐHA", "Công chuẩn": 22, "Công thực tế": 21, "Nghỉ phép (P)": 0, "Nghỉ ốm (Ô)": 1, "Trực đêm (T)": 3, "Tăng giờ (OT)": "4h"},
            {"Mã NV": "NV004", "Họ và tên": "ThS. Đoàn Danh Hiển", "Khoa/Phòng": "Phòng TCCB", "Công chuẩn": 22, "Công thực tế": 22, "Nghỉ phép (P)": 0, "Nghỉ ốm (Ô)": 0, "Trực đêm (T)": 0, "Tăng giờ (OT)": "12h"}
        ])

        if khoa_phong != "Tất cả Khoa/Phòng":
            df_chamcong = df_chamcong[df_chamcong["Khoa/Phòng"] == khoa_phong]

        st.dataframe(df_chamcong, use_container_width=True, hide_index=True)
        
        c1, c2 = st.columns([1, 4])
        with c1:
            st.button("📥 Xuất Bảng công (Excel)", use_container_width=True)

    # --- TAB 2: ĐĂNG KÝ NGHỈ PHÉP / LỊCH TRỰC ---
    with tab2:
        st.subheader("Tạo đơn đăng ký / Phê duyệt nghỉ phép")
        
        col_form1, col_form2 = st.columns(2)
        with col_form1:
            with st.form("form_nghi_phep"):
                st.markdown("<b>TẠO ĐƠN ĐĂNG KÝ NGHỈ PHÉP / TRỰC BÙ</b>", unsafe_allow_html=True)
                nv_select = st.text_input("Nhập Mã nhân viên hoặc Họ tên:", value="Đoàn Danh Hiển")
                loai_nghi = st.selectbox("Loại hình nghỉ:", ["Nghỉ phép năm (P)", "Nghỉ việc riêng có lương (VR)", "Nghỉ không lương (KL)", "Nghỉ ốm/Chế độ BHXH (Ô)", "Trực đổi ca/Trực bù"])
                
                d1, d2 = st.columns(2)
                with d1:
                    tu_ngay = st.date_input("Từ ngày:", datetime.date.today())
                with d2:
                    den_ngay = st.date_input("Đến ngày:", datetime.date.today())
                    
                ly_do = st.text_area("Lý do nghỉ / Ghi chú:", placeholder="Nhập chi tiết lý do...")
                
                btn_submit = st.form_submit_button("📩 Gửi đơn phê duyệt", use_container_width=True)
                if btn_submit:
                    st.success("Đã gửi đơn đăng ký nghỉ phép thành công! Đang chờ Trưởng khoa/Phòng duyệt.")

        with col_form2:
            st.markdown("<b>DANH SÁCH ĐƠN CHỜ PHÊ DUYỆT</b>", unsafe_allow_html=True)
            df_don = pd.DataFrame([
                {"Nhân viên": "BS. Nguyễn Văn An", "Loại nghỉ": "Nghỉ phép năm", "Số ngày": 2, "Từ ngày": "15/09/2026", "Trạng thái": "⏳ Chờ Trưởng khoa duyệt"},
                {"Nhân viên": "ĐĐ. Lê Thị Bích", "Loại nghỉ": "Nghỉ ốm (BHXH)", "Số ngày": 1, "Từ ngày": "12/09/2026", "Trạng thái": "✅ Đã duyệt"}
            ])
            st.dataframe(df_don, use_container_width=True, hide_index=True)

    # --- TAB 3: THỐNG KÊ QUỸ PHÉP & TRỰC CA ---
    with tab3:
        st.subheader("Theo dõi Quỹ phép năm & Định mức Trực ca")
        
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Tổng Quỹ phép năm", "12 ngày", "1 ngày/tháng")
        m2.metric("Đã sử dụng", "4 ngày", "Còn lại 8 ngày")
        m3.metric("Tổng ca trực đêm/Tháng", "185 ca", "Toàn bệnh viện")
        m4.metric("Giờ tăng ca (OT) T9/2026", "320 giờ", "+12% so với T8")

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("<b>Chi tiết Quỹ phép còn lại của Nhân sự:</b>", unsafe_allow_html=True)
        
        df_quyphep = pd.DataFrame([
            {"Mã NV": "NV001", "Họ tên": "BS. Nguyễn Văn An", "Phép chuẩn/Năm": 14, "Đã nghỉ": 3, "Còn lại": 11},
            {"Mã NV": "NV002", "Họ tên": "ĐĐ. Lê Thị Bích", "Phép chuẩn/Năm": 12, "Đã nghỉ": 5, "Còn lại": 7},
            {"Mã NV": "NV003", "Họ tên": "KTV. Phạm Quốc Cường", "Phép chuẩn/Năm": 12, "Đã nghỉ": 2, "Còn lại": 10},
            {"Mã NV": "NV004", "Họ tên": "ThS. Đoàn Danh Hiển", "Phép chuẩn/Năm": 16, "Đã nghỉ": 4, "Còn lại": 12}
        ])
        st.dataframe(df_quyphep, use_container_width=True, hide_index=True)
