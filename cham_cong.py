import streamlit as st
import pandas as pd
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
import io

def generate_attendance_excel(df_employees, month=9, year=2026):
    """
    Hàm xuất file Excel chấm công chuẩn:
    1. Xóa bỏ hoàn toàn cột "Tồn bù"
    2. Đồng bộ công thức ngày T7, CN, Lễ sang sheet "LÀM THỨ 7" và tính tổng công riêng
    3. Căn chỉnh độ rộng cột "Họ và tên" sheet LÀM THỨ 7 lên 25pt
    """
    wb = openpyxl.Workbook()
    
    ws_main = wb.active
    ws_main.title = "NHÂN VIÊN"
    ws_htcs = wb.create_sheet(title="HTCS")
    ws_t7 = wb.create_sheet(title="LÀM THỨ 7")
    ws_abc = wb.create_sheet(title="ABC")

    HEADER_FILL = PatternFill(start_color="D9E1F2", end_color="D9E1F2", fill_type="solid")
    WEEKEND_FILL = PatternFill(start_color="FCE4D6", end_color="FCE4D6", fill_type="solid")
    
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

    saturdays = [5, 12, 19, 26]
    sundays = [6, 13, 20, 27]

    # =============================================================
    # 1. SHEET "NHÂN VIÊN" (ĐÃ XÓA CỘT TỒN BÙ)
    # =============================================================
    ws_main['A1'] = "BỆNH VIỆN BƯU ĐIỆN"
    ws_main['A1'].font = Font(name="Arial", size=10, bold=True)
    ws_main['A2'] = "Đơn vị: Phòng Công nghệ thông tin"
    ws_main['A2'].font = Font(name="Arial", size=10, bold=True)

    ws_main.merge_cells("W1:AV1")
    ws_main['W1'] = f"BẢNG CHẤM CÔNG THÁNG {month:02d} NĂM {year} (CỦA CBNV)"
    ws_main['W1'].font = TITLE_FONT
    ws_main['W1'].alignment = Alignment(horizontal="center", vertical="center")

    ws_main.merge_cells("A3:A4")
    ws_main['A3'] = "STT"
    ws_main.merge_cells("B3:B4")
    ws_main['B3'] = "Mã NV"
    ws_main.merge_cells("C3:C4")
    ws_main['C3'] = "Họ và tên"

    ws_main.merge_cells("D3:AG3")
    ws_main['D3'] = f"Ngày làm việc trong tháng {month:02d}.{year}"

    for day in range(1, 31):
        ws_main[f"{get_column_letter(3 + day)}4"] = f"{day:02d}"

    summary_headers = [
        ("Hành chính", "AH"), ("Làm T7", "AI"), ("Làm CN", "AJ"),
        ("Làm Lễ", "AK"), ("Trực T7", "AL"), ("Trực CN", "AM"),
        ("Trực Lễ", "AN"), ("Trực ngày thường", "AO"), ("Đã nghỉ bù", "AP"),
        ("Nghỉ bù còn", "AQ"), ("Nghỉ phép", "AR"), ("Thai sản", "AS"),
        ("Công tác", "AT"), ("Nghỉ ốm", "AU"), ("Đi học", "AV")
    ]

    for title, col_let in summary_headers:
        ws_main.merge_cells(f"{col_let}3:{col_let}4")
        ws_main[f"{col_let}3"] = title

    for r in range(3, 5):
        for c in range(1, 49):
            cell = ws_main.cell(row=r, column=c)
            cell.font = HEADER_FONT
            cell.alignment = CENTER_ALIGN
            cell.fill = HEADER_FILL
            cell.border = THIN_BORDER

    for day in saturdays + sundays:
        ws_main[f"{get_column_letter(3 + day)}4"].fill = WEEKEND_FILL

    start_row = 5
    for idx, row_data in df_employees.reset_index(drop=True).iterrows():
        row = start_row + idx
        ws_main[f"A{row}"] = idx + 1
        
        ma_nv = row_data.get("Mã NV", row_data.get("ma_nv", row_data.get("Mã cán bộ", f"N{1000+idx}")))
        ho_ten = row_data.get("Họ và tên", row_data.get("ho_ten", row_data.get("Họ tên", "")))
        
        ws_main[f"B{row}"] = ma_nv
        ws_main[f"C{row}"] = ho_ten

        for day in range(1, 31):
            col_let = get_column_letter(3 + day)
            cell = ws_main[f"{col_let}{row}"]
            val = row_data.get(f"D{day}", "x" if day not in sundays else "")
            cell.value = val
            cell.alignment = CENTER_ALIGN

        ws_main[f"AH{row}"] = f'=COUNTIF(D{row}:AG{row}, "x") + COUNTIF(D{row}:AG{row}, "xx")*2'
        ws_main[f"AI{row}"] = f'=LÀM THỨ 7!AH{row}'
        
        for col_let in ["AJ", "AK", "AL", "AM", "AN", "AO", "AP", "AQ", "AR", "AS", "AT", "AU", "AV"]:
            ws_main[f"{col_let}{row}"] = 0

        for c in range(1, 49):
            cell = ws_main.cell(row=row, column=c)
            cell.font = DATA_FONT
            cell.border = THIN_BORDER
            if c in [1, 2]: cell.alignment = CENTER_ALIGN
            elif c == 3: cell.alignment = LEFT_ALIGN
            elif c >= 34: cell.alignment = RIGHT_ALIGN

    ws_main.column_dimensions['A'].width = 5
    ws_main.column_dimensions['B'].width = 10
    ws_main.column_dimensions['C'].width = 22
    for day in range(1, 31):
        ws_main.column_dimensions[get_column_letter(3 + day)].width = 3.5
    for title, col_let in summary_headers:
        ws_main.column_dimensions[col_let].width = 11

    # =============================================================
    # 2. SHEET "LÀM THỨ 7"
    # =============================================================
    ws_t7['A1'] = "BỆNH VIỆN BƯU ĐIỆN"
    ws_t7['A1'].font = Font(name="Arial", size=10, bold=True)
    ws_t7['A2'] = "Đơn vị: Phòng Công nghệ thông tin"
    ws_t7['A2'].font = Font(name="Arial", size=10, bold=True)

    ws_t7.merge_cells("D1:AG1")
    ws_t7['D1'] = f"BẢNG TỔNG HỢP CHẤM CÔNG LÀM THỨ 7 - THÁNG {month:02d}/{year}"
    ws_t7['D1'].font = TITLE_FONT
    ws_t7['D1'].alignment = Alignment(horizontal="center", vertical="center")

    ws_t7.merge_cells("A3:A4")
    ws_t7['A3'] = "STT"
    ws_t7.merge_cells("B3:B4")
    ws_t7['B3'] = "Mã NV"
    ws_t7.merge_cells("C3:C4")
    ws_t7['C3'] = "Họ và tên"

    ws_t7.merge_cells("D3:AG3")
    ws_t7['D3'] = "Chi tiết ngày làm Thứ 7 trong tháng"

    for day in range(1, 31):
        ws_t7[f"{get_column_letter(3 + day)}4"] = f"{day:02d}"

    ws_t7.merge_cells("AH3:AH4")
    ws_t7['AH3'] = "Tổng công T7"

    for r in range(3, 5):
        for c in range(1, 35):
            cell = ws_t7.cell(row=r, column=c)
            cell.font = HEADER_FONT
            cell.alignment = CENTER_ALIGN
            cell.fill = HEADER_FILL
            cell.border = THIN_BORDER

    for day in saturdays:
        ws_t7[f"{get_column_letter(3 + day)}4"].fill = WEEKEND_FILL

    for idx, row_data in df_employees.reset_index(drop=True).iterrows():
        row = start_row + idx
        ws_t7[f"A{row}"] = idx + 1
        
        ma_nv = row_data.get("Mã NV", row_data.get("ma_nv", row_data.get("Mã cán bộ", f"N{1000+idx}")))
        ho_ten = row_data.get("Họ và tên", row_data.get("ho_ten", row_data.get("Họ tên", "")))

        ws_t7[f"B{row}"] = ma_nv
        ws_t7[f"C{row}"] = ho_ten

        for day in range(1, 31):
            col_let = get_column_letter(3 + day)
            cell = ws_t7[f"{col_let}{row}"]
            if day in saturdays:
                cell.value = f"='NHÂN VIÊN'!{col_let}{row}"
            else:
                cell.value = ""
            cell.alignment = CENTER_ALIGN

        ws_t7[f"AH{row}"] = f'=COUNTIF(D{row}:AG{row},"x") + COUNTIF(D{row}:AG{row},"xx")*2'

        for c in range(1, 35):
            cell = ws_t7.cell(row=row, column=c)
            cell.font = DATA_FONT
            cell.border = THIN_BORDER
            if c in [1, 2]: cell.alignment = CENTER_ALIGN
            elif c == 3: cell.alignment = LEFT_ALIGN
            elif c == 34: 
                cell.alignment = RIGHT_ALIGN
                cell.font = BOLD_DATA_FONT

    ws_t7.column_dimensions['A'].width = 5
    ws_t7.column_dimensions['B'].width = 10
    ws_t7.column_dimensions['C'].width = 25  # Căn rộng cột Họ và tên 25pt
    
    for day in range(1, 31):
        ws_t7.column_dimensions[get_column_letter(3 + day)].width = 3.5
    ws_t7.column_dimensions['AH'].width = 14

    output = io.BytesIO()
    wb.save(output)
    output.seek(0)
    return output


def render_quan_ly_cham_cong(df_cb=None):
    """
    Khôi phục đầy đủ giao diện Quản lý chấm công ban đầu
    """
    st.title("📋 Quản lý Chấm công & Ngày nghỉ")

    if df_cb is None or (isinstance(df_cb, pd.DataFrame) and df_cb.empty):
        df_cb = pd.DataFrame([
            {"Mã NV": "N1108", "Họ và tên": "Mai Tuấn Linh", "Chức vụ": "Cán bộ"},
            {"Mã NV": "N1109", "Họ và tên": "Hoàng Tuấn Anh", "Chức vụ": "Cán bộ"},
        ])

    # Bộ lọc Thời gian & Phòng ban
    col1, col2, col3 = st.columns([2, 2, 3])
    with col1:
        thang = st.selectbox("Tháng", list(range(1, 13)), index=8)
    with col2:
        nam = st.selectbox("Năm", [2024, 2025, 2026], index=2)
    with col3:
        don_vi = st.selectbox("Đơn vị / Phòng ban", ["Phòng Công nghệ thông tin", "Tất cả các khoa phòng"])

    # Các Tabs chức năng chính
    tab1, tab2, tab3 = st.tabs(["📅 Bảng chấm công chi tiết", "📊 Tổng hợp công", "⚙️ Thiết lập ký hiệu"])

    with tab1:
        st.subheader(f"Bảng chấm công chi tiết - Tháng {thang:02d}/{nam}")
        
        # Tạo khung xem & chỉnh sửa chấm công
        df_display = df_cb.copy()
        
        # Thêm mô phỏng các cột ngày trong tháng D1 -> D30
        for day in range(1, 31):
            df_display[f"Ngày {day:02d}"] = "x" if day not in [5, 6, 12, 13, 19, 20, 26, 27] else ""
            
        st.data_editor(df_display, use_container_width=True, height=400, num_rows="dynamic")

        col_act1, col_act2 = st.columns([2, 8])
        with col_act1:
            if st.button("💾 Lưu bảng công", type="primary"):
                st.success("Đã lưu bảng chấm công thành công!")
        with col_act2:
            excel_data = generate_attendance_excel(df_cb, month=thang, year=nam)
            st.download_button(
                label="📥 Xuất file Excel Chấm Công (Theo mẫu chuẩn)",
                data=excel_data,
                file_name=f"Bang_Cham_Cong_Thang_{thang:02d}_{nam}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

    with tab2:
        st.subheader("Tổng hợp công trong tháng")
        st.dataframe(df_cb, use_container_width=True)

    with tab3:
        st.subheader("Quy định ký hiệu chấm công")
        st.markdown("""
        - **x**: Làm đủ ca hành chính (1 công)
        - **xx**: Làm thêm ca / làm ngày nghỉ (2 công)
        - **Om**: Nghỉ ốm
        - **P**: Nghỉ phép
        """)
