import streamlit as st
import pandas as pd

# 1. ตั้งค่าหน้าเว็บ
st.set_page_config(page_title="ระบบสืบค้นเบอร์ติดต่อผู้นำชุมชน", page_icon="📞", layout="wide")

st.title("📞 ระบบสืบค้นเบอร์ติดต่อผู้นำชุมชน")
st.markdown("ระบบค้นหาข้อมูลเพื่อประสานงานเตรียมความพร้อมก่อนปล่อยตัวผู้ต้องขังจิตเวช")

# 2. URL ของ Google Sheets
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
    amphoe_list = list(all_sheets_data.keys())
    
    st.markdown("---")
    
    # 3. ส่วนของกล่องค้นหา (หมู่ที่ ➡️ ตำบล)
    col1, col2, col3 = st.columns(3)
    
    with col1:
        selected_amphoe = st.selectbox("📍 เลือกอำเภอ (รายชื่อจากแท็บชีต)", amphoe_list)
        
    df = all_sheets_data[selected_amphoe]
    cols = df.columns.tolist()
    
    def get_column_name(keywords, fallback_index):
        for k in keywords:
            for c in cols:
                if k in c: return c
        return cols[fallback_index] if len(cols) > fallback_index else cols[-1]

    tambon_col = get_column_name(['ตำบล'], 1)
    moo_col = get_column_name(['หมู่'], 2)
    name_col = get_column_name(['ชื่อ'], 3)
    phone_col = get_column_name(['เบอร์', 'โทร'], 4)
    
    with col2:
        moo_options = df[moo_col].unique()
        moo_list = ["ทั้งหมด"] + sorted([str(x) for x in moo_options if x != "-"])
        selected_moo = st.selectbox(f"🏠 เลือก{moo_col}", moo_list)

    with col3:
        temp_df = df.copy()
        if selected_moo != "ทั้งหมด":
            temp_df = temp_df[temp_df[moo_col].astype(str) == selected_moo]
