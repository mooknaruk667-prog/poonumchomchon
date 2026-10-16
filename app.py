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
    # 3. จัดการชื่อคอลัมน์อัตโนมัติ
    cols = df.columns.tolist()
    amphoe_col = next((c for c in cols if 'อำเภอ' in c), cols[0] if len(cols) > 0 else "")
    tambon_col = next((c for c in cols if 'ตำบล' in c), cols[1] if len(cols) > 1 else "")
    moo_col = next((c for c in cols if 'หมู่' in c), cols[2] if len(cols) > 2 else "")
    name_col = next((c for c in cols if 'ชื่อ' in c), cols[3] if len(cols) > 3 else "")
    phone_col = next((c for c in cols if 'เบอร์' in c or 'โทร' in c), cols[4] if len(cols) > 4 else "")

    st.markdown("---")
    
    # 4. ส่วนของกล่องค้นหาแบบ Dropdown ต่อเนื่องกัน
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # กรอง อำเภอ
        amphoe_list = ["ทั้งหมด"] + sorted([str(x) for x in df[amphoe_col].unique() if x != "-"])
        selected_amphoe = st.selectbox(f"📍 เลือก{amphoe_col}", amphoe_list)
    
    with col2:
        # กรอง ตำบล (อ้างอิงจากอำเภอที่เลือก)
        if selected_amphoe != "ทั้งหมด":
            tambon_options = df[df[amphoe_col] == selected_amphoe][tambon_col].unique()
        else:
            tambon_options = df[tambon_col].unique()
            
        tambon_list = ["ทั้งหมด"] + sorted([str(x) for x in tambon_options if x != "-"])
        selected_tambon = st.selectbox(f"📍 เลือก{tambon_col}", tambon_list)
        
    with col3:
        # กรอง หมู่ที่ (อ้างอิงจากอำเภอและตำบลที่เลือก)
        temp_df = df.copy()
        if selected_amphoe != "ทั้งหมด":
            temp_df = temp_df[temp_df[amphoe_col] == selected_amphoe]
        if selected_tambon != "ทั้งหมด":
            temp_df = temp_df[temp_df[tambon_col] == selected_tambon]
            
        moo_options = temp_df[moo_col].unique()
        moo_list = ["ทั้งหมด"] + sorted([str(x) for x in moo_options if x != "-"])
        selected_moo = st.selectbox(f"🏠 เลือก{moo_col}", moo_list)

    # 5. กระบวนการกรองข้อมูลเพื่อแสดงผล
    filtered_df = df.copy()
    
    if selected_amphoe != "ทั้งหมด":
        filtered_df = filtered_df[filtered_df[amphoe_col] == selected_amphoe]
        
    if selected_tambon != "ทั้งหมด":
        filtered_df = filtered_df[filtered_df[tambon_col] == selected_tambon]
        
    if selected_moo != "ทั้งหมด":
        # ตรวจสอบแปลงค่าเป็น string ก่อนเทียบเพื่อป้องกันปัญหาชนิดข้อมูลตัวเลข
        filtered_df = filtered_df[filtered_df[moo_col].astype(str) == selected_moo]

    st.markdown("---")
    st.markdown(f"**พบข้อมูล {len(filtered_df)} รายการ**")
    
    # 6. เลือกแสดงผลเฉพาะข้อมูลที่จำเป็น (เน้นชื่อและเบอร์โทร)
    if not filtered_df.empty:
        display_cols = [amphoe_col, tambon_col, moo_col, name_col, phone_col]
        
        st.dataframe(
            filtered_df[display_cols],
            use_container_width=True,
            hide_index=True
        )
    else:
        st.warning("ไม่พบข้อมูลที่ตรงกับเงื่อนไขการค้นหา")
