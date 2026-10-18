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
    .stApp { background-color: #eef2f6 !important; }

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
        max-width: 450px; margin: 60px auto; background: white !important; padding: 40px 30px;
        border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); text-align: center; border: 1px solid #e9ecef;
    }
    .login-logo { width: 90px; height: 90px; object-fit: contain; margin: 0 auto 15px auto; display: block; }
    
    /* 🟢 คลาสพิเศษสำหรับหัวข้อ (Label) ที่เราสร้างขึ้นมาเอง */
    .custom-label {
        color: #1b365d !important;
        -webkit-text-fill-color: #1b365d !important;
        font-weight: bold !important;
        font-size: 15px !important;
        margin-bottom: 5px !important;
        margin-top: 10px !important;
        display: block !important;
    }

    /* ตกแต่งปุ่มยืนยัน */
    div[data-testid="stFormSubmitButton"] button {
        background-color: #1b365d !important;
        color: white !important;
        -webkit-text-fill-color: white !important; 
        border-radius: 10px !important;
        font-weight: bold !important;
        padding: 10px !important;
        border: none !important;
        box-shadow: 0 4px 6px rgba(27, 54, 93, 0.2) !important;
        transition: all 0.3s ease-in-out !important;
        margin-top: 15px !important;
    }
    div[data-testid="stFormSubmitButton"] button:hover {
        background-color: #2b5c8f !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 12px rgba(27, 54, 93, 0.3) !important;
    }
    
    .search-card {
        background-color: white !important; padding: 25px 30px; border-radius: 12px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.03); margin-bottom: 30px; border: 1px solid #e9ecef;
    }
    .search-title { font-size: 18px; font-weight: bold; margin-bottom: 20px; color: #333; }
    .results-title { font-size: 18px; font-weight: bold; color: #1b365d; margin-bottom: 15px; }
    
    .custom-table { width: 100%; border-collapse: collapse; background: white !important; border-radius: 10px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.05); border: 1px solid #eee;}
    .custom-table th { background-color: #f8f9fa !important; color: #333 !important; padding: 12px 20px; text-align: left; font-size: 14px; border-bottom: 1px solid #ddd;}
    .custom-table td { padding: 12px 20px; border-bottom: 1px solid #eee; font-size: 14px; color: #444 !important; -webkit-text-fill-color: #444 !important;}
    .custom-table tr:hover { background-color: #fbfbfc !important; }
    
    .call-button { background-color: #1e7b34; color: white !important; -webkit-text-fill-color: white !important; padding: 6px 15px; border-radius: 6px; text-decoration: none; font-size: 13px; display: inline-flex; align-items: center; gap: 5px; }
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
    
    st.markdown("""
    <div style="text-align: center; color:#1b365d; -webkit-text-fill-color: #1b365d; font-size: 16px; font-weight: bold; line-height: 1.4; margin-bottom: 15px;">
        ศูนย์ฟื้นฟูสภาพทางสังคม ส่วนพัฒนาผู้ต้องขัง<br>
        เรือนจำจังหวัดบุรีรัมย์
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('<h3 style="text-align: center; color:#1b365d; -webkit-text-fill-color: #1b365d; margin-bottom: 5px;">ระบบสืบค้นข้อมูลผู้นำชุมชน</h3>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; color:#666; -webkit-text-fill-color: #666; font-size:14px; margin-bottom: 25px;">กรุณาลงชื่อก่อนเข้าใช้งาน</p>', unsafe_allow_html=True)
    
    with st.form("login_form"):
        # 🟢 แก้ไข: สร้างหัวข้อแยกต่างหาก และซ่อนหัวข้อของ Streamlit
        st.markdown('<div class="custom-label">ชื่อ</div>', unsafe_allow_html=True)
        user_firstname = st.text_input("firstname_input", placeholder="เช่น หล่อ", label_visibility="collapsed")
        
        st.markdown('<div class="custom-label">สกุล</div>', unsafe_allow_html=True)
        user_lastname = st.text_input("lastname_input", placeholder="เช่น พิลึก", label_visibility="collapsed")
        
        st.markdown('<div class="custom-label">ฝ่าย</div>', unsafe_allow_html=True)
        user_dept = st.text_input("dept_input", placeholder="เช่น ทัณฑปฏิบัติ", label_visibility="collapsed")
        
        consent_checked = st.checkbox("ข้าพเจ้ารับทราบและยินยอมให้บันทึกประวัติการเข้าใช้งาน")
        
        submitted = st.form_submit_button("เข้าสู่ระบบ", use_container_width=True)
        
        st.markdown("""
        <div style="font-size: 11px; color: #666; -webkit-text-fill-color: #666; text-align: center; margin-top: 15px; padding: 10px; background-color: #f8f9fa; border-radius: 8px;">
            <b>คำชี้แจง:</b> ระบบมีการบันทึก ชื่อ สกุล ฝ่าย และเวลาเข้าใช้งาน เพื่อประโยชน์ในการรักษาความปลอดภัยของระบบข้อมูลสารสนเทศ
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
                <p class="header-title" style="-webkit-text-fill-color: white;">ระบบสืบค้นข้อมูลผู้นำชุมชน</p>
                <p class="header-subtitle" style="-webkit-text-fill-color: #ffcc00;">เพื่อเตรียมความพร้อมก่อนปล่อยตัวผู้ต้องขังจิตเวช</p>
            </div>
        </div>
        <div class="header-user" style="-webkit-text-fill-color: white;">
            👤 <b>{st.session_state.user_name}</b><br>
            <span style="color:#a5c8ea; -webkit-text-fill-color: #a5c8ea; font-size:12px;">{st.session_state.user_dept}</span>
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
        st.markdown('<div class="search-title" style="color:#000000; -webkit-text-fill-color:#000000;">🔍 ค้นหาข้อมูลผู้นำชุมชน</div>', unsafe_allow_html=True)
        
        amphoe_list = list(all_sheets_data.keys())
        
        col1, col2, col3 = st.columns(3)
        with col1:
            # 🟢 แก้ไข: สร้างหัวข้อแยกต่างหากด้วย HTML และซ่อน Label ของ Streamlit
            st.markdown('<div class="custom-label">📍 เลือกอำเภอ (จากแท็บชีต)</div>', unsafe_allow_html=True)
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
            # 🟢 แก้ไขหัวข้อหมู่ที่
            st.markdown(f'<div class="custom-label">🏠 เลือก{moo_col}</div>', unsafe_allow_html=True)
            selected_moo = st.selectbox("moo_select", moo_list, label_visibility="collapsed")

        with col3:
            temp_df = df.copy()
            if selected_moo != "ทั้งหมด":
                temp_df = temp_df[temp_df[moo_col].astype(str) == selected_moo]
                
            tambon_options = temp_df[tambon_col].unique()
            tambon_list = ["ทั้งหมด"] + sorted([str(x) for x in tambon_options if x != "-"])
            # 🟢 แก้ไขหัวข้อตำบล
            st.markdown(f'<div class="custom-label">📍 เลือก{tambon_col}</div>', unsafe_allow_html=True)
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
            st.markdown(f'<div class="results-title" style="color:#1b365d; -webkit-text-fill-color: #1b365d;">ผลการค้นหา ({len(filtered_df)} รายการ)</div>', unsafe_allow_html=True)
            
            st.markdown("""
            <div style="background-color: #fff3cd; color: #856404; -webkit-text-fill-color: #856404; padding: 12px 15px; border-radius: 8px; border-left: 5px solid #ffeeba; margin-bottom: 20px; font-size: 14px; line-height: 1.5;">
                ⚠️ <b>ข้อควรระวัง:</b> ข้อมูลนี้ใช้เพื่อการประสานงานเตรียมความพร้อมก่อนปล่อยตัวผู้ต้องขังของทางราชการเท่านั้น <u>ห้ามมิให้คัดลอก แคปหน้าจอ หรือนำไปเผยแพร่ต่อสาธารณะโดยเด็ดขาด</u>
            </div>
            """, unsafe_allow_html=True)
            
            if not filtered_df.empty:
                table_html = '<table class="custom-table"><thead><tr><th style="color:#000000; -webkit-text-fill-color:#000000;">ที่อยู่</th><th style="color:#000000; -webkit-text-fill-color:#000000;">ตำแหน่ง/ชื่อ</th><th style="color:#000000; -webkit-text-fill-color:#000000;">เบอร์ติดต่อ</th></tr></thead><tbody>'
                
                for _, row in filtered_df.iterrows():
                    address_str = f"หมู่ {row[moo_col]} ต.{row[tambon_col]} อ.{selected_amphoe}"
                    
                    pos = row[position_col]
                    role_name_str = f"{pos} - {row[name_col]}" if pos != "-" else row[name_col]
                    
                    phone_str = str(row[phone_col])
                    clean_phone = "".join(filter(str.isdigit, phone_str))
                    
                    if clean_phone and clean_phone != "-":
                        btn_html = f"<a href='tel:{clean_phone}' class='call-button'>📞 โทร {phone_str}</a>"
                    else:
                        btn_html = "-"
                    
                    table_html += f"<tr><td style='color:#000000; -webkit-text-fill-color:#000000;'>{address_str}</td><td style='color:#000000; -webkit-text-fill-color:#000000;'>{role_name_str}</td><td>{btn_html}</td></tr>"
                    
                table_html += '</tbody></table>'
                st.markdown(table_html, unsafe_allow_html=True)
            else:
                st.warning("ไม่พบข้อมูลที่ตรงกับเงื่อนไขการค้นหา")
        else:
            st.info("👈 กรุณาเลือก 'หมู่ที่' หรือ 'ตำบล' ในกล่องค้นหาด้านบน เพื่อแสดงรายชื่อผู้นำชุมชนครับ")

    st.markdown('''
    <div class="custom-footer">
        <div style="color: #1b365d; -webkit-text-fill-color: #1b365d; font-weight: bold; margin-bottom: 8px;">ศูนย์ฟื้นฟูสภาพทางสังคม ส่วนพัฒนาผู้ต้องขัง เรือนจำจังหวัดบุรีรัมย์</div>
        พัฒนาโดย: Km Ureka Moment
    </div>
    ''', unsafe_allow_html=True)
