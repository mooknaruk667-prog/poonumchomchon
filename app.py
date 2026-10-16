import streamlit as st
import pandas as pd
from datetime import datetime
import pytz

# 1. ตั้งค่าหน้าเว็บ
st.set_page_config(page_title="ระบบสืบค้นข้อมูลผู้นำชุมชน", layout="wide", initial_sidebar_state="collapsed")

# 2. แทรกโค้ด CSS สำหรับตกแต่ง UI
st.markdown("""
<style>
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    .block-container {padding-top: 0rem; padding-bottom: 2rem; max-width: 1200px;}
    
    .stApp { background-color: #eef2f6; }

    .custom-header {
        background-color: #1b365d;
        color: white;
        padding: 15px 30px;
        border-radius: 0 0 15px 15px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .header-title-box { display: flex; align-items: center; gap: 15px; }
    .header-logo-img { width: 48px; height: 48px; object-fit: contain; }
    .header-title { margin: 0; font-size: 22px; font-weight: bold; }
    .header-subtitle { margin: 0; font-size: 13px; color: #ffcc00; }
    .header-user { font-size: 14px; text-align: right; line-height: 1.4; }
    
    .login-container {
        max-width: 450px;
        margin: 60px auto;
        background: white;
        padding: 40px 30px;
        border-radius: 12px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        text-align: center;
        border: 1px solid #e9ecef;
    }
    .login-logo { width: 90px; margin-bottom: 20px; }
    
    .search-card {
        background-color: white;
        padding: 25px 30px;
        border-radius: 12px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.03);
        margin-bottom: 30px;
        border: 1px solid #e9ecef;
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

# 3. ระบบจัดการสถานะการล็อกอิน (Session State)
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# ---------------------------------------------------------
# หน้าลงชื่อเข้าใช้งาน
# ---------------------------------------------------------
if not st.session_state.logged_in:
    st.markdown('<div class="login-container">', unsafe_allow_html=True)
    st.markdown('<img src="https://raw.githubusercontent.com/the-m-moment/image-host/main/corrections-logo.png" class="login-logo">', unsafe_allow_html=True)
    st.markdown('<h3 style="color:#1b365d; margin-bottom: 5px;">ระบบสืบค้นข้อมูลผู้นำชุมชน</h3>', unsafe_allow_html=True)
    st.markdown('<p style="color:#666; font-size:14px; margin-bottom: 25px;">กรุณาลงชื่อเพื่อบันทึกประวัติการเข้าใช้งาน</p>', unsafe_allow_html=True)
    
    with st.form("login_form"):
        user_name = st.text_input("ชื่อ-นามสกุล ผู้ใช้งาน", placeholder="เช่น นายสมชาย รักดี")
        user_dept = st.text_input("ตำแหน่ง / ฝ่าย / แผนก", placeholder="เช่น นักสังคมสงเคราะห์ / ฝ่ายทัณฑปฏิบัติ")
        
        submitted = st.form_submit_button("เข้าสู่ระบบ", use_container_width=True)
        
        if submitted:
            if user_name.strip() and user_dept.strip():
                # บันทึกข้อมูลลง Session
                st.session_state.logged_in = True
                st.session_state.user_name = user_name.strip()
                st.session_state.user_dept = user_dept.strip()
                
                # บันทึกเวลาเข้าใช้งาน (เวลาไทย)
                bkk_tz = pytz.timezone('Asia/Bangkok')
                st.session_state.login_time = datetime.now(bkk_tz).strftime("%d/%m/%Y %H:%M:%S")
                
                # โค้ดส่วนนี้คือจุดที่จะส่งข้อมูลไปบันทึกลงฐานข้อมูลในอนาคต
                print(f"Log: {st.session_state.user_name} ({st.session_state.user_dept}) เข้าใช้งานเวลา {st.session_state.login_time}")
                
                st.rerun()
            else:
                st.error("⚠️ กรุณากรอกชื่อและฝ่ายให้ครบถ้วนก่อนเข้าใช้งาน")
    st.markdown('</div>', unsafe_allow_html=True)

# ---------------------------------------------------------
# หน้าหลักของระบบ (เมื่อลงชื่อเข้าใช้แล้ว)
# ---------------------------------------------------------
else:
    # 4. สร้าง Header และปุ่มออกจากระบบ
    st.markdown(f"""
    <div class="custom-header">
        <div class="header-title-box">
            <img class="header-logo-img" src="https://raw.githubusercontent.com/the-m-moment/image-host/main/corrections-logo.png" alt="โลโก้กรมราชทัณฑ์">
            <div>
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

    # 5. ดึงข้อมูลจาก Google Sheets
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

    # 6. ระบบค้นหา (Search Card)
    if all_sheets_data:
        st.markdown('<div class="search-card">', unsafe_allow_html=True)
        st.markdown('<div class="search-title">🔍 ค้นหาข้อมูลผู้นำชุมชน</div>', unsafe_allow_html=True)
        
        amphoe_list = list(all_sheets_data.keys())
        
        col1, col2, col3 = st.columns(3)
        with col1:
            selected_amphoe = st.selectbox("📍 เลือกอำเภอ (จากแท็บชีต)", amphoe_list)
            
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
            selected_moo = st.selectbox(f"🏠 เลือก{moo_col}", moo_list)

        with col3:
            temp_df = df.copy()
            if selected_moo != "ทั้งหมด":
                temp_df = temp_df[temp_df[moo_col].astype(str) == selected_moo]
                
            tambon_options = temp_df[tambon_col].unique()
            tambon_list = ["ทั้งหมด"] + sorted([str(x) for x in tambon_options if x != "-"])
            selected_tambon = st.selectbox(f"📍 เลือก{tambon_col}", tambon_list)
            
        st.markdown('</div>', unsafe_allow_html=True)

        # 7. กรองข้อมูลและแสดงผล
        is_filtered = False
        filtered_df = df.copy()
        
        if selected_moo != "ทั้งหมด":
            filtered_df = filtered_df[filtered_df[moo_col].astype(str) == selected_moo]
            is_filtered = True
            
        if selected_tambon != "ทั้งหมด":
            filtered_df = filtered_df[filtered_df[tambon_col] == selected_tambon]
            is_filtered = True

        if is_filtered:
            st.markdown(f'<div class="results-title">ผลการค้นหา ({len(filtered_df)} รายการ)</div>', unsafe_allow_html=True)
            
            if not filtered_df.empty:
                table_html = '<table class="custom-table"><thead><tr><th>ที่อยู่</th><th>ตำแหน่ง/ชื่อ</th><th>เบอร์ติดต่อ</th></tr></thead><tbody>'
                
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
                    
                    table_html += f"<tr><td>{address_str}</td><td>{role_name_str}</td><td>{btn_html}</td></tr>"
                    
                table_html += '</tbody></table>'
                st.markdown(table_html, unsafe_allow_html=True)
            else:
                st.warning("ไม่พบข้อมูลที่ตรงกับเงื่อนไขการค้นหา")
        else:
            st.info("👈 กรุณาเลือก 'หมู่ที่' หรือ 'ตำบล' ในกล่องค้นหาด้านบน เพื่อแสดงรายชื่อผู้นำชุมชนครับ")

    # 8. แสดงชื่อผู้พัฒนา (Footer)
    st.markdown('<div class="custom-footer">พัฒนาโดย: Km Ureka Moment</div>', unsafe_allow_html=True)
