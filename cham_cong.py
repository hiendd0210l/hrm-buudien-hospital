import streamlit as st
import pandas as pd
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
import io
import plotly.express as px

# Config trang Streamlit
st.set_page_config(page_title="Quản lý Chấm công & Ngày nghỉ", layout="wide", page_icon="📋")

# ==============================================================================
# HÀM XUẤT FILE EXCEL MẪU CHUẨN CỦA BỆNH VIỆN BƯU ĐIỆN
# ==============================================================================
def generate_attendance_excel(df_employees, unit_name="Phòng Công nghệ thông tin", month=9, year=2026):
    wb = openpyxl.Workbook()
    
    # Tạo các Sheets
    ws_main = wb.active
    ws_main.title = "NHÂN VIÊN"
    ws_htcs = wb.create_sheet(title="HTCS")
    ws_t7 = wb.create_sheet(title="LÀM THỨ 7")
    ws_abc = wb.create_sheet(title="ABC")

    # Styling
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

    # -------------------------------------------------------------
    # 1. SHEET "NHÂN VIÊN" (Đã loại bỏ cột Tồn bù)
    # -------------------------------------------------------------
    ws_main['A1'] = "BỆNH VIỆN BƯU ĐIỆN"
    ws_main['A1'].font = Font(name="Arial", size=10, bold=True)
    ws_main['A2'] = f"Đơn vị: {unit_name}"
    ws_main['A2'].font = Font(name="Arial", size=10, bold=True)

    ws_main.merge_cells("W1:AV1")
    ws_main['W1'] = f"BẢNG CHẤM CÔNG THÁNG {month:02d} NĂM {year} (CỦA CBNV)"
    ws_main['W1'].font = TITLE_FONT
    ws_main['W1'].alignment = CENTER_ALIGN

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
        
        ma_nv = row_data.get("Mã NV", f"N{1000+idx}")
        ho_ten = row_data.get("Họ và tên", "")
        
        ws_main[f"B{row}"] = ma_nv
        ws_main[f"C{row}"] = ho_ten

        for day in range(1, 31):
            col_let = get_column_letter(3 + day)
            cell = ws_main[f"{col_let}{row}"]
            val = row_data.get(f"{day:02d}", "x" if day not in sundays else "")
            cell.value = val
            cell.alignment = CENTER_ALIGN

        ws_main[f"AH{row}"] = f'=COUNTIF(D{row}:AG{row}, "x") + COUNTIF(D{row}:AG{row}, "xx")*2'
        ws_main[f"AI{row}"] = f'=LÀM THỨ 7!AH{row}'
        
        for col_let in ["AJ", "AK", "AL", "AM", "AN", "AO", "AP", "AQ", "AR", "AS", "AT", "AU", "AV"]:
            ws_main[f"{col_let}{row}"] = f'=COUNTIF(D{row}:AG{row}, "{col_let}")' if col_let in ["AR", "AS", "AT", "AU"] else 0

        for c in range(1, 49):
            cell = ws_main.cell(row=row, column=c)
            cell.font = DATA_FONT
            cell.border = THIN_BORDER
            if c in [1, 2]: cell.alignment = CENTER_ALIGN
            elif c == 3: cell.alignment = LEFT_ALIGN
            elif c >= 34: cell.alignment = RIGHT_ALIGN

    ws_main.column_dimensions['A'].width = 5
    ws_main.column_dimensions['B'].width = 10
    ws_main.column_dimensions['C'].width = 25  # Độ rộng 25pt
    for day in range(1, 31):
        ws_main.column_dimensions[get_column_letter(3 + day)].width = 3.5
    for title, col_let in summary_headers:
        ws_main.column_dimensions[col_let].width = 11

    # -------------------------------------------------------------
    # 2. SHEET "LÀM THỨ 7"
    # -------------------------------------------------------------
    ws_t7['A1'] = "BỆNH VIỆN BƯU ĐIỆN"
    ws_t7['A1'].font = Font(name="Arial", size=10, bold=True)
    ws_t7['A2'] = f"Đơn vị: {unit_name}"
    ws_t7['A2'].font = Font(name="Arial", size=10, bold=True)

    ws_t7.merge_cells("D1:AG1")
    ws_t7['D1'] = f"BẢNG TỔNG HỢP CHẤM CÔNG LÀM THỨ 7 - THÁNG {month:02d}/{year}"
    ws_t7['D1'].font = TITLE_FONT
    ws_t7['D1'].alignment = CENTER_ALIGN

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
        ws_t7[f"B{row}"] = row_data.get("Mã NV", f"N{1000+idx}")
        ws_t7[f"C{row}"] = row_data.get("Họ và tên", "")

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
    ws_t7.column_dimensions['C'].width = 25  # Căn chỉnh 25pt chuẩn
    for day in range(1, 31):
        ws_t7.column_dimensions[get_column_letter(3 + day)].width = 3.5
    ws_t7.column_dimensions['AH'].width = 14

    output = io.BytesIO()
    wb.save(output)
    output.seek(0)
    return output


# ==============================================================================
# GIAO DIỆN CHÍNH STREAMLIT
# ==============================================================================
st.title("📋 Quản lý Chấm công & Ngày nghỉ - BV Bưu Điện")

# Sidebar điều hướng
menu = st.sidebar.radio(
    "📌 Phân hệ chức năng",
    [
        "1. Chấm công & Xuất file Đơn vị",
        "2. Đăng ký & Duyệt nghỉ phép/Nghỉ bù",
        "3. Upload & Tổng hợp File Đơn vị",
        "4. Quy định Ký hiệu & Công thức",
        "5. Báo cáo & Thống kê Tổng hợp"
    ]
)

st.sidebar.markdown("---")
st.sidebar.info("💡 **Hệ thống Quản trị Nhân sự v2.5**\nĐã tối ưu giao diện & công thức chấm công.")

# ------------------------------------------------------------------------------
# 1. CHẤM CÔNG VÀ XUẤT FILE TỪNG ĐƠN VỊ
# ------------------------------------------------------------------------------
if menu == "1. Chấm công & Xuất file Đơn vị":
    st.header("📅 Quản lý Chấm công & Xuất File theo Đơn vị")
    
    col_sel1, col_sel2, col_sel3 = st.columns([2, 2, 3])
    with col_sel1:
        thang = st.selectbox("Tháng chấm công", list(range(1, 13)), index=8)
    with col_sel2:
        nam = st.selectbox("Năm", [2024, 2025, 2026], index=2)
    with col_sel3:
        don_vi = st.selectbox("Chọn Khoa / Phòng / Trung tâm", [
            "Phòng Công nghệ thông tin",
            "Khoa Ngoại tổng hợp",
            "Khoa Khám bệnh",
            "Trung tâm Y lao động"
        ])

    st.markdown("---")

    # Giả lập danh sách nhân viên lọc sạch
    data_demo = [
        {"Mã NV": "N1108", "Họ và tên": "Mai Tuấn Linh", "Chức danh": "Kỹ sư CNTT"},
        {"Mã NV": "N1109", "Họ và tên": "Hoàng Tuấn Anh", "Chức danh": "Chuyên viên"},
        {"Mã NV": "N1090", "Họ và tên": "Phạm Văn Hiếu", "Chức danh": "Kỹ sư"},
        {"Mã NV": "N1092", "Họ và tên": "Nguyễn Quang Trung", "Chức danh": "Trưởng phòng"},
        {"Mã NV": "N1095", "Họ và tên": "Vũ Thị Hoa", "Chức danh": "Phó phòng"},
    ]
    df_grid = pd.DataFrame(data_demo)
    
    sundays = [6, 13, 20, 27]
    for day in range(1, 31):
        df_grid[f"{day:02d}"] = "x" if day not in sundays else ""

    st.subheader(f"Bảng chấm công chi tiết - {don_vi} (Tháng {thang:02d}/{nam})")
    
    # Grid chỉnh sửa công
    edited_df = st.data_editor(
        df_grid,
        use_container_width=True,
        height=350,
        num_rows="fixed"
    )

    c_btn1, c_btn2 = st.columns([2, 8])
    with c_btn1:
        if st.button("💾 Lưu dữ liệu chấm công", type="primary", use_container_width=True):
            st.success("Đã lưu dữ liệu thành công!")
            
    with c_btn2:
        excel_file = generate_attendance_excel(edited_df, unit_name=don_vi, month=thang, year=nam)
        st.download_button(
            label=f"📥 Tải File Excel Chấm Công chuẩn ({don_vi})",
            data=excel_file,
            file_name=f"Bang_Cham_Cong_{don_vi.replace(' ', '_')}_T{thang:02d}_{nam}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )

# ------------------------------------------------------------------------------
# 2. KHAI BÁO & DUYỆT NGHỈ PHÉP / NGHỈ BÙ
# ------------------------------------------------------------------------------
elif menu == "2. Đăng ký & Duyệt nghỉ phép/Nghỉ bù":
    st.header("📝 Đăng ký & Duyệt Đơn Xin Nghỉ")
    
    t1, t2 = st.tabs(["📝 Tạo đơn xin nghỉ mới", "📊 Danh sách & Phê duyệt đơn"])
    
    with t1:
        st.subheader("Tạo đơn xin nghỉ bù / nghỉ phép / công tác")
        with st.form("form_nghi"):
            col1, col2 = st.columns(2)
            with col1:
                ma_nv = st.text_input("Mã nhân viên", value="N1108")
                ho_ten = st.text_input("Họ và tên", value="Mai Tuấn Linh")
                loai_nghi = st.selectbox("Loại ngày nghỉ", ["Nghỉ phép (P)", "Nghỉ bù (NB)", "Nghỉ ốm (Om)", "Nghỉ thai sản (TS)", "Đi công tác (CT)"])
            with col2:
                tu_ngay = st.date_input("Từ ngày")
                den_ngay = st.date_input("Đến ngày")
                ly_do = st.text_area("Lý do nghỉ", placeholder="Nhập chi tiết lý do xin nghỉ...")
            
            submit = st.form_submit_button("📩 Gửi đơn xin phê duyệt", type="primary")
            if submit:
                st.success("Đơn xin nghỉ đã được gửi tới Lãnh đạo đơn vị phê duyệt!")

    with t2:
        st.subheader("Danh sách đơn xin nghỉ chờ duyệt")
        requests_data = pd.DataFrame([
            {"Mã NV": "N1108", "Họ tên": "Mai Tuấn Linh", "Loại nghỉ": "Nghỉ bù", "Từ ngày": "2026-09-10", "Đến ngày": "2026-09-11", "Số ngày": 2, "Trạng thái": "Chờ duyệt"},
            {"Mã NV": "N1090", "Họ tên": "Phạm Văn Hiếu", "Loại nghỉ": "Nghỉ phép", "Từ ngày": "2026-09-15", "Đến ngày": "2026-09-15", "Số ngày": 1, "Trạng thái": "Đã duyệt"},
            {"Mã NV": "N1095", "Họ tên": "Vũ Thị Hoa", "Loại nghỉ": "Công tác", "Từ ngày": "2026-09-20", "Đến ngày": "2026-09-22", "Số ngày": 3, "Trạng thái": "Chờ duyệt"},
        ])
        st.dataframe(requests_data, use_container_width=True)

# ------------------------------------------------------------------------------
# 3. UPLOAD VÀ TỔNG HỢP BẢNG CHẤM CÔNG FILE EXCEL CỦA CÁC ĐƠN VỊ
# ------------------------------------------------------------------------------
elif menu == "3. Upload & Tổng hợp File Đơn vị":
    st.header("📤 Upload & Tổng hợp Bảng chấm công toàn Bệnh viện")
    st.info("Chức năng cho phép Phòng Tổ chức Cán bộ tải lên nhiều file Excel chấm công từ các đơn vị để tổng hợp tự động.")

    uploaded_files = st.file_uploader(
        "Kéo thả hoặc chọn các file Excel chấm công (.xlsx) của các Đơn vị",
        type=["xlsx"],
        accept_multiple_files=True
    )

    if uploaded_files:
        st.success(f"Đã nhận {len(uploaded_files)} file Excel. Đang tiến hành đọc và tổng hợp...")
        
        summary_list = []
        for file in uploaded_files:
            try:
                # Đọc dữ liệu từ file Excel
                df_upload = pd.read_excel(file, sheet_name="NHÂN VIÊN", skiprows=3)
                don_vi_name = file.name.split(".")[0].replace("Bang_Cham_Cong_", "")
                
                num_staff = len(df_upload.dropna(subset=[df_upload.columns[1]]))
                summary_list.append({
                    "Tên File": file.name,
                    "Đơn vị / Khoa Phòng": don_vi_name,
                    "Số lượng CBNV": num_staff,
                    "Trạng thái": "✅ Hợp lệ"
                })
            except Exception as e:
                summary_list.append({
                    "Tên File": file.name,
                    "Đơn vị / Khoa Phòng": "Không xác định",
                    "Số lượng CBNV": 0,
                    "Trạng thái": f"❌ Lỗi định dạng ({str(e)})"
                })

        st.subheader("Kết quả đọc File các đơn vị")
        st.table(pd.DataFrame(summary_list))

        if st.button("⚡ Tiến hành Tổng hợp công Toàn Bệnh viện", type="primary"):
            st.balloons()
            st.success("Đã tổng hợp thành công công lao động toàn bệnh viện Tháng 09/2026!")

# ------------------------------------------------------------------------------
# 4. QUY ĐỊNH KÝ HIỆU VÀ CÔNG THỨC TỔNG HỢP
# ------------------------------------------------------------------------------
elif menu == "4. Quy định Ký hiệu & Công thức":
    st.header("⚙️ Quy định Ký hiệu Chấm công & Công thức Tổng hợp")
    
    col_k1, col_k2 = st.columns(2)
    
    with col_k1:
        st.subheader("📌 Danh mục Ký hiệu Chấm công")
        ky_hieu_df = pd.DataFrame([
            {"Ký hiệu": "x", "Tên quy đổi": "Làm ngày hành chính", "Hệ số công": "1.0"},
            {"Ký hiệu": "xx", "Tên quy đổi": "Làm 2 ca / Làm tăng cường", "Hệ số công": "2.0"},
            {"Ký hiệu": "T7", "Tên quy đổi": "Làm ngày Thứ 7", "Hệ số công": "1.0 / 1.5"},
            {"Ký hiệu": "CN", "Tên quy đổi": "Làm ngày Chủ nhật", "Hệ số công": "2.0"},
            {"Ký hiệu": "P", "Tên quy đổi": "Nghỉ phép hưởng lương", "Hệ số công": "1.0"},
            {"Ký hiệu": "Om", "Tên quy đổi": "Nghỉ ốm (BHXH trả)", "Hệ số công": "0.0"},
            {"Ký hiệu": "TS", "Tên quy đổi": "Nghỉ thai sản", "Hệ số công": "0.0"},
            {"Ký hiệu": "NB", "Tên quy đổi": "Nghỉ bù", "Hệ số công": "0.0"},
            {"Ký hiệu": "CT", "Tên quy đổi": "Đi công tác", "Hệ số công": "1.0"},
        ])
        st.table(ky_hieu_df)

    with col_k2:
        st.subheader("🧮 Công thức Tổng hợp Ngày công Excel")
        st.markdown("""
        * **Tổng ngày Hành chính (Cột AH):**
          `=COUNTIF(D[Row]:AG[Row], "x") + COUNTIF(D[Row]:AG[Row], "xx")*2`
        
        * **Tổng ngày Làm Thứ 7 (Cột AI):**
          `='LÀM THỨ 7'!AH[Row]`
        
        * **Tổng ngày Nghỉ phép (Cột AR):**
          `=COUNTIF(D[Row]:AG[Row], "P")`
          
        * **Công thức sheet LÀM THỨ 7:**
          Lấy dữ liệu tự động từ sheet NHÂN VIÊN sang sheet LÀM THỨ 7 bằng công thức `='NHÂN VIÊN'!{Cột}{Dòng}` cho các ngày Thứ 7 trong tháng.
        """)

# ------------------------------------------------------------------------------
# 5. BÁO CÁO & THỐNG KÊ TỔNG HỢP
# ------------------------------------------------------------------------------
elif menu == "5. Báo cáo & Thống kê Tổng hợp":
    st.header("📊 Báo cáo & Thống kê Chấm công Toàn Bệnh viện")
    
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("👥 Tổng CBNV toàn viện", "1,250 người", "+12 so với tháng trước")
    m2.metric("🟢 Tỷ lệ đi làm bình quân", "96.8%", "+0.5%")
    m3.metric("🏖️ Tổng số ngày nghỉ phép", "142 ngày")
    m4.metric("⏰ Tổng giờ làm T7/Trực", "1,850 giờ")

    st.markdown("---")
    
    col_g1, col_g2 = st.columns(2)
    with col_g1:
        st.subheader("Tỷ lệ các loại ngày công trong tháng")
        chart_data = pd.DataFrame({
            "Loại công": ["Hành chính", "Làm T7", "Nghỉ phép", "Nghỉ ốm/TS", "Công tác"],
            "Số lượng": [22000, 3200, 450, 120, 300]
        })
        fig = px.pie(chart_data, values="Số lượng", names="Loại công", hole=0.4, color_discrete_sequence=px.colors.qualitative.Pastel)
        st.plotly_chart(fig, use_container_width=True)

    with col_g2:
        st.subheader("So sánh ngày công giữa các Đơn vị")
        unit_chart = pd.DataFrame({
            "Đơn vị": ["Khoa Khám bệnh", "Khoa Ngoại", "Phòng CNTT", "TT Y lao động"],
            "Công trung bình": [22.5, 23.1, 22.0, 21.8]
        })
        fig_bar = px.bar(unit_chart, x="Đơn vị", y="Công trung bình", color="Đơn vị", text_auto=True)
        st.plotly_chart(fig_bar, use_container_width=True)
