import streamlit as st
import pandas as pd

# 1. ตั้งค่าหน้าเว็บ
st.set_page_config(page_title="ระบบสืบค้นเบอร์ติดต่อผู้นำชุมชน", page_icon="📞", layout="wide")

st.title("📞 ระบบสืบค้นเบอร์ติดต่อผู้นำชุมชน")
st.markdown("ระบบค้นหาข้อมูลเพื่อประสานงานเตรียมความพร้อมก่อนปล่อยตัวผู้ต้องขังจิตเวช")

# 2. URL ของ Google Sheets
SHEET_URL = "https://docs.google.com/spreadsheets/d/1xpG9TQH5rAIUwECgy8LKQLO4lGPQrc_jE-ZwRFLK0hE/export?format=csv"

@st.cache_data(ttl=600)
def load_data():
    try:
        df = pd.read_csv(SHEET_URL)
        df = df.fillna("-")
        
        # 🟢 แก้ไข Error: บังคับตัดคอลัมน์ที่มีชื่อซ้ำกันออก เพื่อไม่ให้ระบบพัง
        df = df.loc[:, ~df.columns.duplicated()]
        
        # จัดการคอลัมน์เบอร์โทร
        for col in df.columns:
            if 'เบอร์' in col or 'โทร' in col:
                df[col] = df[col].astype(str).str.replace(r'\.0$', '', regex=True)
        return df
    except Exception as e:
        st.error(f"ไม่สามารถโหลดข้อมูลได้: {e}")
        return pd.DataFrame()

df = load_data()

if not df.empty:
    cols = df.columns.tolist()
    
    # 3. กำหนดชื่อคอลัมน์แบบรัดกุม ป้องกันการเกิดชื่อซ้ำ
    def get_column_name(keywords, fallback_index):
        for k in keywords:
            for c in cols:
                if k in c: return c
        return cols[fallback_index] if len(cols) > fallback_index else cols[-1]

    amphoe_col = get_column_name(['อำเภอ'], 1)
    tambon_col = get_column_name(['ตำบล'], 2)
    moo_col = get_column_name(['หมู่'], 3)
    name_col = get_column_name(['ชื่อ'], 4)
    phone_col = get_column_name(['เบอร์', 'โทร'], 5)

    st.markdown("---")
    
    # 4. ส่วนของกล่องค้นหาแบบ Dropdown
    col1, col2, col3 = st.columns(3)
    
    with col1:
        amphoe_list = ["ทั้งหมด"] + sorted([str(x) for x in df[amphoe_col].unique() if x != "-"])
        selected_amphoe = st.selectbox(f"📍 เลือก{amphoe_col}", amphoe_list)
    
    with col2:
        if selected_amphoe != "ทั้งหมด":
            tambon_options = df[df[amphoe_col] == selected_amphoe][tambon_col].unique()
        else:
            tambon_options = df[tambon_col].unique()
            
        tambon_list = ["ทั้งหมด"] + sorted([str(x) for x in tambon_options if x != "-"])
        selected_tambon = st.selectbox(f"📍 เลือก{tambon_col}", tambon_list)
        
    with col3:
        temp_df = df.copy()
        if selected_amphoe != "ทั้งหมด":
            temp_df = temp_df[temp_df[amphoe_col] == selected_amphoe]
        if selected_tambon != "ทั้งหมด":
            temp_df = temp_df[temp_df[tambon_col] == selected_tambon]
            
        moo_options = temp_df[moo_col].unique()
        moo_list = ["ทั้งหมด"] + sorted([str(x) for x in moo_options if x != "-"])
        selected_moo = st.selectbox(f"🏠 เลือก{moo_col}", moo_list)

    # 5. กรองข้อมูล
    filtered_df = df.copy()
    
    if selected_amphoe != "ทั้งหมด":
        filtered_df = filtered_df[filtered_df[amphoe_col] == selected_amphoe]
        if selected_tambon != "ทั้งหมด":
            filtered_df = filtered_df[filtered_df[tambon_col] == selected_tambon]
            if selected_moo != "ทั้งหมด":
                filtered_df = filtered_df[filtered_df[moo_col].astype(str) == selected_moo]

    st.markdown("---")
    st.markdown(f"**พบข้อมูล {len(filtered_df)} รายการ**")
    
    # 6. แสดงผลลัพธ์
    if not filtered_df.empty:
        # 🟢 แก้ไข Error: ตรวจสอบอีกครั้งเพื่อไม่ให้มีชื่อคอลัมน์ซ้ำกันก่อนส่งไปแสดงตาราง
        raw_display_cols = [amphoe_col, tambon_col, moo_col, name_col, phone_col]
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
