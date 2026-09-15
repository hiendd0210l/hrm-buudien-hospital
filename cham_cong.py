import io
import calendar
import pandas as pd
import streamlit as st
from datetime import datetime, date
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

# ---------------------------------------------------------------------
# HÀM BỔ TRỢ PHÂN LOẠI NGÀY (T7, CN, LỄ)
# ---------------------------------------------------------------------
def get_day_type(day: int, month: int, year: int):
    dt = date(year, month, day)
    weekday = dt.weekday()  # 5: Thứ 7, 6: Chủ nhật
    fixed_holidays = [(1, 1), (30, 4), (1, 5), (2, 9), (3, 9)]
    
    if (day, month) in fixed_holidays:
        return PatternFill(start_color="FFC7CE", end_color="FFC7CE", fill_type="solid"), "HOLIDAY"
    elif weekday == 5:
        return PatternFill(start_color="FCE4D6", end_color="FCE4D6", fill_type="solid"), "SAT"
    elif weekday == 6:
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
# HÀM TẠO FILE EXCEL CHUẨN ĐÚNG NGUYÊN TẮC
# ---------------------------------------------------------------------
def generate_excel_mau_cham_cong(month: int, year: int, phong_ban: str, df_cb: pd.DataFrame) -> bytes:
    wb = openpyxl.Workbook()
    
    # Danh sách cán bộ mẫu nếu không truyền df_cb
    nv_list = []
    if df_cb is not None and not df_cb.empty and 'khoa_phong' in df_cb.columns:
        df_dept = df_cb[df_cb['khoa_phong'] == phong_ban].copy()
        if not df_dept.empty:
            for _, row in df_dept.iterrows():
                nv_list.append({
                    "ma_cb": str(row.get('ma_can_bo', '')),
                    "ho_ten": str(row.get('ho_ten', '')),
                    "chuc_vu": str(row.get('chuc_vu', 'Nhân viên'))
                })

    if not nv_list:
        nv_list = [
            {"ma_cb": "N1096", "ho_ten": "Nguyễn Thị Thảo Nguyên", "chuc_vu": "Bác sĩ"},
            {"ma_cb": "N1048", "ho_ten": "Đỗ Thanh Mai", "chuc_vu": "Bác sĩ"},
            {"ma_cb": "N0668", "ho_ten": "Đào Tiến Luật", "chuc_vu": "Bác sĩ"},
            {"ma_cb": "N0418", "ho_ten": "Phạm Ngọc Mai", "chuc_vu": "Điều dưỡng"},
            {"ma_cb": "N0162", "ho_ten": "Nguyễn Thị Mai Phương", "chuc_vu": "Điều dưỡng"}
        ]

    font_title = Font(name="Arial", size=12, bold=True, color="002060")
    font_subtitle = Font(name="Arial", size=10, bold=True)
    font_header = Font(name="Arial", size=9, bold=True)
    font_data = Font(name="Arial", size=10)
    font_bold = Font(name="Arial", size=10, bold=True)
    
    fill_header_default = PatternFill(start_color="D9E1F2", end_color="D9E1F2", fill_type="solid")
    align_center = Alignment(horizontal="center", vertical="center", wrap_text=True)
    align_left = Alignment(horizontal="left", vertical="center")
    align_center_nowrap = Alignment(horizontal="center", vertical="center")
    
    thin_border = Border(
        left=Side(style='thin', color='BFBFBF'), right=Side(style='thin', color='BFBFBF'),
        top=Side(style='thin', color='BFBFBF'), bottom=Side(style='thin', color='BFBFBF')
    )
    
    num_days = calendar.monthrange(year, month)[1]

    # Phân loại cột theo ngày Thứ 7, Chủ Nhật, Ngày Lễ
    sat_cols, sun_cols, hol_cols = [], [], []
    for d in range(1, num_days + 1):
        col_letter = get_column_letter(3 + d)
        _, day_type = get_day_type(d, month, year)
        if day_type == "SAT":
            sat_cols.append(col_letter)
        elif day_type == "SUN":
            sun_cols.append(col_letter)
        elif day_type == "HOLIDAY":
            hol_cols.append(col_letter)

    # Hàm tạo công thức tính ngày công hỗ trợ cả chữ HOA và chữ thường (X/x = 0.5, XX/xx = 1.0)
    def build_work_formula(col_list, row_idx):
        if not col_list:
            return "0"
        parts = []
        for c in col_list:
            parts.append(f'IF(OR({c}{row_idx}="XX",{c}{row_idx}="xx"),1,IF(OR({c}{row_idx}="X",{c}{row_idx}="x"),0.5,0))')
        return " + ".join(parts)

    def build_duty_formula(col_list, row_idx):
        if not col_list:
            return "0"
        parts = []
        for c in col_list:
            parts.append(f'IF(OR({c}{row_idx}="T",{c}{row_idx}="t"),1,0)')
        return " + ".join(parts)

    # =====================================================================
    # SHEET 1: NHÂN VIÊN
    # =====================================================================
    ws_nv = wb.active
    ws_nv.title = "NHÂN VIÊN"
    
    ws_nv.cell(1, 1, "BỆNH VIỆN BƯU ĐIỆN"); set_style(ws_nv.cell(1, 1), font=font_subtitle)
    ws_nv.cell(1, 4, f"BẢNG CHẤM CÔNG THÁNG {month:02d} NĂM {year} CỦA CBNV")
    ws_nv.merge_cells(start_row=1, start_column=4, end_row=1, end_column=num_days + 18)
    set_style(ws_nv.cell(1, 4), font=font_title, alignment=align_center)
    ws_nv.cell(2, 1, f"Đơn vị: {phong_ban}"); set_style(ws_nv.cell(2, 1), font=font_subtitle)
    
    ws_nv.cell(3, 1, "STT"); ws_nv.merge_cells("A3:A4")
    ws_nv.cell(3, 2, "Mã NV"); ws_nv.merge_cells("B3:B4")
    ws_nv.cell(3, 3, "Họ và tên"); ws_nv.merge_cells("C3:C4")
    ws_nv.cell(3, 4, f"Ngày làm việc trong tháng {month:02d}.{year}")
    ws_nv.merge_cells(start_row=3, start_column=4, end_row=3, end_column=3 + num_days)
    
    day_fills = {}
    for d in range(1, num_days + 1):
        col_idx = 3 + d
        ws_nv.cell(4, col_idx, f"{d:02d}")
        fill_color, _ = get_day_type(d, month, year)
        day_fills[col_idx] = fill_color if fill_color else fill_header_default

    start_sum = 4 + num_days
    # Cột tổng hợp phân tách riêng biệt
    headers_sum = [
        "Hành chính", "Làm Thứ 7", "Làm Chủ Nhật", "Làm Lễ/Tết", 
        "Trực Thứ 7", "Trực Chủ Nhật", "Trực Lễ/Tết", "Trực ngoài giờ",
        "Đã nghỉ bù", "Nghỉ bù còn lại", "Thai sản", "Công tác", "Nghỉ ốm", "Đi học", "Tồn bù"
    ]
    for i, h in enumerate(headers_sum):
        c_idx = start_sum + i
        ws_nv.cell(3, c_idx, h)
        ws_nv.merge_cells(start_row=3, start_column=c_idx, end_row=4, end_column=c_idx)

    for r in range(3, 5):
        for c in range(1, start_sum + len(headers_sum)):
            cell = ws_nv.cell(r, c)
            f_fill = day_fills[c] if (4 <= c <= 3 + num_days and r == 4) else fill_header_default
            set_style(cell, font=font_header, fill=f_fill, alignment=align_center)

    # Đổ dữ liệu cán bộ & Công thức sheet NHÂN VIÊN
    for idx, nv in enumerate(nv_list, start=5):
        ws_nv.cell(idx, 1, idx - 4)
        ws_nv.cell(idx, 2, nv["ma_cb"])
        ws_nv.cell(idx, 3, nv["ho_ten"])
        
        st_l = get_column_letter(4)
        en_l = get_column_letter(3 + num_days)
        
        # Công thức tính chính xác theo yêu cầu
        ws_nv.cell(idx, start_sum, f'=(COUNTIF({st_l}{idx}:{en_l}{idx},"XX")+COUNTIF({st_l}{idx}:{en_l}{idx},"xx")) + (COUNTIF({st_l}{idx}:{en_l}{idx},"X")+COUNTIF({st_l}{idx}:{en_l}{idx},"x"))*0.5')
        ws_nv.cell(idx, start_sum+1, f'={build_work_formula(sat_cols, idx)}')
        ws_nv.cell(idx, start_sum+2, f'={build_work_formula(sun_cols, idx)}')
        ws_nv.cell(idx, start_sum+3, f'={build_work_formula(hol_cols, idx)}')
        ws_nv.cell(idx, start_sum+4, f'={build_duty_formula(sat_cols, idx)}')
        ws_nv.cell(idx, start_sum+5, f'={build_duty_formula(sun_cols, idx)}')
        ws_nv.cell(idx, start_sum+6, f'={build_duty_formula(hol_cols, idx)}')
        ws_nv.cell(idx, start_sum+7, f'=COUNTIF({st_l}{idx}:{en_l}{idx},"T") + COUNTIF({st_l}{idx}:{en_l}{idx},"t")')
        ws_nv.cell(idx, start_sum+8, f'=(COUNTIF({st_l}{idx}:{en_l}{idx},"BB")+COUNTIF({st_l}{idx}:{en_l}{idx},"bb")) + (COUNTIF({st_l}{idx}:{en_l}{idx},"B")+COUNTIF({st_l}{idx}:{en_l}{idx},"b"))*0.5')
        
        # Loại bỏ hoàn toàn số âm ở cột Nghỉ bù còn lại
        ton_col = get_column_letter(start_sum+14)
        da_nghi_col = get_column_letter(start_sum+8)
        ws_nv.cell(idx, start_sum+9, f'=MAX(0, {ton_col}{idx} - {da_nghi_col}{idx})')
        
        ws_nv.cell(idx, start_sum+10, f'=COUNTIF({st_l}{idx}:{en_l}{idx},"TS") + COUNTIF({st_l}{idx}:{en_l}{idx},"ts")')
        ws_nv.cell(idx, start_sum+11, f'=(COUNTIF({st_l}{idx}:{en_l}{idx},"CC")+COUNTIF({st_l}{idx}:{en_l}{idx},"cc")) + (COUNTIF({st_l}{idx}:{en_l}{idx},"C")+COUNTIF({st_l}{idx}:{en_l}{idx},"c"))*0.5')
        ws_nv.cell(idx, start_sum+12, f'=(COUNTIF({st_l}{idx}:{en_l}{idx},"ÔÔ")+COUNTIF({st_l}{idx}:{en_l}{idx},"ôô")) + (COUNTIF({st_l}{idx}:{en_l}{idx},"Ô")+COUNTIF({st_l}{idx}:{en_l}{idx},"ô"))*0.5')
        ws_nv.cell(idx, start_sum+13, f'=(COUNTIF({st_l}{idx}:{en_l}{idx},"HH")+COUNTIF({st_l}{idx}:{en_l}{idx},"hh")) + (COUNTIF({st_l}{idx}:{en_l}{idx},"H")+COUNTIF({st_l}{idx}:{en_l}{idx},"h"))*0.5')
        ws_nv.cell(idx, start_sum+14, 0)

        for c_idx in range(1, start_sum + len(headers_sum)):
            cell = ws_nv.cell(idx, c_idx)
            f_fill = day_fills[c_idx] if (c_idx in day_fills and day_fills[c_idx] != fill_header_default) else None
            set_style(cell, font=font_data, fill=f_fill, border=thin_border)
            cell.alignment = align_center_nowrap if (c_idx in [1, 2] or c_idx >= 4) else align_left

    # =====================================================================
    # SHEET 2: LÀM THỨ 7 (Tính X/x = 0.5 công, XX/xx = 1.0 công)
    # =====================================================================
    ws_t7 = wb.create_sheet(title="LÀM THỨ 7")
    ws_t7.cell(1, 1, "BỆNH VIỆN BƯU ĐIỆN"); set_style(ws_t7.cell(1, 1), font=font_subtitle)
    ws_t7.cell(1, 4, f"BẢNG CHẤM CÔNG NGÀY LÀM THỨ 7, CHỦ NHẬT & NGÀY LỄ CỦA CBNV THÁNG {month:02d}/{year}")
    
    weekend_days = []
    for d in range(1, num_days + 1):
        fill_color, day_type = get_day_type(d, month, year)
        if day_type in ["SAT", "SUN", "HOLIDAY"]:
            weekend_days.append((d, fill_color))
            
    tot_col = 4 + len(weekend_days)
    ws_t7.merge_cells(start_row=1, start_column=4, end_row=1, end_column=tot_col)
    set_style(ws_t7.cell(1, 4), font=font_title, alignment=align_center)
    ws_t7.cell(2, 1, f"Đơn vị: {phong_ban}"); set_style(ws_t7.cell(2, 1), font=font_subtitle)

    ws_t7.cell(3, 1, "STT"); set_style(ws_t7.cell(3, 1), font=font_header, fill=fill_header_default, alignment=align_center)
    ws_t7.cell(3, 2, "Mã NV"); set_style(ws_t7.cell(3, 2), font=font_header, fill=fill_header_default, alignment=align_center)
    ws_t7.cell(3, 3, "Họ và tên"); set_style(ws_t7.cell(3, 3), font=font_header, fill=fill_header_default, alignment=align_center)

    for w_i, (d, fill_color) in enumerate(weekend_days, start=4):
        c = ws_t7.cell(3, w_i, f"Ngày {d:02d}")
        set_style(c, font=font_header, fill=fill_color, alignment=align_center)
        
    ws_t7.cell(3, tot_col, "Tổng ngày công")
    set_style(ws_t7.cell(3, tot_col), font=font_header, fill=fill_header_default, alignment=align_center)

    for idx, nv in enumerate(nv_list, start=4):
        ws_t7.cell(idx, 1, idx - 3)
        ws_t7.cell(idx, 2, nv["ma_cb"])
        ws_t7.cell(idx, 3, nv["ho_ten"])
        
        st_l = get_column_letter(4)
        en_l = get_column_letter(tot_col - 1)
        # Sửa lại công thức tổng ngày công đúng quy tắc X = 0.5, XX = 1
        ws_t7.cell(idx, tot_col, f'=(COUNTIF({st_l}{idx}:{en_l}{idx},"XX")+COUNTIF({st_l}{idx}:{en_l}{idx},"xx")) + (COUNTIF({st_l}{idx}:{en_l}{idx},"T")+COUNTIF({st_l}{idx}:{en_l}{idx},"t")) + (COUNTIF({st_l}{idx}:{en_l}{idx},"X")+COUNTIF({st_l}{idx}:{en_l}{idx},"x"))*0.5')
        
        for c_idx in range(1, tot_col + 1):
            cell = ws_t7.cell(idx, c_idx)
            fill_color = weekend_days[c_idx - 4][1] if (4 <= c_idx < tot_col) else None
            set_style(cell, font=font_data, fill=fill_color, border=thin_border)
            cell.alignment = align_center_nowrap if (c_idx in [1, 2] or c_idx >= 4) else align_left

    # =====================================================================
    # SHEET 3: ABC (TỔNG HỢP HIỂN THỊ ĐẦY ĐỦ CÁC CỘT THEO KÝ HIỆU)
    # =====================================================================
    ws_abc = wb.create_sheet(title="ABC")
    ws_abc.cell(1, 1, "BỆNH VIỆN BƯU ĐIỆN"); set_style(ws_abc.cell(1, 1), font=font_subtitle)
    ws_abc.cell(2, 1, f"Đơn vị: {phong_ban}"); set_style(ws_abc.cell(2, 1), font=font_subtitle)
    ws_abc.cell(3, 1, f"BẢNG BÌNH BẦU XẾP LOẠI LAO ĐỘNG THÁNG {month:02d}/{year}")
    ws_abc.merge_cells("A3:N3")
    set_style(ws_abc.cell(3, 1), font=font_title, alignment=align_center)

    headers_abc = [
        "STT", "Mã NV", "HỌ VÀ TÊN", "CHỨC VỤ", 
        "ĐI LÀM (X/XX)", "TRỰC (T)", "NGHỈ BÙ (B/BB)", "NGHỈ PHÉP (P/PP)",
        "THAI SẢN (TS)", "NGHỈ ỐM (Ô/ÔÔ)", "CÔNG TÁC (C/CC)", "ĐI HỌC (H/HH)",
        "XẾP LOẠI", "TỒN BÙ CÒN LẠI"
    ]
    for col_i, h in enumerate(headers_abc, 1):
        c = ws_abc.cell(5, col_i, h)
        set_style(c, font=font_header, fill=fill_header_default, alignment=align_center)

    for idx, nv in enumerate(nv_list, start=6):
        ws_abc.cell(idx, 1, idx - 5)
        ws_abc.cell(idx, 2, nv["ma_cb"])
        ws_abc.cell(idx, 3, nv["ho_ten"])
        ws_abc.cell(idx, 4, nv["chuc_vu"])
        
        nv_row = idx - 1  # Dòng tương ứng bên sheet NHÂN VIÊN
        ws_abc.cell(idx, 5, f"='NHÂN VIÊN'!{get_column_letter(start_sum)}{nv_row}")       # Đi làm
        ws_abc.cell(idx, 6, f"='NHÂN VIÊN'!{get_column_letter(start_sum+7)}{nv_row}")     # Trực
        ws_abc.cell(idx, 7, f"='NHÂN VIÊN'!{get_column_letter(start_sum+8)}{nv_row}")     # Nghỉ bù
        ws_abc.cell(idx, 8, f"=(COUNTIF('NHÂN VIÊN'!D{nv_row}:AH{nv_row},\"PP\")+COUNTIF('NHÂN VIÊN'!D{nv_row}:AH{nv_row},\"pp\")) + (COUNTIF('NHÂN VIÊN'!D{nv_row}:AH{nv_row},\"P\")+COUNTIF('NHÂN VIÊN'!D{nv_row}:AH{nv_row},\"p\"))*0.5") # Nghỉ phép
        ws_abc.cell(idx, 9, f"='NHÂN VIÊN'!{get_column_letter(start_sum+10)}{nv_row}")    # Thai sản
        ws_abc.cell(idx, 10, f"='NHÂN VIÊN'!{get_column_letter(start_sum+12)}{nv_row}")   # Nghỉ ốm
        ws_abc.cell(idx, 11, f"='NHÂN VIÊN'!{get_column_letter(start_sum+11)}{nv_row}")   # Công tác
        ws_abc.cell(idx, 12, f"='NHÂN VIÊN'!{get_column_letter(start_sum+13)}{nv_row}")   # Đi học
        ws_abc.cell(idx, 13, "A")                                                       # Xếp loại
        ws_abc.cell(idx, 14, f"='NHÂN VIÊN'!{get_column_letter(start_sum+9)}{nv_row}")    # Tồn bù còn lại
        
        for c_idx in range(1, 15):
            cell = ws_abc.cell(idx, c_idx)
            set_style(cell, font=font_data, border=thin_border)
            cell.alignment = align_center_nowrap if (c_idx in [1, 2] or c_idx >= 5) else align_left

    # Đảm bảo bật lưới hiển thị ô cho toàn bộ sheet
    for ws in wb.worksheets:
        ws.views.sheetView[0].showGridLines = True
        for col in ws.columns:
            max_len = max(len(str(cell.value or '')) for cell in col)
            col_letter = get_column_letter(col[0].column)
            ws.column_dimensions[col_letter].width = max(max_len + 3, 10)

    output = io.BytesIO()
    wb.save(output)
    return output.getvalue()
