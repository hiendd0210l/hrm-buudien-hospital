import io
import calendar
import pandas as pd
import streamlit as st
from datetime import datetime, date
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

# ---------------------------------------------------------------------
# HÀM BỔ TRỢ ĐỊNH DẠNG VÀ TẠO MÀU NGÀY NGHỈ / LỄ
# ---------------------------------------------------------------------
def get_day_fill_and_type(day: int, month: int, year: int):
    dt = date(year, month, day)
    weekday = dt.weekday()  # 5: Thứ 7, 6: Chủ nhật
    
    fixed_holidays = [(1, 1), (30, 4), (1, 5), (2, 9), (3, 9)]
    
    if (day, month) in fixed_holidays:
        # Lễ / Tết -> Đỏ nhạt
        return PatternFill(start_color="FFC7CE", end_color="FFC7CE", fill_type="solid"), "HOLIDAY"
    elif weekday == 5:
        # Thứ 7 -> Cam nhạt
        return PatternFill(start_color="FCE4D6", end_color="FCE4D6", fill_type="solid"), "SAT"
    elif weekday == 6:
        # Chủ nhật -> Xanh dương nhạt
        return PatternFill(start_color="DDEBF7", end_color="DDEBF7", fill_type="solid"), "SUN"
    return None, "WORKDAY"

def set_style(cell, font=None, fill=None, alignment=None, border=None):
    if font is not None:
        cell.font = font
    if fill is not None:
        cell.fill = fill
    if alignment is not None:
        cell.alignment = alignment
    if border is not None:
        cell.border = border


# ---------------------------------------------------------------------
# HÀM TẠO FILE EXCEL MẪU TỰ ĐỘNG CÓ DỮ LIỆU & CÔNG THỨC
# ---------------------------------------------------------------------
def generate_excel_mau_cham_cong(month: int, year: int, phong_ban: str, df_cb: pd.DataFrame) -> bytes:
    wb = openpyxl.Workbook()
    
    # Lọc danh sách nhân viên thuộc Khoa / Phòng
    if not df_cb.empty and 'khoa_phong' in df_cb.columns:
        df_dept = df_cb[df_cb['khoa_phong'] == phong_ban].copy()
    else:
        df_dept = pd.DataFrame()
        
    nv_list = []
    if not df_dept.empty:
        for _, row in df_dept.iterrows():
            nv_list.append({
                "ma_cb": str(row.get('ma_can_bo', '')),
                "ho_ten": str(row.get('ho_ten', '')),
                "chuc_vu": str(row.get('chuc_vu', 'Nhân viên'))
            })
    else:
        # Dữ liệu mẫu nếu chưa chọn/chưa có cán bộ
        nv_list = [
            {"ma_cb": "N1971", "ho_ten": "Khuất Duy Tiến", "chuc_vu": "Trưởng khoa"},
            {"ma_cb": "N2088", "ho_ten": "Nguyễn Văn An", "chuc_vu": "Bác sĩ"},
            {"ma_cb": "N2105", "ho_ten": "Trần Thị Bình", "chuc_vu": "Điều dưỡng"}
        ]

    # Kiểu Font & Màu sắc
    font_title = Font(name="Times New Roman", size=13, bold=True, color="002060")
    font_subtitle = Font(name="Times New Roman", size=10, bold=True)
    font_header = Font(name="Times New Roman", size=9, bold=True)
    font_sub_header = Font(name="Times New Roman", size=8, bold=True, italic=True)
    font_data = Font(name="Times New Roman", size=10)
    font_bold = Font(name="Times New Roman", size=10, bold=True)
    
    fill_header_default = PatternFill(start_color="D9E1F2", end_color="D9E1F2", fill_type="solid")
    
    align_center = Alignment(horizontal="center", vertical="center", wrap_text=True)
    align_left = Alignment(horizontal="left", vertical="center")
    align_center_no_wrap = Alignment(horizontal="center", vertical="center")
    
    thin_border = Border(
        left=Side(style='thin', color='BFBFBF'),
        right=Side(style='thin', color='BFBFBF'),
        top=Side(style='thin', color='BFBFBF'),
        bottom=Side(style='thin', color='BFBFBF')
    )
    
    num_days = calendar.monthrange(year, month)[1]

    # =====================================================================
    # TAB 1: NHÂN VIÊN
    # =====================================================================
    ws_nv = wb.active
    ws_nv.title = "NHÂN VIÊN"
    
    set_style(ws_nv.cell(1, 1, "BỆNH VIỆN BƯU ĐIỆN"), font=font_subtitle)
    ws_nv.cell(1, 4, f"BẢNG CHẤM CÔNG THÁNG {month:02d} NĂM {year} CỦA CBNV")
    ws_nv.merge_cells(start_row=1, start_column=4, end_row=1, end_column=num_days + 13)
    set_style(ws_nv.cell(1, 4), font=font_title, alignment=align_center)
    
    set_style(ws_nv.cell(2, 1, f"Đơn vị: {phong_ban}"), font=font_subtitle)
    
    ws_nv.cell(3, 1, "STT"); ws_nv.merge_cells("A3:A4")
    ws_nv.cell(3, 2, "Mã NV"); ws_nv.merge_cells("B3:B4")
    ws_nv.cell(3, 3, "Họ và tên"); ws_nv.merge_cells("C3:C4")
    
    ws_nv.cell(3, 4, f"Ngày làm việc trong tháng {month:02d}.{year}")
    ws_nv.merge_cells(start_row=3, start_column=4, end_row=3, end_column=3 + num_days)
    
    day_fills = {}
    for d in range(1, num_days + 1):
        col_idx = 3 + d
        ws_nv.cell(4, col_idx, f"{d:02d}")
        fill_color, _ = get_day_fill_and_type(d, month, year)
        day_fills[col_idx] = fill_color if fill_color else fill_header_default

    start_sum = 4 + num_days
    ws_nv.cell(3, start_sum, "Hành chính"); ws_nv.merge_cells(start_row=3, start_column=start_sum, end_row=4, end_column=start_sum)
    ws_nv.cell(3, start_sum+1, "Trực ngoài giờ"); ws_nv.merge_cells(start_row=3, start_column=start_sum+1, end_row=4, end_column=start_sum+1)
    ws_nv.cell(3, start_sum+2, "Nghỉ bù"); ws_nv.merge_cells(start_row=3, start_column=start_sum+2, end_row=3, end_column=start_sum+3)
    
    ws_nv.cell(4, start_sum+2, "Đã nghỉ")
    ws_nv.cell(4, start_sum+3, "Còn lại")
    
    ws_nv.cell(3, start_sum+4, "Thai sản"); ws_nv.merge_cells(start_row=3, start_column=start_sum+4, end_row=4, end_column=start_sum+4)
    ws_nv.cell(3, start_sum+5, "Công tác, họp"); ws_nv.merge_cells(start_row=3, start_column=start_sum+5, end_row=4, end_column=start_sum+5)
    ws_nv.cell(3, start_sum+6, "Nghỉ ốm"); ws_nv.merge_cells(start_row=3, start_column=start_sum+6, end_row=4, end_column=start_sum+6)
    ws_nv.cell(3, start_sum+7, "Trực lễ"); ws_nv.merge_cells(start_row=3, start_column=start_sum+7, end_row=4, end_column=start_sum+7)
    ws_nv.cell(3, start_sum+8, "Đi học"); ws_nv.merge_cells(start_row=3, start_column=start_sum+8, end_row=4, end_column=start_sum+8)
    ws_nv.cell(3, start_sum+9, "Tồn bù"); ws_nv.merge_cells(start_row=3, start_column=start_sum+9, end_row=4, end_column=start_sum+9)

    for r in range(3, 5):
        for c in range(1, start_sum + 10):
            cell = ws_nv.cell(r, c)
            f_font = font_sub_header if (r == 4 and c in [start_sum+2, start_sum+3]) else font_header
            f_fill = day_fills[c] if (4 <= c <= 3 + num_days and r == 4) else fill_header_default
            set_style(cell, font=f_font, fill=f_fill, alignment=align_center)

    # Đổ danh sách cán bộ + Công thức tự động
    for idx, nv in enumerate(nv_list, start=5):
        ws_nv.cell(idx, 1, idx - 4)
        ws_nv.cell(idx, 2, nv["ma_cb"])
        ws_nv.cell(idx, 3, nv["ho_ten"])
        
        start_letter = get_column_letter(4)
        end_letter = get_column_letter(3 + num_days)
        
        # Chèn Công thức tính tổng tự động
        ws_nv.cell(idx, start_sum, f'=COUNTIF({start_letter}{idx}:{end_letter}{idx}, "XX") + COUNTIF({start_letter}{idx}:{end_letter}{idx}, "X")*0.5')
        ws_nv.cell(idx, start_sum+1, f'=COUNTIF({start_letter}{idx}:{end_letter}{idx}, "T")')
        ws_nv.cell(idx, start_sum+2, f'=COUNTIF({start_letter}{idx}:{end_letter}{idx}, "BB") + COUNTIF({start_letter}{idx}:{end_letter}{idx}, "B")*0.5')
        ws_nv.cell(idx, start_sum+3, f'={get_column_letter(start_sum+9)}{idx}-{get_column_letter(start_sum+2)}{idx}')
        ws_nv.cell(idx, start_sum+4, f'=COUNTIF({start_letter}{idx}:{end_letter}{idx}, "TS")')
        ws_nv.cell(idx, start_sum+5, f'=COUNTIF({start_letter}{idx}:{end_letter}{idx}, "CC") + COUNTIF({start_letter}{idx}:{end_letter}{idx}, "C")*0.5')
        ws_nv.cell(idx, start_sum+6, f'=COUNTIF({start_letter}{idx}:{end_letter}{idx}, "ÔÔ") + COUNTIF({start_letter}{idx}:{end_letter}{idx}, "Ô")*0.5')
        ws_nv.cell(idx, start_sum+7, f'=COUNTIF({start_letter}{idx}:{end_letter}{idx}, "TL")')
        ws_nv.cell(idx, start_sum+8, f'=COUNTIF({start_letter}{idx}:{end_letter}{idx}, "HH") + COUNTIF({start_letter}{idx}:{end_letter}{idx}, "H")*0.5')
        ws_nv.cell(idx, start_sum+9, 0) # Giá trị Tồn bù mặc định

        for c_idx in range(1, start_sum + 10):
            cell = ws_nv.cell(idx, c_idx)
            f_fill = day_fills[c_idx] if (c_idx in day_fills and day_fills[c_idx] != fill_header_default) else None
            set_style(cell, font=font_data, fill=f_fill, border=thin_border)
            if c_idx in [1, 2] or c_idx >= 4:
                cell.alignment = align_center_no_wrap
            elif c_idx == 3:
                cell.alignment = align_left

    sign_row = len(nv_list) + 7
    ws_nv.cell(sign_row, 3, "Lãnh đạo đơn vị")
    set_style(ws_nv.cell(sign_row, 3), font=font_bold)
    ws_nv.cell(sign_row, start_sum + 4, "Người lập biểu")
    set_style(ws_nv.cell(sign_row, start_sum + 4), font=font_bold)

    # =====================================================================
    # TAB 2: LÀM THỨ 7 (ĐÃ CẬP NHẬT THEO YÊU CẦU MỚI)
    # =====================================================================
    ws_t7 = wb.create_sheet(title="LÀM THỨ 7")
    set_style(ws_t7.cell(1, 1, "BỆNH VIỆN BƯU ĐIỆN"), font=font_subtitle)
    ws_t7.cell(1, 4, f"BẢNG CHẤM CÔNG NGÀY LÀM THỨ 7, CHỦ NHẬT & NGÀY LỄ CỦA CBNV THÁNG {month:02d}/{year}")
    
    # Tìm các ngày T7, CN và Lễ trong tháng
    weekend_days = []
    for d in range(1, num_days + 1):
        fill_color, day_type = get_day_fill_and_type(d, month, year)
        if day_type in ["SAT", "SUN", "HOLIDAY"]:
            weekend_days.append((d, fill_color, day_type))
            
    num_we_cols = len(weekend_days)
    ws_t7.merge_cells(start_row=1, start_column=4, end_row=1, end_column=4 + num_we_cols)
    set_style(ws_t7.cell(1, 4), font=font_title, alignment=align_center)

    set_style(ws_t7.cell(2, 1, f"Đơn vị: {phong_ban}"), font=font_subtitle)

    ws_t7.cell(3, 1, "STT")
    ws_t7.cell(3, 2, "Mã NV")
    ws_t7.cell(3, 3, "Họ và tên")
    
    for w_i, (d, fill_color, _) in enumerate(weekend_days, start=4):
        c = ws_t7.cell(3, w_i, f"Ngày {d:02d}")
        set_style(c, font=font_header, fill=fill_color, alignment=align_center)
        
    tot_col = 4 + num_we_cols
    ws_t7.cell(3, tot_col, "Tổng ngày")
    set_style(ws_t7.cell(3, 1), font=font_header, fill=fill_header_default, alignment=align_center)
    set_style(ws_t7.cell(3, 2), font=font_header, fill=fill_header_default, alignment=align_center)
    set_style(ws_t7.cell(3, 3), font=font_header, fill=fill_header_default, alignment=align_center)
    set_style(ws_t7.cell(3, tot_col), font=font_header, fill=fill_header_default, alignment=align_center)

    for idx, nv in enumerate(nv_list, start=4):
        ws_t7.cell(idx, 1, idx - 3)
        ws_t7.cell(idx, 2, nv["ma_cb"])
        ws_t7.cell(idx, 3, nv["ho_ten"])
        
        # Công thức tổng các ngày làm T7/CN/Lễ
        st_l = get_column_letter(4)
        en_l = get_column_letter(tot_col - 1)
        ws_t7.cell(idx, tot_col, f'=COUNTA({st_l}{idx}:{en_l}{idx})')
        
        for c_idx in range(1, tot_col + 1):
            cell = ws_t7.cell(idx, c_idx)
            fill_color = weekend_days[c_idx - 4][1] if (4 <= c_idx < tot_col) else None
            set_style(cell, font=font_data, fill=fill_color, border=thin_border)
            if c_idx in [1, 2] or c_idx >= 4:
                cell.alignment = align_center_no_wrap
            elif c_idx == 3:
                cell.alignment = align_left

    sign_r_t7 = len(nv_list) + 6
    ws_t7.cell(sign_r_t7, 3, "Lãnh đạo đơn vị")
    set_style(ws_t7.cell(sign_r_t7, 3), font=font_bold)
    ws_t7.cell(sign_r_t7, tot_col - 1, "Người lập biểu")
    set_style(ws_t7.cell(sign_r_t7, tot_col - 1), font=font_bold)

    # =====================================================================
    # TAB 3: ABC
    # =====================================================================
    ws_abc = wb.create_sheet(title="ABC")
    set_style(ws_abc.cell(1, 1, "BỆNH VIỆN BƯU ĐIỆN"), font=font_subtitle)
    set_style(ws_abc.cell(2, 1, f"Đơn vị: {phong_ban}"), font=font_subtitle)
    ws_abc.cell(3, 1, f"BẢNG BÌNH BẦU XẾP LOẠI LAO ĐỘNG THÁNG {month:02d}/{year}")
    ws_abc.merge_cells("A3:J3")
    set_style(ws_abc.cell(3, 1), font=font_title, alignment=align_center)

    headers_abc = ["STT", "Mã NV", "HỌ VÀ TÊN", "CHỨC VỤ", "ĐI LÀM", "TRỰC", "NGHỈ BÙ", "NGHỈ KHÁC", "XẾP LOẠI", "TỒN BÙ"]
    for col_i, h in enumerate(headers_abc, 1):
        c = ws_abc.cell(5, col_i, h)
        set_style(c, font=font_header, fill=fill_header_default, alignment=align_center)

    for idx, nv in enumerate(nv_list, start=6):
        ws_abc.cell(idx, 1, idx - 5)
        ws_abc.cell(idx, 2, nv["ma_cb"])
        ws_abc.cell(idx, 3, nv["ho_ten"])
        ws_abc.cell(idx, 4, nv["chuc_vu"])
        
        # Link công thức tự động lấy từ sheet 'NHÂN VIÊN'
        ws_abc.cell(idx, 5, f"='NHÂN VIÊN'!{get_column_letter(start_sum)}{idx-1}") # Đi làm
        ws_abc.cell(idx, 6, f"='NHÂN VIÊN'!{get_column_letter(start_sum+1)}{idx-1}") # Trực
        ws_abc.cell(idx, 7, f"='NHÂN VIÊN'!{get_column_letter(start_sum+2)}{idx-1}") # Nghỉ bù
        ws_abc.cell(idx, 8, f"='NHÂN VIÊN'!{get_column_letter(start_sum+4)}{idx-1}+'NHÂN VIÊN'!{get_column_letter(start_sum+6)}{idx-1}") # Nghỉ khác
        ws_abc.cell(idx, 9, "A") # Mặc định xếp loại A
        ws_abc.cell(idx, 10, f"='NHÂN VIÊN'!{get_column_letter(start_sum+3)}{idx-1}") # Tồn bù còn lại
        
        for c_idx in range(1, 11):
            cell = ws_abc.cell(idx, c_idx)
            set_style(cell, font=font_data, border=thin_border)
            if c_idx in [1, 2] or c_idx >= 5:
                cell.alignment = align_center_no_wrap
            elif c_idx in [3, 4]:
                cell.alignment = align_left

    sign_r_abc = len(nv_list) + 8
    ws_abc.cell(sign_r_abc, 3, "Lãnh đạo đơn vị")
    set_style(ws_abc.cell(sign_r_abc, 3), font=font_bold)
    ws_abc.cell(sign_r_abc, 8, "Người lập biểu")
    set_style(ws_abc.cell(sign_r_abc, 8), font=font_bold)

    # =====================================================================
    # TAB 4: KÝ HIỆU CHẤM CÔNG
    # =====================================================================
    ws_kh = wb.create_sheet(title="Ký hiệu")
    set_style(ws_kh.cell(1, 1, "BẢNG GIẢI THÍCH KÝ HIỆU CHẤM CÔNG"), font=font_title)
    
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
    
    set_style(ws_kh.cell(3, 1, "Ký hiệu"), font=font_header, fill=fill_header_default, alignment=align_center)
    set_style(ws_kh.cell(3, 2, "Diễn giải ý nghĩa"), font=font_header, fill=fill_header_default, alignment=align_center)
    
    for r_idx, (kh, val) in enumerate(ky_hieu_data, start=4):
        c_kh = ws_kh.cell(r_idx, 1, kh)
        c_val = ws_kh.cell(r_idx, 2, val)
        set_style(c_kh, font=font_header, alignment=align_center, border=thin_border)
        set_style(c_val, font=font_data, border=thin_border)

    # =====================================================================
    # CĂN CHỈNH ĐỘ RỘNG CÁC CỘT CHO CHUẨN ĐẸP (CUSTOM COLUMN WIDTH)
    # =====================================================================
    for ws in wb.worksheets:
        if ws.title in ["NHÂN VIÊN", "HTCS"]:
            ws.column_dimensions['A'].width = 6   # STT
            ws.column_dimensions['B'].width = 11  # Mã NV
            ws.column_dimensions['C'].width = 24  # Họ tên
            
            # Cột ngày (01 - 31) thu gọn vừa đẹp
            for d in range(1, num_days + 1):
                col_let = get_column_letter(3 + d)
                ws.column_dimensions[col_let].width = 4.5
                
            # Cột tổng hợp công
            for s_i in range(start_sum, start_sum + 10):
                col_let = get_column_letter(s_i)
                ws.column_dimensions[col_let].width = 11
                
        elif ws.title == "LÀM THỨ 7":
            ws.column_dimensions['A'].width = 6
            ws.column_dimensions['B'].width = 11
            ws.column_dimensions['C'].width = 24
            for w_i in range(4, tot_col):
                ws.column_dimensions[get_column_letter(w_i)].width = 10
            ws.column_dimensions[get_column_letter(tot_col)].width = 12
            
        elif ws.title == "ABC":
            ws.column_dimensions['A'].width = 6
            ws.column_dimensions['B'].width = 11
            ws.column_dimensions['C'].width = 24
            ws.column_dimensions['D'].width = 18
            for c_i in range(5, 11):
                ws.column_dimensions[get_column_letter(c_i)].width = 11
                
        elif ws.title == "Ký hiệu":
            ws.column_dimensions['A'].width = 12
            ws.column_dimensions['B'].width = 75

    output = io.BytesIO()
    wb.save(output)
    return output.getvalue()


# ---------------------------------------------------------------------
# STREAMLIT UI COMPONENTS
# ---------------------------------------------------------------------
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
        st.caption("Xuất file Excel chuẩn tự động điền danh sách nhân sự, căn chỉnh độ rộng cột và gán sẵn công thức tính tổng công.")
        
        c_m1, c_m2, c_m3 = st.columns([1, 1, 2])
        sel_month = c_m1.selectbox("Chọn tháng xuất mẫu:", list(range(1, 13)), index=datetime.now().month - 1)
        sel_year = c_m2.number_input("Chọn năm:", min_value=2024, max_value=2030, value=2026)
        
        dept_list = ["Khoa Ngoại tổng hợp", "Khoa Khám bệnh", "Khoa Hồi sức cấp cứu", "Phòng Tổ chức Cán bộ"]
        if not df_cb.empty and 'khoa_phong' in df_cb.columns:
            dept_list = list(df_cb['khoa_phong'].dropna().unique())
            
        sel_dept = st.selectbox("Tên Khoa / Phòng tạo bảng chấm công:", dept_list)
        
        try:
            excel_bytes = generate_excel_mau_cham_cong(sel_month, sel_year, sel_dept, df_cb)
            st.download_button(
                label=f"📥 Tải File Excel Mẫu Chấm Công Tháng {sel_month:02d}/{sel_year} ({sel_dept})",
                data=excel_bytes,
                file_name=f"Mau_Bang_Cham_Cong_{sel_dept.replace(' ', '_')}_T{sel_month:02d}_{sel_year}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
        except Exception as e:
            st.error(f"Lỗi khởi tạo file Excel: {e}")

        st.markdown("---")
        st.markdown("##### 📥 **2. Tải lên Bảng Chấm Công đã chấm từ các Đơn vị**")
        file_cc = st.file_uploader("Tải file chấm công đã điền (.xlsx, .csv):", type=["xlsx", "xls", "csv"], key="file_uploader_cc")
        if file_cc is not None:
            st.success("File chấm công đã được tải lên thành công. Hệ thống đã sẵn sàng đối soát dữ liệu!")
