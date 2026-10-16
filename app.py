import streamlit as st
import pandas as pd

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
        margin-bottom: 30px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .header-title-box { display: flex; align-items: center; gap: 15px; }
    .header-logo { width: 45px; height: 45px; background: white; border-radius: 50%; display: flex; align-items: center; justify-content: center; color: #1b365d; font-weight: bold; font-size: 10px;}
    .header-title { margin: 0; font-size: 22px; font-weight: bold; }
    .header-subtitle { margin: 0; font-size: 13px; color: #ffcc00; }
    .header-user { font-size: 14px; display: flex; align-items: center; gap: 15px; }
    .logout-btn { border: 1px solid white; padding: 5px 15px; border-radius: 20px; font-size: 12px; cursor: pointer; }

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
    
    .call-button {
        background-color: #1e7b34;
        color: white !important;
        padding: 6px 15px;
        border-radius: 6px;
        text-decoration: none;
        font-size: 13px;
        display: inline-flex;
        align-items: center;
        gap: 5px;
    }
</style>
""", unsafe_allow_html=True)

# 3. สร้าง Header ด้านบน
st.markdown("""
<div class="custom-header">
    <div class="header-title-box">
        <div class="header-logo">รท.</div>
        <div>
            <p class="header-title">ระบบสืบค้นข้อมูลผู้นำชุมชน</p>
            <p class="header-subtitle">เพื่อเตรียมความพร้อมก่อนปล่อยตัวผู้ต้องขังจิตเวช</p>
        </div>
    </div>
    <div class="header-user">
        👤 officer@correction.go.th
    </div>
</div>
""", unsafe_allow_html=True)

# 4. ดึงข้อมูลจาก Google Sheets
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

# 5. ระบบค้นหา (Search Card)
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

    # 6. กรองข้อมูลและแสดงผล
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
