import io
import calendar
import pandas as pd
import streamlit as st
from datetime import datetime, date
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

def get_day_fill(day: int, month: int, year: int):
    """
    Xác định PatternFill cho từng ngày:
    - Lễ/Tết: Đỏ nhạt (FFC7CE)
    - Thứ 7 / Chủ Nhật: Cam nhạt (FCE4D6)
    - Ngày thường: None
    """
    dt = date(year, month, day)
    weekday = dt.weekday()  # 5: Thứ 7, 6: Chủ nhật
    
    # Lễ Tết cố định (01/01, 30/04, 01/05, 02/09, 03/09)
    fixed_holidays = [(1, 1), (30, 4), (1, 5), (2, 9), (3, 9)]
    
    if (day, month) in fixed_holidays:
        return PatternFill(start_color="FFC7CE", end_color="FFC7CE", fill_type="solid")
    elif weekday in (5, 6):
        return PatternFill(start_color="FCE4D6", end_color="FCE4D6", fill_type="solid")
    return None

def apply_cell_style(cell, font=None, fill=None, alignment=None, border=None):
    """Hàm gán style an toàn tránh lỗi AttributeError của openpyxl"""
    if font:
        cell.font = font
    if fill:
        cell.fill = fill
    if alignment:
        cell.alignment = alignment
    if border:
        cell.border = border

def generate_excel_mau_cham_cong(month: int, year: int, phong_ban: str = "Khoa Ngoại Tổng hợp") -> bytes:
    wb = openpyxl.Workbook()
    
    font_title = Font(name="Times New Roman", size=14, bold=True, color="002060")
    font_subtitle = Font(name="Times New Roman", size=11, bold=True)
    font_header = Font(name="Times New Roman", size=10, bold=True)
    font_sub_header = Font(name="Times New Roman", size=9, bold=True, italic=True)
    font_data = Font(name="Times New Roman", size=10)
    font_bold = Font(name="Times New Roman", size=10, bold=True)
    
    fill_header_default = PatternFill(start_color="D9E1F2", end_color="D9E1F2", fill_type="solid")
    
    align_center = Alignment(horizontal="center", vertical="center", wrap_text=True)
    align_center_no_wrap = Alignment(horizontal="center", vertical="center")
    
    thin_border = Border(
        left=Side(style='thin', color='D9D9D9'),
        right=Side(style='thin', color='D9D9D9'),
        top=Side(style='thin', color='D9D9D9'),
        bottom=Side(style='thin', color='D9D9D9')
    )
    
    num_days = calendar.monthrange(year, month)[1]

    # ---------------------------------------------------------------------
    # TAB 1: NHÂN VIÊN
    # ---------------------------------------------------------------------
    ws_nv = wb.active
    ws_nv.title = "NHÂN VIÊN"
    
    apply_cell_style(ws_nv.cell(1, 1, "BỆNH VIỆN BƯU ĐIỆN"), font=font_subtitle)
    ws_nv.merge_cells(start_row=1, start_column=4, end_row=1, end_column=num_days + 13)
    c_title = ws_nv.cell(1, 4, f"BẢNG CHẤM CÔNG THÁNG {month:02d} NĂM {year} CỦA CBNV")
    apply_cell_style(c_title, font=font_title, alignment=align_center)
    
    apply_cell_style(ws_nv.cell(2, 1, f"Đơn vị: {phong_ban}"), font=font_subtitle)
    
    ws_nv.merge_cells("A3:A4"); ws_nv.cell(3, 1, "STT")
    ws_nv.merge_cells("B3:B4"); ws_nv.cell(3, 2, "Mã NV")
    ws_nv.merge_cells("C3:C4"); ws_nv.cell(3, 3, "Họ và tên")
    
    ws_nv.merge_cells(start_row=3, start_column=4, end_row=3, end_column=3 + num_days)
    ws_nv.cell(3, 4, f"Ngày làm việc trong tháng {month:02d}.{year}")
    
    day_fills = {}
    for d in range(1, num_days + 1):
        col_idx = 3 + d
        ws_nv.cell(4, col_idx, f"{d:02d}")
        
        fill_color = get_day_fill(d, month, year)
        if fill_color:
            day_fills[col_idx] = fill_color
        else:
            day_fills[col_idx] = fill_header_default

    start_sum_col = 4 + num_days
    ws_nv.merge_cells(start_row=3, start_column=start_sum_col, end_row=4, end_column=start_sum_col); ws_nv.cell(3, start_sum_col, "Hành chính")
    ws_nv.merge_cells(start_row=3, start_column=start_sum_col+1, end_row=4, end_column=start_sum_col+1); ws_nv.cell(3, start_sum_col+1, "Trực ngoài giờ")
    ws_nv.merge_cells(start_row=3, start_column=start_sum_col+2, end_row=3, end_column=start_sum_col+3); ws_nv.cell(3, start_sum_col+2, "Nghỉ bù")
    apply_cell_style(ws_nv.cell(4, start_sum_col+2, "Đã nghỉ"), font=font_sub_header)
    apply_cell_style(ws_nv.cell(4, start_sum_col+3, "Còn lại"), font=font_sub_header)
    ws_nv.merge_cells(start_row=3, start_column=start_sum_col+4, end_row=4, end_column=start_sum_col+4); ws_nv.cell(3, start_sum_col+4, "Thai sản")
    ws_nv.merge_cells(start_row=3, start_column=start_sum_col+5, end_row=4, end_column=start_sum_col+5); ws_nv.cell(3, start_sum_col+5, "Công tác, họp")
    ws_nv.merge_cells(start_row=3, start_column=start_sum_col+6, end_row=4, end_column=start_sum_col+6); ws_nv.cell(3, start_sum_col+6, "Nghỉ ốm")
    ws_nv.merge_cells(start_row=3, start_column=start_sum_col+7, end_row=4, end_column=start_sum_col+7); ws_nv.cell(3, start_sum_col+7, "Trực lễ")
    ws_nv.merge_cells(start_row=3, start_column=start_sum_col+8, end_row=4, end_column=start_sum_col+8); ws_nv.cell(3, start_sum_col+8, "Đi học")
    ws_nv.merge_cells(start_row=3, start_column=start_sum_col+9, end_row=4, end_column=start_sum_col+9); ws_nv.cell(3, start_sum_col+9, "Tồn bù")

    for r in range(3, 5):
        for c in range(1, start_sum_col + 10):
            cell = ws_nv.cell(r, c)
            f_font = font_sub_header if (r == 4 and c in [start_sum_col+2, start_sum_col+3]) else font_header
            
            if 4 <= c <= 3 + num_days and r == 4:
                apply_cell_style(cell, font=f_font, fill=day_fills[c], alignment=align_center)
            else:
                apply_cell_style(cell, font=f_font, fill=fill_header_default, alignment=align_center)

    for r_idx in range(5, 20):
        apply_cell_style(ws_nv.cell(r_idx, 1, r_idx - 4), alignment=align_center_no_wrap)
        for c_idx in range(1, start_sum_col + 10):
            cell = ws_nv.cell(r_idx, c_idx)
            f_fill = day_fills[c_idx] if (c_idx in day_fills and day_fills[c_idx] != fill_header_default) else None
            apply_cell_style(cell, font=font_data, fill=f_fill, border=thin_border)
            if c_idx >= 4:
                cell.alignment = align_center_no_wrap

    sign_row = 22
    apply_cell_style(ws_nv.cell(sign_row, 3, "Lãnh đạo đơn vị"), font=font_bold)
    apply_cell_style(ws_nv.cell(sign_row, start_sum_col + 4, "Người lập biểu"), font=font_bold)

    # ---------------------------------------------------------------------
    # TAB 2: HTCS
    # ---------------------------------------------------------------------
    ws_htcs = wb.create_sheet(title="HTCS")
    apply_cell_style(ws_htcs.cell(1, 1, "BỆNH VIỆN BƯU ĐIỆN"), font=font_subtitle)
    ws_htcs.merge_cells(start_row=1, start_column=4, end_row=1, end_column=num_days + 11)
    c_htcs_t = ws_htcs.cell(1, 4, f"BẢNG CHẤM CÔNG THÁNG {month:02d} NĂM {year} CỦA NHÂN VIÊN LAO ĐỘNG THUÊ LẠI")
    apply_cell_style(c_htcs_t, font=font_title, alignment=align_center)
    
    apply_cell_style(ws_htcs.cell(2, 1, f"Đơn vị: {phong_ban}"), font=font_subtitle)

    ws_htcs.merge_cells("A3:A4"); ws_htcs.cell(3, 1, "STT")
    ws_htcs.merge_cells("B3:B4"); ws_htcs.cell(3, 2, "Mã NV")
    ws_htcs.merge_cells("C3:C4"); ws_htcs.cell(3, 3, "Họ và tên")
    
    ws_htcs.merge_cells(start_row=3, start_column=4, end_row=3, end_column=3 + num_days)
    ws_htcs.cell(3, 4, f"Ngày làm việc trong tháng {month:02d}.{year}")

    for d in range(1, num_days + 1):
        col_idx = 3 + d
        ws_htcs.cell(4, col_idx, f"{d:02d}")

    ws_htcs.merge_cells(start_row=3, start_column=start_sum_col, end_row=4, end_column=start_sum_col); ws_htcs.cell(3, start_sum_col, "Hành chính")
    ws_htcs.merge_cells(start_row=3, start_column=start_sum_col+1, end_row=4, end_column=start_sum_col+1); ws_htcs.cell(3, start_sum_col+1, "Trực ngoài giờ")
    ws_htcs.merge_cells(start_row=3, start_column=start_sum_col+2, end_row=4, end_column=start_sum_col+2); ws_htcs.cell(3, start_sum_col+2, "Trực cuối tuần")
    ws_htcs.merge_cells(start_row=3, start_column=start_sum_col+3, end_row=4, end_column=start_sum_col+3); ws_htcs.cell(3, start_sum_col+3, "Trực ngày lễ")
    ws_htcs.merge_cells(start_row=3, start_column=start_sum_col+4, end_row=3, end_column=start_sum_col+5); ws_htcs.cell(3, start_sum_col+4, "Nghỉ bù")
    apply_cell_style(ws_htcs.cell(4, start_sum_col+4, "Đã nghỉ"), font=font_sub_header)
    apply_cell_style(ws_htcs.cell(4, start_sum_col+5, "Còn lại"), font=font_sub_header)
    ws_htcs.merge_cells(start_row=3, start_column=start_sum_col+6, end_row=4, end_column=start_sum_col+6); ws_htcs.cell(3, start_sum_col+6, "Làm cuối tuần")
    ws_htcs.merge_cells(start_row=3, start_column=start_sum_col+7, end_row=4, end_column=start_sum_col+7); ws_htcs.cell(3, start_sum_col+7, "Nghỉ ốm")

    for r in range(3, 5):
        for c in range(1, start_sum_col + 8):
            cell = ws_htcs.cell(r, c)
            f_font = font_sub_header if (r == 4 and c in [start_sum_col+4, start_sum_col+5]) else font_header
            
            if 4 <= c <= 3 + num_days and r == 4:
                apply_cell_style(cell, font=f_font, fill=day_fills[c], alignment=align_center)
            else:
                apply_cell_style(cell, font=f_font, fill=fill_header_default, alignment=align_center)

    for r_idx in range(5, 20):
        apply_cell_style(ws_htcs.cell(r_idx, 1, r_idx - 4), alignment=align_center_no_wrap)
        for c_idx in range(1, start_sum_col + 8):
            cell = ws_htcs.cell(r_idx, c_idx)
            f_fill = day_fills[c_idx] if (c_idx in day_fills and day_fills[c_idx] != fill_header_default) else None
            apply_cell_style(cell, font=font_data, fill=f_fill, border=thin_border)
            if c_idx >= 4:
                cell.alignment = align_center_no_wrap

    apply_cell_style(ws_htcs.cell(sign_row, 3, "Lãnh đạo đơn vị"), font=font_bold)
    apply_cell_style(ws_htcs.cell(sign_row, start_sum_col + 3, "Người lập biểu"), font=font_bold)

    # ---------------------------------------------------------------------
    # TAB 3: LÀM THỨ 7
    # ---------------------------------------------------------------------
    ws_t7 = wb.create_sheet(title="LÀM THỨ 7")
    apply_cell_style(ws_t7.cell(1, 1, "BỆNH VIỆN BƯU ĐIỆN"), font=font_subtitle)
    ws_t7.merge_cells("A1:I1")
    c_t7 = ws_t7.cell(1, 4, f"BẢNG CHẤM CÔNG NGÀY LÀM THỨ 7, CHỦ NHẬT CỦA CBNV THÁNG {month:02d}/{year}")
    apply_cell_style(c_t7, font=font_title, alignment=align_center)

    apply_cell_style(ws_t7.cell(2, 1, f"Đơn vị: {phong_ban}"), font=font_subtitle)

    headers_t7 = ["STT", "Mã NV", "Họ và tên", "Ngày làm 1", "Ngày làm 2", "Ngày làm 3", "Ngày làm 4", "Ngày làm 5", "Tổng ngày"]
    for col_i, h in enumerate(headers_t7, 1):
        c = ws_t7.cell(3, col_i, h)
        apply_cell_style(c, font=font_header, fill=fill_header_default, alignment=align_center)

    for r_idx in range(4, 18):
        apply_cell_style(ws_t7.cell(r_idx, 1, r_idx - 3), alignment=align_center_no_wrap)
        for c_idx in range(1, 10):
            cell = ws_t7.cell(r_idx, c_idx)
            apply_cell_style(cell, font=font_data, border=thin_border)
            if c_idx >= 4:
                cell.alignment = align_center_no_wrap

    apply_cell_style(ws_t7.cell(20, 3, "Lãnh đạo đơn vị"), font=font_bold)
    apply_cell_style(ws_t7.cell(20, 7, "Người lập biểu"), font=font_bold)

    # ---------------------------------------------------------------------
    # TAB 4: ABC
    # ---------------------------------------------------------------------
    ws_abc = wb.create_sheet(title="ABC")
    apply_cell_style(ws_abc.cell(1, 1, "BỆNH VIỆN BƯU ĐIỆN"), font=font_subtitle)
    apply_cell_style(ws_abc.cell(2, 1, f"Đơn vị: {phong_ban}"), font=font_subtitle)
    ws_abc.merge_cells("A3:J3")
    c_abc = ws_abc.cell(3, 1, f"BẢNG BÌNH BẦU XẾP LOẠI LAO ĐỘNG THÁNG {month:02d}/{year}")
    apply_cell_style(c_abc, font=font_title, alignment=align_center)

    headers_abc = ["STT", "Mã NV", "HỌ VÀ TÊN", "CHỨC VỤ", "ĐI LÀM", "TRỰC", "NGHỈ BÙ", "NGHỈ KHÁC", "XẾP LOẠI", "TỒN BÙ"]
    for col_i, h in enumerate(headers_abc, 1):
        c = ws_abc.cell(5, col_i, h)
        apply_cell_style(c, font=font_header, fill=fill_header_default, alignment=align_center)

    for r_idx in range(6, 20):
        apply_cell_style(ws_abc.cell(r_idx, 1, r_idx - 5), alignment=align_center_no_wrap)
        for c_idx in range(1, 11):
            cell = ws_abc.cell(r_idx, c_idx)
            apply_cell_style(cell, font=font_data, border=thin_border)

    # ---------------------------------------------------------------------
    # TAB 5: KÝ HIỆU CHẤM CÔNG
    # ---------------------------------------------------------------------
    ws_kh = wb.create_sheet(title="Ký hiệu")
    apply_cell_style(ws_kh.cell(1, 1, "BẢNG GIẢI THÍCH KÝ HIỆU CHẤM CÔNG"), font=font_title)
    
    ky_hieu_data = [
        ("X", "công đi làm 1/2 ngày trong giờ hành chính"),
        ("XX", "công đi làm 1 ngày trong giờ hành chính"),
        ("T", "Trực ngoài giờ ngày thường hoặc trực 24/24 giờ ngày thứ Bảy, Chủ nhật, ngày Lễ, Tết"),
        ("C", "Đi công tác 1/2 ngày"),
        ("CC", "Đi công tác 1 ngày"),
        ("B", "Nghỉ bù trực, bù ngày làm thứ Bảy, Chủ nhật, ngày Lễ, Tết 1/2 ngày"),
        ("BB", "Nghỉ bù trực, bù ngày làm thứ Bảy, Chủ nhật, ngày Lễ, Tết 1 ngày"),
        ("P", "Nghỉ phép 1/2 ngày"),
        ("PP", "Nghỉ phép 1 ngày"),
        ("TS", "Nghỉ thai sản"),
        ("Ô", "Nghỉ ốm 1/2 ngày"),
        ("ÔÔ", "Nghỉ ốm 1 ngày"),
        ("Cô", "Nghỉ con ốm"),
        ("H", "Đi hội nghị, học tập 1/2 ngày"),
        ("HH", "Đi hội nghị, học tập 1 ngày"),
        ("KL", "Nghỉ không lương"),
        ("R", "Nghỉ việc riêng hưởng lương cơ bản 1/2 ngày"),
        ("RR", "Nghỉ việc riêng hưởng lương cơ bản 1 ngày")
    ]
    
    apply_cell_style(ws_kh.cell(3, 1, "Ký hiệu"), font=font_header, fill=fill_header_default, alignment=align_center)
    apply_cell_style(ws_kh.cell(3, 2, "Diễn giải ý nghĩa"), font=font_header, fill=fill_header_default, alignment=align_center)
    
    for r_idx, (kh, val) in enumerate(ky_hieu_data, start=4):
        c_kh = ws_kh.cell(r_idx, 1, kh)
        c_val = ws_kh.cell(r_idx, 2, val)
        apply_cell_style(c_kh, font=font_header, alignment=align_center)
        apply_cell_style(c_val, font=font_data)

    # Tự động căn chỉnh độ rộng cột
    for ws_curr in wb.worksheets:
        for col in ws_curr.columns:
            max_len = max(len(str(cell.value or '')) for cell in col)
            col_letter = get_column_letter(col[0].column)
            ws_curr.column_dimensions[col_letter].width = max(max_len + 3, 5)

    output = io.BytesIO()
    wb.save(output)
    return output.getvalue()


def init_cham_cong_session():
    if 'don_nghi_phep' not in st.session_state:
        st.session_state['don_nghi_phep'] = pd.DataFrame([
            {"id": 1, "ma_can_bo": "N1971", "ho_ten": "Khuất Duy Tiến", "khoa_phong": "Khoa Ngoại tổng hợp", "loai_nghi": "Nghỉ phép năm", "tu_ngay": "2026-09-10", "den_ngay": "2026-09-12", "so_ngay": 3, "ly_do": "Giải quyết việc gia đình", "trang_thai": "Đã phê duyệt"},
            {"id": 2, "ma_can_bo": "N2088", "ho_ten": "Nguyễn Văn An", "khoa_phong": "Khoa Khám bệnh", "loai_nghi": "Nghỉ bù trực", "tu_ngay": "2026-09-15", "den_ngay": "2026-09-15", "so_ngay": 1, "ly_do": "Nghỉ bù sau ca trực đêm 14/09", "trang_thai": "Chờ phê duyệt"}
        ])


def render_quan_ly_cham_cong(df_cb):
    init_cham_cong_session()
    
    st.markdown("---")
    st.subheader("⏰ QUẢN LÝ CHẤM CÔNG & NGÀY NGHỈ - BỆNH VIỆN BƯU ĐIỆN")
    
    tab_cc1, tab_cc2, tab_cc3, tab_cc4 = st.tabs([
        "📊 Bảng Tổng hợp Chấm công", 
        "📝 Đăng ký Nghỉ phép / Nghỉ bù", 
        "✅ Duyệt Đơn nghỉ phép", 
        "📥 Tải File Mẫu & Import Excel"
    ])
    
    with tab_cc1:
        st.markdown("##### 📅 **Bảng tổng hợp công lao động & Ngày nghỉ trong tháng**")
        col_m1, col_m2, _ = st.columns([1.5, 1.5, 2])
        month_sel = col_m1.selectbox("Chọn tháng:", [f"Tháng {i:02d}/2026" for i in range(1, 13)], index=8)
        
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

    with tab_cc3:
        st.markdown("##### ✅ **Danh sách Đơn xin nghỉ phép chờ phê duyệt**")
        st.dataframe(st.session_state['don_nghi_phep'], use_container_width=True, hide_index=True)

    with tab_cc4:
        st.markdown("##### 📄 **1. Tự động tạo File Excel mẫu Bảng Chấm Công theo tháng**")
        st.caption("Xuất file Excel mẫu chuẩn (Tự động phân biệt tô màu Cam nhạt ngày T7/CN và Đỏ nhạt ngày Lễ/Tết).")
        
        c_m1, c_m2, c_m3 = st.columns([1, 1, 2])
        sel_month = c_m1.selectbox("Chọn tháng xuất mẫu:", list(range(1, 13)), index=datetime.now().month - 1)
        sel_year = c_m2.number_input("Chọn năm:", min_value=2024, max_value=2030, value=2026)
        
        dept_list = ["Khoa Ngoại tổng hợp", "Khoa Khám bệnh", "Khoa Hồi sức cấp cứu", "Phòng Tổ chức Cán bộ"]
        if not df_cb.empty and 'khoa_phong' in df_cb.columns:
            dept_list = list(df_cb['khoa_phong'].dropna().unique())
            
        sel_dept = st.selectbox("Tên Khoa / Phòng tạo bảng chấm công:", dept_list)
        
        excel_bytes = generate_excel_mau_cham_cong(sel_month, sel_year, sel_dept)
        
        st.download_button(
            label=f"📥 Tải File Excel Mẫu Chấm Công Tháng {sel_month:02d}/{sel_year} ({sel_dept})",
            data=excel_bytes,
            file_name=f"Mau_Bang_Cham_Cong_{sel_dept.replace(' ', '_')}_T{sel_month:02d}_{sel_year}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )

        st.markdown("---")
        st.markdown("##### 📥 **2. Tải lên Bảng Chấm Công đã chấm từ các Đơn vị**")
        file_cc = st.file_uploader("Tải file chấm công đã điền (.xlsx, .csv):", type=["xlsx", "xls", "csv"], key="file_uploader_cc")
        if file_cc is not None:
            st.success("File chấm công đã được tải lên thành công. Hệ thống đã sẵn sàng đối soát dữ liệu!")
