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

# 3. แทรกโค้ด CSS ตกแต่งให้สวยงาม (Modern UI)
st.markdown("""
<style>
    :root { color-scheme: light !important; }
    
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    .block-container {padding-top: 0rem; padding-bottom: 2rem; max-width: 1200px;}
    
    /* พื้นหลังของแอปแบบสีเทาอมฟ้าสว่างๆ */
    .stApp { background-color: #f4f7fa !important; }

    /* ตกแต่งแถบหัวเว็บบนสุดด้วยการไล่สี (Gradient) */
    .custom-header {
        background: linear-gradient(135deg, #1b365d 0%, #3a6096 100%);
        color: white; padding: 18px 30px;
        border-radius: 0 0 20px 20px; display: flex; justify-content: space-between;
        align-items: center; margin-bottom: 25px; 
        box-shadow: 0 10px 20px rgba(27, 54, 93, 0.15);
    }
    .header-title-box { display: flex; align-items: center; gap: 18px; }
    .header-logo-img { width: 60px; height: 60px; object-fit: contain; filter: drop-shadow(0px 2px 4px rgba(0,0,0,0.2)); }
    .header-title { margin: 0; font-size: 24px; font-weight: 800; line-height: 1.2; letter-spacing: 0.5px; }
    .header-subtitle { margin: 0; font-size: 13.5px; color: #ffd700; font-weight: 500; }
    .header-user { font-size: 14px; text-align: right; line-height: 1.4; background: rgba(255,255,255,0.1); padding: 8px 15px; border-radius: 10px; border: 1px solid rgba(255,255,255,0.2); }
    
    /* กล่องเข้าสู่ระบบ */
    .login-container {
        max-width: 420px; margin: 60px auto; background: white !important; padding: 45px 35px;
        border-radius: 20px; box-shadow: 0 15px 35px rgba(0,0,0,0.08); text-align: center; border: 1px solid #edf1f5;
    }
    .login-logo { width: 100px; height: 100px; object-fit: contain; margin: 0 auto 20px auto; display: block; filter: drop-shadow(0px 4px 6px rgba(0,0,0,0.1)); }
    
    /* 🟢 ป้ายหัวข้อ (Badge) สีฟ้าละมุน พร้อมให้ไอคอนแสดงผลได้ชัดเจน */
    .custom-label {
        color: #1b365d !important;
        -webkit-text-fill-color: #1b365d !important;
        background: linear-gradient(to right, #e6f0fa, #f0f5ff) !important;
        padding: 7px 14px !important;
        border-radius: 8px !important;
        font-weight: 700 !important;
        font-size: 14.5px !important;
        margin-bottom: 8px !important;
        margin-top: 12px !important;
        display: inline-block !important;
        border: 1px solid #c4dcf5 !important;
        box-shadow: 0 2px 5px rgba(27, 54, 93, 0.05) !important;
    }
    
    /* ฟอนต์สำหรับไอคอน Emoji ป้องกันสีเพี้ยน */
    .icon-emoji { font-family: "Apple Color Emoji", "Segoe UI Emoji", "Noto Color Emoji", sans-serif; margin-right: 6px; font-size: 16px; }

    /* ปุ่มยืนยันเข้าสู่ระบบ */
    div[data-testid="stFormSubmitButton"] button {
        background: linear-gradient(135deg, #1b365d 0%, #2a5298 100%) !important;
        color: white !important; -webkit-text-fill-color: white !important; 
        border-radius: 12px !important; font-weight: bold !important;
        padding: 12px !important; border: none !important;
        box-shadow: 0 6px 15px rgba(27, 54, 93, 0.25) !important;
        transition: all 0.3s ease-in-out !important; margin-top: 20px !important; letter-spacing: 0.5px;
    }
    div[data-testid="stFormSubmitButton"] button:hover {
        transform: translateY(-3px) !important;
        box-shadow: 0 8px 20px rgba(27, 54, 93, 0.35) !important;
    }
    
    /* การ์ดค้นหา */
    .search-card {
        background-color: white !important; padding: 30px; border-radius: 16px;
        box-shadow: 0 8px 25px rgba(0,0,0,0.04); margin-bottom: 30px; border: 1px solid #edf1f5;
    }
    .search-title { font-size: 20px; font-weight: 800; margin-bottom: 25px; color: #1b365d !important; -webkit-text-fill-color: #1b365d !important; border-bottom: 2px solid #edf1f5; padding-bottom: 10px;}
    .results-title { font-size: 18px; font-weight: bold; color: #1b365d; margin-bottom: 15px; display: flex; align-items: center; gap: 8px;}
    
    /* ตกแต่งตาราง */
    .custom-table { width: 100%; border-collapse: separate; border-spacing: 0; background: white !important; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 15px rgba(0,0,0,0.03); border: 1px solid #eef2f6;}
    .custom-table th { background-color: #1b365d !important; color: white !important; padding: 14px 20px; text-align: left; font-size: 14.5px; font-weight: 600;}
    .custom-table td { padding: 14px 20px; border-bottom: 1px solid #f4f7fa; font-size: 14px; color: #333 !important; -webkit-text-fill-color: #333 !important;}
    .custom-table tr:hover td { background-color: #f8fbff !important; }
    .custom-table tr:last-child td { border-bottom: none; }
    
    /* ปุ่มโทรออก */
    .call-button { background: linear-gradient(135deg, #1e7b34 0%, #28a745 100%); color: white !important; -webkit-text-fill-color: white !important; padding: 8px 16px; border-radius: 8px; text-decoration: none; font-size: 13.5px; font-weight: 600; display: inline-flex; align-items: center; gap: 6px; box-shadow: 0 4px 10px rgba(30, 123, 52, 0.2); transition: all 0.2s ease;}
    .call-button:hover { transform: translateY(-2px); box-shadow: 0 6px 15px rgba(30, 123, 52, 0.3); }
    
    .custom-footer { text-align: center; padding: 25px; margin-top: 50px; color: #6c757d; font-size: 13px; border-top: 1px solid #dce2e8; background-color: #f4f7fa;}
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
    
    st.markdown("""
    <div style="text-align: center; color:#1b365d; -webkit-text-fill-color: #1b365d; font-size: 17px; font-weight: 800; line-height: 1.5; margin-bottom: 12px;">
        ศูนย์ฟื้นฟูสภาพทางสังคม<br>ส่วนพัฒนาผู้ต้องขัง เรือนจำจังหวัดบุรีรัมย์
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('<h3 style="text-align: center; color:#4a6582; -webkit-text-fill-color: #4a6582; font-size: 15px; font-weight: 600; margin-bottom: 25px;">🔐 ระบบสืบค้นข้อมูลผู้นำชุมชน</h3>', unsafe_allow_html=True)
    
    with st.form("login_form"):
        st.markdown('<div class="custom-label"><span class="icon-emoji">👤</span>ชื่อ</div>', unsafe_allow_html=True)
        user_firstname = st.text_input("firstname_input", placeholder="กรุณากรอกชื่อ", label_visibility="collapsed")
        
        st.markdown('<div class="custom-label"><span class="icon-emoji">📝</span>สกุล</div>', unsafe_allow_html=True)
        user_lastname = st.text_input("lastname_input", placeholder="กรุณากรอกนามสกุล", label_visibility="collapsed")
        
        st.markdown('<div class="custom-label"><span class="icon-emoji">🏢</span>ฝ่าย</div>', unsafe_allow_html=True)
        user_dept = st.text_input("dept_input", placeholder="เช่น ทัณฑปฏิบัติ", label_visibility="collapsed")
        
        st.markdown('<br>', unsafe_allow_html=True)
        consent_checked = st.checkbox("✅ ข้าพเจ้ารับทราบและยินยอมให้บันทึกประวัติการเข้าใช้งาน")
        
        submitted = st.form_submit_button("เข้าสู่ระบบ", use_container_width=True)
        
        st.markdown("""
        <div style="font-size: 11.5px; color: #666; -webkit-text-fill-color: #666; text-align: center; margin-top: 20px; padding: 12px; background-color: #f8f9fa; border-radius: 10px; border: 1px dashed #ced4da;">
            <b>📌 คำชี้แจง:</b> ระบบมีการบันทึก ชื่อ สกุล ฝ่าย และเวลาเข้าใช้งาน เพื่อประโยชน์ในการรักษาความปลอดภัยของข้อมูล
        </div>
        """, unsafe_allow_html=True)
        
        if submitted:
            if not consent_checked:
                st.error("⚠️ กรุณาติ๊กช่อง 'ยอมรับเงื่อนไข' ก่อนเข้าสู่ระบบ")
            elif user_firstname.strip() and user_lastname.strip() and user_dept.strip():
                user_full_name = f"{user_firstname.strip()} {user_lastname.strip()}"
                
                st.session_state.logged_in = True
                st.session_state.user_name = user_full_name
                st.session_state.user_dept = user_dept.strip()
                
                bkk_tz = pytz.timezone('Asia/Bangkok')
                login_time = datetime.now(bkk_tz).strftime("%d/%m/%Y %H:%M:%S")
                
                LOG_API_URL = "https://script.google.com/macros/s/AKfycbwyAP6ML_ad1eDhI5clisbp_PYddk2GYx7X7DcdA0cL1Hju9xErZFtl8T25SkmvBmTN/exec"
                
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
                <p class="header-title" style="-webkit-text-fill-color: white;">ระบบสืบค้นข้อมูลผู้นำชุมชน</p>
                <p class="header-subtitle" style="-webkit-text-fill-color: #ffcc00;">เพื่อเตรียมความพร้อมก่อนปล่อยตัวผู้ต้องขังจิตเวช</p>
            </div>
        </div>
        <div class="header-user" style="-webkit-text-fill-color: white;">
            <span style="font-size:12px; color: #a5c8ea; -webkit-text-fill-color: #a5c8ea;">ผู้เข้าใช้งาน</span><br>
            👤 <b>{st.session_state.user_name}</b> ({st.session_state.user_dept})
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    col_empty, col_logout = st.columns([8.8, 1.2])
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
                    if 'เบอร์' in col or 'โทร' in col:
                        df[col] = df[col].astype(str).str.replace(r'\.0$', '', regex=True)
                df_dict[sheet] = df
            return df_dict
        except Exception as e:
            st.error(f"ไม่สามารถโหลดข้อมูลได้: {e}")
            return None

    all_sheets_data = load_data()

    if all_sheets_data:
        st.markdown('<div class="search-card">', unsafe_allow_html=True)
        st.markdown('<div class="search-title"><span class="icon-emoji">🔍</span> ค้นหาข้อมูลผู้นำชุมชน</div>', unsafe_allow_html=True)
        
        amphoe_list = list(all_sheets_data.keys())
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown('<div class="custom-label"><span class="icon-emoji">📍</span>เลือกอำเภอ (จากแท็บชีต)</div>', unsafe_allow_html=True)
            selected_amphoe = st.selectbox("amphoe_select", amphoe_list, label_visibility="collapsed")
            
        df = all_sheets_data[selected_amphoe]
        cols = df.columns.tolist()
        
        def get_column_name(keywords, fallback_index):
            for k in keywords:
                for c in cols:
                    if k in c: return c
            return cols[fallback_index] if len(cols) > fallback_index else cols[-1]

        tambon_col = get_column_name(['ตำบล'], 1)
        moo_col = get_column_name(['หมู่'], 2)
        position_col = get_column_name(['ตำแหน่ง', 'ประเภท'], 3)
        name_col = get_column_name(['ชื่อ'], 4)
        phone_col = get_column_name(['เบอร์', 'โทร'], 5)
        
        with col2:
            moo_options = df[moo_col].unique()
            moo_list = ["ทั้งหมด"] + sorted([str(x) for x in moo_options if x != "-"])
            st.markdown(f'<div class="custom-label"><span class="icon-emoji">🏘️</span>เลือก{moo_col}</div>', unsafe_allow_html=True)
            selected_moo = st.selectbox("moo_select", moo_list, label_visibility="collapsed")

        with col3:
            temp_df = df.copy()
            if selected_moo != "ทั้งหมด":
                temp_df = temp_df[temp_df[moo_col].astype(str) == selected_moo]
                
            tambon_options = temp_df[tambon_col].unique()
            tambon_list = ["ทั้งหมด"] + sorted([str(x) for x in tambon_options if x != "-"])
            st.markdown(f'<div class="custom-label"><span class="icon-emoji">📌</span>เลือก{tambon_col}</div>', unsafe_allow_html=True)
            selected_tambon = st.selectbox("tambon_select", tambon_list, label_visibility="collapsed")
            
        st.markdown('</div>', unsafe_allow_html=True)

        is_filtered = False
        filtered_df = df.copy()
        
        if selected_moo != "ทั้งหมด":
            filtered_df = filtered_df[filtered_df[moo_col].astype(str) == selected_moo]
            is_filtered = True
            
        if selected_tambon != "ทั้งหมด":
            filtered_df = filtered_df[filtered_df[tambon_col] == selected_tambon]
            is_filtered = True

        if is_filtered:
            st.markdown(f'<div class="results-title" style="color:#1b365d; -webkit-text-fill-color: #1b365d;"><span class="icon-emoji">📋</span> ผลการค้นหา ({len(filtered_df)} รายการ)</div>', unsafe_allow_html=True)
            
            st.markdown("""
            <div style="background-color: #fff8e6; color: #856404; -webkit-text-fill-color: #856404; padding: 15px 20px; border-radius: 12px; border-left: 6px solid #ffc107; margin-bottom: 20px; font-size: 14px; line-height: 1.6; box-shadow: 0 2px 8px rgba(255,193,7,0.15);">
                <span class="icon-emoji">⚠️</span> <b>ข้อควรระวัง:</b> ข้อมูลนี้ใช้เพื่อการประสานงานเตรียมความพร้อมก่อนปล่อยตัวผู้ต้องขังของทางราชการเท่านั้น <u>ห้ามมิให้คัดลอก แคปหน้าจอ หรือนำไปเผยแพร่ต่อสาธารณะโดยเด็ดขาด</u>
            </div>
            """, unsafe_allow_html=True)
            
            if not filtered_df.empty:
                table_html = '<table class="custom-table"><thead><tr><th style="color:white; -webkit-text-fill-color:white;">ที่อยู่</th><th style="color:white; -webkit-text-fill-color:white;">ตำแหน่ง / ชื่อ-สกุล</th><th style="color:white; -webkit-text-fill-color:white;">เบอร์ติดต่อ</th></tr></thead><tbody>'
                
                for _, row in filtered_df.iterrows():
                    address_str = f"หมู่ {row[moo_col]} ต.{row[tambon_col]} อ.{selected_amphoe}"
                    
                    pos = row[position_col]
                    role_name_str = f"<b>{pos}</b> <br> {row[name_col]}" if pos != "-" else row[name_col]
                    
                    phone_str = str(row[phone_col])
                    clean_phone = "".join(filter(str.isdigit, phone_str))
                    
                    if clean_phone and clean_phone != "-":
                        # แก้ไขเครื่องหมายคำพูดใน class="icon-emoji" เป็น class='icon-emoji' เรียบร้อยแล้ว
                        btn_html = f"<a href='tel:{clean_phone}' class='call-button'><span class='icon-emoji'>📞</span> โทรออก</a>"
                    else:
                        btn_html = "-"
                    
                    table_html += f"<tr><td>{address_str}</td><td>{role_name_str}</td><td>{btn_html}</td></tr>"
                    
                table_html += '</tbody></table>'
                st.markdown(table_html, unsafe_allow_html=True)
            else:
                st.warning("ไม่พบข้อมูลที่ตรงกับเงื่อนไขการค้นหา")
        else:
            st.info("👈 กรุณาเลือก 'หมู่ที่' หรือ 'ตำบล' ในกล่องค้นหาด้านบน เพื่อแสดงรายชื่อผู้นำชุมชนครับ")

    st.markdown('''
    <div class="custom-footer">
        <div style="color: #1b365d; -webkit-text-fill-color: #1b365d; font-weight: bold; margin-bottom: 5px; font-size: 14.5px;">ศูนย์ฟื้นฟูสภาพทางสังคม ส่วนพัฒนาผู้ต้องขัง เรือนจำจังหวัดบุรีรัมย์</div>
        <div style="font-size: 12px; color: #888;">พัฒนาโดย: Km Ureka Moment</div>
    </div>
    ''', unsafe_allow_html=True)
