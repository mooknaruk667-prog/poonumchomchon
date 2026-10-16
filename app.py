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
        # กรณีหาไม่เจอจริงๆ จะคืนค่าคอลัมน์สุดท้ายเพื่อไม่ให้ระบบพัง
        return cols[fallback_index] if len(cols) > fallback_index else cols[-1]

    # ดึงชื่อคอลัมน์อัตโนมัติ
    tambon_col = get_column_name(['ตำบล'], 1)
    moo_col = get_column_name(['หมู่'], 2)
    position_col = get_column_name(['ตำแหน่ง', 'ประเภท'], 3) # 🟢 เพิ่มการค้นหาคอลัมน์ตำแหน่ง
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
        
    is_filtered = False
    filtered_df = df.copy()
    
    if selected_moo != "ทั้งหมด":
        filtered_df = filtered_df[filtered_df[moo_col].astype(str) == selected_moo]
        is_filtered = True
        
    if selected_tambon != "ทั้งหมด":
        filtered_df = filtered_df[filtered_df[tambon_col] == selected_tambon]
        is_filtered = True

    st.markdown("---")
    
    # 4. แสดงผลลัพธ์
    if is_filtered:
        st.markdown(f"**พบข้อมูล จำนวน {len(filtered_df)} รายการ**")
        
        if not filtered_df.empty:
            
            def make_tel_link(phone_str):
                if pd.isna(phone_str) or str(phone_str).strip() == "-":
                    return None
                digits = "".join(filter(str.isdigit, str(phone_str)))
                return f"tel:{digits}" if digits else None

            filtered_df["กดโทรออก"] = filtered_df[phone_col].apply(make_tel_link)

            # 🟢 จัดเรียงคอลัมน์ที่จะแสดงผล: เพิ่ม position_col (ตำแหน่ง) เข้ามาในตาราง
            raw_display_cols = [moo_col, tambon_col, position_col, name_col, phone_col, "กดโทรออก"]
            display_cols = []
            
            # ป้องกันกรณีหาคอลัมน์บางอันไม่เจอในชีต จะได้ไม่เกิด Error
            for c in raw_display_cols:
                if c not in display_cols and c in filtered_df.columns:
                    display_cols.append(c)
            
            st.dataframe(
                filtered_df[display_cols],
                use_container_width=True,
                hide_index=True,
                column_config={
                    "กดโทรออก": st.column_config.LinkColumn(
                        "กดโทรออก",
                        help="คลิกเพื่อโทรออกทันทีผ่านโทรศัพท์มือถือ",
                        display_text="📞 โทรออก" 
                    )
                }
            )
        else:
            st.warning("ไม่พบข้อมูลที่ตรงกับเงื่อนไขการค้นหา")
    else:
        st.info("👈 กรุณาเลือก 'หมู่ที่' หรือ 'ตำบล' ด้านบน เพื่อแสดงรายชื่อผู้นำชุมชนครับ")
