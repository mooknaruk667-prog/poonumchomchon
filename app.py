import streamlit as st
import pandas as pd
from datetime import datetime
import pytz
import requests
import base64
import os

# 1. ฟังก์ชันดึงรูปภาพจากในระบบมาแสดงผล
def get_base64_of_bin_file(bin_file):
    if os.path.exists(bin_file):
        with open(bin_file, 'rb') as f:
            data = f.read()
        return base64.b64encode(data).decode()
    return None

logo_b64 = get_base64_of_bin_file('logo.png')
if logo_b64:
    logo_src = f"data:image/png;base64,{logo_b64}"
else:
    logo_src = "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4b/Official_emblem_of_the_Department_of_Corrections_%28Thailand%29.png/150px-Official_emblem_of_the_Department_of_Corrections_%28Thailand%29.png"

# 2. ตั้งค่าหน้าเว็บ
st.set_page_config(page_title="ระบบสืบค้นข้อมูลผู้นำชุมชน", layout="wide", initial_sidebar_state="collapsed")

# 3. แทรกโค้ด CSS
st.markdown("""
<style>
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    .block-container {padding-top: 0rem; padding-bottom: 2rem; max-width: 1200px;}
    .stApp { background-color: #eef2f6; }

    .custom-header {
        background-color: #1b365d; color: white; padding: 15px 30px;
        border-radius: 0 0 15px 15px; display: flex; justify-content: space-between;
        align-items: center; margin-bottom: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .header-title-box { display: flex; align-items: center; gap: 15px; }
    .header-logo-img { width: 55px; height: 55px; object-fit: contain; }
    .header-title { margin: 0; font-size: 22px; font-weight: bold; line-height: 1.2; }
    .header-subtitle { margin: 0; font-size: 13px; color: #ffcc00; }
    .header-user { font-size: 14px; text-align: right; line-height: 1.4; }
    
    .login-container {
        max-width: 450px; margin: 60px auto; background: white; padding: 40px 30px;
        border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); text-align: center; border: 1px solid #e9ecef;
    }
    /* 🟢 ปรับโลโก้ให้อยู่กึ่งกลางเป๊ะๆ ด้วย display: block และ margin: auto */
    .login-logo { width: 90px; height: 90px; object-fit: contain; margin: 0 auto 15px auto; display: block; }
    
    .search-card {
        background-color: white; padding: 25px 30px; border-radius: 12px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.03); margin-bottom: 30px; border: 1px solid #e9ecef;
    }
    .search-title { font-size: 18px; font-weight: bold; margin-bottom: 20px; color: #333; }
    .results-title { font-size: 18px; font-weight: bold; color: #1b365d; margin-bottom: 15px; }
    
    .custom-table { width: 100%; border-collapse: collapse; background: white; border-radius: 10px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.05); border: 1px solid #eee;}
    .custom-table th { background-color: #f8f9fa; color: #333; padding: 12px 20px; text-align: left; font-size: 14px; border-bottom: 1px solid #ddd;}
    .custom-table td { padding: 12px 20px; border-bottom: 1px solid #eee; font-size: 14px; color: #444;}
    .custom-table tr:hover { background-color: #fbfbfc; }
    
    .call-button { background-color: #1e7b34; color: white !important; padding: 6px 15px; border-radius: 6px; text-decoration: none; font-size: 13px; display: inline-flex; align-items: center; gap: 5px; }
    .custom-footer { text-align: center; padding: 20px; margin-top: 40px; color: #6c757d; font-size: 14px; border-top: 1px solid #dce2e8; }
</style>
""", unsafe_allow_html=True)

# 4. สถานะล็อกอิน
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# ---------------------------------------------------------
# หน้าลงชื่อเข้าใช้งาน
# ---------------------------------------------------------
if not st.session_state.logged_in:
    st.markdown('<div class="login-container">', unsafe_allow_html=True)
    st.markdown(f'<img src="{logo_src}" class="login-logo">', unsafe_allow_html=True)
    
    # 🟢 เพิ่มบรรทัดที่ 2 เรือนจำจังหวัดบุรีรัมย์ และจัดกึ่งกลาง
    st.markdown("""
    <div style="color:#1b365d; font-size: 16px; font-weight: bold; line-height: 1.4; margin-bottom: 15px;">
        ศูนย์ฟื้นฟูสภาพทางสังคม ส่วนพัฒนาผู้ต้องขัง<br>
        เรือนจำจังหวัดบุรีรัมย์
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('<h3 style="color:#1b365d; margin-bottom: 5px;">ระบบสืบค้นข้อมูลผู้นำชุมชน</h3>', unsafe_allow_html=True)
    st.markdown('<p style="color:#666; font-size:14px; margin-bottom: 25px;">กรุณาลงชื่อก่อนเข้าใช้งาน</p>', unsafe_allow_html=True)
    
    with st.form("login_form"):
        user_firstname = st.text_input("ชื่อ", placeholder="เช่น สมชาย")
        user_lastname = st.text_input("สกุล", placeholder="เช่น รักดี")
        user_dept = st.text_input("ฝ่าย", placeholder="เช่น ทัณฑปฏิบัติ")
        
        submitted = st.form_submit_button("เข้าสู่ระบบ", use_container_width=True)
        
        if submitted:
            if user_firstname.strip() and user_lastname.strip() and user_dept.strip():
                user_full_name = f"{user_firstname.strip()} {user_lastname.strip()}"
                
                st.session_state.logged_in = True
                st.session_state.user_name = user_full_name
                st.session_state.user_dept = user_dept.strip()
                
                bkk_tz = pytz.timezone('Asia/Bangkok')
                login_time = datetime.now(bkk_tz).strftime("%d/%m/%Y %H:%M:%S")
                
                # ⚠️ นำ URL ของ Web App จาก Google Apps Script มาใส่ตรงนี้
                LOG_API_URL = "ใส่_URL_WEB_APP_ของคุณที่นี่"
                
                if LOG_API_URL != "ใส่_URL_WEB_APP_ของคุณที่นี่":
                    try:
                        payload = {
                            "name": user_full_name,
                            "dept": user_dept.strip(),
                            "time": login_time
                        }
                        requests.get(LOG_API_URL, params=payload, timeout=5)
                    except Exception as e:
                        print("Error logging to sheets:", e)
                
                st.rerun()
            else:
                st.error("⚠️ กรุณากรอก ชื่อ, สกุล และฝ่าย ให้ครบถ้วนก่อนเข้าใช้งาน")
    st.markdown('</div>', unsafe_allow_html=True)

# ---------------------------------------------------------
# หน้าหลักของระบบ
# ---------------------------------------------------------
else:
    st.markdown(f"""
    <div class="custom-header">
        <div class="header-title-box">
            <img class="header-logo-img" src="{logo_src}" alt="โลโก้กรมราชทัณฑ์">
            <div>
                <!-- 🟢 อัปเดตชื่อหน่วยงานให้ตรงกับหน้าล็อกอิน -->
                <p style="margin: 0; font-size: 11px; color: #a5c8ea;">ศูนย์ฟื้นฟูสภาพทางสังคม ส่วนพัฒนาผู้ต้องขัง เรือนจำจังหวัดบุรีรัมย์</p>
                <p class="header-title">ระบบสืบค้นข้อมูลผู้นำชุมชน</p>
                <p class="header-subtitle">เพื่อเตรียมความพร้อมก่อนปล่อยตัวผู้ต้องขังจิตเวช</p>
            </div>
        </div>
        <div class="header-user">
            👤 <b>{st.session_state.user_name}</b><br>
            <span style="color:#a5c8ea; font-size:12px;">{st.session_state.user_dept}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    col_empty, col_logout = st.columns([8.5, 1.5])
    with col_logout:
        if st.button("🚪 ออกจากระบบ", use_container_width=True):
            st.session_state.logged_in = False
            st.rerun()

    SHEET_URL = "https://docs.google.com/spreadsheets/d/1xpG9TQH5rAIUwECgy8LKQLO4lGPQrc_jE-ZwRFLK0hE/export?format=xlsx"

    @st.cache_data(ttl=600)
    def load_data():
        try:
            df_dict = pd.read_excel(SHEET_URL, sheet_name=None)
            for sheet, df in df_dict.items():
                df = df.fillna("-")
                df = df.loc[:, ~df.columns.duplicated()] 
                for col in df.columns:
                    if '
