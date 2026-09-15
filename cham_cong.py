import io
import calendar
import pandas as pd
import streamlit as st
from datetime import datetime, date
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

def generate_excel_mau_cham_cong(month: int, year: int, df_cb: pd.DataFrame) -> bytes:
    """Tạo file Excel mẫu Bảng chấm công đầy đủ các tab theo chuẩn cấu trúc thực tế"""
    wb = openpyxl.Workbook()
    
    # Font & Style
    font_title = Font(name="Times New Roman", size=14, bold=True, color="002060")
    font_subtitle = Font(name="Times New Roman", size=11, bold=True)
    font_header = Font(name="Times New Roman", size=10, bold=True)
    font_data = Font(name="Times New Roman", size=10)
    fill_header = PatternFill(start_color="D9E1F2", end_color="D9E1F2", fill_type="solid")
    
    thin_border = Border(
        left=Side(style='thin', color='D9D9D9'),
        right=Side(style='thin', color='D9D9D9'),
        top=Side(style='thin', color='D9D9D9'),
        bottom=Side(style='thin', color='D9D9D9')
    )
    
    num_days = calendar.monthrange(year, month)[1]

    # ---------------------------------------------------------------------
    # TAB 1: NHÂN VIÊN & TAB 2: HTCS
    # ---------------------------------------------------------------------
    sheets_config = [
        ("NHÂN VIÊN", f"BẢNG CHẤM CÔNG THÁNG {month:02d} NĂM {year} CỦA CBNV"),
        ("HTCS", f"BẢNG CHẤM CÔNG THÁNG {month:02d} NĂM {year} CỦA NHÂN VIÊN LAO ĐỘNG THUÊ LẠI")
    ]
    
    # Loại bỏ sheet mặc định ban đầu
    first_sheet = True
    
    for sheet_name, title_text in sheets_config:
        if first_sheet:
            ws = wb.active
            ws.title = sheet_name
            first_sheet = False
        else:
            ws = wb.create_sheet(title=sheet_name)
            
        # Tiêu đề
        ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=num_days + 3)
        cell_t = ws.cell(1, 1, title_text)
        cell_t.font = font_title
        cell_t.alignment = Alignment(horizontal="center", vertical="center")
        
        # Header cột
        ws.cell(3, 1, "STT").font = font_header
        ws.cell(3, 2, "Mã NV").font = font_header
        ws.cell(3, 3, "Họ và tên").font = font_header
        
        for d in range(1, num_days + 1):
            col_idx = 3 + d
            cell_d = ws.cell(3, col_idx, f"{d:02d}/{month:02d}")
            cell_d.font = font_header
            cell_d.alignment = Alignment(horizontal="center")
            cell_d.fill = fill_header

        ws.cell(3, num_days + 4, "Tổng công").font = font_header

        # Đổ danh sách nhân sự mẫu
        row_start = 4
        if not df_cb.empty:
            for idx, r in df_cb.iterrows():
                ws.cell(row_start, 1, idx + 1).alignment = Alignment(horizontal="center")
                ws.cell(row_start, 2, str(r.get('ma_can_bo', ''))).alignment = Alignment(horizontal="center")
                ws.cell(row_start, 3, str(r.get('ho_ten', '')))
                
                # Điền ký hiệu XX mặc định cho ngày làm việc
                for d in range(1, num_days + 1):
                    weekday = datetime(year, month, d).weekday()
                    val = "XX" if weekday < 5 else ""
                    c_day = ws.cell(row_start, 3 + d, val)
                    c_day.alignment = Alignment(horizontal="center")
                    c_day.font = font_data
                row_start += 1

    # ---------------------------------------------------------------------
    # TAB 3: LÀM THỨ 7
    # ---------------------------------------------------------------------
    ws_t7 = wb.create_sheet(title="LÀM THỨ 7")
    ws_t7.merge_cells("A1:H1")
    cell_t7 = ws_t7.cell(1, 1, f"BẢNG CHẤM CÔNG NGÀY LÀM THỨ 7, CHỦ NHẬT CỦA CBNV THÁNG {month:02d}/{year}")
    cell_t7.font = font_title
    cell_t7.alignment = Alignment(horizontal="center")

    headers_t7 = ["STT", "Mã NV", "Họ và tên", "Khoa / Phòng", "Ngày làm 1", "Ngày làm 2", "Ngày làm 3", "Tổng ngày"]
    for col_i, h in enumerate(headers_t7, 1):
        c = ws_t7.cell(3, col_i, h)
        c.font = font_header
        c.fill = fill_header

    # ---------------------------------------------------------------------
    # TAB 4: ABC (BÌNH BẦU XẾP LOẠI)
    # ---------------------------------------------------------------------
    ws_abc = wb.create_sheet(title="ABC")
    ws_abc.cell(1, 1, "BỆNH VIỆN BƯU ĐIỆN").font = font_subtitle
    ws_abc.merge_cells("A3:J3")
    c_abc = ws_abc.cell(3, 1, f"BẢNG BÌNH BẦU XẾP LOẠI LAO ĐỘNG THÁNG {month:02d}/{year}")
    c_abc.font = font_title
    c_abc.alignment = Alignment(horizontal="center")

    headers_abc = ["STT", "Mã NV", "HỌ VÀ TÊN", "CHỨC VỤ", "ĐI LÀM", "TRỰC", "NGHỈ BÙ", "NGHỈ KHÁC", "XẾP LOẠI", "TỒN BÙ"]
    for col_i, h in enumerate(headers_abc, 1):
        c = ws_abc.cell(5, col_i, h)
        c.font = font_header
        c.fill = fill_header

    # ---------------------------------------------------------------------
    # TAB 5: KÝ HIỆU
    # ---------------------------------------------------------------------
    ws_kh = wb.create_sheet(title="Ký hiệu")
    ws_kh.cell(1, 1, "BẢNG GIẢI THÍCH KÝ HIỆU CHẤM CÔNG").font = font_title
    
    ky_hieu_data = [
        ("X", "Công đi làm 1/2 ngày trong giờ hành chính"),
        ("XX", "Công đi làm 1 ngày trong giờ hành chính"),
        ("T", "Trực ngoài giờ ngày thường hoặc trực 24/24 giờ ngày Thứ Bảy, Chủ Nhật, Lễ, Tết"),
        ("C", "Đi công tác 1/2 ngày"),
        ("CC", "Đi công tác 1 ngày"),
        ("B", "Nghỉ bù trực, bù ngày làm Thứ Bảy, Chủ Nhật, Lễ Tết 1/2 ngày"),
        ("BB", "Nghỉ bù trực, bù ngày làm Thứ Bảy, Chủ Nhật, Lễ Tết 1 ngày"),
        ("P", "Nghỉ phép 1/2 ngày"),
        ("PP", "Nghỉ phép 1 ngày"),
        ("TS", "Nghỉ thai sản"),
        ("Ô", "Nghỉ ốm 1/2 ngày"),
        ("ÔÔ", "Nghỉ ốm 1 ngày"),
        ("Cô", "Nghỉ con ốm")
    ]
    
    ws_kh.cell(3, 1, "Ký hiệu").font = font_header
    ws_kh.cell(3, 2, "Diễn giải ý nghĩa").font = font_header
    
    for r_idx, (kh, val) in enumerate(ky_hieu_data, start=4):
        c_kh = ws_kh.cell(r_idx, 1, kh)
        c_val = ws_kh.cell(r_idx, 2, val)
        c_kh.font = font_header
        c_kh.alignment = Alignment(horizontal="center")
        c_val.font = font_data

    # Tự động chỉnh độ rộng cột
    for ws_curr in wb.worksheets:
        for col in ws_curr.columns:
            max_len = max(len(str(cell.value or '')) for cell in col)
            col_letter = get_column_letter(col[0].column)
            ws_curr.column_dimensions[col_letter].width = max(max_len + 3, 10)

    output = io.BytesIO()
    wb.save(output)
    return output.getvalue()


def init_cham_cong_session():
    """Khởi tạo session state riêng cho mô-đun chấm công nếu chưa có"""
    if 'don_nghi_phep' not in st.session_state:
        st.session_state['don_nghi_phep'] = pd.DataFrame([
            {"id": 1, "ma_can_bo": "N1971", "ho_ten": "Khuất Duy Tiến", "khoa_phong": "Khoa Ngoại tổng hợp", "loai_nghi": "Nghỉ phép năm", "tu_ngay": "2026-09-10", "den_ngay": "2026-09-12", "so_ngay": 3, "ly_do": "Giải quyết việc gia đình", "trang_thai": "Đã phê duyệt"},
            {"id": 2, "ma_can_bo": "N2088", "ho_ten": "Nguyễn Văn An", "khoa_phong": "Khoa Khám bệnh", "loai_nghi": "Nghỉ bù trực", "tu_ngay": "2026-09-15", "den_ngay": "2026-09-15", "so_ngay": 1, "ly_do": "Nghỉ bù sau ca trực đêm 14/09", "trang_thai": "Chờ phê duyệt"}
        ])


def render_quan_ly_cham_cong(df_cb):
    """Hàm chính hiển thị giao diện Quản lý Chấm công & Ngày nghỉ."""
    init_cham_cong_session()
    
    st.markdown("---")
    st.subheader("⏰ QUẢN LÝ CHẤM CÔNG & NGÀY NGHỈ - BỆNH VIỆN BƯU ĐIỆN")
    
    tab_cc1, tab_cc2, tab_cc3, tab_cc4 = st.tabs([
        "📊 Bảng Tổng hợp Chấm công", 
        "📝 Đăng ký Nghỉ phép / Nghỉ bù", 
        "✅ Duyệt Đơn nghỉ phép", 
        "📥 Tải File Mẫu & Import Excel"
    ])
    
    # TAB 1: BẢNG TỔNG HỢP CHẤM CÔNG
    with tab_cc1:
        st.markdown("##### 📅 **Bảng tổng hợp công lao động & Ngày nghỉ trong tháng**")
        col_m1, col_m2, _ = st.columns([1.5, 1.5, 2])
        month_sel = col_m1.selectbox("Chọn tháng:", [f"Tháng {i:02d}/2026" for i in range(1, 13)], index=7)
        
        dept_options = ["-- Tất cả Khoa / Phòng --"]
        if not df_cb.empty and 'khoa_phong' in df_cb.columns:
            dept_options += list(df_cb['khoa_phong'].dropna().unique())
        dept_filter = col_m2.selectbox("Lọc theo Khoa / Phòng:", dept_options)
        
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
                "Nghỉ phép năm", "Nghỉ bù trực", "Nghỉ ốm / BHXH", "Nghỉ thai sản", "Nghỉ việc riêng"
            ])
            tu_ngay = col_dk2.date_input("Từ ngày (*):", value=date.today())
            den_ngay = col_dk2.date_input("Đến ngày (*):", value=date.today())
            ly_do_nghi = st.text_area("Lý do xin nghỉ (*):", placeholder="Nhập lý do xin nghỉ...")
            
            submit_don = st.form_submit_button("🚀 Gửi Đơn Đăng Ký Nghỉ", use_container_width=True)
            if submit_don:
                if selected_cb_nghi == "-- Chọn cán bộ nghỉ --" or not ly_do_nghi.strip():
                    st.error("⚠️ Vui lòng điền đầy đủ thông tin bắt buộc!")
                else:
                    st.success("🎉 Gửi đơn thành công!")

    # TAB 3: DUYỆT ĐƠN NGHỈ PHÉP
    with tab_cc3:
        st.markdown("##### ✅ **Danh sách Đơn xin nghỉ phép chờ phê duyệt**")
        st.dataframe(st.session_state['don_nghi_phep'], use_container_width=True, hide_index=True)

    # TAB 4: IMPORT & TẠO FILE MẪU EXCEL
    with tab_cc4:
        st.markdown("##### 📄 **1. Tự động tạo File Excel mẫu Bảng Chấm Công theo tháng**")
        st.caption("Xuất file mẫu chuẩn gồm các Sheet: **NHÂN VIÊN**, **HTCS**, **LÀM THỨ 7**, **ABC** và **Ký hiệu** để gửi các Khoa/Phòng.")
        
        c_m1, c_m2, c_m3 = st.columns([1, 1, 2])
        sel_month = c_m1.selectbox("Chọn tháng xuất mẫu:", list(range(1, 13)), index=datetime.now().month - 1)
        sel_year = c_m2.number_input("Chọn năm:", min_value=2024, max_value=2030, value=2026)
        
        excel_bytes = generate_excel_mau_cham_cong(sel_month, sel_year, df_cb)
        
        c_m3.markdown("<br>", unsafe_allow_html=True)
        c_m3.download_button(
            label=f"📥 Tải File Excel Mẫu Chấm Công Tháng {sel_month:02d}/{sel_year}",
            data=excel_bytes,
            file_name=f"Mau_Bang_Cham_Cong_Thang_{sel_month:02d}_{sel_year}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )

        st.markdown("---")
        st.markdown("##### 📥 **2. Tải lên Bảng Chấm Công từ các Đơn vị**")
        file_cc = st.file_uploader("Tải file chấm công đã điền (.xlsx, .csv):", type=["xlsx", "xls", "csv"], key="file_uploader_cc")
        if file_cc is not None:
            st.success("File chấm công đã được tải lên thành công. Hệ thống đã sẵn sàng đối soát và tổng hợp dữ liệu!")
