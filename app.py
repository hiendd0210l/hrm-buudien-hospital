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
# 4. DASHBOARD TRANG CHỦ (ĐÃ TÍCH HỢP DỮ LIỆU ĐỘNG TỪ DB)
# ---------------------------------------------------------
def render_dashboard_home():
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Lấy dữ liệu thực tế từ Database để tính toán số liệu thống kê
    df_db = load_data_from_db()
    total_staff = len(df_db)
    
    # Hiển thị tổng số nhân sự nổi bật
    st.info(f"📊 **Tổng số lượng cán bộ, nhân viên hiện có trong cơ sở dữ liệu hệ thống:** **{total_staff}** nhân sự.")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"<div class='card-box card-red'><div class='card-title'>👨‍⚕️ HỒ SƠ CÁN BỘ CNV</div><div class='card-desc'>Tổng số: <b>{total_staff}</b> hồ sơ đang quản lý và cập nhật toàn viện.</div><div class='card-link'>XEM CHI TIẾT ➔</div></div>", unsafe_allow_html=True)
        st.markdown("<div class='card-box card-dark'><div class='card-title'>📜 HỢP ĐỒNG LAO ĐỘNG</div><div class='card-desc'>Theo dõi hợp đồng xác định thời hạn, không xác định thời hạn và lịch sử ký.</div><div class='card-link'>QUẢN LÝ HỒ SƠ ➔</div></div>", unsafe_allow_html=True)
    with col2:
        st.markdown("<div class='card-box card-green'><div class='card-title'>📊 BÁO CÁO & THỐNG KÊ</div><div class='card-desc'>Truy xuất dữ liệu báo cáo BYT, BVT và biến động nhân sự theo thời gian thực.</div><div class='card-link'>XEM BÁO CÁO ➔</div></div>", unsafe_allow_html=True)
        st.markdown("<div class='card-box card-orange'><div class='card-title'>📈 NÂNG BẬC LƯƠNG & NGẠCH</div><div class='card-desc'>Quản lý nâng lương, ngạch viên chức và cảnh báo danh sách đủ điều kiện nâng lương.</div><div class='card-link'>XEM DANH SÁCH ➔</div></div>", unsafe_allow_html=True)
    with col3:
        st.markdown("<div class='card-box card-blue'><div class='card-title'>🏥 GPHN & ĐÀO TẠO CME</div><div class='card-desc'>Quản lý Chứng chỉ hành nghề và tiến độ tích lũy 48 tiết CME của Bác sĩ / Điều dưỡng.</div><div class='card-link'>XEM CHI TIẾT ➔</div></div>", unsafe_allow_html=True)
        st.markdown("<div class='card-box card-teal'><div class='card-title'>🩺 QUẢN LÝ BHOI & SỨC KHỎE</div><div class='card-desc'>Theo dõi chế độ bảo hiểm sở hữu, đóng xem và đợt khám sức khỏe định kỳ.</div><div class='card-link'>CHI TIẾT ➔</div></div>", unsafe_allow_html=True)
    
    # PHẦN DƯỚI TRANG CHỦ: 3 CỘT (CẢNH BÁO TỰ ĐỘNG - NHÂN SỰ THEO TRÌNH ĐỘ - PHÂN LOẠI HỢP ĐỒNG)
    st.markdown("---")
    
    col_dash1, col_dash2, col_dash3 = st.columns([1.1, 1, 1], gap="medium")
    
    # --- CỘT 1: CẢNH BÁO TỰ ĐỘNG ---
    with col_dash1:
        st.markdown("##### 📌 **Cảnh báo tự động**")
        
        # Hàm hiển thị từng dòng cảnh báo dạng card nhỏ gọn
        def render_alert_card(title, desc, count, color_border):
            st.markdown(f"""
                <div style="
                    display: flex; 
                    align-items: center; 
                    justify-content: space-between; 
                    background-color: #ffffff; 
                    padding: 10px 12px; 
                    border-radius: 8px; 
                    margin-bottom: 8px; 
                    border-left: 5px solid {color_border};
                    box-shadow: 0 1px 3px rgba(0,0,0,0.05);
                ">
                    <div>
                        <div style="font-weight: 600; font-size: 13.5px; color: #333;">{title}</div>
                        <div style="font-size: 11.5px; color: #666; margin-top: 2px;">{desc}</div>
                    </div>
                    <div style="
                        background-color: #fff5f5; 
                        color: {color_border}; 
                        font-weight: bold; 
                        font-size: 14px; 
                        padding: 4px 10px; 
                        border-radius: 6px;
                        border: 1px solid {color_border}33;
                    ">
                        {count}
                    </div>
                </div>
            """, unsafe_allow_html=True)

        render_alert_card("⏰ Sắp hết hạn HĐLĐ", "Cần ký lại / gia hạn trong 30 ngày", "12", "#ff4d4f")
        render_alert_card("💰 Đến hạn nâng bậc lương", "Đủ thời hạn xét nâng ngạch, bậc", "08", "#fa8c16")
        render_alert_card("⚠️ Cảnh báo thiếu giờ CME", "Chưa tích lũy đủ 48 tiết / 2 năm", "25", "#1890ff")
        render_alert_card("📜 GPHN cần cập nhật", "Bổ sung thông tin chứng chỉ mới", "04", "#52c41a")

    # --- CỘT 2: NHÂN SỰ THEO TRÌNH ĐỘ (Dùng Plotly Bar Chart) ---
    with col_dash2:
        st.markdown("##### 📊 **Nhân sự theo Trình độ**")
        
        import plotly.express as px
        import pandas as pd

        # Dữ liệu mẫu minh họa (có thể thay thế bằng dữ liệu truy vấn từ CSDL của bạn)
        df_trinh_do = pd.DataFrame({
            'Trình độ': ['Tiến sĩ/CKI', 'Thạc sĩ/CKI', 'Đại học', 'Cao đẳng', 'Trung cấp/Khác'],
            'Số lượng': [25, 142, 450, 180, 80]
        })
        
        fig_td = px.bar(
            df_trinh_do, 
            x='Trình độ', 
            y='Số lượng',
            text='Số lượng',
            color='Trình độ',
            color_discrete_sequence=['#fa8c16', '#5c6bc0', '#26a69a', '#9ccc65', '#ab47bc']
        )
        fig_td.update_traces(textposition='outside', textfont_size=11)
        fig_td.update_layout(
            margin=dict(t=10, b=10, l=10, r=10),
            height=260,
            showlegend=False,
            xaxis=dict(title='', tickfont=dict(size=10)),
            yaxis=dict(title='', showgrid=True, gridcolor='#f0f0f0')
        )
        st.plotly_chart(fig_td, use_container_width=True, config={'displayModeBar': False})

    # --- CỘT 3: PHÂN LOẠI HỢP ĐỒNG (Dùng Plotly Donut Chart) ---
    with col_dash3:
        st.markdown("##### 🍩 **Phân loại Hợp đồng**")
        
        df_hd = pd.DataFrame({
            'Loại hợp đồng': ['Không xác định thời hạn', 'Xác định thời hạn (1-3 năm)', 'Thử việc / Ngắn hạn'],
            'Số lượng': [520, 310, 47]
        })
        
        fig_hd = px.pie(
            df_hd, 
            names='Loại hợp đồng', 
            values='Số lượng',
            hole=0.55,
            color_discrete_sequence=['#1890ff', '#fa8c16', '#00b96b']
        )
        fig_hd.update_traces(textposition='inside', textinfo='percent+value')
        fig_hd.update_layout(
            margin=dict(t=10, b=10, l=10, r=10),
            height=260,
            legend=dict(
                orientation="h", 
                yanchor="bottom", 
                y=-0.3, 
                xanchor="center", 
                x=0.5,
                font=dict(size=10)
            )
        )
        st.plotly_chart(fig_hd, use_container_width=True, config={'displayModeBar': False})

# ---------------------------------------------------------
# 5. QUẢN LÝ CÁN BỘ CNV
# ---------------------------------------------------------
def init_db():
    if engine:
        try:
            with engine.begin() as conn:
                # Tạo bảng và đảm bảo ma_can_bo là UNIQUE để chống trùng lặp
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS can_bo (
                        id SERIAL PRIMARY KEY,
                        ma_can_bo VARCHAR(50) UNIQUE,
                        ho_ten VARCHAR(255) NOT NULL,
                        ngay_sinh DATE,
                        so_cccd VARCHAR(50),
                        chuc_danh VARCHAR(255),
                        khoa_phong VARCHAR(255),
                        trinh_do VARCHAR(255),
                        so_dien_thoai VARCHAR(50),
                        email VARCHAR(255)
                    );
                """))
                # Tạo index unique phòng trường hợp bảng cũ chưa có constraint
                conn.execute(text("""
                    CREATE UNIQUE INDEX IF NOT EXISTS idx_can_bo_ma_unique ON can_bo (ma_can_bo);
                """))
        except Exception as e:
            st.error(f"Lỗi khởi tạo CSDL: {e}")

init_db()

# Gọi hàm khởi tạo bảng khi chạy app
init_db()
def render_quan_ly_can_bo():
    st.markdown("---")
    st.subheader("📁 QUẢN LÝ CÁN BỘ CNV BỆNH VIỆN BƯU ĐIỆN")
    if not engine:
        st.error("Chưa kết nối được Cơ sở dữ liệu Neon. Vui lòng kiểm tra lại cấu hình Secrets.")
        return
        
    df = load_data_from_db()
    total_count = len(df)
    st.success(f"📋 **Tổng số nhân sự hiện có trong CSDL:** **{total_count}** cán bộ, nhân viên.")
    
    tab1, tab2, tab3, tab4 = st.tabs([
        "📋 Danh sách & Xóa", 
        "➕ Thêm / ✏️ Sửa Nhân sự", 
        "📥 Tải File Mẫu & Nhập Excel", 
        "📤 Xuất Data Excel"
    ])
    
# TAB 1: DANH SÁCH & XÓA (HOÀN THIỆN THÔNG BÁO VÀ RESET TRẠNG THÁI)
    with tab1:
        col_t1, col_t2, col_t3 = st.columns([3, 1.2, 1.2])
        col_t1.markdown("##### **Danh sách cán bộ nhân viên hiện có**")
        
        if col_t2.button("🔄 Tải lại dữ liệu", use_container_width=True):
            st.cache_data.clear()
            st.toast("🔄 Đã làm mới dữ liệu từ CSDL thành công!")
            st.rerun()
            
        if col_t3.button("🧹 Xóa hết dữ liệu", use_container_width=True):
            try:
                with engine.begin() as conn:
                    conn.execute(text("DELETE FROM can_bo;"))
                st.cache_data.clear()
                if "select_del_widget" in st.session_state:
                    del st.session_state["select_del_widget"]
                st.success("Đã làm sạch toàn bộ CSDL!")
                st.rerun()
            except Exception as e_clean:
                st.error(f"Lỗi khi làm sạch CSDL: {e_clean}")
                
        if df.empty:
            st.info("Chưa có dữ liệu nhân sự trong CSDL. Bạn có thể thêm mới hoặc nhập từ file Excel mẫu 2C-BNV.")
        else:
            def get_department_priority(kp):
                if not kp or pd.isna(kp):
                    return 99
                s = str(kp).lower().strip()
                if any(x in s for x in ['giám đốc', 'hđql', 'ban giám đốc']):
                    return 1
                if any(x in s for x in ['phòng', 'tổ chức', 'kế hoạch', 'tài chính', 'điều dưỡng', 'hành chính', 'quản trị', 'vật tư', 'cntt']):
                    return 2
                if any(x in s for x in ['ngoại', 'nội', 'sản', 'nhi', 'cấp cứu', 'hồi sức', 'y học cổ truyền', 'phục hồi chức năng', 'truyền nhiễm', 'da liễu', 'ung bướu']):
                    return 3
                if 'khám' in s:
                    return 4
                if any(x in s for x in ['mắt', 'tai mũi họng', 'răng hàm mặt', 'rhm', 'tmh']):
                    return 5
                if any(x in s for x in ['chẩn đoán hình ảnh', 'xét nghiệm', 'nội soi', 'thăm dò chức năng', 'gây mê', 'dược', 'kiểm soát nhiễm khuẩn', 'vi sinh', 'sinh hóa']):
                    return 6
                if 'trung tâm' in s:
                    return 7
                return 50

            df_sorted = df.copy()
            df_sorted['priority'] = df_sorted['khoa_phong'].apply(get_department_priority)
            df_sorted = df_sorted.sort_values(by=['priority', 'khoa_phong', 'ho_ten'], ascending=[True, True, True])
            
            display_df = df_sorted.drop(columns=['id', 'priority']).copy()
            
            if 'ngay_sinh' in display_df.columns:
                display_df['ngay_sinh'] = pd.to_datetime(display_df['ngay_sinh'], errors='coerce').dt.strftime('%d/%m/%Y').fillna('')

            display_df.columns = [
                'Mã Cán bộ', 'Họ và Tên', 'Ngày sinh', 'Số CCCD', 
                'Chức danh', 'Khoa / Phòng', 'Trình độ', 'Số điện thoại', 'Email'
            ]
            st.dataframe(display_df, use_container_width=True, hide_index=True)
            
            st.markdown("---")
            st.markdown("##### 🗑️ **Xóa dữ liệu cá nhân**")
            
            # Kiểm tra xem có thông báo cần hiển thị hay không (dùng session state lưu message thông báo)
            if "status_message" in st.session_state and st.session_state["status_message"]:
                st.info(st.session_state["status_message"])
                if st.button("OK, Trở lại màn hình ban đầu", use_container_width=False, key="btn_ok_status"):
                    st.session_state["status_message"] = ""
                    st.rerun()
            else:
                col_del1, col_del2, col_del3 = st.columns([2.5, 1, 1])
                
                options_del = ["-- Chọn nhân sự để xóa --"]
                mapping_del = {"-- Chọn nhân sự để xóa --": None}
                
                for _, row in df_sorted.iterrows():
                    mcb = str(row['ma_can_bo']) if pd.notna(row['ma_can_bo']) else "N/A"
                    hoten = str(row['ho_ten']) if pd.notna(row['ho_ten']) else "N/A"
                    khoa = str(row['khoa_phong']) if pd.notna(row['khoa_phong']) else "Chưa phân khoa"
                    label = f"{mcb} - {hoten} ({khoa})"
                    options_del.append(label)
                    mapping_del[label] = row['id']
                
                # Xử lý xóa state của selectbox nếu có cờ reset
                if st.session_state.get("trigger_reset_selectbox", False):
                    if "select_del_widget" in st.session_state:
                        del st.session_state["select_del_widget"]
                    st.session_state["trigger_reset_selectbox"] = False

                selected_del_label = col_del1.selectbox(
                    "Chọn nhân sự muốn xóa:", 
                    options_del, 
                    key="select_del_widget"
                )
                
                target_id = mapping_del.get(selected_del_label, None)
                
                # Nút Xóa nhân sự
                if col_del2.button("🗑️ Xóa nhân sự", use_container_width=True):
                    if target_id is None:
                        st.warning("⚠️ Bạn chưa chọn nhân sự nào để xóa!")
                    else:
                        with engine.begin() as conn:
                            conn.execute(text("DELETE FROM can_bo WHERE id = :id"), {"id": target_id})
                        st.cache_data.clear()
                        st.session_state["trigger_reset_selectbox"] = True
                        st.session_state["status_message"] = "✅ Đã xóa nhân sự được chọn thành công!"
                        st.rerun()
                        
                # Nút Hủy thao tác
                if col_del3.button("❌ Hủy thao tác", use_container_width=True):
                    st.session_state["trigger_reset_selectbox"] = True
                    st.session_state["status_message"] = "ℹ️ Đã hủy thao tác."
                    st.rerun()
    
 # TAB 2: THÊM & SỬA NHÂN SỰ (DÙNG SELECTBOX DANH MỤC VÀ DATE_INPUT LỊCH CHỌN)
    with tab2:
        st.markdown("##### ➕ **Thêm mới hoặc Chỉnh sửa thông tin Cán bộ nhân viên**")
        
        mode = st.radio("Chọn thao tác:", ["Thêm mới nhân sự", "Sửa thông tin nhân sự có sẵn"], horizontal=True, key="mode_them_sua")
        
        # Danh mục tùy chọn chuẩn hệ thống (có thể điều chỉnh thêm bớt danh sách tại đây)
        danh_muc_khoa_phong = [
            "-- Chọn Khoa / Phòng --",
            "Phòng Nhân sự - Tổng hợp",
            "Phòng Kế hoạch Tổng hợp",
            "Phòng Tài chính Kế toán",
            "Khoa Khám bệnh",
            "Khoa Nội tổng hợp",
            "Khoa Ngoại tổng hợp",
            "Khoa Cấp cứu - Hồi sức tích cực",
            "Khoa Nhi",
            "Khoa Phụ sản",
            "Khoa Chẩn đoán hình ảnh",
            "Khoa Xét nghiệm",
            "Khoa Dược",
            "Khoa Kiểm soát nhiễm khuẩn"
        ]
        
        danh_muc_trinh_do = [
            "-- Chọn Trình độ chuyên môn --",
            "Tiến sĩ, Bác sĩ CKI",
            "Thạc sĩ, Bác sĩ CKII",
            "Bác sĩ CKII",
            "Bác sĩ CKI",
            "Bác sĩ đa khoa",
            "Dược sĩ đại học",
            "Cử nhân điều dưỡng",
            "Cao đẳng điều dưỡng",
            "Trung cấp",
            "Khác"
        ]
        
        danh_muc_chuc_danh = [
            "-- Chọn Chức danh --",
            "Ban Giám đốc",
            "Trưởng khoa / Trưởng phòng",
            "Phó trưởng khoa / Phó phòng",
            "Bác sĩ",
            "Điều dưỡng trưởng",
            "Điều dưỡng viên",
            "Kỹ thuật viên",
            "Dược sĩ",
            "Nhân viên hành chính"
        ]

        if mode == "Thêm mới nhân sự":
            st.markdown("---")
            
            if st.session_state.get("add_success_msg", ""):
                st.success(st.session_state["add_success_msg"])
                if st.button("OK, Trở về màn hình ban đầu", key="btn_ok_add_success"):
                    st.session_state["add_success_msg"] = ""
                    st.rerun()
            else:
                with st.form("form_them_nhan_su_moi", clear_on_submit=False):
                    c1, c2 = st.columns(2)
                    with c1:
                        new_mcb = st.text_input("Mã Cán bộ (*)", placeholder="Ví dụ: N1971")
                        new_hoten = st.text_input("Họ và Tên (*)", placeholder="Ví dụ: Khuất Duy Tiến")
                        
                        # Sử dụng date_input với giới hạn năm từ 1930 đến hiện tại
                        from datetime import date
                        new_ngaysinh = st.date_input(
                            "Ngày sinh", 
                            value=date(1975, 1, 1), 
                            min_value=date(1930, 1, 1), 
                            max_value=date.today(),
                            format="DD/MM/YYYY"
                        )
                        
                        new_cccd = st.text_input("Số CCCD", placeholder="Ví dụ: 001085123456")
                        new_chucdanh = st.selectbox("Chức danh", danh_muc_chuc_danh)
                        
                    with c2:
                        new_khoaphong = st.selectbox("Khoa / Phòng (*)", danh_muc_khoa_phong)
                        new_trinhdo = st.selectbox("Trình độ chuyên môn", danh_muc_trinh_do)
                        new_sdt = st.text_input("Số điện thoại", placeholder="Ví dụ: 0912222606")
                        new_email = st.text_input("Email", placeholder="Ví dụ: example@hospital.vn")
                    
                    submitted_add = st.form_submit_button("💾 Lưu Nhân sự Mới", use_container_width=True)
                    
                    if submitted_add:
                        if not new_mcb or not new_hoten or new_khoaphong == "-- Chọn Khoa / Phòng --":
                            st.error("⚠️ Vui lòng điền đầy đủ các trường bắt buộc có dấu (*): Mã cán bộ, Họ tên và chọn Khoa/Phòng hợp lệ!")
                        else:
                            try:
                                check_query = text("SELECT COUNT(*) FROM can_bo WHERE ma_can_bo = :mcb")
                                with engine.connect() as conn:
                                    count = conn.execute(check_query, {"mcb": new_mcb.strip()}).scalar()
                                
                                if count > 0:
                                    st.error(f"⚠️ **Lỗi trùng lặp dữ liệu:** Mã cán bộ '{new_mcb.strip()}' đã tồn tại trong hệ thống!")
                                else:
                                    insert_query = text("""
                                        INSERT INTO can_bo (ma_can_bo, ho_ten, ngay_sinh, so_cccd, chuc_danh, khoa_phong, trinh_do, so_dien_thoai, email)
                                        VALUES (:ma_can_bo, :ho_ten, :ngay_sinh, :so_cccd, :chuc_danh, :khoa_phong, :trinh_do, :so_dien_thoai, :email)
                                    """)
                                    with engine.begin() as conn:
                                        conn.execute(insert_query, {
                                            "ma_can_bo": new_mcb.strip(),
                                            "ho_ten": new_hoten.strip(),
                                            "ngay_sinh": new_ngaysinh,
                                            "so_cccd": new_cccd.strip() if new_cccd else None,
                                            "chuc_danh": new_chucdanh if new_chucdanh != "-- Chọn Chức danh --" else None,
                                            "khoa_phong": new_khoaphong,
                                            "trinh_do": new_trinhdo if new_trinhdo != "-- Chọn Trình độ chuyên môn --" else None,
                                            "so_dien_thoai": new_sdt.strip() if new_sdt else None,
                                            "email": new_email.strip() if new_email else None
                                        })
                                    st.cache_data.clear()
                                    st.session_state["add_success_msg"] = f"🎉 Thêm mới nhân sự [{new_mcb} - {new_hoten}] thành công!"
                                    st.rerun()
                            except Exception as e:
                                st.error(f"⚠️ Đã xảy ra lỗi: {e}")

        else: # Chế độ Sửa thông tin nhân sự có sẵn
            st.markdown("---")
            if df.empty:
                st.info("Chưa có dữ liệu nhân sự để chỉnh sửa.")
            else:
                options_edit = ["-- Chọn nhân sự để chỉnh sửa --"]
                mapping_edit = {"-- Chọn nhân sự để chỉnh sửa --": None}
                
                for _, row in df.iterrows():
                    mcb = str(row['ma_can_bo']) if pd.notna(row['ma_can_bo']) else "N/A"
                    hoten = str(row['ho_ten']) if pd.notna(row['ho_ten']) else "N/A"
                    khoa = str(row['khoa_phong']) if pd.notna(row['khoa_phong']) else "Chưa phân khoa"
                    label = f"{mcb} - {hoten} ({khoa})"
                    options_edit.append(label)
                    mapping_edit[label] = row['id']
                
                selected_edit_label = st.selectbox("Chọn nhân sự muốn chỉnh sửa:", options_edit, key="select_edit_widget")
                target_edit_id = mapping_edit.get(selected_edit_label, None)
                
                if target_edit_id is not None:
                    current_row = df[df['id'] == target_edit_id].iloc[0]
                    
                    # Thiết lập giá trị ngày sinh mặc định an toàn cho date_input
                    default_dob = date(1975, 1, 1)
                    if pd.notna(current_row.get('ngay_sinh')):
                        try:
                            default_dob = pd.to_datetime(current_row['ngay_sinh']).date()
                        except:
                            pass

                    # Tìm vị trí index mặc định cho các selectbox danh mục
                    val_kp = current_row.get('khoa_phong', '')
                    idx_kp = danh_muc_khoa_phong.index(val_kp) if val_kp in danh_muc_khoa_phong else 0

                    val_td = current_row.get('trinh_do', '')
                    idx_td = danh_muc_trinh_do.index(val_td) if val_td in danh_muc_trinh_do else 0

                    val_cd = current_row.get('chuc_danh', '')
                    idx_cd = danh_muc_chuc_danh.index(val_cd) if val_cd in danh_muc_chuc_danh else 0

                    with st.form("form_sua_nhan_su"):
                        st.markdown(f"Đang chỉnh sửa cho: **{selected_edit_label}**")
                        sc1, sc2 = st.columns(2)
                        
                        with sc1:
                            edit_mcb = st.text_input("Mã Cán bộ (*)", value=str(current_row.get('ma_can_bo', '')), placeholder="Ví dụ: N1971")
                            edit_hoten = st.text_input("Họ và Tên (*)", value=str(current_row.get('ho_ten', '')), placeholder="Ví dụ: Khuất Duy Tiến")
                            edit_ngaysinh = st.date_input("Ngày sinh", value=default_dob, min_value=date(1930, 1, 1), max_value=date.today(), format="DD/MM/YYYY")
                            edit_cccd = st.text_input("Số CCCD", value=str(current_row.get('so_cccd', '')) if pd.notna(current_row.get('so_cccd')) else '', placeholder="Ví dụ: 001085123456")
                            edit_chucdanh = st.selectbox("Chức danh", danh_muc_chuc_danh, index=idx_cd)
                        with sc2:
                            edit_khoaphong = st.selectbox("Khoa / Phòng (*)", danh_muc_khoa_phong, index=idx_kp)
                            edit_trinhdo = st.selectbox("Trình độ chuyên môn", danh_muc_trinh_do, index=idx_td)
                            edit_sdt = st.text_input("Số điện thoại", value=str(current_row.get('so_dien_thoai', '')) if pd.notna(current_row.get('so_dien_thoai')) else '', placeholder="Ví dụ: 0912222606")
                            edit_email = st.text_input("Email", value=str(current_row.get('email', '')) if pd.notna(current_row.get('email')) else '', placeholder="Ví dụ: email@hospital.vn")
                        
                        submitted_update = st.form_submit_button("💾 Cập nhật thông tin", use_container_width=True)
                        
                        if submitted_update:
                            if not edit_mcb or not edit_hoten or edit_khoaphong == "-- Chọn Khoa / Phòng --":
                                st.error("⚠️ Vui lòng điền đầy đủ các trường bắt buộc có dấu (*): Mã cán bộ, Họ tên và chọn Khoa/Phòng hợp lệ!")
                            else:
                                try:
                                    check_dup_query = text("SELECT COUNT(*) FROM can_bo WHERE ma_can_bo = :mcb AND id != :id")
                                    with engine.connect() as conn:
                                        dup_count = conn.execute(check_dup_query, {"mcb": edit_mcb.strip(), "id": target_edit_id}).scalar()
                                    
                                    if dup_count > 0:
                                        st.error(f"⚠️ Mã cán bộ '{edit_mcb.strip()}' đã được sử dụng bởi nhân sự khác!")
                                    else:
                                        update_query = text("""
                                            UPDATE can_bo 
                                            SET ma_can_bo = :ma_can_bo, 
                                                ho_ten = :ho_ten, 
                                                ngay_sinh = :ngay_sinh, 
                                                so_cccd = :so_cccd, 
                                                chuc_danh = :chuc_danh, 
                                                khoa_phong = :khoa_phong, 
                                                trinh_do = :trinh_do, 
                                                so_dien_thoai = :so_dien_thoai, 
                                                email = :email
                                            WHERE id = :id
                                        """)
                                        with engine.begin() as conn:
                                            conn.execute(update_query, {
                                                "ma_can_bo": edit_mcb.strip(),
                                                "ho_ten": edit_hoten.strip(),
                                                "ngay_sinh": edit_ngaysinh,
                                                "so_cccd": edit_cccd.strip() if edit_cccd else None,
                                                "chuc_danh": edit_chucdanh if edit_chucdanh != "-- Chọn Chức danh --" else None,
                                                "khoa_phong": edit_khoaphong,
                                                "trinh_do": edit_trinhdo if edit_trinhdo != "-- Chọn Trình độ chuyên môn --" else None,
                                                "so_dien_thoai": edit_sdt.strip() if edit_sdt else None,
                                                "email": edit_email.strip() if edit_email else None,
                                                "id": target_edit_id
                                            })
                                        st.cache_data.clear()
                                        st.success(f"✅ Đã cập nhật thành công thông tin cho [{edit_mcb} - {edit_hoten}]!")
                                        st.rerun()
                                except Exception as e:
                                    st.error(f"⚠️ Đã xảy ra lỗi khi cập nhật: {e}")

   # TAB 3: TẢI MẪU & UPLOAD EXCEL (CHỐNG TRÙNG LẶP & HIỂN THỊ THÔNG BÁO RÕ RÀNG)
    with tab3:
        col_m1, col_m2 = st.columns([1.5, 2])
        
        with col_m1:
            st.markdown("##### 📥 **1. Tải về file Excel mẫu chuẩn 2C-BNV**")
            st.caption("Mẫu chuẩn đầy đủ các trường theo Sơ yếu lý lịch Bộ Nội Vụ (BV Bưu Điện).")
            
            sample_2c_df = pd.DataFrame({
                'Ma_NV': ['N0003', 'N0009', 'N0125'],
                'Ho_Ten': ['Trần Hùng Mạnh', 'Phạm Thị Thanh Tú', 'Phạm Trường Giang'],
                'Ten_Goi_Khac': ['BVBD000628', 'BVBD000630', 'BVBD000092'],
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
                'Trinh_Do_Chuyen_Mon': ['Thạc sĩ, Bác sĩ CKII', 'Thạc sĩ kinh tế', 'Thạc sĩ, Bác sĩ CKII'],
                'Email': ['', '', '']
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
            
            # Hiển thị thông báo lưu trữ từ session_state nếu có
            if "upload_success_msg" in st.session_state:
                st.success(st.session_state["upload_success_msg"])
                del st.session_state["upload_success_msg"]
                
            if "upload_error_msg" in st.session_state:
                st.error(st.session_state["upload_error_msg"])
                del st.session_state["upload_error_msg"]

            uploaded_file = st.file_uploader("Chọn file Excel (.xlsx) chuẩn 2C-BNV:", type=['xlsx', 'xls'], key="excel_uploader_2c_v3")
            
            if uploaded_file is not None:
                try:
                    xls_file = pd.ExcelFile(uploaded_file)
                    sheet_to_read = 'Mau_2C_BNV' if 'Mau_2C_BNV' in xls_file.sheet_names else xls_file.sheet_names[0]
                    df_up = pd.read_excel(uploaded_file, sheet_name=sheet_to_read)
                    
                    st.markdown(f"**Xem trước dữ liệu (Tổng số dòng trong file: {len(df_up)}):**")
                    st.dataframe(df_up.head(3), use_container_width=True, hide_index=True)
                    
                    st.markdown("<br>", unsafe_allow_html=True)
                    if st.button("🚀 Xác nhận Upload dữ liệu vào Hệ thống", use_container_width=True, type="primary"):
                        count_inserted = 0
                        count_updated = 0
                        count_errors = 0
                        error_logs = []
                        
                        col_mapping = {c.strip().lower(): c for c in df_up.columns}
                        
                        def find_val(row_item, possible_keys):
                            for pk in possible_keys:
                                pk_norm = pk.strip().lower()
                                if pk_norm in col_mapping:
                                    real_col = col_mapping[pk_norm]
                                    val = row_item[real_col]
                                    if pd.notna(val):
                                        s = str(val).strip()
                                        if s.lower() not in ['nan', 'none', '', 'null']:
                                            if s.endswith('.0'):
                                                s = s[:-2]
                                            return s
                            return None

                        with engine.begin() as conn:
                            for idx, row in df_up.iterrows():
                                try:
                                    h_val = find_val(row, ['Ho_Ten', 'Họ và Tên', 'Ho Ten', 'hoten'])
                                    if not h_val:
                                        count_errors += 1
                                        error_logs.append(f"Dòng {idx+1}: Thiếu Họ tên.")
                                        continue
                                        
                                    m_val = find_val(row, ['Ma_NV', 'Mã NV', 'Ma_Can_Bo', 'Mã Cán Bộ', 'macanbo']) or f"N{idx+1:04d}"
                                    
                                    ns_val = None
                                    raw_ns = None
                                    for date_key in ['Ngay_Sinh', 'Ngày Sinh', 'NgaySinh', 'ngaysinh']:
                                        if date_key.lower() in col_mapping:
                                            raw_ns = row[col_mapping[date_key.lower()]]
                                            break
                                            
                                    if pd.notna(raw_ns):
                                        try:
                                            if isinstance(raw_ns, datetime):
                                                ns_val = raw_ns.date()
                                            else:
                                                parsed_date = pd.to_datetime(raw_ns, errors='coerce', dayfirst=True)
                                                if pd.notna(parsed_date):
                                                    ns_val = parsed_date.date()
                                        except Exception:
                                            ns_val = None
                                            
                                    cccd_val = find_val(row, ['So_CCCD', 'Số CCCD', 'CCCD', 'socccd'])
                                    chuc_vu_val = find_val(row, ['Chuc_Vu', 'Chức Vụ', 'Chuc_Danh', 'Chức danh', 'chucvu'])
                                    khoa_phong_val = find_val(row, ['Khoa_Phong', 'Khoa / Phòng', 'KhoaPhong', 'khoaphong'])
                                    trinh_do_val = find_val(row, ['Trinh_Do_Chuyen_Mon', 'Trình Độ Chuyên Môn', 'Trinh_Do', 'Trình độ', 'trinhdo'])
                                    sdt_val = find_val(row, ['Dien_Thoai', 'Điện Thoại', 'So_Dien_thoai', 'Số điện thoại', 'dienthoai'])
                                    email_val = find_val(row, ['Email', 'email'])
                                    
                                    # Sử dụng UPSERT: Nếu ma_can_bo đã tồn tại thì CẬP NHẬT, chưa có thì THÊM MỚI
                                    result = conn.execute(text("""
                                        INSERT INTO can_bo (ma_can_bo, ho_ten, ngay_sinh, so_cccd, chuc_danh, khoa_phong, trinh_do, so_dien_thoai, email)
                                        VALUES (:m, :h, :ns, :cccd, :cv, :kp, :td, :sdt, :email)
                                        ON CONFLICT (ma_can_bo) 
                                        DO UPDATE SET 
                                            ho_ten = EXCLUDED.ho_ten,
                                            ngay_sinh = EXCLUDED.ngay_sinh,
                                            so_cccd = EXCLUDED.so_cccd,
                                            chuc_danh = EXCLUDED.chuc_danh,
                                            khoa_phong = EXCLUDED.khoa_phong,
                                            trinh_do = EXCLUDED.trinh_do,
                                            so_dien_thoai = EXCLUDED.so_dien_thoai,
                                            email = EXCLUDED.email
                                    """), {
                                        "m": m_val, "h": h_val, "ns": ns_val, "cccd": cccd_val, 
                                        "cv": chuc_vu_val, "kp": khoa_phong_val, "td": trinh_do_val, 
                                        "sdt": sdt_val, "email": email_val
                                    })
                                    count_inserted += 1
                                except Exception as row_ex:
                                    count_errors += 1
                                    error_logs.append(f"Dòng {idx+1} lỗi: {str(row_ex)}")

                        st.cache_data.clear()
                        
                        if count_inserted > 0:
                            msg = f"🎉 **Xử lý thành công!** Đã cập nhật / thêm mới **{count_inserted}** bản ghi nhân sự vào Cơ sở dữ liệu."
                            if count_errors > 0:
                                msg += f" (Bỏ qua {count_errors} dòng lỗi)."
                            st.session_state["upload_success_msg"] = msg
                            st.balloons()
                            st.rerun()
                        else:
                            st.session_state["upload_error_msg"] = "❌ Không có dữ liệu nào được nạp vào CSDL."
                            st.rerun()
                except Exception as e_up:
                    st.error(f"Lỗi đọc file Excel: {e_up}")

    # TAB 4: XUẤT EXCEL
    with tab4:
        st.markdown("##### 📊 **Tải toàn bộ dữ liệu Cán bộ CNV ra file Excel chuẩn 2C-BNV**")
        if df.empty:
            st.info("Chưa có dữ liệu để xuất file.")
        else:
            export_df = df[['ma_can_bo', 'ho_ten', 'ngay_sinh', 'so_cccd', 'chuc_danh', 'khoa_phong', 'trinh_do', 'so_dien_thoai', 'email']].copy()
            export_df.columns = ['Ma_NV', 'Ho_Ten', 'Ngay_Sinh', 'So_CCCD', 'Chuc_Vu', 'Khoa_Phong', 'Trình_Do_Chuyen_Mon', 'Dien_Thoai', 'Email']
            
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
