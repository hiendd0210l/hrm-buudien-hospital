import io
import calendar
import pandas as pd
import streamlit as st
from datetime import datetime, date
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

# =====================================================================
# 1. HÀM BỔ TRỢ PHÂN LOẠI NGÀY & CẤU HÌNH STYLE EXCEL
# =====================================================================
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

def set_optimal_column_widths(ws):
    for col in ws.columns:
        col_idx = col[0].column
        col_letter = get_column_letter(col_idx)
        
        if col_idx == 1:       # STT
            ws.column_dimensions[col_letter].width = 5
        elif col_idx == 2:     # Mã NV
            ws.column_dimensions[col_letter].width = 11
        elif col_idx in [3, 4] and ws.title in ["NHÂN VIÊN", "HTCS", "LÀM THỨ 7"]:
            if col_idx == 3:
                ws.column_dimensions[col_letter].width = 22
            else:
                ws.column_dimensions[col_letter].width = 6
        elif ws.title == "ABC" and col_idx == 4: # Chức vụ
            ws.column_dimensions[col_letter].width = 18
        else:
            ws.column_dimensions[col_letter].width = 7

# =====================================================================
# 2. HÀM TẠO FILE EXCEL CHUẨN 4 SHEET
# =====================================================================
def generate_excel_mau_cham_cong(month: int, year: int, phong_ban: str, df_cb: pd.DataFrame = None) -> bytes:
    wb = openpyxl.Workbook()
    
    nv_list = []
    htcs_list = []

    if df_cb is not None and not df_cb.empty and 'khoa_phong' in df_cb.columns:
        if phong_ban and phong_ban != "Tất cả khoa/phòng/trung tâm":
            df_dept = df_cb[df_cb['khoa_phong'] == phong_ban].copy()
        else:
            df_dept = df_cb.copy()
            
        if not df_dept.empty:
            for _, row in df_dept.iterrows():
                item = {
                    "ma_cb": str(row.get('ma_can_bo', '')),
                    "ho_ten": str(row.get('ho_ten', '')),
                    "chuc_vu": str(row.get('chuc_vu', 'Nhân viên')),
                    "khoa_phong": str(row.get('khoa_phong', '')),
                    "ton_bu_dau_ky": float(row.get('ton_bu_dau_ky', 0))
                }
                loai_hd = str(row.get('loai_hop_dong', '')).upper()
                if 'HTCS' in loai_hd or 'THUÊ LẠI' in loai_hd or 'THUE LAI' in loai_hd:
                    htcs_list.append(item)
                else:
                    nv_list.append(item)

    if not nv_list and not htcs_list:
        nv_list = [
            {"ma_cb": "N0883", "ho_ten": "Vũ Hồng Vân", "chuc_vu": "Bác sĩ", "khoa_phong": "Phòng Nhân sự", "ton_bu_dau_ky": 0},
            {"ma_cb": "N0901", "ho_ten": "Phạm Thị Quý Nhi", "chuc_vu": "Bác sĩ", "khoa_phong": "Phòng Nhân sự", "ton_bu_dau_ky": 0},
            {"ma_cb": "N0872", "ho_ten": "Lê Hà Minh", "chuc_vu": "Bác sĩ", "khoa_phong": "Phòng Nhân sự", "ton_bu_dau_ky": 0},
            {"ma_cb": "N0648", "ho_ten": "Đỗ Thị Mai Quyên", "chuc_vu": "Chuyên viên", "khoa_phong": "Phòng Nhân sự", "ton_bu_dau_ky": 0},
            {"ma_cb": "N0591", "ho_ten": "Phạm Thị Thanh Hương", "chuc_vu": "Chuyên viên", "khoa_phong": "Phòng Nhân sự", "ton_bu_dau_ky": 0}
        ]
        htcs_list = [
            {"ma_cb": "HT001", "ho_ten": "Nguyễn Văn Hỗ Trợ", "chuc_vu": "Lao động thuê lại", "khoa_phong": "Phòng Nhân sự", "ton_bu_dau_ky": 0}
        ]

    font_title = Font(name="Arial", size=12, bold=True, color="002060")
    font_subtitle = Font(name="Arial", size=10, bold=True)
    font_header = Font(name="Arial", size=9, bold=True)
    font_data = Font(name="Arial", size=10)
    
    fill_header_default = PatternFill(start_color="D9E1F2", end_color="D9E1F2", fill_type="solid")
    fill_total = PatternFill(start_color="FFF2CC", end_color="FFF2CC", fill_type="solid")
    
    align_center = Alignment(horizontal="center", vertical="center", wrap_text=True)
    align_left = Alignment(horizontal="left", vertical="center")
    align_center_nowrap = Alignment(horizontal="center", vertical="center")
    
    thin_border = Border(
        left=Side(style='thin', color='BFBFBF'), right=Side(style='thin', color='BFBFBF'),
        top=Side(style='thin', color='BFBFBF'), bottom=Side(style='thin', color='BFBFBF')
    )
    
    num_days = calendar.monthrange(year, month)[1]

    workday_cols, sat_cols, sun_cols, hol_cols = [], [], [], []
    for d in range(1, num_days + 1):
        col_letter = get_column_letter(3 + d)
        _, day_type = get_day_type(d, month, year)
        if day_type == "WORKDAY":
            workday_cols.append(col_letter)
        elif day_type == "SAT":
            sat_cols.append(col_letter)
        elif day_type == "SUN":
            sun_cols.append(col_letter)
        elif day_type == "HOLIDAY":
            hol_cols.append(col_letter)

    def build_code_formula(col_list, row_idx, single_code, double_code):
        if not col_list:
            return "0"
        sc_u, sc_l = single_code.upper(), single_code.lower()
        dc_u, dc_l = double_code.upper(), double_code.lower()
        parts = [
            f'IF(OR({c}{row_idx}="{dc_u}",{c}{row_idx}="{dc_l}"),1,IF(OR({c}{row_idx}="{sc_u}",{c}{row_idx}="{sc_l}"),0.5,0))' 
            for c in col_list
        ]
        return " + ".join(parts)

    def build_duty_formula(col_list, row_idx):
        if not col_list:
            return "0"
        parts = [f'IF(OR({c}{row_idx}="T",{c}{row_idx}="t"),1,0)' for c in col_list]
        return " + ".join(parts)

    def build_main_sheet(ws, title_sheet, data_list):
        ws.cell(1, 1, "BỆNH VIỆN BƯU ĐIỆN"); set_style(ws.cell(1, 1), font=font_subtitle)
        ws.cell(1, 4, f"BẢNG CHẤM CÔNG THÁNG {month:02d} NĂM {year} ({title_sheet})")
        ws.merge_cells(start_row=1, start_column=4, end_row=1, end_column=num_days + 19)
        set_style(ws.cell(1, 4), font=font_title, alignment=align_center)
        ws.cell(2, 1, f"Đơn vị: {phong_ban}"); set_style(ws.cell(2, 1), font=font_subtitle)
        
        ws.cell(3, 1, "STT"); ws.merge_cells("A3:A4")
        ws.cell(3, 2, "Mã NV"); ws.merge_cells("B3:B4")
        ws.cell(3, 3, "Họ và tên"); ws.merge_cells("C3:C4")
        ws.cell(3, 4, f"Ngày làm việc trong tháng {month:02d}.{year}")
        ws.merge_cells(start_row=3, start_column=4, end_row=3, end_column=3 + num_days)
        
        day_fills = {}
        for d in range(1, num_days + 1):
            col_idx = 3 + d
            ws.cell(4, col_idx, f"{d:02d}")
            fill_color, _ = get_day_type(d, month, year)
            day_fills[col_idx] = fill_color if fill_color else fill_header_default

        start_sum = 4 + num_days
        headers_sum = [
            "Hành chính", "Làm T7", "Làm CN", "Làm Lễ", 
            "Trực T7", "Trực CN", "Trực Lễ", "Trực ngày thường",
            "Đã nghỉ bù", "Nghỉ bù còn", "Nghỉ phép", "Thai sản", "Công tác", "Nghỉ ốm", "Đi học", "Tồn bù"
        ]
        for i, h in enumerate(headers_sum):
            c_idx = start_sum + i
            ws.cell(3, c_idx, h)
            ws.merge_cells(start_row=3, start_column=c_idx, end_row=4, end_column=c_idx)

        for r in range(3, 5):
            for c in range(1, start_sum + len(headers_sum)):
                cell = ws.cell(r, c)
                f_fill = day_fills[c] if (4 <= c <= 3 + num_days and r == 4) else fill_header_default
                set_style(cell, font=font_header, fill=f_fill, alignment=align_center)

        all_month_cols = [get_column_letter(3 + d) for d in range(1, num_days + 1)]

        for idx, nv in enumerate(data_list, start=5):
            ws.cell(idx, 1, idx - 4)
            ws.cell(idx, 2, nv["ma_cb"])
            ws.cell(idx, 3, nv["ho_ten"])
            
            # Ngày công & Trực
            ws.cell(idx, start_sum, f'={build_code_formula(workday_cols, idx, "x", "xx")}')
            ws.cell(idx, start_sum+1, f'={build_code_formula(sat_cols, idx, "x", "xx")}')
            ws.cell(idx, start_sum+2, f'={build_code_formula(sun_cols, idx, "x", "xx")}')
            ws.cell(idx, start_sum+3, f'={build_code_formula(hol_cols, idx, "x", "xx")}')
            
            ws.cell(idx, start_sum+4, f'={build_duty_formula(sat_cols, idx)}')       
            ws.cell(idx, start_sum+5, f'={build_duty_formula(sun_cols, idx)}')       
            ws.cell(idx, start_sum+6, f'={build_duty_formula(hol_cols, idx)}')       
            ws.cell(idx, start_sum+7, f'={build_duty_formula(workday_cols, idx)}')   
            
            # Đã nghỉ bù
            ws.cell(idx, start_sum+8, f'={build_code_formula(all_month_cols, idx, "b", "bb")}')
            
            c_truc_t7 = get_column_letter(start_sum+4)
            c_truc_cn = get_column_letter(start_sum+5)
            c_truc_le = get_column_letter(start_sum+6)
            c_truc_th = get_column_letter(start_sum+7)
            c_da_nghi = get_column_letter(start_sum+8)
            c_ton_bu  = get_column_letter(start_sum+15)

            ton_dau_ky = nv.get("ton_bu_dau_ky", 0)

            # Tồn bù
            ws.cell(idx, start_sum+15, f'={ton_dau_ky} + ({c_truc_t7}{idx} + {c_truc_cn}{idx} + {c_truc_th}{idx})*1 + ({c_truc_le}{idx})*2')

            # Nghỉ bù còn
            ws.cell(idx, start_sum+9, f'=MAX(0, {c_ton_bu}{idx} - {c_da_nghi}{idx})')

            # Nghỉ phép (p/pp)
            ws.cell(idx, start_sum+10, f'={build_code_formula(all_month_cols, idx, "p", "pp")}')

            # Thai sản, Công tác, Nghỉ ốm, Đi học
            ws.cell(idx, start_sum+11, f'={build_code_formula(all_month_cols, idx, "ts", "ts")}')
            ws.cell(idx, start_sum+12, f'={build_code_formula(all_month_cols, idx, "c", "cc")}')
            ws.cell(idx, start_sum+13, f'={build_code_formula(all_month_cols, idx, "ô", "ôô")}')
            ws.cell(idx, start_sum+14, f'={build_code_formula(all_month_cols, idx, "h", "hh")}')

            for c_idx in range(1, start_sum + len(headers_sum)):
                cell = ws.cell(idx, c_idx)
                f_fill = day_fills[c_idx] if (c_idx in day_fills and day_fills[c_idx] != fill_header_default) else None
                set_style(cell, font=font_data, fill=f_fill, border=thin_border)
                cell.alignment = align_center_nowrap if (c_idx in [1, 2] or c_idx >= 4) else align_left
        return start_sum

    # SHEET 1: NHÂN VIÊN
    ws_nv = wb.active
    ws_nv.title = "NHÂN VIÊN"
    start_sum = build_main_sheet(ws_nv, "CỦA CBNV", nv_list)

    # SHEET 2: HTCS
    ws_htcs = wb.create_sheet(title="HTCS")
    build_main_sheet(ws_htcs, "LAO ĐỘNG THUÊ LẠI / HTCS", htcs_list)

    # SHEET 3: LÀM THỨ 7
    ws_t7 = wb.create_sheet(title="LÀM THỨ 7")
    ws_t7.cell(1, 1, "BỆNH VIỆN BƯU ĐIỆN"); set_style(ws_t7.cell(1, 1), font=font_subtitle)
    ws_t7.cell(1, 4, f"BẢNG CHẤM CÔNG NGÀY LÀM THỨ 7, CHỦ NHẬT & NGÀY LỄ THÁNG {month:02d}/{year}")
    
    weekend_days = []
    wk_sat_sun_cols, wk_holiday_cols = [], []
    for d in range(1, num_days + 1):
        fill_color, day_type = get_day_type(d, month, year)
        if day_type in ["SAT", "SUN", "HOLIDAY"]:
            col_letter = get_column_letter(4 + len(weekend_days))
            weekend_days.append((d, fill_color, day_type))
            if day_type in ["SAT", "SUN"]:
                wk_sat_sun_cols.append(col_letter)
            else:
                wk_holiday_cols.append(col_letter)
            
    c_tot_sat = 4 + len(weekend_days)
    c_tot_hol = c_tot_sat + 1
    c_tot_all = c_tot_sat + 2

    ws_t7.merge_cells(start_row=1, start_column=4, end_row=1, end_column=c_tot_all)
    set_style(ws_t7.cell(1, 4), font=font_title, alignment=align_center)
    ws_t7.cell(2, 1, f"Đơn vị: {phong_ban}"); set_style(ws_t7.cell(2, 1), font=font_subtitle)

    ws_t7.cell(3, 1, "STT"); set_style(ws_t7.cell(3, 1), font=font_header, fill=fill_header_default, alignment=align_center)
    ws_t7.cell(3, 2, "Mã NV"); set_style(ws_t7.cell(3, 2), font=font_header, fill=fill_header_default, alignment=align_center)
    ws_t7.cell(3, 3, "Họ và tên"); set_style(ws_t7.cell(3, 3), font=font_header, fill=fill_header_default, alignment=align_center)

    for w_i, (d, fill_color, _) in enumerate(weekend_days, start=4):
        c = ws_t7.cell(3, w_i, f"Ngày {d:02d}")
        set_style(c, font=font_header, fill=fill_color, alignment=align_center)
        
    ws_t7.cell(3, c_tot_sat, "Tổng T7, CN")
    set_style(ws_t7.cell(3, c_tot_sat), font=font_header, fill=fill_header_default, alignment=align_center)

    ws_t7.cell(3, c_tot_hol, "Tổng Lễ/Tết")
    set_style(ws_t7.cell(3, c_tot_hol), font=font_header, fill=fill_header_default, alignment=align_center)

    ws_t7.cell(3, c_tot_all, "Tổng cộng")
    set_style(ws_t7.cell(3, c_tot_all), font=font_header, fill=fill_total, alignment=align_center)

    all_comb_list = nv_list + htcs_list
    for idx, nv in enumerate(all_comb_list, start=4):
        ws_t7.cell(idx, 1, idx - 3)
        ws_t7.cell(idx, 2, nv["ma_cb"])
        ws_t7.cell(idx, 3, nv["ho_ten"])
        
        ws_t7.cell(idx, c_tot_sat, f'={build_code_formula(wk_sat_sun_cols, idx, "x", "xx")} + {build_duty_formula(wk_sat_sun_cols, idx)}')
        ws_t7.cell(idx, c_tot_hol, f'={build_code_formula(wk_holiday_cols, idx, "x", "xx")} + {build_duty_formula(wk_holiday_cols, idx)}')
        
        c_sat_l = get_column_letter(c_tot_sat)
        c_hol_l = get_column_letter(c_tot_hol)
        ws_t7.cell(idx, c_tot_all, f'={c_sat_l}{idx} + {c_hol_l}{idx}')
        
        for c_idx in range(1, c_tot_all + 1):
            cell = ws_t7.cell(idx, c_idx)
            fill_color = weekend_days[c_idx - 4][1] if (4 <= c_idx < c_tot_sat) else (fill_total if c_idx == c_tot_all else None)
            set_style(cell, font=font_data, fill=fill_color, border=thin_border)
            cell.alignment = align_center_nowrap if (c_idx in [1, 2] or c_idx >= 4) else align_left

    # SHEET 4: ABC
    ws_abc = wb.create_sheet(title="ABC")
    ws_abc.cell(1, 1, "BỆNH VIỆN BƯU ĐIỆN"); set_style(ws_abc.cell(1, 1), font=font_subtitle)
    ws_abc.cell(2, 1, f"Đơn vị: {phong_ban}"); set_style(ws_abc.cell(2, 1), font=font_subtitle)
    ws_abc.cell(3, 1, f"BẢNG BÌNH BẦU XẾP LOẠI LAO ĐỘNG THÁNG {month:02d}/{year}")
    
    headers_abc = [
        "STT", "Mã NV", "HỌ VÀ TÊN", "CHỨC VỤ", 
        "Hành chính", "Làm T7", "Làm CN", "Làm Lễ",
        "Trực thường", "Trực T7", "Trực CN", "Trực Lễ",
        "Đã nghỉ bù", "Nghỉ phép (P/PP)", "Thai sản (TS)", 
        "Nghỉ ốm (Ô/ÔÔ)", "Công tác (C/CC)", "Đi học (H/HH)",
        "XẾP LOẠI", "TỒN BÙ CÒN LẠI"
    ]
    
    ws_abc.merge_cells(start_row=3, start_column=1, end_row=3, end_column=len(headers_abc))
    set_style(ws_abc.cell(3, 1), font=font_title, alignment=align_center)

    for col_i, h in enumerate(headers_abc, 1):
        c = ws_abc.cell(5, col_i, h)
        set_style(c, font=font_header, fill=fill_header_default, alignment=align_center)

    for idx, nv in enumerate(nv_list, start=6):
        ws_abc.cell(idx, 1, idx - 5)
        ws_abc.cell(idx, 2, nv["ma_cb"])
        ws_abc.cell(idx, 3, nv["ho_ten"])
        ws_abc.cell(idx, 4, nv["chuc_vu"])
        
        nv_row = idx - 1
        ws_abc.cell(idx, 5, f"='NHÂN VIÊN'!{get_column_letter(start_sum)}{nv_row}")
        ws_abc.cell(idx, 6, f"='NHÂN VIÊN'!{get_column_letter(start_sum+1)}{nv_row}")
        ws_abc.cell(idx, 7, f"='NHÂN VIÊN'!{get_column_letter(start_sum+2)}{nv_row}")
        ws_abc.cell(idx, 8, f"='NHÂN VIÊN'!{get_column_letter(start_sum+3)}{nv_row}")
        
        ws_abc.cell(idx, 9, f"='NHÂN VIÊN'!{get_column_letter(start_sum+7)}{nv_row}")
        ws_abc.cell(idx, 10, f"='NHÂN VIÊN'!{get_column_letter(start_sum+4)}{nv_row}")
        ws_abc.cell(idx, 11, f"='NHÂN VIÊN'!{get_column_letter(start_sum+5)}{nv_row}")
        ws_abc.cell(idx, 12, f"='NHÂN VIÊN'!{get_column_letter(start_sum+6)}{nv_row}")
        
        ws_abc.cell(idx, 13, f"='NHÂN VIÊN'!{get_column_letter(start_sum+8)}{nv_row}") # Đã nghỉ bù
        ws_abc.cell(idx, 14, f"='NHÂN VIÊN'!{get_column_letter(start_sum+10)}{nv_row}") # Nghỉ phép
        ws_abc.cell(idx, 15, f"='NHÂN VIÊN'!{get_column_letter(start_sum+11)}{nv_row}") # Thai sản
        ws_abc.cell(idx, 16, f"='NHÂN VIÊN'!{get_column_letter(start_sum+13)}{nv_row}") # Nghỉ ốm
        ws_abc.cell(idx, 17, f"='NHÂN VIÊN'!{get_column_letter(start_sum+12)}{nv_row}") # Công tác
        ws_abc.cell(idx, 18, f"='NHÂN VIÊN'!{get_column_letter(start_sum+14)}{nv_row}") # Đi học
        
        ws_abc.cell(idx, 19, "A")
        ws_abc.cell(idx, 20, f"='NHÂN VIÊN'!{get_column_letter(start_sum+9)}{nv_row}") # Nghỉ bù còn
        
        for c_idx in range(1, len(headers_abc) + 1):
            cell = ws_abc.cell(idx, c_idx)
            set_style(cell, font=font_data, border=thin_border)
            cell.alignment = align_center_nowrap if (c_idx in [1, 2] or c_idx >= 5) else align_left

    for ws in wb.worksheets:
        ws.views.sheetView[0].showGridLines = True
        set_optimal_column_widths(ws)

    output = io.BytesIO()
    wb.save(output)
    return output.getvalue()
