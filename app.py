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
        df_dict = pd.read_excel(SHEET_URL, sheet_
