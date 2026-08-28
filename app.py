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
if 'db_initialized' not in st.session_state:
    st.session_state['db_initialized'] = False

# ---------------------------------------------------------
# 2. DATABASE NEON
# ---------------------------------------------------------
@st.cache_resource
def get_db_engine():
    try:
        if "DATABASE_URL" in st.secrets:
            raw_url = st.secrets["DATABASE_URL"].strip()
            if raw_url.startswith("postgres://"):
                raw_url = raw_url.replace("postgres://", "postgresql://", 1)
            return create_engine(raw_url, pool_pre_ping=True, pool_recycle=300)
        elif "postgres" in st.secrets:
            pg = st.secrets["postgres"]
            db_url = f"postgresql://{pg['user']}:{pg['password']}@{pg['host']}:{pg['port']}/{pg['database']}?sslmode=require"
            return create_engine(db_url, pool_pre_ping=True, pool_recycle=300)
        return None
    except Exception as e:
        st.error(f"Lỗi khởi tạo Engine DB: {e}")
        return None

engine = get_db_engine()

def init_db_structure():
    if not engine or st.session_state['db_initialized']:
        return
    try:
        with engine.connect() as conn:
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS can_bo (
                    id SERIAL PRIMARY KEY,
                    ma_can_bo VARCHAR(50),
                    ho_ten VARCHAR(255),
                    ngay_sinh DATE,
                    so_cccd VARCHAR(50),
                    chuc_danh VARCHAR(100),
                    khoa_phong VARCHAR(255),
                    trinh_do VARCHAR(100),
                    so_dien_thoai VARCHAR(20),
                    email VARCHAR(100)
                );
            """))
            conn.commit()
            st.session_state['db_initialized'] = True
    except Exception as e:
        print(f"Khởi tạo DB warning: {e}")

init_db_structure()

@st.cache_data(ttl=1)
def load_data_from_db():
    if not engine:
        return pd.DataFrame()
    try:
        with engine.connect() as conn:
            query = text("SELECT id, ma_can_bo, ho_ten, ngay_sinh, so_cccd, chuc_danh, khoa_phong, trinh_do, so_dien_thoai, email FROM can_bo ORDER BY id DESC")
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
# 5. QUẢN LÝ CÁN BỘ CNV
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

   # TAB 1: DANH SÁCH & XÓA
    with tab1:
        col_t1, col_t2, col_t3 = st.columns([3, 1.2, 1.2])
        col_t1.markdown("##### **Danh sách cán bộ nhân viên hiện có**")
        
        if col_t2.button("🔄 Tải lại dữ liệu", use_container_width=True):
            st.cache_data.clear()
            st.toast("🔄 Đã làm mới dữ liệu từ CSDL thành công!")
            st.rerun()

        if col_t3.button("🧹 Xóa hết dữ liệu", use_container_width=True):
            try:
                with engine.connect() as conn:
                    conn.execute(text("DELETE FROM can_bo;"))
                    conn.commit()
                st.cache_data.clear()
                st.success("Đã làm sạch toàn bộ CSDL!")
                st.rerun()
            except Exception as e_clean:
                st.error(f"Lỗi khi làm sạch CSDL: {e_clean}")

        if df.empty:
            st.info("Chưa có dữ liệu nhân sự trong CSDL. Bạn có thể thêm mới hoặc nhập từ file Excel mẫu 2C-BNV.")
        else:
            display_df = df.drop(columns=['id']).copy()
            display_df.columns = [
                'Mã Cán bộ', 'Họ và Tên', 'Ngày sinh', 'Số CCCD', 
                'Chức danh', 'Khoa / Phòng', 'Trình độ', 'Số điện thoại', 'Email'
            ]
            st.dataframe(display_df, use_container_width=True, hide_index=True)
            
            st.markdown("---")
            st.markdown("##### 🗑️ **Xóa dữ liệu cá nhân**")
            col_del1, col_del2, col_del3 = st.columns([2.5, 1, 1])
            
            options_del = {"-- Chọn nhân sự để xóa --": None}
            for _, row in df.iterrows():
                mcb = str(row['ma_can_bo']) if pd.notna(row['ma_can_bo']) else "N/A"
                hoten = str(row['ho_ten']) if pd.notna(row['ho_ten']) else "N/A"
                khoa = str(row['khoa_phong']) if pd.notna(row['khoa_phong']) else "Chưa phân khoa"
                label = f"{mcb} - {hoten} ({khoa})"
                options_del[label] = row['id']
                
            # Đặt key rõ ràng cho selectbox để quản lý state dễ dàng
            selected_del_label = col_del1.selectbox(
                "Chọn nhân sự muốn xóa:", 
                list(options_del.keys()), 
                key="select_target_del"
            )
            target_id = options_del[selected_del_label]

            if col_del2.button("🗑️ Xóa nhân sự", use_container_width=True):
                if target_id is None:
                    st.warning("⚠️ Bạn chưa chọn nhân sự nào!")
                else:
                    with engine.connect() as conn:
                        conn.execute(text("DELETE FROM can_bo WHERE id = :id"), {"id": target_id})
                        conn.commit()
                    st.cache_data.clear()
                    st.success(f"Đã xóa thành công [{selected_del_label}]!")
                    st.rerun()

            # Sửa lại logic nút Hủy thao tác hoạt động chính xác
            if col_del3.button("❌ Hủy thao tác", use_container_width=True):
                if "select_target_del" in st.session_state:
                    del st.session_state["select_target_del"]
                st.toast("Đã hủy thao tác chọn nhân sự.")
                st.rerun()

    # TAB 2: THÊM & SỬA
    with tab2:
        action_mode = st.radio("Chọn thao tác:", ["➕ Thêm Nhân sự Mới", "✏️ Chỉnh sửa thông tin Cán bộ"], horizontal=True)
        
        if action_mode == "➕ Thêm Nhân sự Mới":
            with st.form("form_add_member", clear_on_submit=True):
                c1, c2 = st.columns(2)
                ma_can_bo = c1.text_input("Mã Cán bộ (*)", placeholder="Ví dụ: N0003")
                ho_ten = c2.text_input("Họ và Tên (*)", placeholder="Ví dụ: Trần Hùng Mạnh")
                ngay_sinh = c1.date_input("Ngày sinh", value=datetime(1967, 1, 1))
                so_cccd = c2.text_input("Số CCCD / CMND", placeholder="Ví dụ: 12243422")
                chuc_danh = c1.selectbox("Chức danh / Chức vụ", ["Chủ tịch HĐQL, Giám đốc", "Phó Giám đốc", "Trưởng phòng", "Phó trưởng phòng", "Nhân viên"])
                khoa_phong = c2.text_input("Khoa / Phòng", placeholder="Ví dụ: Ban Giám đốc")
                trinh_do = c1.selectbox("Trình độ chuyên môn", ["Thạc sĩ, Bác sĩ CKII", "Thạc sĩ kinh tế", "Kỹ sư điện tử viễn thông", "Cử nhân Quản lý kinh doanh", "Đại học", "Khác"])
                sdt = c2.text_input("Số điện thoại", placeholder="Ví dụ: 912222606")
                email = c1.text_input("Email")
                
                btn_add = st.form_submit_button("💾 Lưu Nhân sự Mới")
                
                if btn_add:
                    if not ma_can_bo or not ho_ten:
                        st.warning("Vui lòng nhập đầy đủ Mã Cán bộ và Họ Tên!")
                    else:
                        try:
                            cccd_save = so_cccd.strip() if so_cccd and so_cccd.strip() else None
                            sdt_save = sdt.strip() if sdt and sdt.strip() else None
                            email_save = email.strip() if email and email.strip() else None
                            
                            with engine.connect() as conn:
                                conn.execute(text("""
                                    INSERT INTO can_bo (ma_can_bo, ho_ten, ngay_sinh, so_cccd, chuc_danh, khoa_phong, trinh_do, so_dien_thoai, email)
                                    VALUES (:m, :h, :ns, :cccd, :c, :k, :t, :s, :e)
                                """), {"m": ma_can_bo.strip(), "h": ho_ten.strip(), "ns": ngay_sinh, "cccd": cccd_save, "c": chuc_danh, "k": khoa_phong, "t": trinh_do, "s": sdt_save, "e": email_save})
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
                    so_cccd = c2.text_input("Số CCCD / CMND", value=str(curr_row['so_cccd'] or ''))
                    
                    chuc_danh = c1.text_input("Chức vụ", value=str(curr_row['chuc_danh'] or ''))
                    khoa_phong = c1.text_input("Khoa / Phòng", value=str(curr_row['khoa_phong'] or ''))
                    trinh_do = c2.text_input("Trình độ chuyên môn", value=str(curr_row['trinh_do'] or ''))
                    
                    sdt = c1.text_input("Số điện thoại", value=str(curr_row['so_dien_thoai'] or ''))
                    email = c2.text_input("Email", value=str(curr_row['email'] or ''))
                    
                    btn_update = st.form_submit_button("🔄 Cập nhật Thông tin")
                    
                    if btn_update:
                        try:
                            cccd_save = so_cccd.strip() if so_cccd and so_cccd.strip() else None
                            sdt_save = sdt.strip() if sdt and sdt.strip() else None
                            email_save = email.strip() if email and email.strip() else None

                            with engine.connect() as conn:
                                conn.execute(text("""
                                    UPDATE can_bo 
                                    SET ma_can_bo = :m, ho_ten = :h, ngay_sinh = :ns, so_cccd = :cccd, chuc_danh = :c, 
                                        khoa_phong = :k, trinh_do = :t, so_dien_thoai = :s, email = :e
                                    WHERE id = :id
                                """), {"m": ma_can_bo.strip(), "h": ho_ten.strip(), "ns": ngay_sinh, "cccd": cccd_save, "c": chuc_danh, "k": khoa_phong, "t": trinh_do, "s": sdt_save, "e": email_save, "id": edit_id})
                                conn.commit()
                            st.cache_data.clear()
                            st.success("Đã cập nhật thông tin thành công!")
                            st.rerun()
                        except Exception as ex:
                            st.error(f"Lỗi cập nhật: {ex}")

    # TAB 3: TẢI MẪU & UPLOAD EXCEL (CHUẨN XÁC ÁNH XẠ CỘT 2C-BNV)
    with tab3:
        col_m1, col_m2 = st.columns([1.5, 2])
        
        with col_m1:
            st.markdown("##### 📥 **1. Tải về file Excel mẫu chuẩn 2C-BNV**")
            st.caption("Mẫu chuẩn đầy đủ các trường theo Sơ yếu lý lịch Bộ Nội Vụ (BV Bưu Điện).")
            
            sample_2c_df = pd.DataFrame({
                'Ma_NV': ['N0003', 'N0009', 'N0125'],
                'Ho_Ten': ['Trần Hùng Mạnh', 'Phạm Thị Thanh Tú', 'Phạm Trường Giang'],
                'Ten_Goi_Khac': ['BVBD000628', 'BVBD000630', 'BVBD000092'],
                'Ma_NV.1': ['N0003', 'N0009', 'N0125'],
                'Ngay_Sinh': ['01/01/1967', '17/09/1975', '11/07/1975'],
                'Gioi_Tinh': ['Nam', 'Nữ', 'Nam'],
                'Noi_Sinh': ['Nghệ An', 'Hà Nội', 'Hà Nam'],
                'Que_Quan': ['Nghệ Tĩnh', 'Hà Nội', 'Hà Nam'],
                'Dan_Toc': ['Kinh (Việt)', 'Kinh (Việt)', 'Kinh (Việt)'],
                'Ton_Giao': ['Không', 'Không', 'Không'],
                'Noi_O_Hien_Nay': ['P 501 CT8 Định Công', '', 'Số 40, ngõ 161 Thái Hà'],
                'Dien_Thoai': ['912222606', '916369699', '906528686'],
                'So_CCCD': ['12243422', '1175014697', '1075022616'],
                'Khoa_Phong': ['Ban Giám đốc', 'Ban Giám đốc', 'Ban Giám đốc'],
                'Chuc_Vu': ['Chủ tịch HĐQL, Giám đốc', 'Phó Giám đốc', 'Phó Giám đốc'],
                'Ngach_Vien_Chuc': ['Viên chức A2', 'Viên chức A1', 'Viên chức A1'],
                'Bac_Luong': ['8/8', '9/9', '9/9'],
                'He_So_Luong': ['6.78', '4.98', '4.98'],
                'Ngay_Nang_Luong': ['2025-09-01', '2025-08-01', '2025-09-01'],
                'Trinh_Do_Giao_Duc': ['12 / 12', '12 / 12', '12 / 12'],
                'Trinh_Do_Chuyen_Mon': ['Thạc sĩ, Bác sĩ CKII', 'Thạc sĩ kinh tế', 'Thạc sĩ, Bác sĩ CKII'],
                'Ly_Luan_Chinh_Tri': [None, None, None],
                'Ngoai_Ngu': [None, None, None],
                'Tin_Hoc': [None, None, None],
                'So_CCHN': ['005542/BYT-CCHN', None, '0013785/BYT-CCHN'],
                'Gio_CME': [None, None, None],
                'Ngay_Vao_Dang': ['29/10/2004', '15/02/2001', '15/03/2012'],
                'Ngay_Nhap_Ngu': [None, None, None],
                'Danh_Hieu_Phong_Tang': [None, None, None],
                'Khen_Thuong_Ky_Luat': [None, None, None],
                'Suc_Khoe_Thuong_Binh': [None, None, None],
                'Loai_HD': ['Không có thời hạn xác định', 'Không có thời hạn xác định', 'Không có thời hạn xác định'],
                'Ngay_Het_Han_HD': [None, None, None],
                'Trang_Thai': ['Chính thức', 'Chính thức', 'Chính thức']
            })
            
            output_sample = io.BytesIO()
            with pd.ExcelWriter(output_sample, engine='openpyxl') as writer:
                sample_2c_df.to_excel(writer, index=False, sheet_name='Mau_2C_BNV')
            
            st.download_button(
                label="📄 Tải Mẫu Sơ Yếu Lý Lịch 2C - BNV (.xlsx)",
                data=output_sample.getvalue(),
                file_name="Mau_Ly_Lich_2C_BNV.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )

        with col_m2:
            st.markdown("##### 📤 **2. Tải lên file Excel theo mẫu 2C-BNV**")
            uploaded_file = st.file_uploader("Chọn file Excel (.xlsx) chuẩn 2C-BNV:", type=['xlsx', 'xls'], key="excel_uploader_2c")
            
            if uploaded_file is not None:
                try:
                    xls_file = pd.ExcelFile(uploaded_file)
                    sheet_to_read = 'Mau_2C_BNV' if 'Mau_2C_BNV' in xls_file.sheet_names else xls_file.sheet_names[0]
                    df_up = pd.read_excel(uploaded_file, sheet_name=sheet_to_read)
                    
                    st.markdown(f"**Xem trước dữ liệu (Tổng số dòng: {len(df_up)}):**")
                    st.dataframe(df_up.head(3), use_container_width=True, hide_index=True)
                    
                    st.markdown("<br>", unsafe_allow_html=True)

                    if st.button("🚀 Xác nhận Upload dữ liệu vào Hệ thống", use_container_width=True, type="primary"):
                        count_inserted = 0
                        col_list = list(df_up.columns)
                        
                        def get_val(row_item, key):
                            if key in col_list:
                                val = row_item[key]
                                if pd.notna(val):
                                    s = str(val).strip()
                                    if s.lower() not in ['nan', 'none', '', 'null']:
                                        if s.endswith('.0'):
                                            s = s[:-2]
                                        return s
                            return None

                        with engine.connect() as conn:
                            for idx, row in df_up.iterrows():
                                try:
                                    h_val = get_val(row, 'Ho_Ten')
                                    if not h_val:
                                        continue
                                        
                                    m_val = get_val(row, 'Ma_NV') or f"N{idx+1:04d}"
                                    
                                    # Đọc đúng trường ngày sinh
                                    raw_ns = row.get('Ngay_Sinh')
                                    ns_val = None
                                    if pd.notna(raw_ns):
                                        try:
                                            if isinstance(raw_ns, datetime):
                                                ns_val = raw_ns.date()
                                            else:
                                                ns_val = pd.to_datetime(raw_ns, dayfirst=True).date()
                                        except Exception:
                                            ns_val = None

                                    cccd_val = get_val(row, 'So_CCCD')
                                    chuc_vu_val = get_val(row, 'Chuc_Vu')
                                    khoa_phong_val = get_val(row, 'Khoa_Phong')
                                    trinh_do_val = get_val(row, 'Trinh_Do_Chuyen_Mon')
                                    sdt_val = get_val(row, 'Dien_Thoai')
                                    email_val = get_val(row, 'Email') if 'Email' in col_list else None

                                    conn.execute(text("""
                                        INSERT INTO can_bo (ma_can_bo, ho_ten, ngay_sinh, so_cccd, chuc_danh, khoa_phong, trinh_do, so_dien_thoai, email)
                                        VALUES (:m, :h, :ns, :cccd, :cv, :kp, :td, :sdt, :email)
                                    """), {
                                        "m": m_val, 
                                        "h": h_val, 
                                        "ns": ns_val, 
                                        "cccd": cccd_val, 
                                        "cv": chuc_vu_val, 
                                        "kp": khoa_phong_val, 
                                        "td": trinh_do_val, 
                                        "sdt": sdt_val, 
                                        "email": email_val
                                    })
                                    count_inserted += 1
                                except Exception as row_ex:
                                    print(f"Lỗi dòng {idx+1}: {row_ex}")
                            
                            conn.commit()
                        
                        if count_inserted > 0:
                            st.cache_data.clear()
                            st.success(f"🎉 Đã nhập thành công {count_inserted} nhân sự vào CSDL và ánh xạ đúng chuẩn các cột!")
                            st.balloons()
                            st.rerun()
                        else:
                            st.error("❌ Không chèn được dữ liệu. Vui lòng kiểm tra lại cấu trúc tiêu đề file Excel.")

                except Exception as e_up:
                    st.error(f"Lỗi đọc file Excel: {e_up}")

    # TAB 4: XUẤT EXCEL
    with tab4:
        st.markdown("##### 📊 **Tải toàn bộ dữ liệu Cán bộ CNV ra file Excel chuẩn 2C-BNV**")
        if df.empty:
            st.info("Chưa có dữ liệu để xuất file.")
        else:
            export_df = df[['ma_can_bo', 'ho_ten', 'ngay_sinh', 'so_cccd', 'chuc_danh', 'khoa_phong', 'trinh_do', 'so_dien_thoai', 'email']].copy()
            export_df.columns = ['Ma_NV', 'Ho_Ten', 'Ngay_Sinh', 'So_CCCD', 'Chuc_Vu', 'Khoa_Phong', 'Trinh_Do_Chuyen_Mon', 'Dien_Thoai', 'Email']
            
            output_exp = io.BytesIO()
            with pd.ExcelWriter(output_exp, engine='openpyxl') as writer:
                export_df.to_excel(writer, index=False, sheet_name='Mau_2C_BNV')
            
            st.download_button(
                label="📥 Tải Danh sách Nhân sự Đầy Đủ Cột (Chuẩn 2C-BNV .xlsx)",
                data=output_exp.getvalue(),
                file_name="Danh_Sach_Nhan_Su_Chuan_2C_BNV.xlsx",
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
