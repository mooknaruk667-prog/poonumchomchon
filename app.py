import streamlit as st
import pandas as pd

# 1. ตั้งค่าหน้าเว็บ
st.set_page_config(page_title="ระบบสืบค้นเบอร์ติดต่อผู้นำชุมชน", page_icon="📞", layout="wide")

st.title("📞 ระบบสืบค้นเบอร์ติดต่อผู้นำชุมชน")
st.markdown("ระบบค้นหาข้อมูลเพื่อประสานงานเตรียมความพร้อมก่อนปล่อยตัวผู้ต้องขังจิตเวช")

# 2. เปลี่ยน URL เป็น format=xlsx เพื่อให้อ่านได้ทุกแท็บ (ทุกชีต)
SHEET_URL = "https://docs.google.com/spreadsheets/d/1xpG9TQH5rAIUwECgy8LKQLO4lGPQrc_jE-ZwRFLK0hE/export?format=xlsx"

@st.cache_data(ttl=600)
def load_data():
    try:
        # sheet_name=None จะดึงข้อมูลทุกชีตมาเก็บในรูปแบบ Dictionary { 'ชื่ออำเภอ': ข้อมูล }
        df_dict = pd.read_excel(SHEET_URL, sheet_name=None)
        
        # ทำความสะอาดข้อมูลให้ทุกชีต
        for sheet, df in df_dict.items():
            df = df.fillna("-")
            df = df.loc[:, ~df.columns.duplicated()] # ป้องกันชื่อคอลัมน์ซ้ำ
            
            for col in df.columns:
                if 'เบอร์' in col or 'โทร' in col:
                    df[col] = df[col].astype(str).str.replace(r'\.0$', '', regex=True)
                    
            df_dict[sheet] = df
            
        return df_dict
    except Exception as e:
        st.error(f"ไม่สามารถโหลดข้อมูลได้: {e}")
        return None

# โหลดข้อมูลทุกอำเภอ
all_sheets_data = load_data()

if all_sheets_data:
    # ดึงชื่อแท็บทั้งหมดมาเป็นรายการอำเภอ
    amphoe_list = list(all_sheets_data.keys())
    
    st.markdown("---")
    
    # 3. ส่วนของกล่องค้นหา
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # เลือกอำเภอจากชื่อแท็บ
        selected_amphoe = st.selectbox("📍 เลือกอำเภอ (รายชื่อจากแท็บชีต)", amphoe_list)
        
    # ดึงข้อมูลเฉพาะอำเภอ(แท็บ) ที่เลือกมาใช้งาน
    df = all_sheets_data[selected_amphoe]
    cols = df.columns.tolist()
    
    # ฟังก์ชันช่วยหาชื่อคอลัมน์ (ป้องกัน Error กรณีชีตแต่ละหน้าตั้งชื่อคอลัมน์ไม่เหมือนกันเป๊ะๆ)
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
        # ดึงรายชื่อตำบลในอำเภอนั้นๆ
        tambon_options = df[tambon_col].unique()
        tambon_list = ["ทั้งหมด"] + sorted([str(x) for x in tambon_options if x != "-"])
        selected_tambon = st.selectbox(f"📍 เลือก{tambon_col}", tambon_list)
        
    with col3:
        # ดึงรายชื่อหมู่ที่ตามตำบลที่เลือก
        temp_df = df.copy()
        if selected_tambon != "ทั้งหมด":
            temp_df = temp_df[temp_df[tambon_col] == selected_tambon]
            
        moo_options = temp_df[moo_col].unique()
        moo_list = ["ทั้งหมด"] + sorted([str(x) for x in moo_options if x != "-"])
        selected_moo = st.selectbox(f"🏠 เลือก{moo_col}", moo_list)

    # 4. กรองข้อมูลตาม ตำบล และ หมู่ที่
    filtered_df = df.copy()
    if selected_tambon != "ทั้งหมด":
        filtered_df = filtered_df[filtered_df[tambon_col] == selected_tambon]
    if selected_moo != "ทั้งหมด":
        filtered_df = filtered_df[filtered_df[moo_col].astype(str) == selected_moo]

    st.markdown("---")
    st.markdown(f"**พบข้อมูลผู้นำชุมชน อำเภอ{selected_amphoe} จำนวน {len(filtered_df)} รายการ**")
    
    # 5. แสดงผลลัพธ์
    if not filtered_df.empty:
        # เตรียมคอลัมน์ที่จะแสดงผล (ไม่ต้องแสดงคอลัมน์อำเภอแล้ว เพราะเลือกมาจากแท็บแล้ว)
        raw_display_cols = [tambon_col, moo_col, name_col, phone_col]
        display_cols = []
        for c in raw_display_cols:
            if c not in display_cols and c in filtered_df.columns:
                display_cols.append(c)
        
        st.dataframe(
            filtered_df[display_cols],
            use_container_width=True,
            hide_index=True
        )
    else:
        st.warning("ไม่พบข้อมูลที่ตรงกับเงื่อนไขการค้นหา")
