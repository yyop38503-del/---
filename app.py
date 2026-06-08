# -*- coding: utf-8 -*-
"""
Created on Thu Jun  4 15:25:05 2026

@author: NIU
"""

import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
import json

# ==========================================
# 1. 設定你的設定值（請把這裡改成你的表單名稱）
# ==========================================
SPREADSHEET_NAME = "物流查詢系統" # 👈 請確認這是否與你 Google Sheet 的標題名稱一模一樣

# ==========================================
# 2. 連結 Google 試算表（改用 Secrets 保險箱寫法）
# ==========================================
@st.cache_data(ttl=60)
def fetch_data_from_sheets():
    SCOPES = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    try:
        # 🔒 從 Streamlit Secrets 保險箱讀取憑證內容
        secret_info = st.secrets["gcp"]["service_account"]
        # 將字串轉換成 Python 字典格式
        info_dict = json.loads(secret_info)
        
        creds = Credentials.from_service_account_info(info_dict, scopes=SCOPES)
        client = gspread.authorize(creds)
        spreadsheet = client.open(SPREADSHEET_NAME)
        worksheet = spreadsheet.get_worksheet(0)
        data = worksheet.get_all_records()
        return pd.DataFrame(data)
    except Exception as e:
        st.error(f"❌ 後台連線發生錯誤：{e}")
        return None

# ==========================================
# 3. 網頁前端畫面設計
# ==========================================
st.set_page_config(page_title="買家物流狀態查詢系統", page_icon="📦", layout="centered")
st.title("📦 買家物流狀態查詢系統")
st.write("請在下方輸入您的姓名，查詢最新的商品與物流狀態。")

df = fetch_data_from_sheets()

if df is not None:
    buyer_name = st.text_input("👤 請輸入您的買家姓名：", key="name_input").strip()

    if buyer_name:
        search_result = df[df['買家姓名'].astype(str).str.strip() == buyer_name]
        
        if not search_result.empty:
            st.success(f"✨ 找到買家 【{buyer_name}】 的物流紀錄：")
            
            for index, row in search_result.iterrows():
                st.markdown("---")
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric(label="🛍️ 商品名稱", value=str(row.get('商品欄', '無資料')))
                with col2:
                    st.metric(label="⏳ 待運回商品", value=str(row.get('待運回商品', '無資料')))
                with col3:
                    status = str(row.get('已交易完畢的商品', '無資料'))
                    if status == "是":
                        st.markdown("### ✅ 狀態\n**已交易完畢**")
                    else:
                        st.markdown("### 🚚 狀態\n**處理中**")
        else:
            st.warning(f"🔍 找不到買家 【{buyer_name}】 的資料，請確認名字是否正確。")
else:
    st.info("💡 正在等待後台資料庫連線...")
    
    


