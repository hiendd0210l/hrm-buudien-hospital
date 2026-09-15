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
    """
    Đặt độ rộng cột tối ưu, tránh bị giãn rộng bất thường do Title/Header bị merged.
    """
    for col in ws.columns:
        col_idx = col[0].column
        col_letter = get_column_letter(col_idx)
        
        if col_idx == 1:       # STT
            ws.column_dimensions[col_letter].width = 5
        elif col_idx == 2:     # Mã NV
            ws.column_dimensions[col_letter].width = 11
        elif col_idx in [3, 4] and ws.title in ["NHÂN VIÊN", "HTCS", "LÀM THỨ 7"]:
            # Cột Họ và tên (hoặc Chức vụ ở sheet ABC)
            if col_idx == 3:
                ws.column_dimensions[col_letter].width = 22
            else:
                ws.column_dimensions[col_letter].width = 6
        elif ws.title == "ABC" and col_idx == 4: # Chức vụ
            ws.column_dimensions[col_letter].width = 18
        else:
            # Các cột Ngày (01, 02...) và cột Chỉ số Tổng hợp
            ws.column_dimensions[col_letter].width = 6


# =====================================================================
# 2. HÀM TẠO FILE EXCEL CHUẨN 4 SHEET (NHÂN VIÊN, HTCS, LÀM THỨ 7, ABC)
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
                    "khoa_phong": str(row.get('khoa_phong', ''))
                }
                loai_hd = str(row.get('loai_hop_dong', '')).upper()
                if 'HTCS' in loai_hd or 'THUÊ LẠI' in loai_hd or 'THUE LAI' in loai_hd:
                    htcs_list.append(item)
                else:
                    nv_list.append(item)

    # Dữ liệu mẫu fallback nếu chưa load danh sách
    if not nv_list and not htcs_list:
        nv_list = [
            {"ma_cb": "N1096", "ho_ten": "Nguyễn Thị Thảo Nguyên", "chuc_vu": "Bác sĩ", "khoa_phong": "Khoa Khám bệnh"},
            {"ma_cb": "N1048", "ho_ten": "Đỗ Thanh Mai", "chuc_vu": "Bác sĩ", "khoa_phong": "Khoa Khám bệnh"},
            {"ma_cb": "N0668", "ho_ten": "Đào Tiến Luật", "chuc_vu": "Bác sĩ", "khoa_phong": "Khoa Khám bệnh"},
            {"ma_cb": "N0418", "ho_ten": "Phạm Ngọc Mai", "chuc_vu": "Điều dưỡng", "khoa_phong": "Khoa Khám bệnh"}
        ]
        htcs_list = [
            {"ma_cb": "HT001", "ho_ten": "Nguyễn Văn Hỗ Trợ", "chuc_vu": "Lao động thuê lại", "khoa_phong": "Khoa Khám bệnh"},
            {"ma_cb": "HT002", "ho_ten": "Trần Thị Chăm Sóc", "chuc_vu": "Lao động thuê lại", "khoa_phong": "Khoa Khám bệnh"}
        ]

    font_title = Font(name="Arial", size=12, bold=True, color="002060")
    font_subtitle = Font(name="Arial", size=10, bold=True)
    font_header = Font(name="Arial", size=9, bold=True)
    font_data = Font(name="Arial", size=10)
    
    fill_header_default = PatternFill(start_color="D9E1F2", end_color="D9E1F2", fill_type="solid")
    align_center = Alignment(horizontal="center", vertical="center", wrap_text=True)
    align_left = Alignment(horizontal="left", vertical="center")
    align_center_nowrap = Alignment(horizontal="center", vertical="center")
    
    thin_border = Border(
        left=Side(style='thin', color='BFBFBF'), right=Side(style='thin', color='BFBFBF'),
        top=Side(style='thin', color='BFBFBF'), bottom=Side(style='thin', color='BFBFBF')
    )
    
    num_days = calendar.monthrange(year, month)[1]

    # Phân loại danh sách cột theo ngày
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

    # HÀM BỔ TRỢ CÔNG THỨC: 1 KÝ TỰ = 0.5, 2 KÝ TỰ = 1.0
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

    # Hàm dựng Bảng chấm công chính
    def build_main_sheet(ws, title_sheet, data_list):
        ws.cell(1, 1, "BỆNH VIỆN BƯU ĐIỆN"); set_style(ws.cell(1, 1), font=font_subtitle)
        ws.cell(1, 4, f"BẢNG CHẤM CÔNG THÁNG {month:02d} NĂM {year} ({title_sheet})")
        ws.merge_cells(start_row=1, start_column=4, end_row=1, end_column=num_days + 18)
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
            "Đã nghỉ bù", "Nghỉ bù còn", "Thai sản", "Công tác", "Nghỉ ốm", "Đi học", "Tồn bù"
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
            
            st_l = get_column_letter(4)
            en_l = get_column_letter(3 + num_days)
            
            # Công thức Tổng hợp tuân thủ đúng nguyên tắc: 1 ký tự = 0.5, 2 ký tự = 1.0
            ws.cell(idx, start_sum, f'={build_code_formula(workday_cols, idx, "x", "xx")}')
            ws.cell(idx, start_sum+1, f'={build_code_formula(sat_cols, idx, "x", "xx")}')
            ws.cell(idx, start_sum+2, f'={build_code_formula(sun_cols, idx, "x", "xx")}')
            ws.cell(idx, start_sum+3, f'={build_code_formula(hol_cols, idx, "x", "xx")}')
            
            ws.cell(idx, start_sum+4, f'={build_duty_formula(sat_cols, idx)}')
            ws.cell(idx, start_sum+5, f'={build_duty_formula(sun_cols, idx)}')
            ws.cell(idx, start_sum+6, f'={build_duty_formula(hol_cols, idx)}')
            ws.cell(idx, start_sum+7, f'={build_duty_formula(workday_cols, idx)}')
            
            ws.cell(idx, start_sum+8, f'={build_code_formula(all_month_cols, idx, "b", "bb")}')
            
            ton_col = get_column_letter(start_sum+14)
            da_nghi_col = get_column_letter(start_sum+8)
            ws.cell(idx, start_sum+9, f'=MAX(0, {ton_col}{idx} - {da_nghi_col}{idx})')
            
            ws.cell(idx, start_sum+10, f'={build_code_formula(all_month_cols, idx, "ts", "ts")}') # Thai sản
            ws.cell(idx, start_sum+11, f'={build_code_formula(all_month_cols, idx, "c", "cc")}') # Công tác
            ws.cell(idx, start_sum+12, f'={build_code_formula(all_month_cols, idx, "ô", "ôô")}') # Nghỉ ốm
            ws.cell(idx, start_sum+13, f'={build_code_formula(all_month_cols, idx, "h", "hh")}') # Đi học
            ws.cell(idx, start_sum+14, 0) # Tồn bù ban đầu

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
        
    ws_t7.cell(3, tot_col, "Tổng công")
    set_style(ws_t7.cell(3, tot_col), font=font_header, fill=fill_header_default, alignment=align_center)

    all_comb_list = nv_list + htcs_list
    for idx, nv in enumerate(all_comb_list, start=4):
        ws_t7.cell(idx, 1, idx - 3)
        ws_t7.cell(idx, 2, nv["ma_cb"])
        ws_t7.cell(idx, 3, nv["ho_ten"])
        
        wk_cols_letters = [get_column_letter(4 + i) for i in range(len(weekend_days))]
        ws_t7.cell(idx, tot_col, f'={build_code_formula(wk_cols_letters, idx, "x", "xx")} + {build_duty_formula(wk_cols_letters, idx)}')
        
        for c_idx in range(1, tot_col + 1):
            cell = ws_t7.cell(idx, c_idx)
            fill_color = weekend_days[c_idx - 4][1] if (4 <= c_idx < tot_col) else None
            set_style(cell, font=font_data, fill=fill_color, border=thin_border)
            cell.alignment = align_center_nowrap if (c_idx in [1, 2] or c_idx >= 4) else align_left

    # SHEET 4: ABC (MỞ RỘNG ĐẦY ĐỦ CÁC CỘT TỔNG HỢP THEO YÊU CẦU)
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

    all_month_cols = [get_column_letter(3 + d) for d in range(1, num_days + 1)]

    for idx, nv in enumerate(nv_list, start=6):
        ws_abc.cell(idx, 1, idx - 5)
        ws_abc.cell(idx, 2, nv["ma_cb"])
        ws_abc.cell(idx, 3, nv["ho_ten"])
        ws_abc.cell(idx, 4, nv["chuc_vu"])
        
        nv_row = idx - 1
        # Liên kết công thức từ Sheet "NHÂN VIÊN"
        ws_abc.cell(idx, 5, f"='NHÂN VIÊN'!{get_column_letter(start_sum)}{nv_row}")     # Hành chính
        ws_abc.cell(idx, 6, f"='NHÂN VIÊN'!{get_column_letter(start_sum+1)}{nv_row}")   # Làm T7
        ws_abc.cell(idx, 7, f"='NHÂN VIÊN'!{get_column_letter(start_sum+2)}{nv_row}")   # Làm CN
        ws_abc.cell(idx, 8, f"='NHÂN VIÊN'!{get_column_letter(start_sum+3)}{nv_row}")   # Làm Lễ
        
        ws_abc.cell(idx, 9, f"='NHÂN VIÊN'!{get_column_letter(start_sum+7)}{nv_row}")   # Trực thường
        ws_abc.cell(idx, 10, f"='NHÂN VIÊN'!{get_column_letter(start_sum+4)}{nv_row}")  # Trực T7
        ws_abc.cell(idx, 11, f"='NHÂN VIÊN'!{get_column_letter(start_sum+5)}{nv_row}")  # Trực CN
        ws_abc.cell(idx, 12, f"='NHÂN VIÊN'!{get_column_letter(start_sum+6)}{nv_row}")  # Trực Lễ
        
        ws_abc.cell(idx, 13, f"='NHÂN VIÊN'!{get_column_letter(start_sum+8)}{nv_row}")  # Đã nghỉ bù
        ws_abc.cell(idx, 14, f"={build_code_formula([f\"'NHÂN VIÊN'!{c}\" for c in all_month_cols], nv_row, 'p', 'pp')}") # Nghỉ phép
        ws_abc.cell(idx, 15, f"='NHÂN VIÊN'!{get_column_letter(start_sum+10)}{nv_row}") # Thai sản
        ws_abc.cell(idx, 16, f"='NHÂN VIÊN'!{get_column_letter(start_sum+12)}{nv_row}") # Nghỉ ốm
        ws_abc.cell(idx, 17, f"='NHÂN VIÊN'!{get_column_letter(start_sum+11)}{nv_row}") # Công tác
        ws_abc.cell(idx, 18, f"='NHÂN VIÊN'!{get_column_letter(start_sum+13)}{nv_row}") # Đi học
        
        ws_abc.cell(idx, 19, "A")
        ws_abc.cell(idx, 20, f"='NHÂN VIÊN'!{get_column_letter(start_sum+9)}{nv_row}")  # Tồn bù còn lại
        
        for c_idx in range(1, len(headers_abc) + 1):
            cell = ws_abc.cell(idx, c_idx)
            set_style(cell, font=font_data, border=thin_border)
            cell.alignment = align_center_nowrap if (c_idx in [1, 2] or c_idx >= 5) else align_left

    # Tối ưu hóa kích thước độ rộng các cột cho tất cả các sheet
    for ws in wb.worksheets:
        ws.views.sheetView[0].showGridLines = True
        set_optimal_column_widths(ws)

    output = io.BytesIO()
    wb.save(output)
    return output.getvalue()


# =====================================================================
# 3. HÀM SẮP XẾP DANH SÁCH "ĐƠN VỊ XUẤT DỮ LIỆU" THEO ĐÚNG THỨ TỰ
# Thứ tự: Tất cả -> Phòng (ABC) -> Khoa (ABC) -> Trung tâm (ABC)
# =====================================================================
def get_ordered_phong_ban_list(df_cb):
    list_phong, list_khoa, list_trung_tam = [], [], []
    
    if isinstance(df_cb, pd.DataFrame) and not df_cb.empty and "khoa_phong" in df_cb.columns:
        unique_kp = [str(kp).strip() for kp in df_cb["khoa_phong"].dropna().unique() if str(kp).strip()]
        for kp in unique_kp:
            kp_lower = kp.lower()
            if "phòng" in kp_lower or "phong" in kp_lower:
                list_phong.append(kp)
            elif "trung tâm" in kp_lower or "trung tam" in kp_lower:
                list_trung_tam.append(kp)
            else:
                list_khoa.append(kp)

    if not list_phong and not list_khoa and not list_trung_tam:
        list_phong = ["Phòng Kế hoạch Tổng hợp", "Phòng Tài chính Kế toán", "Phòng Tổ chức Cán bộ"]
        list_khoa = ["Khoa Cấp cứu", "Khoa Khám bệnh", "Khoa Ngoại tổng hợp", "Khoa Nội tổng hợp"]
        list_trung_tam = ["Trung tâm Đột quỵ", "Trung tâm Y học hạt nhân"]

    list_phong.sort(key=lambda x: x.lower())
    list_khoa.sort(key=lambda x: x.lower())
    list_trung_tam.sort(key=lambda x: x.lower())

    return ["Tất cả khoa/phòng/trung tâm"] + list_phong + list_khoa + list_trung_tam


# =====================================================================
# 4. GIAO DIỆN STREAMLIT DASHBOARD
# =====================================================================
def render_quan_ly_cham_cong(df_cb=None):
    st.title("📋 Quản lý & Xuất Bảng Chấm Công Bệnh Viện")

    if df_cb is None:
        df_cb = st.session_state.get("df_can_bo", pd.DataFrame())

    danh_sach_don_vi = get_ordered_phong_ban_list(df_cb)

    # 1. Cấu hình thông số
    st.subheader("⚙️ Cấu hình thông số xuất file")
    col1, col2, col3 = st.columns(3)
    with col1:
        month = st.number_input("Tháng chấm công", min_value=1, max_value=12, value=datetime.now().month)
    with col2:
        year = st.number_input("Năm chấm công", min_value=2020, max_value=2030, value=datetime.now().year)
    with col3:
        don_vi_selected = st.selectbox("Đơn vị xuất dữ liệu", options=danh_sach_don_vi)

    st.markdown("---")

    # 2. Hiển thị Metrics
    num_days = calendar.monthrange(year, month)[1]
    
    total_nv = 0
    if isinstance(df_cb, pd.DataFrame) and not df_cb.empty and "khoa_phong" in df_cb.columns:
        if don_vi_selected == "Tất cả khoa/phòng/trung tâm":
            total_nv = len(df_cb)
        else:
            total_nv = len(df_cb[df_cb["khoa_phong"] == don_vi_selected])
    else:
        total_nv = 6

    m1, m2, m3 = st.columns(3)
    m1.metric("Tổng cán bộ / Nhân viên", f"{total_nv} người")
    m2.metric("Số ngày trong tháng", f"{num_days} ngày")
    m3.metric("Tháng / Năm áp dụng", f"T{month:02d}/{year}")

    # Tự động cập nhật dữ liệu file theo đúng tùy chọn Đơn vị xuất dữ liệu
    excel_data = generate_excel_mau_cham_cong(month, year, don_vi_selected, df_cb)

    # 3. Khu vực Xuất File Excel
    st.write("### 📥 Tải xuống Bảng chấm công Excel")
    file_name_clean = don_vi_selected.replace("Tất cả khoa/phòng/trung tâm", "Tat_Ca_Khoa_Phong").replace(" ", "_").replace("/", "_")
    target_file_name = f"Bang_Cham_Cong_{file_name_clean}_T{month:02d}_{year}.xlsx"

    col_btn1, col_btn2 = st.columns([2, 3])
    with col_btn1:
        if st.button("🚀 Khởi tạo & Tạo File Excel", type="primary", use_container_width=True):
            st.session_state["cham_cong_excel_bytes"] = excel_data
            st.session_state["cham_cong_file_name"] = target_file_name
            st.success("Tạo file chấm công thành công!")

    with col_btn2:
        download_bytes = st.session_state.get("cham_cong_excel_bytes", excel_data)
        download_name = st.session_state.get("cham_cong_file_name", target_file_name)
        
        st.download_button(
            label="Tải xuống file Excel (.xlsx)",
            data=download_bytes,
            file_name=download_name,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )

    # 4. Hiển thị Bảng tổng hợp bình bầu xếp loại lao động (Sheet ABC)
    st.markdown("---")
    st.subheader(f"📊 Bảng tổng hợp bình bầu xếp loại lao động toàn Bệnh viện (Tháng {month:02d}/{year})")
    
    if isinstance(df_cb, pd.DataFrame) and not df_cb.empty:
        df_abc = df_cb.copy()
        if don_vi_selected != "Tất cả khoa/phòng/trung tâm" and "khoa_phong" in df_abc.columns:
            df_abc = df_abc[df_abc["khoa_phong"] == don_vi_selected]
    else:
        df_abc = pd.DataFrame([
            {"ma_can_bo": "N1096", "ho_ten": "Nguyễn Thị Thảo Nguyên", "chuc_vu": "Bác sĩ", "khoa_phong": "Khoa Khám bệnh"},
            {"ma_can_bo": "N1048", "ho_ten": "Đỗ Thanh Mai", "chuc_vu": "Bác sĩ", "khoa_phong": "Khoa Khám bệnh"},
            {"ma_can_bo": "N0668", "ho_ten": "Đào Tiến Luật", "chuc_vu": "Bác sĩ", "khoa_phong": "Khoa Khám bệnh"},
            {"ma_can_bo": "N0418", "ho_ten": "Phạm Ngọc Mai", "chuc_vu": "Điều dưỡng", "khoa_phong": "Khoa Khám bệnh"},
            {"ma_can_bo": "HT001", "ho_ten": "Nguyễn Văn Hỗ Trợ", "chuc_vu": "Lao động thuê lại", "khoa_phong": "Khoa Khám bệnh"}
        ])

    records = []
    for idx, row in df_abc.reset_index(drop=True).iterrows():
        records.append({
            "STT": idx + 1,
            "Mã NV": row.get("ma_can_bo", f"NV{idx+1:03d}"),
            "Họ và tên": row.get("ho_ten", ""),
            "Chức vụ": row.get("chuc_vu", "Nhân viên"),
            "Đơn vị / Khoa phòng": row.get("khoa_phong", "Khoa Khám bệnh"),
            "Hành chính": 22.0,
            "Làm T7": 0.0,
            "Làm CN": 0.0,
            "Làm Lễ": 0.0,
            "Trực thường": 0,
            "Trực T7": 1,
            "Trực CN": 1,
            "Trực Lễ": 0,
            "Đã nghỉ bù": 0,
            "Nghỉ phép (P/PP)": 1.0,
            "Thai sản (TS)": 0,
            "Nghỉ ốm (Ô/ÔÔ)": 0,
            "Công tác (C/CC)": 0,
            "Đi học (H/HH)": 0,
            "Xếp loại": "A",
            "Tồn bù còn lại": 0
        })

    df_summary = pd.DataFrame(records)
    
    st.dataframe(
        df_summary, 
        use_container_width=True, 
        hide_index=True,
        column_config={
            "STT": st.column_config.NumberColumn("STT", width="small"),
            "Mã NV": st.column_config.TextColumn("Mã NV", width="small"),
            "Họ và tên": st.column_config.TextColumn("Họ và tên", width="medium"),
            "Đơn vị / Khoa phòng": st.column_config.TextColumn("Đơn vị / Khoa phòng", width="medium"),
            "Xếp loại": st.column_config.TextColumn("Xếp loại", width="small")
        }
    )

# Chạy thử trực tiếp nếu gọi file độc lập
if __name__ == "__main__":
    st.set_page_config(page_title="Chấm công Bệnh viện", layout="wide")
    render_quan_ly_cham_cong()
