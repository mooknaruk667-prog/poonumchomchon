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
        
        # จัดการคอลัมน์เบอร์โทรไม่ให้มี .0
        for col in df.columns:
            if 'เบอร์' in col or 'โทร' in col:
                df[col] = df[col].astype(str).str.replace(r'\.0$', '', regex=True)
        return df
    except Exception as e:
        st.error(f"ไม่สามารถโหลดข้อมูลได้: {e}")
        return pd.DataFrame()

df = load_data()

if not df.empty:
    # 3. กำหนดชื่อคอลัมน์ให้ตรงกับใน Google Sheets แบบเจาะจง 
    # (หากหัวตารางในชีทของคุณสะกดต่างจากนี้ สามารถแก้ข้อความในเครื่องหมายคำพูดได้เลยครับ)
    amphoe_col = "อำเภอ" 
    tambon_col = "ตำบล"
    moo_col = "หมู่ที่"
    name_col = "ชื่อผู้นำชุมชน" # หรือ "ชื่อ-นามสกุล"
    phone_col = "เบอร์ติดต่อ"   # หรือ "เบอร์โทร"
    
    # ระบบตรวจสอบสำรอง (เผื่อชื่อคอลัมน์ไม่ตรง จะได้ไม่พัง และข้ามคอลัมน์แรกที่เป็นลำดับ)
    cols = df.columns.tolist()
    if amphoe_col not in cols: amphoe_col = next((c for c in cols if 'อำเภอ' in c), cols[1] if len(cols) > 1 else cols[0])
    if tambon_col not in cols: tambon_col = next((c for c in cols if 'ตำบล' in c), cols[2] if len(cols) > 2 else cols[0])
    if moo_col not in cols: moo_col = next((c for c in cols if 'หมู่' in c), cols[3] if len(cols) > 3 else cols[0])
    if name_col not in cols: name_col = next((c for c in cols if 'ชื่อ' in c), cols[4] if len(cols) > 4 else cols[0])
    if phone_col not in cols: phone_col = next((c for c in cols if 'เบอร์' in c or 'โทร' in c), cols[5] if len(cols) > 5 else cols[0])

    st.markdown("---")
    
    # 4. ส่วนของกล่องค้นหาแบบ Dropdown (อำเภอ -> ตำบล -> หมู่ที่)
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
    
    # 6. แสดงผลลัพธ์โดยซ่อนคอลัมน์ "ลำดับ" ทิ้งไป
    if not filtered_df.empty:
        # เลือกแสดงเฉพาะคอลัมน์เนื้อหาที่ต้องการ
        display_cols = [amphoe_col, tambon_col, moo_col, name_col, phone_col]
        
        st.dataframe(
            filtered_df[display_cols],
            use_container_width=True,
            hide_index=True
        )
    else:
        st.warning("ไม่พบข้อมูลที่ตรงกับเงื่อนไขการค้นหา")
