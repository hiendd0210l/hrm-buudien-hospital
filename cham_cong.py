import streamlit as st
import pandas as pd
from datetime import datetime
from sqlalchemy import text

def render_cham_cong(engine):
    st.markdown("---")
    st.subheader("⏰ QUẢN LÝ CHẤM CÔNG & NGÀY NGHỈ")
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Tổng công tháng", "22 ngày")
    col2.metric("Số lượt đi trễ", "02 lượt")
    col3.metric("Số ngày nghỉ phép", "01 ngày")

    st.markdown("##### 📅 **Bảng chấm công chi tiết**")
    st.info("Màn hình theo dõi lịch làm việc, ca trực và đăng ký nghỉ phép của nhân sự.")
