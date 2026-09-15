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
# HÀM TẠO FILE EXCEL MẪU TỰ ĐỘNG CÓ DỮ LIỆU & CÔNG THỨC MỚI
# ---------------------------------------------------------------------
def generate_excel_mau_cham_cong(month: int, year: int, phong_ban: str, df_cb: pd.DataFrame) -> bytes:
    wb = openpyxl.Workbook()
    
    # 1. Lấy danh sách nhân viên thuộc Khoa / Phòng
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
            {"ma_cb": "N1971", "ho_ten": "Khuất Duy Tiến", "chuc_vu": "Trưởng khoa"},
            {"ma_cb": "N2088", "ho_ten": "Nguyễn Văn An", "chuc_vu": "Bác sĩ"},
            {"ma_cb": "N2105", "ho_ten": "Trần Thị Bình", "chuc_vu": "Điều dưỡng"},
            {"ma_cb": "N2130", "ho_ten": "Phạm Quốc Cường", "chuc_vu": "Kỹ thuật viên"},
            {"ma_cb": "N2155", "ho_ten": "Lê Thị Dung", "chuc_vu": "Điều dưỡng"}
        ]

    # Style chuẩn
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

    # Xác định các cột ngày T7, CN và Lễ
    weekend_holiday_cols = []
    for d in range(1, num_days + 1):
        _, day_type = get_day_fill_and_type(d, month, year)
        if day_type in ["SAT", "SUN", "HOLIDAY"]:
            weekend_holiday_cols.append(get_column_letter(3 + d))

    # =====================================================================
    # TAB 1: NHÂN VIÊN
    # =====================================================================
    ws_nv = wb.active
    ws_nv.title = "NHÂN VIÊN"
    
    set_style(ws_nv.cell(1, 1, "BỆNH VIỆN BƯU ĐIỆN"), font=font_subtitle)
    ws_nv.cell(1, 4, f"BẢNG CHẤM CÔNG THÁNG {month:02d} NĂM {year} CỦA CBNV")
    ws_nv.merge_cells(start_row=1, start_column=4, end_row=1, end_column=num_days + 15)
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
    # Tổng hợp các loại ngày công
    ws_nv.cell(3, start_sum, "Hành chính"); ws_nv.merge_cells(start_row=3, start_column=start_sum, end_row=4, end_column=start_sum)
    ws_nv.cell(3, start_sum+1, "Làm T7/CN/Lễ"); ws_nv.merge_cells(start_row=3, start_column=start_sum+1, end_row=4, end_column=start_sum+1)
    ws_nv.cell(3, start_sum+2, "Trực T7/CN/Lễ"); ws_nv.merge_cells(start_row=3, start_column=start_sum+2, end_row=4, end_column=start_sum+2)
    ws_nv.cell(3, start_sum+3, "Trực ngoài giờ"); ws_nv.merge_cells(start_row=3, start_column=start_sum+3, end_row=4, end_column=start_sum+3)
    
    ws_nv.cell(3, start_sum+4, "Nghỉ bù"); ws_nv.merge_cells(start_row=3, start_column=start_sum+4, end_row=3, end_column=start_sum+5)
    ws_nv.cell(4, start_sum+4, "Đã nghỉ")
    ws_nv.cell(4, start_sum+5, "Còn lại") # Sử dụng MAX(0, ...) loại bỏ dấu -
    
    ws_nv.cell(3, start_sum+6, "Thai sản"); ws_nv.merge_cells(start_row=3, start_column=start_sum+6, end_row=4, end_column=start_sum+6)
    ws_nv.cell(3, start_sum+7, "Công tác"); ws_nv.merge_cells(start_row=3, start_column=start_sum+7, end_row=4, end_column=start_sum+7)
    ws_nv.cell(3, start_sum+8, "Nghỉ ốm"); ws_nv.merge_cells(start_row=3, start_column=start_sum+8, end_row=4, end_column=start_sum+8)
    ws_nv.cell(3, start_sum+9, "Đi học"); ws_nv.merge_cells(start_row=3, start_column=start_sum+9, end_row=4, end_column=start_sum+9)
    ws_nv.cell(3, start_sum+10, "Tồn bù"); ws_nv.merge_cells(start_row=3, start_column=start_sum+10, end_row=4, end_column=start_sum+10)

    for r in range(3, 5):
        for c in range(1, start_sum + 11):
            cell = ws_nv.cell(r, c)
            f_font = font_sub_header if (r == 4 and c in [start_sum+4, start_sum+5]) else font_header
            f_fill = day_fills[c] if (4 <= c <= 3 + num_days and r == 4) else fill_header_default
            set_style(cell, font=f_font, fill=f_fill, alignment=align_center)

    # Đổ danh sách cán bộ & công thức
    for idx, nv in enumerate(nv_list, start=5):
        ws_nv.cell(idx, 1, idx - 4)
        ws_nv.cell(idx, 2, nv["ma_cb"])
        ws_nv.cell(idx, 3, nv["ho_ten"])
        
        start_l = get_column_letter(4)
        end_l = get_column_letter(3 + num_days)
        
        # 1. Hành chính: X = 0.5, XX = 1
        ws_nv.cell(idx, start_sum, f'=COUNTIF({start_l}{idx}:{end_l}{idx}, "XX") + COUNTIF({start_l}{idx}:{end_l}{idx}, "X")*0.5')
        
        # 2. Làm T7/CN/Lễ: X=0.5, XX=1 trên các cột T7/CN/Lễ
        if weekend_holiday_cols:
            formula_lam_t7 = " + ".join([f'IF({col}{idx}="XX",1,IF({col}{idx}="X",0.5,0))' for col in weekend_holiday_cols])
            ws_nv.cell(idx, start_sum+1, f'={formula_lam_t7}')
            
            # 3. Trực T7/CN/Lễ: Đếm 'T' trên các cột T7/CN/Lễ
            formula_truc_t7 = " + ".join([f'IF({col}{idx}="T",1,0)' for col in weekend_holiday_cols])
            ws_nv.cell(idx, start_sum+2, f'={formula_truc_t7}')
        else:
            ws_nv.cell(idx, start_sum+1, 0)
            ws_nv.cell(idx, start_sum+2, 0)

        # 4. Trực ngoài giờ chung
        ws_nv.cell(idx, start_sum+3, f'=COUNTIF({start_l}{idx}:{end_l}{idx}, "T")')
        
        # 5. Nghỉ bù: Đã nghỉ
        ws_nv.cell(idx, start_sum+4, f'=COUNTIF({start_l}{idx}:{end_l}{idx}, "BB") + COUNTIF({start_l}{idx}:{end_l}{idx}, "B")*0.5')
        
        # 6. Nghỉ bù: Còn lại (Sử dụng MAX để không bị dấu -)
        ton_bu_col = get_column_letter(start_sum+10)
        da_nghi_col = get_column_letter(start_sum+4)
        ws_nv.cell(idx, start_sum+5, f'=MAX(0, {ton_bu_col}{idx} - {da_nghi_col}{idx})')
        
        # 7. Thai sản, Công tác, Ốm, Học
        ws_nv.cell(idx, start_sum+6, f'=COUNTIF({start_l}{idx}:{end_l}{idx}, "TS")')
        ws_nv.cell(idx, start_sum+7, f'=COUNTIF({start_l}{idx}:{end_l}{idx}, "CC") + COUNTIF({start_l}{idx}:{end_l}{idx}, "C")*0.5')
        ws_nv.cell(idx, start_sum+8, f'=COUNTIF({start_l}{idx}:{end_l}{idx}, "ÔÔ") + COUNTIF({start_l}{idx}:{end_l}{idx}, "Ô")*0.5')
        ws_nv.cell(idx, start_sum+9, f'=COUNTIF({start_l}{idx}:{end_l}{idx}, "HH") + COUNTIF({start_l}{idx}:{end_l}{idx}, "H")*0.5')
        ws_nv.cell(idx, start_sum+10, 0) # Tồn bù ban đầu

        for c_idx in range(1, start_sum + 11):
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
    ws_nv.cell(sign_row, start_sum + 5, "Người lập biểu")
    set_style(ws_nv.cell(sign_row, start_sum + 5), font=font_bold)

    # =====================================================================
    # TAB 2: HTCS
    # =====================================================================
    ws_htcs = wb.create_sheet(title="HTCS")
    set_style(ws_htcs.cell(1, 1, "BỆNH VIỆN BƯU ĐIỆN"), font=font_subtitle)
    ws_htcs.cell(1, 4, f"BẢNG CHẤM CÔNG THÁNG {month:02d} NĂM {year} CỦA NHÂN VIÊN LAO ĐỘNG THUÊ LẠI")
    ws_htcs.merge_cells(start_row=1, start_column=4, end_row=1, end_column=num_days + 11)
    set_style(ws_htcs.cell(1, 4), font=font_title, alignment=align_center)
    
    set_style(ws_htcs.cell(2, 1, f"Đơn vị: {phong_ban}"), font=font_subtitle)

    ws_htcs.cell(3, 1, "STT"); ws_htcs.merge_cells("A3:A4")
    ws_htcs.cell(3, 2, "Mã NV"); ws_htcs.merge_cells("B3:B4")
    ws_htcs.cell(3, 3, "Họ và tên"); ws_htcs.merge_cells("C3:C4")
    
    ws_htcs.cell(3, 4, f"Ngày làm việc trong tháng {month:02d}.{year}")
    ws_htcs.merge_cells(start_row=3, start_column=4, end_row=3, end_column=3 + num_days)

    for d in range(1, num_days + 1):
        col_idx = 3 + d
        ws_htcs.cell(4, col_idx, f"{d:02d}")

    ws_htcs.cell(3, start_sum, "Hành chính"); ws_htcs.merge_cells(start_row=3, start_column=start_sum, end_row=4, end_column=start_sum)
    ws_htcs.cell(3, start_sum+1, "Làm T7/CN/Lễ"); ws_htcs.merge_cells(start_row=3, start_column=start_sum+1, end_row=4, end_column=start_sum+1)
    ws_htcs.cell(3, start_sum+2, "Trực T7/CN/Lễ"); ws_htcs.merge_cells(start_row=3, start_column=start_sum+2, end_row=4, end_column=start_sum+2)
    ws_htcs.cell(3, start_sum+3, "Trực ngoài giờ"); ws_htcs.merge_cells(start_row=3, start_column=start_sum+3, end_row=4, end_column=start_sum+3)
    ws_htcs.cell(3, start_sum+4, "Nghỉ bù"); ws_htcs.merge_cells(start_row=3, start_column=start_sum+4, end_row=3, end_column=start_sum+5)
    
    ws_htcs.cell(4, start_sum+4, "Đã nghỉ")
    ws_htcs.cell(4, start_sum+5, "Còn lại") # Sử dụng MAX(0, ...)
    ws_htcs.cell(3, start_sum+6, "Tồn bù"); ws_htcs.merge_cells(start_row=3, start_column=start_sum+6, end_row=4, end_column=start_sum+6)

    for r in range(3, 5):
        for c in range(1, start_sum + 7):
            cell = ws_htcs.cell(r, c)
            f_font = font_sub_header if (r == 4 and c in [start_sum+4, start_sum+5]) else font_header
            f_fill = day_fills[c] if (4 <= c <= 3 + num_days and r == 4) else fill_header_default
            set_style(cell, font=f_font, fill=f_fill, alignment=align_center)

    for idx, nv in enumerate(nv_list, start=5):
        ws_htcs.cell(idx, 1, idx - 4)
        ws_htcs.cell(idx, 2, nv["ma_cb"])
        ws_htcs.cell(idx, 3, nv["ho_ten"])
        
        start_l = get_column_letter(4)
        end_l = get_column_letter(3 + num_days)
        
        ws_htcs.cell(idx, start_sum, f'=COUNTIF({start_l}{idx}:{end_l}{idx}, "XX") + COUNTIF({start_l}{idx}:{end_l}{idx}, "X")*0.5')
        
        if weekend_holiday_cols:
            formula_lam_t7 = " + ".join([f'IF({col}{idx}="XX",1,IF({col}{idx}="X",0.5,0))' for col in weekend_holiday_cols])
            ws_htcs.cell(idx, start_sum+1, f'={formula_lam_t7}')
            formula_truc_t7 = " + ".join([f'IF({col}{idx}="T",1,0)' for col in weekend_holiday_cols])
            ws_htcs.cell(idx, start_sum+2, f'={formula_truc_t7}')
        else:
            ws_htcs.cell(idx, start_sum+1, 0)
            ws_htcs.cell(idx, start_sum+2, 0)

        ws_htcs.cell(idx, start_sum+3, f'=COUNTIF({start_l}{idx}:{end_l}{idx}, "T")')
        ws_htcs.cell(idx, start_sum+4, f'=COUNTIF({start_l}{idx}:{end_l}{idx}, "BB") + COUNTIF({start_l}{idx}:{end_l}{idx}, "B")*0.5')
        
        ton_col = get_column_letter(start_sum+6)
        da_nghi_c = get_column_letter(start_sum+4)
        ws_htcs.cell(idx, start_sum+5, f'=MAX(0, {ton_col}{idx} - {da_nghi_c}{idx})')
        ws_htcs.cell(idx, start_sum+6, 0)
        
        for c_idx in range(1, start_sum + 7):
            cell = ws_htcs.cell(idx, c_idx)
            f_fill = day_fills[c_idx] if (c_idx in day_fills and day_fills[c_idx] != fill_header_default) else None
            set_style(cell, font=font_data, fill=f_fill, border=thin_border)
            if c_idx in [1, 2] or c_idx >= 4:
                cell.alignment = align_center_no_wrap
            elif c_idx == 3:
                cell.alignment = align_left

    ws_htcs.cell(sign_row, 3, "Lãnh đạo đơn vị")
    set_style(ws_htcs.cell(sign_row, 3), font=font_bold)
    ws_htcs.cell(sign_row, start_sum + 3, "Người lập biểu")
    set_style(ws_htcs.cell(sign_row, start_sum + 3), font=font_bold)

    # =====================================================================
    # TAB 3: LÀM THỨ 7 (CÔNG THỨC QUY ĐỔI X = 0.5, XX = 1)
    # =====================================================================
    ws_t7 = wb.create_sheet(title="LÀM THỨ 7")
    set_style(ws_t7.cell(1, 1, "BỆNH VIỆN BƯU ĐIỆN"), font=font_subtitle)
    ws_t7.cell(1, 4, f"BẢNG CHẤM CÔNG NGÀY LÀM THỨ 7, CHỦ NHẬT & NGÀY LỄ CỦA CBNV THÁNG {month:02d}/{year}")
    
    weekend_days = []
    for d in range(1, num_days + 1):
        fill_color, day_type = get_day_fill_and_type(d, month, year)
        if day_type in ["SAT", "SUN", "HOLIDAY"]:
            weekend_days.append((d, fill_color, day_type))
            
    num_we_cols = len(weekend_days)
    tot_col = 4 + num_we_cols
    
    ws_t7.merge_cells(start_row=1, start_column=4, end_row=1, end_column=tot_col)
    set_style(ws_t7.cell(1, 4), font=font_title, alignment=align_center)
    set_style(ws_t7.cell(2, 1, f"Đơn vị: {phong_ban}"), font=font_subtitle)

    ws_t7.cell(3, 1, "STT")
    ws_t7.cell(3, 2, "Mã NV")
    ws_t7.cell(3, 3, "Họ và tên")
    
    set_style(ws_t7.cell(3, 1), font=font_header, fill=fill_header_default, alignment=align_center)
    set_style(ws_t7.cell(3, 2), font=font_header, fill=fill_header_default, alignment=align_center)
    set_style(ws_t7.cell(3, 3), font=font_header, fill=fill_header_default, alignment=align_center)

    for w_i, (d, fill_color, _) in enumerate(weekend_days, start=4):
        c = ws_t7.cell(3, w_i, f"Ngày {d:02d}")
        set_style(c, font=font_header, fill=fill_color, alignment=align_center)
        
    ws_t7.cell(3, tot_col, "Tổng ngày công")
    set_style(ws_t7.cell(3, tot_col), font=font_header, fill=fill_header_default, alignment=align_center)

    for idx, nv in enumerate(nv_list, start=4):
        ws_t7.cell(idx, 1, idx - 3)
        ws_t7.cell(idx, 2, nv["ma_cb"])
        ws_t7.cell(idx, 3, nv["ho_ten"])
        
        # Công thức X = 0.5, XX = 1, T = 1
        st_l = get_column_letter(4)
        en_l = get_column_letter(tot_col - 1)
        ws_t7.cell(idx, tot_col, f'=COUNTIF({st_l}{idx}:{en_l}{idx}, "XX") + COUNTIF({st_l}{idx}:{en_l}{idx}, "T") + COUNTIF({st_l}{idx}:{en_l}{idx}, "X")*0.5')
        
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
    ws_t7.cell(sign_r_t7, max(4, tot_col - 1), "Người lập biểu")
    set_style(ws_t7.cell(sign_r_t7, max(4, tot_col - 1)), font=font_bold)

    # =====================================================================
    # TAB 4: ABC (HIỂN THỊ ĐẦY ĐỦ CÁC CỘT THEO KÝ HIỆU CHẤM CÔNG)
    # =====================================================================
    ws_abc = wb.create_sheet(title="ABC")
    set_style(ws_abc.cell(1, 1, "BỆNH VIỆN BƯU ĐIỆN"), font=font_subtitle)
    set_style(ws_abc.cell(2, 1, f"Đơn vị: {phong_ban}"), font=font_subtitle)
    ws_abc.cell(3, 1, f"BẢNG BÌNH BẦU XẾP LOẠI LAO ĐỘNG THÁNG {month:02d}/{year}")
    ws_abc.merge_cells("A3:M3")
    set_style(ws_abc.cell(3, 1), font=font_title, alignment=align_center)

    # Cột tên chuẩn đầy đủ ký hiệu chấm công
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
        
        # Link công thức chính xác từ sheet NHÂN VIÊN
        ws_abc.cell(idx, 5, f"='NHÂN VIÊN'!{get_column_letter(start_sum)}{idx-1}")       # Đi làm (Hành chính)
        ws_abc.cell(idx, 6, f"='NHÂN VIÊN'!{get_column_letter(start_sum+3)}{idx-1}")     # Trực
        ws_abc.cell(idx, 7, f"='NHÂN VIÊN'!{get_column_letter(start_sum+4)}{idx-1}")     # Nghỉ bù (Đã nghỉ)
        ws_abc.cell(idx, 8, f"=COUNTIF('NHÂN VIÊN'!D{idx-1}:AH{idx-1}, \"PP\") + COUNTIF('NHÂN VIÊN'!D{idx-1}:AH{idx-1}, \"P\")*0.5") # Nghỉ phép
        ws_abc.cell(idx, 9, f"='NHÂN VIÊN'!{get_column_letter(start_sum+6)}{idx-1}")     # Thai sản
        ws_abc.cell(idx, 10, f"='NHÂN VIÊN'!{get_column_letter(start_sum+8)}{idx-1}")    # Nghỉ ốm
        ws_abc.cell(idx, 11, f"='NHÂN VIÊN'!{get_column_letter(start_sum+7)}{idx-1}")    # Công tác
        ws_abc.cell(idx, 12, f"='NHÂN VIÊN'!{get_column_letter(start_sum+9)}{idx-1}")    # Đi học
        ws_abc.cell(idx, 13, "A")                                                        # Xếp loại
        ws_abc.cell(idx, 14, f"='NHÂN VIÊN'!{get_column_letter(start_sum+5)}{idx-1}")    # Tồn bù còn lại
        
        for c_idx in range(1, 15):
            cell = ws_abc.cell(idx, c_idx)
            set_style(cell, font=font_data, border=thin_border)
            if c_idx in [1, 2] or c_idx >= 5:
                cell.alignment = align_center_no_wrap
            elif c_idx in [3, 4]:
                cell.alignment = align_left

    sign_r_abc = len(nv_list) + 8
    ws_abc.cell(sign_r_abc, 3, "Lãnh đạo đơn vị")
    set_style(ws_abc.cell(sign_r_abc, 3), font=font_bold)
    ws_abc.cell(sign_r_abc, 12, "Người lập biểu")
    set_style(ws_abc.cell(sign_r_abc, 12), font=font_bold)

    # =====================================================================
    # TAB 5: KÝ HIỆU CHẤM CÔNG
    # =====================================================================
    ws_kh = wb.create_sheet(title="Ký hiệu")
    set_style(ws_kh.cell(1, 1, "BẢNG GIẢI THÍCH KÝ HIỆU CHẤM CÔNG"), font=font_title)
    
    ky_hieu_data = [
        ("X", "công đi làm 1/2 ngày trong giờ hành chính (tính 0.5 công)"),
        ("XX", "công đi làm 1 ngày trong giờ hành chính (tính 1.0 công)"),
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
    # CĂN CHỈNH ĐỘ RỘNG CÁC CỘT CỐ ĐỊNH CHUẨN XÁC
    # =====================================================================
    for ws in wb.worksheets:
        if ws.title in ["NHÂN VIÊN", "HTCS"]:
            ws.column_dimensions['A'].width = 8   # STT
            ws.column_dimensions['B'].width = 12  # Mã NV
            ws.column_dimensions['C'].width = 25  # Họ và tên
            
            for d in range(1, num_days + 1):
                ws.column_dimensions[get_column_letter(3 + d)].width = 4.5
                
            for s_i in range(start_sum, start_sum + 12):
                ws.column_dimensions[get_column_letter(s_i)].width = 13
                
        elif ws.title == "LÀM THỨ 7":
            ws.column_dimensions['A'].width = 8
            ws.column_dimensions['B'].width = 12
            ws.column_dimensions['C'].width = 25
            for w_i in range(4, tot_col):
                ws.column_dimensions[get_column_letter(w_i)].width = 11
            ws.column_dimensions[get_column_letter(tot_col)].width = 14
            
        elif ws.title == "ABC":
            ws.column_dimensions['A'].width = 8
            ws.column_dimensions['B'].width = 12
            ws.column_dimensions['C'].width = 25
            ws.column_dimensions['D'].width = 18
            for c_i in range(5, 15):
                ws.column_dimensions[get_column_letter(c_i)].width = 15
                
        elif ws.title == "Ký hiệu":
            ws.column_dimensions['A'].width = 12
            ws.column_dimensions['B'].width = 75

    output = io.BytesIO()
    wb.save(output)
    return output.getvalue()
