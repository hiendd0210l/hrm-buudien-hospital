import io
import calendar
import pandas as pd
import Streamlit as st
from datetime import datetime, date
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

# ---------------------------------------------------------------------
# HÀM BỔ TRỢ PHÂN LOẠI NGÀY (T7, CN, LỄ)
# ---------------------------------------------------------------------
def get_day_type(day: int, month: int, year: int):
    Dt = date(year, month, day)
    Weekday = dt.weekday()  # 5: Thứ 7, 6: Chủ nhật
    Fixed_holidays = [(1, 1), (30, 4), (1, 5), (2, 9), (3, 9)]
    
    If (day, month) in fixed_holidays:
        Return PatternFill(start_color="FFC7CE", end_color="FFC7CE", fill_type="solid"), "HOLIDAY"
    Elif weekday == 5:
        Return PatternFill(start_color="FCE4D6", end_color="FCE4D6", fill_type="solid"), "SAT"
    Elif weekday == 6:
        Return PatternFill(start_color="DDEBF7", end_color="DDEBF7", fill_type="solid"), "SUN"
    Return None, "WORKDAY"

Def set_style(cell, font=None, fill=None, alignment=None, border=None):
    If font is not None:
        Cell.font = font
    If fill is not None:
        Cell.fill = fill
    If alignment is not None:
        Cell.alignment = alignment
    If border is not None:
        Cell.border = border


# ---------------------------------------------------------------------
# HÀM TẠO FILE EXCEL CHUẨN
# ---------------------------------------------------------------------
def generate_excel_mau_cham_cong(month: int, year: int, phong_ban: str, df_cb: pd.DataFrame) -> bytes:
    Wb = openpyxl.Workbook()
    
    # Danh sách cán bộ mẫu
    Nv_list = []
    If df_cb is not None and not df_cb.empty and 'khoa_phong' in df_cb.columns:
        Df_dept = df_cb[df_cb['khoa_phong'] == phong_ban].copy()
        If not df_dept.empty:
            For _, row in df_dept.iterrows():
                Nv_list.append({
                    "ma_cb": str(row.get('ma_can_bo', '')),
                    "ho_ten": str(row.get('ho_ten', '')),
                    "chuc_vu": str(row.get('chuc_vu', 'Nhân viên'))
                })

    If not nv_list:
        Nv_list = [
            {"ma_cb": "N1096", "ho_ten": "Nguyễn Thị Thảo Nguyên", "chuc_vu": "Bác sĩ"},
            {"ma_cb": "N1048", "ho_ten": "Đỗ Thanh Mai", "chuc_vu": "Bác sĩ"},
            {"ma_cb": "N0668", "ho_ten": "Đào Tiến Luật", "chuc_vu": "Bác sĩ"},
            {"ma_cb": "N0418", "ho_ten": "Phạm Ngọc Mai", "chuc_vu": "Điều dưỡng"},
            {"ma_cb": "N0162", "ho_ten": "Nguyễn Thị Mai Phương", "chuc_vu": "Điều dưỡng"}
        ]

    Font_title = Font(name="Arial", size=12, bold=True, color="002060")
    Font_subtitle = Font(name="Arial", size=10, bold=True)
    Font_header = Font(name="Arial", size=9, bold=True)
    Font_data = Font(name="Arial", size=10)
    Font_bold = Font(name="Arial", size=10, bold=True)
    
    Fill_header_default = PatternFill(start_color="D9E1F2", end_color="D9E1F2", fill_type="solid")
    Align_center = Alignment(horizontal="center", vertical="center", wrap_text=True)
    Align_left = Alignment(horizontal="left", vertical="center")
    Align_center_nowrap = Alignment(horizontal="center", vertical="center")
    
    Thin_border = Border(
        Left=Side(style='thin', color='BFBFBF'), right=Side(style='thin', color='BFBFBF'),
        Top=Side(style='thin', color='BFBFBF'), bottom=Side(style='thin', color='BFBFBF')
    )
    
    Num_days = calendar.monthrange(year, month)[1]

    # Phân loại danh sách cột theo Ngày
    Sat_cols, sun_cols, hol_cols = [], [], []
    For d in range(1, num_days + 1):
        Col_letter = get_column_letter(3 + d)
        _, day_type = get_day_type(d, month, year)
        If day_type == "SAT":
            Sat_cols.append(col_letter)
        Elif day_type == "SUN":
            Sun_cols.append(col_letter)
        Elif day_type == "HOLIDAY":
            Hol_cols.append(col_letter)

    # Hàm tạo công thức tính ngày công hỗ trợ cả chữ HOA và chữ thường (X/x, XX/xx)
    Def build_work_formula(col_list, row_idx):
        If not col_list:
            Return "0"
        Parts = []
        For c in col_list:
            Parts.append(f'IF(OR({c}{row_idx}="XX",{c}{row_idx}="xx"),1,IF(OR({c}{row_idx}="X",{c}{row_idx}="x"),0.5,0))')
        Return " + ".join(parts)

    Def build_duty_formula(col_list, row_idx):
        If not col_list:
            Return "0"
        Parts = []
        For c in col_list:
            Parts.append(f'IF(OR({c}{row_idx}="T",{c}{row_idx}="t"),1,0)')
        Return " + ".join(parts)

    # =====================================================================
    # SHEET 1: NHÂN VIÊN
    # =====================================================================
    Ws_nv = wb.active
    Ws_nv.title = "NHÂN VIÊN"
    
    Ws_nv.cell(1, 1, "BỆNH VIỆN BƯU ĐIỆN"); set_style(ws_nv.cell(1, 1), font=font_subtitle)
    Ws_nv.cell(1, 4, f"BẢNG CHẤM CÔNG THÁNG {month:02d} NĂM {year} CỦA CBNV")
    Ws_nv.merge_cells(start_row=1, start_column=4, end_row=1, end_column=num_days + 18)
    Set_style(ws_nv.cell(1, 4), font=font_title, alignment=align_center)
    Ws_nv.cell(2, 1, f"Đơn vị: {phong_ban}"); set_style(ws_nv.cell(2, 1), font=font_subtitle)
    
    Ws_nv.cell(3, 1, "STT"); ws_nv.merge_cells("A3:A4")
    Ws_nv.cell(3, 2, "Mã NV"); ws_nv.merge_cells("B3:B4")
    Ws_nv.cell(3, 3, "Họ và tên"); ws_nv.merge_cells("C3:C4")
    Ws_nv.cell(3, 4, f"Ngày làm việc trong tháng {month:02d}.{year}")
    Ws_nv.merge_cells(start_row=3, start_column=4, end_row=3, end_column=3 + num_days)
    
    Day_fills = {}
    For d in range(1, num_days + 1):
        Col_idx = 3 + d
        Ws_nv.cell(4, col_idx, f"{d:02d}")
        Fill_color, _ = get_day_type(d, month, year)
        Day_fills[col_idx] = fill_color if fill_color else fill_header_default

    Start_sum = 4 + num_days
    # Tạo tiêu đề các cột tổng hợp tách riêng
    Headers_sum = [
        "Hành chính", "Làm Thứ 7", "Làm Chủ Nhật", "Làm Lễ/Tết", 
        "Trực Thứ 7", "Trực Chủ Nhật", "Trực Lễ/Tết", "Trực ngoài giờ",
        "Đã nghỉ bù", "Nghỉ bù còn lại", "Thai sản", "Công tác", "Nghỉ ốm", "Đi học", "Tồn bù"
    ]
    For i, h in enumerate(headers_sum):
        C_idx = start_sum + i
        Ws_nv.cell(3, c_idx, h)
        Ws_nv.merge_cells(start_row=3, start_column=c_idx, end_row=4, end_column=c_idx)

    For r in range(3, 5):
        For c in range(1, start_sum + len(headers_sum)):
            Cell = ws_nv.cell(r, c)
            F_fill = day_fills[c] if (4 <= c <= 3 + num_days and r == 4) else fill_header_default
            Set_style(cell, font=font_header, fill=f_fill, alignment=align_center)

    # Đổ danh sách & Công thức cho Sheet NHÂN VIÊN
    For idx, nv in enumerate(nv_list, start=5):
        Ws_nv.cell(idx, 1, idx - 4)
        Ws_nv.cell(idx, 2, nv["ma_cb"])
        Ws_nv.cell(idx, 3, nv["ho_ten"])
        
        St_l = get_column_letter(4)
        En_l = get_column_letter(3 + num_days)
        
        # 1. Hành chính
        Ws_nv.cell(idx, start_sum, f'=(COUNTIF({st_l}{idx}:{en_l}{idx},"XX")+COUNTIF({st_l}{idx}:{en_l}{idx},"xx")) + (COUNTIF({st_l}{idx}:{en_l}{idx},"X")+COUNTIF({st_l}{idx}:{en_l}{idx},"x"))*0.5')
        # 2-4. Làm T7, CN, Lễ riêng biệt
        Ws_nv.cell(idx, start_sum+1, f'={build_work_formula(sat_cols, idx)}')
        Ws_nv.cell(idx, start_sum+2, f'={build_work_formula(sun_cols, idx)}')
        Ws_nv.cell(idx, start_sum+3, f'={build_work_formula(hol_cols, idx)}')
        # 5-7. Trực T7, CN, Lễ riêng biệt
        Ws_nv.cell(idx, start_sum+4, f'={build_duty_formula(sat_cols, idx)}')
        Ws_nv.cell(idx, start_sum+5, f'={build_duty_formula(sun_cols, idx)}')
        Ws_nv.cell(idx, start_sum+6, f'={build_duty_formula(hol_cols, idx)}')
        # 8. Trực ngoài giờ chung
        Ws_nv.cell(idx, start_sum+7, f'=COUNTIF({st_l}{idx}:{en_l}{idx},"T") + COUNTIF({st_l}{idx}:{en_l}{idx},"t")')
        # 9. Đã nghỉ bù
        Ws_nv.cell(idx, start_sum+8, f'=(COUNTIF({st_l}{idx}:{en_l}{idx},"BB")+COUNTIF({st_l}{idx}:{en_l}{idx},"bb")) + (COUNTIF({st_l}{idx}:{en_l}{idx},"B")+COUNTIF({st_l}{idx}:{en_l}{idx},"b"))*0.5')
        # 10. Nghỉ bù còn lại (Không âm)
        Ton_col = get_column_letter(start_sum+14)
        Da_nghi_col = get_column_letter(start_sum+8)
        Ws_nv.cell(idx, start_sum+9, f'=MAX(0, {ton_col}{idx} - {da_nghi_col}{idx})')
        # 11-14. Các loại công khác
        Ws_nv.cell(idx, start_sum+10, f'=COUNTIF({st_l}{idx}:{en_l}{idx},"TS") + COUNTIF({st_l}{idx}:{en_l}{idx},"ts")')
        Ws_nv.cell(idx, start_sum+11, f'=(COUNTIF({st_l}{idx}:{en_l}{idx},"CC")+COUNTIF({st_l}{idx}:{en_l}{idx},"cc")) + (COUNTIF({st_l}{idx}:{en_l}{idx},"C")+COUNTIF({st_l}{idx}:{en_l}{idx},"c"))*0.5')
        Ws_nv.cell(idx, start_sum+12, f'=(COUNTIF({st_l}{idx}:{en_l}{idx},"ÔÔ")+COUNTIF({st_l}{idx}:{en_l}{idx},"ôô")) + (COUNTIF({st_l}{idx}:{en_l}{idx},"Ô")+COUNTIF({st_l}{idx}:{en_l}{idx},"ô"))*0.5')
        Ws_nv.cell(idx, start_sum+13, f'=(COUNTIF({st_l}{idx}:{en_l}{idx},"HH")+COUNTIF({st_l}{idx}:{en_l}{idx},"hh")) + (COUNTIF({st_l}{idx}:{en_l}{idx},"H")+COUNTIF({st_l}{idx}:{en_l}{idx},"h"))*0.5')
        Ws_nv.cell(idx, start_sum+14, 0) # Tồn bù ban đầu

        For c_idx in range(1, start_sum + len(headers_sum)):
            Cell = ws_nv.cell(idx, c_idx)
            F_fill = day_fills[c_idx] if (c_idx in day_fills and day_fills[c_idx] != fill_header_default) else None
            Set_style(cell, font=font_data, fill=f_fill, border=thin_border)
            Cell.alignment = align_center_nowrap if (c_idx in [1, 2] or c_idx >= 4) else align_left

    # =====================================================================
    # SHEET 2: LÀM THỨ 7 (Tính X/x = 0.5 công, XX/xx = 1.0 công)
    # =====================================================================
    Ws_t7 = wb.create_sheet(title="LÀM THỨ 7")
    Ws_t7.cell(1, 1, "BỆNH VIỆN BƯU ĐIỆN"); set_style(ws_t7.cell(1, 1), font=font_subtitle)
    Ws_t7.cell(1, 4, f"BẢNG CHẤM CÔNG NGÀY LÀM THỨ 7, CHỦ NHẬT & NGÀY LỄ CỦA CBNV THÁNG {month:02d}/{year}")
    
    Weekend_days = []
    For d in range(1, num_days + 1):
        Fill_color, day_type = get_day_type(d, month, year)
        If day_type in ["SAT", "SUN", "HOLIDAY"]:
            Weekend_days.append((d, fill_color))
            
    Tot_col = 4 + len(weekend_days)
    Ws_t7.merge_cells(start_row=1, start_column=4, end_row=1, end_column=tot_col)
    Set_style(ws_t7.cell(1, 4), font=font_title, alignment=align_center)
    Ws_t7.cell(2, 1, f"Đơn vị: {phong_ban}"); set_style(ws_t7.cell(2, 1), font=font_subtitle)

    Ws_t7.cell(3, 1, "STT"); set_style(ws_t7.cell(3, 1), font=font_header, fill=fill_header_default, alignment=align_center)
    Ws_t7.cell(3, 2, "Mã NV"); set_style(ws_t7.cell(3, 2), font=font_header, fill=fill_header_default, alignment=align_center)
    Ws_t7.cell(3, 3, "Họ và tên"); set_style(ws_t7.cell(3, 3), font=font_header, fill=fill_header_default, alignment=align_center)

    For w_i, (d, fill_color) in enumerate(weekend_days, start=4):
        C = ws_t7.cell(3, w_i, f"Ngày {d:02d}")
        Set_style(c, font=font_header, fill=fill_color, alignment=align_center)
        
    Ws_t7.cell(3, tot_col, "Tổng ngày công")
    Set_style(ws_t7.cell(3, tot_col), font=font_header, fill=fill_header_default, alignment=align_center)

    For idx, nv in enumerate(nv_list, start=4):
        Ws_t7.cell(idx, 1, idx - 3)
        Ws_t7.cell(idx, 2, nv["ma_cb"])
        Ws_t7.cell(idx, 3, nv["ho_ten"])
        
        St_l = get_column_letter(4)
        En_l = get_column_letter(tot_col - 1)
        # Công thức chuẩn X/x = 0.5, XX/xx = 1.0, T/t = 1.0
        Ws_t7.cell(idx, tot_col, f'=(COUNTIF({st_l}{idx}:{en_l}{idx},"XX")+COUNTIF({st_l}{idx}:{en_l}{idx},"xx")) + (COUNTIF({st_l}{idx}:{en_l}{idx},"T")+COUNTIF({st_l}{idx}:{en_l}{idx},"t")) + (COUNTIF({st_l}{idx}:{en_l}{idx},"X")+COUNTIF({st_l}{idx}:{en_l}{idx},"x"))*0.5')
        
        For c_idx in range(1, tot_col + 1):
            Cell = ws_t7.cell(idx, c_idx)
            Fill_color = weekend_days[c_idx - 4][1] if (4 <= c_idx < tot_col) else None
            Set_style(cell, font=font_data, fill=fill_color, border=thin_border)
            Cell.alignment = align_center_nowrap if (c_idx in [1, 2] or c_idx >= 4) else align_left

    # =====================================================================
    # SHEET 3: ABC (TỔNG HỢP HIỂN THỊ ĐẦY ĐỦ KÝ HIỆU CHẤM CÔNG)
    # =====================================================================
    Ws_abc = wb.create_sheet(title="ABC")
    Ws_abc.cell(1, 1, "BỆNH VIỆN BƯU ĐIỆN"); set_style(ws_abc.cell(1, 1), font=font_subtitle)
    Ws_abc.cell(2, 1, f"Đơn vị: {phong_ban}"); set_style(ws_abc.cell(2, 1), font=font_subtitle)
    Ws_abc.cell(3, 1, f"BẢNG BÌNH BẦU XẾP LOẠI LAO ĐỘNG THÁNG {month:02d}/{year}")
    Ws_abc.merge_cells("A3:N3")
    Set_style(ws_abc.cell(3, 1), font=font_title, alignment=align_center)

    Headers_abc = [
        "STT", "Mã NV", "HỌ VÀ TÊN", "CHỨC VỤ", 
        "ĐI LÀM (X/XX)", "TRỰC (T)", "NGHỈ BÙ (B/BB)", "NGHỈ PHÉP (P/PP)",
        "THAI SẢN (TS)", "NGHỈ ỐM (Ô/ÔÔ)", "CÔNG TÁC (C/CC)", "ĐI HỌC (H/HH)",
        "XẾP LOẠI", "TỒN BÙ CÒN LẠI"
    ]
    For col_i, h in enumerate(headers_abc, 1):
        C = ws_abc.cell(5, col_i, h)
        Set_style(c, font=font_header, fill=fill_header_default, alignment=align_center)

    For idx, nv in enumerate(nv_list, start=6):
        Ws_abc.cell(idx, 1, idx - 5)
        Ws_abc.cell(idx, 2, nv["ma_cb"])
        Ws_abc.cell(idx, 3, nv["ho_ten"])
        Ws_abc.cell(idx, 4, nv["chuc_vu"])
        
        Nv_row = idx - 1  # Tương ứng dòng bên sheet NHÂN VIÊN
        # Liên kết trực tiếp công thức từ sheet NHÂN VIÊN sang sheet ABC
        Ws_abc.cell(idx, 5, f"='NHÂN VIÊN'!{get_column_letter(start_sum)}{nv_row}")       # Đi làm
        Ws_abc.cell(idx, 6, f"='NHÂN VIÊN'!{get_column_letter(start_sum+7)}{nv_row}")     # Trực
        Ws_abc.cell(idx, 7, f"='NHÂN VIÊN'!{get_column_letter(start_sum+8)}{nv_row}")     # Nghỉ bù
        Ws_abc.cell(idx, 8, f"=(COUNTIF('NHÂN VIÊN'!D{nv_row}:AH{nv_row},\"PP\")+COUNTIF('NHÂN VIÊN'!D{nv_row}:AH{nv_row},\"pp\")) + (COUNTIF('NHÂN VIÊN'!D{nv_row}:AH{nv_row},\"P\")+COUNTIF('NHÂN VIÊN'!D{nv_row}:AH{nv_row},\"p\"))*0.5") # Nghỉ phép
        Ws_abc.cell(idx, 9, f"='NHÂN VIÊN'!{get_column_letter(start_sum+10)}{nv_row}")    # Thai sản
        Ws_abc.cell(idx, 10, f"='NHÂN VIÊN'!{get_column_letter(start_sum+12)}{nv_row}")   # Nghỉ ốm
        Ws_abc.cell(idx, 11, f"='NHÂN VIÊN'!{get_column_letter(start_sum+11)}{nv_row}")   # Công tác
        Ws_abc.cell(idx, 12, f"='NHÂN VIÊN'!{get_column_letter(start_sum+13)}{nv_row}")   # Đi học
        Ws_abc.cell(idx, 13, "A")                                                       # Xếp loại
        Ws_abc.cell(idx, 14, f"='NHÂN VIÊN'!{get_column_letter(start_sum+9)}{nv_row}")    # Tồn bù còn lại
        
        For c_idx in range(1, 15):
            Cell = ws_abc.cell(idx, c_idx)
            Set_style(cell, font=font_data, border=thin_border)
            Cell.alignment = align_center_nowrap if (c_idx in [1, 2] or c_idx >= 5) else align_left

    # Auto fit độ rộng cột cơ bản
    For ws in wb.worksheets:
        Ws.views.sheetView[0].showGridLines = True
        For col in ws.columns:
            Max_len = max(len(str(cell.value or '')) for cell in col)
            Col_letter = get_column_letter(col[0].column)
            Ws.column_dimensions[col_letter].width = max(max_len + 3, 10)

    Output = io.BytesIO()
    Wb.save(output)
    Return output.getvalue()
