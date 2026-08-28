import os
import io
import base64
import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import plotly.express as px
from datetime import datetime
from sqlalchemy import create_engine, text

# ---------------------------------------------------------
# 1. CẤU HÌNH TRANG & CSS GIAO DIỆN
# ---------------------------------------------------------
st.set_page_config(
    page_title="BỆNH VIỆN BƯU ĐIỆN - Hệ thống Quản trị Nhân sự & Điều hành",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .stApp { background-color: #f1f5f9 !important; }
    [data-testid="stVerticalBlockBorderWrapper"], form[key="login_form"] {
        background-color: #ffffff !important;
        border-radius: 16px !important;
        border: 1px solid #e2e8f0 !important;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.08), 0 8px 10px -6px rgba(0, 0, 0, 0.03) !important;
        padding: 30px 25px 25px 25px !important;
    }
    .hospital-title {
        color: #0066b2 !important; font-weight: 800 !important;
        font-size: 30px !important; text-align: center;
        margin-top: 15px; margin-bottom: 4px; letter-spacing: 0.5px;
    }
    .hospital-subtitle {
        color: #475569 !important; font-size: 16px !important;
        font-weight: 600 !important; text-align: center; margin-bottom: 25px;
    }
    .stTextInput > label, .stSelectbox > label {
        color: #0f172a !important; font-size: 15px !important;
        font-weight: 700 !important; margin-bottom: 4px !important;
    }
    .stTextInput > div > div > input {
        border-radius: 8px !important; border: 1.5px solid #cbd5e1 !important;
        background-color: #ffffff !important; color: #0f172a !important; height: 44px !important;
    }
    .stButton > button, div[data-testid="stFormSubmitButton"] > button {
        background: linear-gradient(180deg, #0070d2 0%, #0056a3 100%) !important;
        color: #ffffff !important; font-weight: 800 !important;
        font-size: 16px !important; border-radius: 8px !important;
        border: 1px solid #004080 !important; height: 44px !important;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.12) !important; width: 100% !important;
    }
    .stButton > button p, div[data-testid="stFormSubmitButton"] > button p {
        color: #ffffff !important; font-weight: 800 !important; font-size: 16px !important;
    }
    .card-box {
        padding: 20px; border-radius: 10px; color: white; margin-bottom: 15px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1); min-height: 130px;
    }
    .card-red { background: linear-gradient(135deg, #e53935, #d32f2f); }
    .card-green { background: linear-gradient(135deg, #00b074, #008a5b); }
    .card-blue { background: linear-gradient(135deg, #29b6f6, #0288d1); }
    .card-dark { background: linear-gradient(135deg, #37474f, #263238); }
    .card-orange { background: linear-gradient(135deg, #ff9200, #e67e00); }
    .card-teal { background: linear-gradient(135deg, #00a896, #028090); }
    .card-title { font-size: 15px; font-weight: bold; margin-bottom: 5px; text-transform: uppercase; }
    .card-desc { font-size: 12px; opacity: 0.9; margin-bottom: 10px; }
    .card-link { font-size: 11px; font-weight: bold; text-align: right; text-transform: uppercase; }
    .badge-circle {
        background-color: #ffffff; border: 2px solid; border-radius: 50%;
        width: 30px; height: 30px; display: inline-flex; align-items: center;
        justify-content: center; font-weight: bold; float: right;
    }
    .badge-red { border-color: #ff4d4f; color: #ff4d4f; }
    .badge-orange { border-color: #ff9200; color: #ff9200; }
    .badge-blue { border-color: #29b6f6; color: #29b6f6; }
    .badge-green { border-color: #00b074; color: #00b074; }
    .alert-item {
        background-color: #ffffff; padding: 12px 15px; border-radius: 8px;
        margin-bottom: 10px; border-left: 4px solid #00b074; box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
</style>
""", unsafe_allow_html=True)

if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

# ---------------------------------------------------------
# 2. KẾT NỐI DATABASE NEON & TỰ ĐỘNG SỬA SCHEMA
# ---------------------------------------------------------
def get_db_engine():
    try:
        if "DATABASE_URL" in st.secrets:
            raw_url = st.secrets["DATABASE_URL"].strip()
            if raw_url.startswith("postgres://"):
                raw_url = raw_url.replace("postgres://", "postgresql://", 1)
            eng = create_engine(raw_url, pool_pre_ping=True)
        elif "postgres" in st.secrets:
            pg = st.secrets["postgres"]
            db_url = f"postgresql://{pg['user']}:{pg['password']}@{pg['host']}:{pg['port']}/{pg['database']}?sslmode=require"
            eng = create_engine(db_url, pool_pre_ping=True)
        else:
            return None

        with eng.connect() as conn:
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS can_bo (
                    id SERIAL PRIMARY KEY,
                    ma_can_bo VARCHAR(50),
                    ho_ten VARCHAR(255),
                    ngay_sinh DATE,
                    chuc_danh VARCHAR(100),
                    khoa_phong VARCHAR(255),
                    trinh_do VARCHAR(100),
                    so_dien_thoai VARCHAR(20),
                    email VARCHAR(100)
                );
            """))
            conn.commit()

            # Thêm cột nếu thiếu
            columns_to_check = [
                ("ma_can_bo", "VARCHAR(50)"),
                ("ho_ten", "VARCHAR(255)"),
                ("ngay_sinh", "DATE"),
                ("chuc_danh", "VARCHAR(100)"),
                ("khoa_phong", "VARCHAR(255)"),
                ("trinh_do", "VARCHAR(100)"),
                ("so_dien_thoai", "VARCHAR(20)"),
                ("email", "VARCHAR(100)")
            ]
            for col_name, col_type in columns_to_check:
                conn.execute(text(f"ALTER TABLE can_bo ADD COLUMN IF NOT EXISTS {col_name} {col_type};"))
            
            # Gỡ bỏ constraint NOT NULL ở cột ngay_sinh để tránh lỗi upload
            try:
                conn.execute(text("ALTER TABLE can_bo ALTER COLUMN ngay_sinh DROP NOT NULL;"))
            except Exception:
                pass

            conn.commit()

        return eng
    except Exception as e:
        st.error(f"Lỗi kết nối CSDL: {e}")
        return None

engine = get_db_engine()

def load_data_from_db():
    if not engine:
        return pd.DataFrame()
    try:
        with engine.connect() as conn:
            query = text("SELECT id, ma_can_bo, ho_ten, ngay_sinh, chuc_danh, khoa_phong, trinh_do, so_dien_thoai, email FROM can_bo ORDER BY id DESC")
            df = pd.read_sql(query, conn)
            return df
    except Exception as e:
        st.error(f"Lỗi đọc dữ liệu: {e}")
        return pd.DataFrame()

# ---------------------------------------------------------
# 3. TRANG ĐĂNG NHẬP
# ---------------------------------------------------------
def render_login():
    st.markdown("<br>", unsafe_allow_html=True)
    col_l, col_center, col_r = st.columns([1.5, 2.2, 1.5])

    with col_center:
        with st.form(key="login_form", clear_on_submit=False):
            logo_path = os.path.join(os.path.dirname(__file__), "logo.png") if '__file__' in globals() else "logo.png"

            if os.path.exists(logo_path):
                with open(logo_path, "rb") as f:
                    encoded_img = base64.b64encode(f.read()).decode("utf-8")
                st.markdown(
                    f"""
                    <div style="display: flex; justify-content: center; align-items: center; margin-bottom: 10px;">
                        <img src="data:image/png;base64,{encoded_img}" width="220" style="object-fit: contain;">
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            else:
                st.image("logo.png", width=220)

            st.markdown("<div class='hospital-title'>BỆNH VIỆN BƯU ĐIỆN</div>", unsafe_allow_html=True)
            st.markdown("<div class='hospital-subtitle'>Hệ thống Quản trị Nhân sự & Điều hành</div>", unsafe_allow_html=True)

            username = st.text_input("Tên đăng nhập / Username:", placeholder="Nhập tên đăng nhập...")
            password = st.text_input("Mật khẩu / Password:", type="password", placeholder="Nhập mật khẩu...")

            st.markdown("<br>", unsafe_allow_html=True)

            b_col1, b_col2 = st.columns(2)
            with b_col1:
                submit_login = st.form_submit_button("🔑 Đăng nhập", use_container_width=True)
            with b_col2:
                submit_exit = st.form_submit_button("✕ Thoát", use_container_width=True)

            if submit_login:
                if username == "admin" and password == "admin123":
                    st.session_state['logged_in'] = True
                    st.success("Đăng nhập thành công!")
                    st.rerun()
                else:
                    st.error("❌ Tên đăng nhập hoặc mật khẩu chưa đúng!")

            if submit_exit:
                st.info("Đã đóng phiên đăng nhập.")

    components.html("""
    <script>
        const doc = window.parent.document;
        doc.addEventListener('keydown', function(e) {
            if (e.key === 'Escape' || e.keyCode === 27) {
                const buttons = doc.querySelectorAll('div[data-testid="stFormSubmitButton"] button');
                if (buttons.length >= 2) {
                    buttons[1].click();
                }
            }
        });
    </script>
    """, height=0)

# ---------------------------------------------------------
# 4. DASHBOARD TRANG CHỦ
# ---------------------------------------------------------
def render_dashboard_home():
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("<div class='card-box card-red'><div class='card-title'>👨‍⚕️ HỒ SƠ CÁN BỘ CNV</div><div class='card-desc'>Theo dõi, cập nhật và quản lý toàn bộ danh sách hồ sơ nhân sự toàn bệnh viện.</div><div class='card-link'>XEM CHI TIẾT ➔</div></div>", unsafe_allow_html=True)
        st.markdown("<div class='card-box card-dark'><div class='card-title'>📜 HỢP ĐỒNG LAO ĐỘNG</div><div class='card-desc'>Theo dõi hợp đồng xác định thời hạn, không xác định thời hạn và lịch sử ký.</div><div class='card-link'>QUẢN LÝ HỒ SƠ ➔</div></div>", unsafe_allow_html=True)

    with col2:
        st.markdown("<div class='card-box card-green'><div class='card-title'>📊 BÁO CÁO & THỐNG KÊ</div><div class='card-desc'>Truy xuất dữ liệu báo cáo BYT, BVT và biến động nhân sự theo thời gian thực.</div><div class='card-link'>XEM BÁO CÁO ➔</div></div>", unsafe_allow_html=True)
        st.markdown("<div class='card-box card-orange'><div class='card-title'>📈 NÂNG BẬC LƯƠNG & NGẠCH</div><div class='card-desc'>Quản lý nâng lương, ngạch viên chức và cảnh báo danh sách đủ điều kiện nâng lương.</div><div class='card-link'>XEM DANH SÁCH ➔</div></div>", unsafe_allow_html=True)

    with col3:
        st.markdown("<div class='card-box card-blue'><div class='card-title'>🏥 GPHN & ĐÀO TẠO CME</div><div class='card-desc'>Quản lý Chứng chỉ hành nghề và tiến độ tích lũy 48 tiết CME của Bác sĩ / Điều dưỡng.</div><div class='card-link'>XEM CHI TIẾT ➔</div></div>", unsafe_allow_html=True)
        st.markdown("<div class='card-box card-teal'><div class='card-title'>🩺 QUẢN LÝ BHOI & SỨC KHỎE</div><div class='card-desc'>Theo dõi chế độ bảo hiểm sở hữu, đóng xem và đợt khám sức khỏe định kỳ.</div><div class='card-link'>CHI TIẾT ➔</div></div>", unsafe_allow_html=True)

    st.markdown("---")

    c_left, c_mid, c_right = st.columns([1.2, 1.4, 1.4])
    with c_left:
        st.subheader("📌 Cảnh báo tự động")
        st.markdown("""
        <div class="alert-item"><span class="badge-circle badge-red">12</span><b>⏳ Sắp hết hạn HĐLĐ</b><br><small style="color: gray;">Cần tái ký / gia hạn trong 30 ngày</small></div>
        <div class="alert-item"><span class="badge-circle badge-orange">08</span><b>💰 Đến hạn nâng bậc lương</b><br><small style="color: gray;">Đủ thời hạn nâng lương ngạch, bậc</small></div>
        <div class="alert-item"><span class="badge-circle badge-blue">25</span><b>⚠️ Cảnh báo thiếu giờ CME</b><br><small style="color: gray;">Chưa tích lũy đủ 48 tiết / 2 năm</small></div>
        <div class="alert-item"><span class="badge-circle badge-green">04</span><b>📜 GPHN cần cập nhật</b><br><small style="color: gray;">Bổ sung thông tin chứng chỉ mới</small></div>
        """, unsafe_allow_html=True)

    with c_mid:
        st.subheader("📊 Nhân sự theo Trình độ")
        data_trinh_do = pd.DataFrame({"Trình độ": ["Tiến sĩ / CKI", "Thạc sĩ / CKI", "Đại học", "Cao đẳng", "Trung cấp / Khác"], "Số lượng": [25, 142, 450, 180, 80]})
        fig_bar = px.bar(data_trinh_do, x="Trình độ", y="Số lượng", text="Số lượng", color="Trình độ", color_discrete_sequence=['#ff9200', '#5c6bc0', '#26a69a', '#9ccc65', '#ec407a'])
        fig_bar.update_layout(showlegend=False, margin=dict(l=10, r=10, t=20, b=20), height=320)
        st.plotly_chart(fig_bar, use_container_width=True)

    with c_right:
        st.subheader("🍩 Phân loại Hợp đồng")
        data_hd = pd.DataFrame({"Loại HĐ": ["Không xác định thời hạn", "Xác định thời hạn (1-3 năm)", "Thử việc / Ngắn hạn"], "Số lượng": [520, 310, 47]})
        fig_donut = px.pie(data_hd, names="Loại HĐ", values="Số lượng", hole=0.5, color_discrete_sequence=['#0288d1', '#ff9200', '#00b074'])
        fig_donut.update_layout(legend=dict(orientation="h", yanchor="bottom", y=-0.3, xanchor="center", x=0.5), margin=dict(l=10, r=10, t=20, b=20), height=320)
        st.plotly_chart(fig_donut, use_container_width=True)

# ---------------------------------------------------------
# 5. CHỨC NĂNG QUẢN LÝ CÁN BỘ CNV
# ---------------------------------------------------------
def render_quan_ly_can_bo():
    st.markdown("---")
    st.subheader("📁 QUẢN LÝ CÁN BỘ CNV BỆNH VIỆN BƯU ĐIỆN")

    if not engine:
        st.error("Chưa kết nối được Cơ sở dữ liệu Neon. Vui lòng kiểm tra lại cấu hình Secrets.")
        return

    df = load_data_from_db()

    tab1, tab2, tab3, tab4 = st.tabs([
        "📋 Danh sách & Xóa", 
        "➕ Thêm / ✏️ Sửa Nhân sự", 
        "📥 Tải File Mẫu & Nhập Excel", 
        "📤 Xuất Data Excel"
    ])

    # TAB 1: DANH SÁCH & XÓA CÁ NHÂN
    with tab1:
        col_t1, col_t2 = st.columns([4, 1])
        col_t1.markdown("##### **Danh sách cán bộ nhân viên hiện có**")
        if col_t2.button("🔄 Tải lại dữ liệu"):
            st.cache_data.clear()
            st.rerun()

        if df.empty:
            st.info("Chưa có dữ liệu nhân sự trong cơ sở dữ liệu. Bạn có thể thêm mới hoặc nhập từ file Excel.")
        else:
            st.dataframe(df, use_container_width=True)
            
            st.markdown("---")
            st.markdown("##### 🗑️ **Xóa dữ liệu cá nhân**")
            col_del1, col_del2 = st.columns([3, 1])
            
            options_del = {f"{row['ma_can_bo']} - {row['ho_ten']} ({row['khoa_phong']})": row['id'] for _, row in df.iterrows()}
            selected_del = col_del1.selectbox("Chọn nhân sự muốn xóa:", list(options_del.keys()), key="select_del")
            
            if col_del2.button("🗑️ Xóa nhân sự", use_container_width=True):
                target_id = options_del[selected_del]
                with engine.connect() as conn:
                    conn.execute(text("DELETE FROM can_bo WHERE id = :id"), {"id": target_id})
                    conn.commit()
                st.cache_data.clear()
                st.success(f"Đã xóa thành công nhân sự [{selected_del}]!")
                st.rerun()

    # TAB 2: THÊM & SỬA
    with tab2:
        action_mode = st.radio("Chọn thao tác:", ["➕ Thêm Nhân sự Mới", "✏️ Chỉnh sửa thông tin Cán bộ"], horizontal=True)
        
        if action_mode == "➕ Thêm Nhân sự Mới":
            with st.form("form_add_member", clear_on_submit=True):
                c1, c2 = st.columns(2)
                ma_can_bo = c1.text_input("Mã Cán bộ (*)", placeholder="Ví dụ: CB001")
                ho_ten = c2.text_input("Họ và Tên (*)", placeholder="Ví dụ: Nguyễn Văn A")
                ngay_sinh = c1.date_input("Ngày sinh", value=datetime(1990, 1, 1))
                chuc_danh = c2.selectbox("Chức danh", ["Bác sĩ", "Dược sĩ", "Điều dưỡng", "Kỹ thuật viên", "Hành chính", "Khác"])
                khoa_phong = c1.text_input("Khoa / Phòng", placeholder="Ví dụ: Khoa Cấp cứu")
                trinh_do = c2.selectbox("Trình độ", ["Tiến sĩ", "Thạc sĩ / CKI", "Đại học", "Cao đẳng", "Trung cấp", "Khác"])
                sdt = c1.text_input("Số điện thoại")
                email = c2.text_input("Email")
                
                btn_add = st.form_submit_button("💾 Lưu Nhân sự Mới")
                
                if btn_add:
                    if not ma_can_bo or not ho_ten:
                        st.warning("Vui lòng nhập đầy đủ Mã Cán bộ và Họ Tên!")
                    else:
                        try:
                            with engine.connect() as conn:
                                conn.execute(text("""
                                    INSERT INTO can_bo (ma_can_bo, ho_ten, ngay_sinh, chuc_danh, khoa_phong, trinh_do, so_dien_thoai, email)
                                    VALUES (:m, :h, :ns, :c, :k, :t, :s, :e)
                                """), {"m": ma_can_bo.strip(), "h": ho_ten.strip(), "ns": ngay_sinh, "c": chuc_danh, "k": khoa_phong, "t": trinh_do, "s": sdt, "e": email})
                                conn.commit()
                            st.cache_data.clear()
                            st.success(f"Đã thêm thành công nhân sự {ho_ten}!")
                            st.rerun()
                        except Exception as ex:
                            st.error(f"Lỗi thêm mới: {ex}")

        else:
            if df.empty:
                st.info("Chưa có dữ liệu để chỉnh sửa.")
            else:
                options_edit = {f"{row['ma_can_bo']} - {row['ho_ten']}": row['id'] for _, row in df.iterrows()}
                selected_edit = st.selectbox("Chọn nhân sự cần sửa thông tin:", list(options_edit.keys()))
                edit_id = options_edit[selected_edit]
                
                curr_row = df[df['id'] == edit_id].iloc[0]
                
                with st.form("form_edit_member"):
                    c1, c2 = st.columns(2)
                    ma_can_bo = c1.text_input("Mã Cán bộ (*)", value=str(curr_row['ma_can_bo'] or ''))
                    ho_ten = c2.text_input("Họ và Tên (*)", value=str(curr_row['ho_ten'] or ''))
                    
                    val_ns = curr_row['ngay_sinh'] if pd.notna(curr_row['ngay_sinh']) else datetime(1990, 1, 1)
                    ngay_sinh = c1.date_input("Ngày sinh", value=val_ns)
                    
                    list_cd = ["Bác sĩ", "Dược sĩ", "Điều dưỡng", "Kỹ thuật viên", "Hành chính", "Khác"]
                    cd_idx = list_cd.index(curr_row['chuc_danh']) if curr_row['chuc_danh'] in list_cd else 0
                    chuc_danh = c2.selectbox("Chức danh", list_cd, index=cd_idx)
                    
                    khoa_phong = c1.text_input("Khoa / Phòng", value=str(curr_row['khoa_phong'] or ''))
                    
                    list_td = ["Tiến sĩ", "Thạc sĩ / CKI", "Đại học", "Cao đẳng", "Trung cấp", "Khác"]
                    td_idx = list_td.index(curr_row['trinh_do']) if curr_row['trinh_do'] in list_td else 0
                    trinh_do = c2.selectbox("Trình độ", list_td, index=td_idx)
                    
                    sdt = c1.text_input("Số điện thoại", value=str(curr_row['so_dien_thoai'] or ''))
                    email = c2.text_input("Email", value=str(curr_row['email'] or ''))
                    
                    btn_update = st.form_submit_button("🔄 Cập nhật Thông tin")
                    
                    if btn_update:
                        try:
                            with engine.connect() as conn:
                                conn.execute(text("""
                                    UPDATE can_bo 
                                    SET ma_can_bo = :m, ho_ten = :h, ngay_sinh = :ns, chuc_danh = :c, 
                                        khoa_phong = :k, trinh_do = :t, so_dien_thoai = :s, email = :e
                                    WHERE id = :id
                                """), {"m": ma_can_bo.strip(), "h": ho_ten.strip(), "ns": ngay_sinh, "c": chuc_danh, "k": khoa_phong, "t": trinh_do, "s": sdt, "e": email, "id": edit_id})
                                conn.commit()
                            st.cache_data.clear()
                            st.success("Đã cập nhật thông tin thành công!")
                            st.rerun()
                        except Exception as ex:
                            st.error(f"Lỗi cập nhật: {ex}")

    # TAB 3: TẢI MẪU & UPLOAD EXCEL (ĐÃ XỬ LÝ CỘT NGÀY SINH TỰ ĐỘNG)
    with tab3:
        col_m1, col_m2 = st.columns([1.5, 2])
        
        with col_m1:
            st.markdown("##### 📥 **1. Tải về file Excel mẫu**")
            st.caption("Hãy dùng file mẫu này để hệ thống nhận diện chính xác 100%.")
            
            sample_df = pd.DataFrame({
                'Mã Cán bộ': ['CB001', 'CB002'],
                'Họ và Tên': ['Nguyễn Văn A', 'Trần Thị B'],
                'Ngày sinh': ['1990-01-15', '1992-05-20'],
                'Chức danh': ['Bác sĩ', 'Điều dưỡng'],
                'Khoa / Phòng': ['Khoa Cấp cứu', 'Khoa Nội'],
                'Trình độ': ['Thạc sĩ / CKI', 'Đại học'],
                'Số điện thoại': ['0912345678', '0987654321'],
                'Email': ['nguyenvana@gmail.com', 'tranthib@gmail.com']
            })
            
            output_sample = io.BytesIO()
            with pd.ExcelWriter(output_sample, engine='openpyxl') as writer:
                sample_df.to_excel(writer, index=False, sheet_name='Mau_Nhan_Su')
            
            st.download_button(
                label="📄 Tải Mẫu Excel (.xlsx)",
                data=output_sample.getvalue(),
                file_name="Mau_Danh_Sach_Nhan_Su.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )

        with col_m2:
            st.markdown("##### 📤 **2. Tải lên file Excel để nhập dữ liệu**")
            uploaded_file = st.file_uploader("Chọn file Excel (.xlsx) để upload:", type=['xlsx', 'xls'])
            
            if uploaded_file is not None:
                try:
                    df_up = pd.read_excel(uploaded_file)
                    st.markdown("**Xem trước 5 dòng đầu tiên trong file:**")
                    st.dataframe(df_up.head(5), use_container_width=True)
                    
                    if st.button("🚀 Xác nhận Upload dữ liệu vào Hệ thống", use_container_width=True):
                        cols = df_up.columns.tolist()
                        
                        def get_col(possible_names):
                            for col in cols:
                                c_clean = str(col).lower().replace(" ", "").replace("_", "").replace("/", "")
                                for p in possible_names:
                                    if p in c_clean:
                                        return col
                            return None

                        c_macb = get_col(['macanbo', 'mcb', 'manhanvien', 'manv', 'stt', 'id'])
                        c_hoten = get_col(['hovaten', 'hoten', 'tencanbo', 'tennhanvien', 'fullname', 'ten'])
                        c_ngaysinh = get_col(['ngaysinh', 'ns', 'dob', 'dateofbirth'])
                        c_chucdanh = get_col(['chucdanh', 'chucvu', 'vitri'])
                        c_khoaphong = get_col(['khoaphong', 'khoa', 'phong', 'phongban', 'donvi'])
                        c_trinhdo = get_col(['trinhdo', 'bangcap', 'hocluc'])
                        c_sdt = get_col(['sodienthoai', 'sdtt', 'sdt', 'dienthoai', 'phone'])
                        c_email = get_col(['email', 'mail'])

                        if not c_hoten and len(cols) >= 2:
                            c_macb = cols[0]
                            c_hoten = cols[1]

                        count_inserted = 0
                        with engine.connect() as conn:
                            for idx, row in df_up.iterrows():
                                h = str(row[c_hoten]).strip() if c_hoten and pd.notna(row[c_hoten]) else ''
                                
                                # Mã Cán bộ
                                raw_m = str(row[c_macb]).strip() if c_macb and pd.notna(row[c_macb]) else ''
                                if not raw_m or raw_m.lower() == 'nan':
                                    m = f"CB{idx+1:04d}"
                                else:
                                    m = raw_m

                                # Ngày sinh: Xử lý định dạng & NULL
                                ns_val = None
                                if c_ngaysinh and pd.notna(row[c_ngaysinh]):
                                    try:
                                        ns_val = pd.to_datetime(row[c_ngaysinh]).date()
                                    except Exception:
                                        ns_val = None

                                c = str(row[c_chucdanh]).strip() if c_chucdanh and pd.notna(row[c_chucdanh]) else ''
                                k = str(row[c_khoaphong]).strip() if c_khoaphong and pd.notna(row[c_khoaphong]) else ''
                                t = str(row[c_trinhdo]).strip() if c_trinhdo and pd.notna(row[c_trinhdo]) else ''
                                s = str(row[c_sdt]).strip() if c_sdt and pd.notna(row[c_sdt]) else ''
                                e = str(row[c_email]).strip() if c_email and pd.notna(row[c_email]) else ''

                                if h and h.lower() != 'nan':
                                    check_res = conn.execute(text("SELECT id FROM can_bo WHERE ma_can_bo = :m"), {"m": m}).fetchone()
                                    if check_res:
                                        conn.execute(text("""
                                            UPDATE can_bo SET 
                                                ho_ten = :h, ngay_sinh = :ns, chuc_danh = :c, khoa_phong = :k, 
                                                trinh_do = :t, so_dien_thoai = :s, email = :e
                                            WHERE ma_can_bo = :m
                                        """), {"m": m, "h": h, "ns": ns_val, "c": c, "k": k, "t": t, "s": s, "e": e})
                                    else:
                                        conn.execute(text("""
                                            INSERT INTO can_bo (ma_can_bo, ho_ten, ngay_sinh, chuc_danh, khoa_phong, trinh_do, so_dien_thoai, email)
                                            VALUES (:m, :h, :ns, :c, :k, :t, :s, :e)
                                        """), {"m": m, "h": h, "ns": ns_val, "c": c, "k": k, "t": t, "s": s, "e": e})
                                    count_inserted += 1
                            
                            conn.commit()
                        
                        st.cache_data.clear()
                        
                        if count_inserted > 0:
                            st.success(f"🎉 Đã nhập thành công {count_inserted} nhân sự vào hệ thống!")
                            st.rerun()
                        else:
                            st.error("❌ Không tìm thấy thông tin Họ và Tên hợp lệ. Vui lòng thử lại!")

                except Exception as e_up:
                    st.error(f"Lỗi nhập dữ liệu: {e_up}")

    # TAB 4: XUẤT EXCEL
    with tab4:
        st.markdown("##### 📊 **Tải toàn bộ dữ liệu Cán bộ CNV ra file Excel**")
        if df.empty:
            st.info("Chưa có dữ liệu để xuất file.")
        else:
            export_df = df[['ma_can_bo', 'ho_ten', 'ngay_sinh', 'chuc_danh', 'khoa_phong', 'trinh_do', 'so_dien_thoai', 'email']].copy()
            export_df.columns = ['Mã Cán bộ', 'Họ và Tên', 'Ngày sinh', 'Chức danh', 'Khoa / Phòng', 'Trình độ', 'Số điện thoại', 'Email']
            
            output_exp = io.BytesIO()
            with pd.ExcelWriter(output_exp, engine='openpyxl') as writer:
                export_df.to_excel(writer, index=False, sheet_name='Nhan_Su_BV_Buu_Dien')
            
            st.download_button(
                label="📥 Tải Danh sách Nhân sự (.xlsx)",
                data=output_exp.getvalue(),
                file_name="Danh_Sach_Nhan_Su_BV_Buu_Dien.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )

# ---------------------------------------------------------
# 6. ĐIỀU HƯỚNG MỤC DASHBOARD
# ---------------------------------------------------------
def render_dashboard():
    st.sidebar.title("DANH MỤC CHỨC NĂNG")
    st.sidebar.caption("👤 **Xin chào:** Đoàn Danh Hiển")

    if st.sidebar.button("🔒 Đăng xuất", use_container_width=True):
        st.session_state['logged_in'] = False
        st.rerun()

    st.sidebar.markdown("---")
    st.sidebar.caption("Điều hướng chức năng")

    menu = st.sidebar.radio(
        "",
        [
            "📌 Trang chủ / Dashboard",
            "📑 Thông báo & Văn bản",
            "👤 Hồ sơ Cán bộ CNV",
            "🎓 Phân loại Trình độ",
            "📝 Hợp đồng Lao động",
            "🏛️ Hồ sơ Đảng viên",
            "📜 Giấy phép hành nghề (GPHN)",
            "📚 Theo dõi Đào tạo CME",
            "📈 Nâng bậc lương & Ngạch",
            "🔄 Bố trí & Điều chuyển",
            "🏥 Quản lý BHXH",
            "🩺 Quản lý BHOI & Sức khỏe",
            "⏱️ Báo cáo - Thống kê",
            "📊 Thống kê Tiến độ Đào tạo MS",
            "⚙️ Cấu hình Hệ thống"
        ]
    )

    col_user_img, col_user_info = st.columns([1, 11])
    with col_user_img:
        st.image("https://cdn-icons-png.flaticon.com/512/3135/3135715.png", width=70)
    with col_user_info:
        st.title("Xin chào, Đoàn Danh Hiển")
        st.caption("Quản trị viên Hệ thống — Bệnh viện Bưu điện")

    if menu == "📌 Trang chủ / Dashboard":
        render_dashboard_home()
    elif menu == "👤 Hồ sơ Cán bộ CNV":
        render_quan_ly_can_bo()
    else:
        st.markdown("---")
        st.info(f"⚙️ Chức năng **{menu}** đang được đồng bộ dữ liệu.")

# ---------------------------------------------------------
# 7. CHẠY APP
# ---------------------------------------------------------
if not st.session_state['logged_in']:
    render_login()
else:
    render_dashboard()
