import io
import pandas as pd
import streamlit as st
from datetime import datetime, date

def init_cham_cong_session():
    """Khởi tạo session state riêng cho mô-đun chấm công nếu chưa có"""
    if 'don_nghi_phep' not in st.session_state:
        st.session_state['don_nghi_phep'] = pd.DataFrame([
            {"id": 1, "ma_can_bo": "N1971", "ho_ten": "Khuất Duy Tiến", "khoa_phong": "Khoa Ngoại tổng hợp", "loai_nghi": "Nghỉ phép năm", "tu_ngay": "2026-09-10", "den_ngay": "2026-09-12", "so_ngay": 3, "ly_do": "Giải quyết việc gia đình", "trang_thai": "Đã phê duyệt"},
            {"id": 2, "ma_can_bo": "N2088", "ho_ten": "Nguyễn Văn An", "khoa_phong": "Khoa Khám bệnh", "loai_nghi": "Nghỉ bù trực", "tu_ngay": "2026-09-15", "den_ngay": "2026-09-15", "so_ngay": 1, "ly_do": "Nghỉ bù sau ca trực đêm 14/09", "trang_thai": "Chờ phê duyệt"},
            {"id": 3, "ma_can_bo": "N3012", "ho_ten": "Trần Thị Bích", "khoa_phong": "Phòng Kế hoạch Tổng hợp", "loai_nghi": "Nghỉ ốm / BHXH", "tu_ngay": "2026-09-14", "den_ngay": "2026-09-16", "so_ngay": 3, "ly_do": "Điều trị ngoại trú theo chỉ định Bác sĩ", "trang_thai": "Chờ phê duyệt"}
        ])

def render_quan_ly_cham_cong(df_cb):
    """
    Hàm chính hiển thị giao diện Quản lý Chấm công & Ngày nghỉ.
    nhận tham số df_cb (Danh sách cán bộ từ database ở app.py)
    """
    init_cham_cong_session()
    
    st.markdown("---")
    st.subheader("⏰ QUẢN LÝ CHẤM CÔNG & NGÀY NGHỈ - BỆNH VIỆN BƯU ĐIỆN")
    
    tab_cc1, tab_cc2, tab_cc3, tab_cc4 = st.tabs([
        "📊 Bảng Tổng hợp Chấm công", 
        "📝 Đăng ký Nghỉ phép / Nghỉ bù", 
        "✅ Duyệt Đơn nghỉ phép", 
        "📥 Import Bảng chấm công Excel"
    ])
    
    # TAB 1: BẢNG TỔNG HỢP CHẤM CÔNG
    with tab_cc1:
        st.markdown("##### 📅 **Bảng tổng hợp công lao động & Ngày nghỉ trong tháng**")
        col_m1, col_m2, col_m3 = st.columns([1.5, 1.5, 2])
        month_sel = col_m1.selectbox("Chọn tháng:", [f"Tháng {i:02d}/2026" for i in range(1, 13)], index=8)
        
        dept_options = ["-- Tất cả Khoa / Phòng --"]
        if not df_cb.empty and 'khoa_phong' in df_cb.columns:
            dept_options += list(df_cb['khoa_phong'].dropna().unique())
        dept_filter = col_m2.selectbox("Lọc theo Khoa / Phòng:", dept_options)
        
        # Tạo dữ liệu giả lập bảng công từ danh sách cán bộ
        data_cc = []
        if not df_cb.empty:
            for idx, r in df_cb.iterrows():
                data_cc.append({
                    "Mã Cán bộ": r.get('ma_can_bo', 'N/A'),
                    "Họ và Tên": r.get('ho_ten', 'N/A'),
                    "Khoa / Phòng": r.get('khoa_phong', 'N/A'),
                    "Công chuẩn": 22,
                    "Công thực tế": 21,
                    "Công trực 24h": 3,
                    "Phép năm": 1,
                    "Nghỉ BHXH/Ốm": 0,
                    "Tăng giờ (giờ)": 12.5,
                    "Ghi chú": "Đủ công"
                })
            df_cc = pd.DataFrame(data_cc)
            if dept_filter != "-- Tất cả Khoa / Phòng --":
                df_cc = df_cc[df_cc['Khoa / Phòng'] == dept_filter]
            st.dataframe(df_cc, use_container_width=True, hide_index=True)
        else:
            st.info("Chưa có danh sách nhân sự để tổng hợp chấm công.")

    # TAB 2: ĐĂNG KÝ NGHỈ PHÉP
    with tab_cc2:
        st.markdown("##### 📝 **Tạo đơn đăng ký nghỉ phép / nghỉ bù / nghỉ BHXH**")
        with st.form("form_dang_ky_nghi"):
            col_dk1, col_dk2 = st.columns(2)
            
            options_cb = ["-- Chọn cán bộ nghỉ --"]
            if not df_cb.empty:
                for _, r in df_cb.iterrows():
                    options_cb.append(f"{r['ma_can_bo']} - {r['ho_ten']} ({r['khoa_phong']})")
                    
            selected_cb_nghi = col_dk1.selectbox("Cán bộ đăng ký (*):", options_cb)
            loai_nghi = col_dk1.selectbox("Loại hình nghỉ (*):", [
                "Nghỉ phép năm", "Nghỉ bù trực", "Nghỉ ốm / BHXH", 
                "Nghỉ thai sản", "Nghỉ việc riêng (Kết hôn, hiếu, hỷ)", "Nghỉ không hưởng lương"
            ])
            
            tu_ngay = col_dk2.date_input("Từ ngày (*):", value=date.today())
            den_ngay = col_dk2.date_input("Đến ngày (*):", value=date.today())
            ly_do_nghi = st.text_area("Lý do xin nghỉ (*):", placeholder="Ghi rõ lý do và người bàn giao công việc...")
            
            submit_don = st.form_submit_button("🚀 Gửi Đơn Đăng Ký Nghỉ", use_container_width=True)
            if submit_don:
                if selected_cb_nghi == "-- Chọn cán bộ nghỉ --" or not ly_do_nghi.strip():
                    st.error("⚠️ Vui lòng chọn Cán bộ và điền đầy đủ lý do xin nghỉ!")
                elif tu_ngay > den_ngay:
                    st.error("⚠️ Ngày bắt đầu không thể lớn hơn ngày kết thúc!")
                else:
                    try:
                        parts = selected_cb_nghi.split(" - ")
                        mcb = parts[0]
                        rest = parts[1].split(" (")
                        hoten = rest[0]
                        khoa = rest[1].replace(")", "")
                        
                        so_ngay = (den_ngay - tu_ngay).days + 1
                        
                        new_id = len(st.session_state['don_nghi_phep']) + 1
                        new_don = {
                            "id": new_id,
                            "ma_can_bo": mcb,
                            "ho_ten": hoten,
                            "khoa_phong": khoa,
                            "loai_nghi": loai_nghi,
                            "tu_ngay": tu_ngay.strftime('%Y-%m-%d'),
                            "den_ngay": den_ngay.strftime('%Y-%m-%d'),
                            "so_ngay": so_ngay,
                            "ly_do": ly_do_nghi,
                            "trang_thai": "Chờ phê duyệt"
                        }
                        st.session_state['don_nghi_phep'] = pd.concat([
                            st.session_state['don_nghi_phep'], 
                            pd.DataFrame([new_don])
                        ], ignore_index=True)
                        st.success("🎉 Đơn xin nghỉ đã được gửi thành công! Đang chờ Lãnh đạo phê duyệt.")
                    except Exception as e:
                        st.error(f"Lỗi khi lưu đơn nghỉ: {e}")

    # TAB 3: DUYỆT ĐƠN NGHỈ PHÉP
    with tab_cc3:
        st.markdown("##### ✅ **Danh sách Đơn xin nghỉ phép chờ phê duyệt**")
        df_don = st.session_state['don_nghi_phep']
        
        if df_don.empty:
            st.info("Hiện không có đơn xin nghỉ nào.")
        else:
            st.dataframe(df_don, use_container_width=True, hide_index=True)
            st.markdown("---")
            st.markdown("##### ⚙️ **Thao tác Phê duyệt**")
            
            df_cho = df_don[df_don['trang_thai'] == 'Chờ phê duyệt']
            if df_cho.empty:
                st.success("✨ Tất cả các đơn đăng ký đã được xử lý xong!")
            else:
                list_cho = [f"Đơn #{r['id']} - {r['ho_ten']} ({r['loai_nghi']}: {r['tu_ngay']} đến {r['den_ngay']})" for _, r in df_cho.iterrows()]
                selected_don_approve = st.selectbox("Chọn đơn cần xử lý:", list_cho)
                
                target_don_id = int(selected_don_approve.split(" - ")[0].replace("Đơn #", ""))
                
                col_ap1, col_ap2 = st.columns(2)
                if col_ap1.button("✅ Phê Duyệt Đơn", use_container_width=True):
                    st.session_state['don_nghi_phep'].loc[st.session_state['don_nghi_phep']['id'] == target_don_id, 'trang_thai'] = 'Đã phê duyệt'
                    st.toast("✅ Đã phê duyệt đơn thành công!")
                    st.rerun()
                if col_ap2.button("❌ Từ Chối Đơn", use_container_width=True):
                    st.session_state['don_nghi_phep'].loc[st.session_state['don_nghi_phep']['id'] == target_don_id, 'trang_thai'] = 'Từ chối'
                    st.toast("❌ Đã từ chối đơn!")
                    st.rerun()

    # TAB 4: IMPORT BẢNG CHẤM CÔNG EXCEL
    with tab_cc4:
        st.markdown("##### 📥 **Nhập file dữ liệu chấm công từ máy chấm công vân tay / khuôn mặt**")
        file_cc = st.file_uploader("Tải file chấm công (.xlsx, .csv):", type=["xlsx", "xls", "csv"], key="file_uploader_cc")
        if file_cc is not None:
            st.success("File đã tải lên thành công. Hệ thống đang sẵn sàng xử lý dữ liệu chấm công tự động!")
