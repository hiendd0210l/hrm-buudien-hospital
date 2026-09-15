import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

def generate_attendance_sheet():
    # 1. Khởi tạo Workbook và các Sheet
    wb = openpyxl.Workbook()
    
    ws_main = wb.active
    ws_main.title = "NHÂN VIÊN"
    ws_htcs = wb.create_sheet(title="HTCS")
    ws_t7 = wb.create_sheet(title="LÀM THỨ 7")
    ws_abc = wb.create_sheet(title="ABC")

    # Danh sách nhân viên mẫu
    employees = [
        ("N1108", "Mai Tuấn Linh"),
        ("N1109", "Hoàng Tuấn Anh"),
        ("N1090", "Phạm Văn Hiếu"),
        ("N0875", "Phạm Diệu Linh"),
        ("N1034", "Vũ Đức Chính"),
        ("N0855", "Nguyễn Văn Tiềm"),
        ("N0564", "Nguyễn Đức Phương"),
        ("N0456", "Ngô Đức Hinh"),
        ("N0451", "Nguyễn Cảnh Việt"),
        ("N0223", "Nguyễn Vũ Ngọc Ánh"),
        ("N0380", "Nguyễn Minh Hải"),
    ]

    # Định nghĩa Font, Màu sắc và Định dạng ô
    HEADER_FILL = PatternFill(start_color="D9E1F2", end_color="D9E1F2", fill_type="solid")
    WEEKEND_FILL = PatternFill(start_color="FCE4D6", end_color="FCE4D6", fill_type="solid") # Màu cam nhạt cho T7, CN
    
    TITLE_FONT = Font(name="Arial", size=11, bold=True, color="002060")
    HEADER_FONT = Font(name="Arial", size=8, bold=True)
    DATA_FONT = Font(name="Arial", size=9)
    BOLD_DATA_FONT = Font(name="Arial", size=9, bold=True)
    
    CENTER_ALIGN = Alignment(horizontal="center", vertical="center", wrap_text=True)
    LEFT_ALIGN = Alignment(horizontal="left", vertical="center")
    RIGHT_ALIGN = Alignment(horizontal="right", vertical="center")

    THIN_BORDER = Border(
        left=Side(style='thin', color='D9D9D9'),
        right=Side(style='thin', color='D9D9D9'),
        top=Side(style='thin', color='D9D9D9'),
        bottom=Side(style='thin', color='D9D9D9')
    )

    # Các ngày Thứ 7 trong tháng 09/2026: 5, 12, 19, 26
    saturdays = [5, 12, 19, 26]
    # Các ngày Chủ nhật trong tháng 09/2026: 6, 13, 20, 27
    sundays = [6, 13, 20, 27]

    # =============================================================
    # 2. XÂY DỰNG SHEET "NHÂN VIÊN" (ĐÃ XÓA CỘT "TỒN BÙ")
    # =============================================================
    ws_main['A1'] = "BỆNH VIỆN BƯU ĐIỆN"
    ws_main['A1'].font = Font(name="Arial", size=10, bold=True)
    ws_main['A2'] = "Đơn vị: Phòng Công nghệ thông tin"
    ws_main['A2'].font = Font(name="Arial", size=10, bold=True)

    ws_main.merge_cells("W1:AV1")
    ws_main['W1'] = "BẢNG CHẤM CÔNG THÁNG 09 NĂM 2026 (CỦA CBNV)"
    ws_main['W1'].font = TITLE_FONT
    ws_main['W1'].alignment = Alignment(horizontal="center", vertical="center")

    # Header hàng 3 & 4
    ws_main.merge_cells("A3:A4")
    ws_main['A3'] = "STT"
    ws_main.merge_cells("B3:B4")
    ws_main['B3'] = "Mã NV"
    ws_main.merge_cells("C3:C4")
    ws_main['C3'] = "Họ và tên"

    # Tiêu đề Ngày 1 - 30 (Cột D -> AG)
    ws_main.merge_cells("D3:AG3")
    ws_main['D3'] = "Ngày làm việc trong tháng 09.2026"

    for day in range(1, 31):
        col_letter = get_column_letter(3 + day)
        ws_main[f"{col_letter}4"] = f"{day:02d}"

    # Danh sách các cột Tổng hợp (ĐÃ BỎ "Tồn bù")
    summary_headers = [
        ("Hành chính", "AH"),
        ("Làm T7", "AI"),
        ("Làm CN", "AJ"),
        ("Làm Lễ", "AK"),
        ("Trực T7", "AL"),
        ("Trực CN", "AM"),
        ("Trực Lễ", "AN"),
        ("Trực ngày thường", "AO"),
        ("Đã nghỉ bù", "AP"),
        ("Nghỉ bù còn", "AQ"),
        ("Nghỉ phép", "AR"),
        ("Thai sản", "AS"),
        ("Công tác", "AT"),
        ("Nghỉ ốm", "AU"),
        ("Đi học", "AV")
    ]

    for title, col_let in summary_headers:
        ws_main.merge_cells(f"{col_let}3:{col_let}4")
        ws_main[f"{col_let}3"] = title

    # Định dạng Header sheet "NHÂN VIÊN"
    for r in range(3, 5):
        for c in range(1, 49): # Từ A (1) đến AV (48)
            cell = ws_main.cell(row=r, column=c)
            cell.font = HEADER_FONT
            cell.alignment = CENTER_ALIGN
            cell.fill = HEADER_FILL
            cell.border = THIN_BORDER

    # Tô màu nổi bật cột Thứ 7 & Chủ Nhật
    for day in saturdays + sundays:
        col_let = get_column_letter(3 + day)
        ws_main[f"{col_let}4"].fill = WEEKEND_FILL

    # Đổ dữ liệu Nhân viên & Công thức sheet "NHÂN VIÊN"
    start_row = 5
    for idx, (code, name) in enumerate(employees, start=1):
        row = start_row + idx - 1
        ws_main[f"A{row}"] = idx
        ws_main[f"B{row}"] = code
        ws_main[f"C{row}"] = name
        
        # Mẫu dữ liệu chấm công từng ngày
        for day in range(1, 31):
            col_let = get_column_letter(3 + day)
            cell = ws_main[f"{col_let}{row}"]
            if day in saturdays:
                cell.value = "x" if idx % 2 != 0 else "xx" # Mẫu ký hiệu đi làm T7
            elif day in sundays:
                cell.value = ""
            else:
                cell.value = "x"
            cell.alignment = CENTER_ALIGN

        # Công thức tính tổng hợp
        ws_main[f"AH{row}"] = f'=COUNTIF(D{row}:AG{row}, "x") + COUNTIF(D{row}:AG{row}, "xx")*2' # Hành chính
        ws_main[f"AI{row}"] = f'=LÀM THỨ 7!AH{row}' # Lấy tổng công làm T7 từ sheet "LÀM THỨ 7"
        
        for col_let in ["AJ", "AK", "AL", "AM", "AN", "AO", "AP", "AQ", "AR", "AS", "AT", "AU", "AV"]:
            ws_main[f"{col_let}{row}"] = 0

        # Áp dụng định dạng cho hàng dữ liệu
        for c in range(1, 49):
            cell = ws_main.cell(row=row, column=c)
            cell.font = DATA_FONT
            cell.border = THIN_BORDER
            if c in [1, 2]:
                cell.alignment = CENTER_ALIGN
            elif c == 3:
                cell.alignment = LEFT_ALIGN
            elif c >= 34:
                cell.alignment = RIGHT_ALIGN

    # Căn chỉnh độ rộng cột cho sheet "NHÂN VIÊN"
    ws_main.column_dimensions['A'].width = 5
    ws_main.column_dimensions['B'].width = 10
    ws_main.column_dimensions['C'].width = 22
    for day in range(1, 31):
        col_let = get_column_letter(3 + day)
        ws_main.column_dimensions[col_let].width = 3.5
    for title, col_let in summary_headers:
        ws_main.column_dimensions[col_let].width = 11


    # =============================================================
    # 3. XÂY DỰNG SHEET "LÀM THỨ 7" (ĐỒNG BỘ DỮ LIỆU & CĂN CHỈNH)
    # =============================================================
    ws_t7['A1'] = "BỆNH VIỆN BƯU ĐIỆN"
    ws_t7['A1'].font = Font(name="Arial", size=10, bold=True)
    ws_t7['A2'] = "Đơn vị: Phòng Công nghệ thông tin"
    ws_t7['A2'].font = Font(name="Arial", size=10, bold=True)

    ws_t7.merge_cells("D1:AG1")
    ws_t7['D1'] = "BẢNG TỔNG HỢP CHẤM CÔNG LÀM THỨ 7 - THÁNG 09/2026"
    ws_t7['D1'].font = TITLE_FONT
    ws_t7['D1'].alignment = Alignment(horizontal="center", vertical="center")

    # Header hàng 3 & 4
    ws_t7.merge_cells("A3:A4")
    ws_t7['A3'] = "STT"
    ws_t7.merge_cells("B3:B4")
    ws_t7['B3'] = "Mã NV"
    ws_t7.merge_cells("C3:C4")
    ws_t7['C3'] = "Họ và tên"

    ws_t7.merge_cells("D3:AG3")
    ws_t7['D3'] = "Chi tiết ngày làm Thứ 7 trong tháng"

    for day in range(1, 31):
        col_letter = get_column_letter(3 + day)
        ws_t7[f"{col_letter}4"] = f"{day:02d}"

    ws_t7.merge_cells("AH3:AH4")
    ws_t7['AH3'] = "Tổng công T7"

    # Định dạng Header sheet "LÀM THỨ 7"
    for r in range(3, 5):
        for c in range(1, 35): # Từ A (1) đến AH (34)
            cell = ws_t7.cell(row=r, column=c)
            cell.font = HEADER_FONT
            cell.alignment = CENTER_ALIGN
            cell.fill = HEADER_FILL
            cell.border = THIN_BORDER

    # Tô màu cột Thứ 7
    for day in saturdays:
        col_let = get_column_letter(3 + day)
        ws_t7[f"{col_let}4"].fill = WEEKEND_FILL

    # Đổ dữ liệu & Đồng bộ công thức từ sheet "NHÂN VIÊN"
    for idx, (code, name) in enumerate(employees, start=1):
        row = start_row + idx - 1
        ws_t7[f"A{row}"] = idx
        ws_t7[f"B{row}"] = code
        ws_t7[f"C{row}"] = name
        
        # Liên kết trực tiếp ngày Thứ 7 từ sheet NHÂN VIÊN
        for day in range(1, 31):
            col_let = get_column_letter(3 + day)
            cell = ws_t7[f"{col_let}{row}"]
            if day in saturdays:
                # Đồng bộ công thức lấy từ sheet NHÂN VIÊN
                cell.value = f"='NHÂN VIÊN'!{col_let}{row}"
            else:
                cell.value = ""
            cell.alignment = CENTER_ALIGN

        # Công thức tính tổng công T7 (Tính cả 'x' và 'xx')
        ws_t7[f"AH{row}"] = f'=COUNTIF(D{row}:AG{row},"x") + COUNTIF(D{row}:AG{row},"xx")*2'

        # Định dạng dòng dữ liệu
        for c in range(1, 35):
            cell = ws_t7.cell(row=row, column=c)
            cell.font = DATA_FONT
            cell.border = THIN_BORDER
            if c in [1, 2]:
                cell.alignment = CENTER_ALIGN
            elif c == 3:
                cell.alignment = LEFT_ALIGN
            elif c == 34:
                cell.alignment = RIGHT_ALIGN
                cell.font = BOLD_DATA_FONT

    # Căn chỉnh độ rộng cột cho sheet "LÀM THỨ 7"
    ws_t7.column_dimensions['A'].width = 5
    ws_t7.column_dimensions['B'].width = 10
    
    # === CĂN CHỈNH ĐỘ RỘNG CỘT "HỌ VÀ TÊN" THÍCH HỢP (25pt) ===
    ws_t7.column_dimensions['C'].width = 25 
    
    for day in range(1, 31):
        col_let = get_column_letter(3 + day)
        ws_t7.column_dimensions[col_let].width = 3.5
    ws_t7.column_dimensions['AH'].width = 14

    # Lưu Workbook ra file
    output_filename = "Bang_Cham_Cong_Thang_09_2026.xlsx"
    wb.save(output_filename)
    print(f"Tạo file thành công: {output_filename}")

if __name__ == "__main__":
    generate_attendance_sheet()
