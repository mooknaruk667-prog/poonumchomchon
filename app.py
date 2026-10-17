import streamlit as st
import pandas as pd
from datetime import datetime
import pytz
import requests
import base64
import os

# 1. ฟังก์ชันดึงรูปภาพจากในระบบมาแสดงผล
def get_base64_of_bin_file(bin_file):
    if os.path.exists(bin_file):
        with open(bin_file, 'rb') as f:
            data = f.read()
        return base64.b64encode(data).decode()
    return None

logo_b64 = get_base64_of_bin_file('logo.png')
if logo_b64:
    logo_src = f"data:image/png;base64,{logo_b64}"
else:
    logo_src = "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4b/Official_emblem_of_the_Department_of_Corrections_%28Thailand%29.png/150px-Official_emblem_of_the_Department_of_Corrections_%28Thailand%29.png"

# 2. ตั้งค่าหน้าเว็บ
st.set_page_config(page_title="ระบบสืบค้นข้อมูลผู้นำชุมชน", layout="wide", initial_sidebar_state="collapsed")

# 3. แทรกโค้ด CSS
st.markdown("""
<style>
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    .block-container {padding-top: 0rem; padding-bottom: 2rem; max-width: 1200px;}
    .stApp { background-color: #eef2f6; }

    .custom-header {
        background-color: #1b365d; color: white; padding: 15px 30px;
        border-radius: 0 0 15px 15px; display: flex; justify-content: space-between;
        align-items: center; margin-bottom: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .header-title-box { display: flex; align-items: center; gap: 15px; }
    .header-logo-img { width: 55px; height: 55px; object-fit: contain; }
    .header-title { margin: 0; font-size: 22px; font-weight: bold; line-height: 1.2; }
    .header-subtitle { margin: 0; font-size: 13px; color: #ffcc00; }
    .header-user { font-size: 14px; text-align: right; line-height: 1.4; }
    
    .login-container {
        max-width: 450px; margin: 60px auto; background: white; padding: 40px 30px;
        border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); text-align: center; border: 1px solid #e9ecef;
    }
    .login-logo { width: 90px; height: 90px; object-fit: contain; margin: 0 auto 15px auto; display: block; }
    
    /* พื้นหลังกรอบกล่องกรอกข้อมูล */
    div[data-baseweb="input"] {
        background-color: #eaf4ff !important;
        border: 2px solid #8ab4f8 !important;
        border-radius: 10px !important;
        transition: all 0.3s ease;
    }
    div[data-baseweb="input"]:focus-within {
        background-color: #ffffff !important;
        border-color: #1b365d !important;
        box-shadow: 0 0 8px rgba(27, 54, 93, 0.4) !important;
    }
    
    /* พื้นหลังกล่อง Selectbox ตอนพับ */
    div[data-testid="stSelectbox"] div[data-baseweb="select"] > div {
        background-color: #ffffff !important;
        border: 1px solid #cbd5e1 !important;
        border-radius: 8px !important;
    }

    /* ========================================================= */
    /* 🟢 ท่าไม้ตาย: บังคับสีตัวอักษรทับ Dark Mode ของมือถือแบบ 100% */
    /* ========================================================= */
    
    /* 1. ล็อกเป้าข้อความหัวข้อหลังไอคอน (📍เลือกอำเภอ, 🏠เลือกหมู่) */
    div[data-testid="stWidgetLabel"] p,
    div[data-testid="stWidgetLabel"] span,
    label, label p, label span {
        color: #1b365d !important;
        -webkit-text-fill-color: #1b365d !important; /* บังคับระบบ iOS/Android */
        font-weight: 70
