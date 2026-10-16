import streamlit as st
import pandas as pd

# 1. ตั้งค่าหน้าเว็บให้เต็มจอ (Wide Layout)
st.set_page_config(page_title="ระบบสืบค้นข้อมูลผู้นำชุมชน", layout="wide", initial_sidebar_state="collapsed")

# 2. แทรกโค้ด CSS เพื่อปรับแต่งหน้าตาให้เหมือนภาพต้นแบบ
st.markdown("""
<style>
    /* ซ่อนแถบเมนูเดิมของ Streamlit และปรับขอบพื้นที่ */
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    .block-container {padding-top: 0rem; padding-bottom: 0rem; max-width: 1200px;}
    
    /* พื้นหลังของหน้าเว็บ */
    .stApp { background-color: #eef2f6; }

    /* แถบ Header สีน้ำเงินเข้ม */
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

    /* กล่องค้นหาสีขาว (Card) */
    .search-card {
        background-color: white;
        padding: 25px 30px;
        border-radius: 12px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.03);
        margin-bottom: 30px;
        border: 1px solid #e9ecef;
    }
    
    /* หัวข้อในกล่องค้นหา */
    .search-title { font-size: 18px; font-weight: bold; margin-bottom: 20px; color: #333; }
    
    /* ปรับแต่งปุ่มค้นหาและล้างข้อมูล */
    .btn-search div[data-testid="stButton"] > button {
        background-color: #2b5c8f; color: white; border-radius: 6px; width: 100%; border: none; height: 40px; margin-top: 28px;
    }
    .btn-clear div[data-testid="stButton"] > button {
        background-color: #6c757d; color: white; border-radius: 6px; width: 100%; border: none; height: 40px; margin-top: 28px;
    }

    /* ปรับแต่งตาราง HTML ให้เหมือนต้นแบบ */
    .results-title { font-size: 18px; font-weight: bold; color: #1b365d; margin-bottom: 15px; }
    .custom-table { width: 100%; border-collapse: collapse; background: white; border-radius: 10px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.05); border: 1px solid #eee;}
    .custom-table th { background-color: #f8f9fa; color: #333; padding: 12px 20px; text-align: left; font-size: 14px; border-bottom: 1px solid #ddd;}
    .custom-table td { padding: 12px 20px; border-bottom: 1px solid #eee; font-size: 14px; color: #444;}
    .custom-table tr:hover { background-color: #fbfbfc; }
    
    /* ปุ่มกดโทรออกสีเขียว */
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

# 3. ส่วน Header (แถบสีน้ำเงินด้านบน)
st.markdown("""
<div class="custom-header">
    <div class="header-title-box">
        <div class="header-logo">LOGO</div>
        <div>
            <p class="header-title">ระบบสืบค้นข้อมูลผู้นำชุมชน</p>
            <p class="header-subtitle">เพื่อเตรียมความพร้อมก่อนปล่อยตัวผู้ต้องขังจิตเวช</p>
        </div>
    </div>
    <div class="header-user">
        👤 user.test@correction.go.th
        <span class="logout-btn">ออกจากระบบ</span>
    </div>
</div>
""", unsafe_allow_html=True)

# 4. ส่วนกล่องค้นหา (Search Card)
st.markdown('<div class="search-card">', unsafe_allow_html=True)
st.markdown('<div class="search-title">🔍 ค้นหาข้อมูลผู้นำชุมชน</div>', unsafe_allow_html=True)

# สร้าง Layout สำหรับช่องกรอกข้อมูล
col1, col2, col3, col4, col5 = st.columns([2.5, 2.5, 2.5, 1, 1])

with col1:
    amphoe = st.selectbox("เลือกอำเภอ", ["ทั้งหมด", "อ.เมืองบุรีรัมย์", "อ.นางรอง"])
with col2:
    tambon = st.text_input("ตำบล/หมู่บ้าน", placeholder="ใส่ชื่อตำบลหรือหมู่ที่...")
with col3:
    name = st.text_input("ชื่อผู้นำชุมชน", placeholder="ใส่ชื่อหรือนามสกุล...")
    
with col4:
    st.markdown('<div class="btn-search">', unsafe_allow_html=True)
    btn_search = st.button("🔍 ค้นหา")
    st.markdown('</div>', unsafe_allow_html=True)
    
with col5:
    st.markdown('<div class="btn-clear">', unsafe_allow_html=True)
    btn_clear = st.button("ล้างข้อมูล")
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True) # ปิดกล่องค้นหา

# 5. ส่วนแสดงผลตาราง (HTML Table เรนเดอร์ด้วยข้อมูลตัวอย่าง)
# ดึงข้อมูลจริงของคุณมาใส่ใน list นี้แทน
mock_data = [
    {"address": "หมู่ 3 ต.ในเมือง อ.เมืองบุรีรัมย์", "role": "ผู้ใหญ่บ้าน", "name": "นายสมชาย ดีงาม", "phone": "081-234-xxxx"},
    {"address": "หมู่ 5 ต.รอบเขา อ.นางรอง", "role": "กำนัน", "name": "นายวิชัย ยอดดี", "phone": "089-567-xxxx"},
    {"address": "หมู่ 6 ต.ในเมือง อ.เมืองบุรีรัมย์", "role": "ผู้ใหญ่บ้าน", "name": "นายธงชัย ดีงาม", "phone": "089-567-xxxx"}
]

st.markdown(f'<div class="results-title">ผลการค้นหา ({len(mock_data)} รายการ)</div>', unsafe_allow_html=True)

# สร้าง HTML Table จากข้อมูล
table_html = '<table class="custom-table"><thead><tr><th>ที่อยู่</th><th>ตำแหน่ง/ชื่อ</th><th>เบอร์ติดต่อ</th></tr></thead><tbody>'

for row in mock_data:
    table_html += f"""
    <tr>
        <td>{row['address']}</td>
        <td>{row['role']} - {row['name']}</td>
        <td>
            <a href="tel:{row['phone'].replace('-', '')}" class="call-button">
                📞 โทร {row['phone']}
            </a>
        </td>
    </tr>
    """

table_html += '</tbody></table>'
st.markdown(table_html, unsafe_allow_html=True)
