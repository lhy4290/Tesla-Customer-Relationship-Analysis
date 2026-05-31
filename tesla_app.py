import streamlit as st
import pandas as pd
import random
import time

# ==========================================
# 1. App 基本設定 (模擬手機介面置中)
# ==========================================
st.set_page_config(
    page_title="Tesla Guardian",
    layout="centered" # 使用置中佈局模擬手機畫面
)

# 載入先前分析的區域充電站資料 (作為智慧充電功能的基底)
@st.cache_data
def load_charging_data():
    # 這裡可以直接讀取你清洗好的 CSV，這裡為了方便展示 App 邏輯，先寫死報告中的聚合數據
    data = {
        'Region': ['Middle East', 'Asia', 'Europe', 'North America'],
        'Charging_Stations': [5900000, 4200000, 5800000, 3900000]
    }
    return pd.DataFrame(data)

df_charge = load_charging_data()

# ==========================================
# 2. 模擬車輛狀態 (Session State)
# ==========================================
if 'battery_12v_health' not in st.session_state:
    st.session_state.battery_12v_health = 15  # 刻意設定低於安全值 (20%) 來展示預警功能
if 'ota_status' not in st.session_state:
    st.session_state.ota_status = "有新的安全更新可用 (v11.2)"

# ==========================================
# 3. App 標頭與使用者設定
# ==========================================
st.title("Tesla Guardian")
st.markdown("歡迎回來，**Model Y 車主**")

# 使用側邊欄當作 App 的設定選單
st.sidebar.title("車輛設定")
st.sidebar.markdown("車牌：`ABC-1234`")
st.sidebar.markdown("當前里程：`24,500 km`")
current_region = st.sidebar.selectbox("當前所在區域", df_charge['Region'].tolist())

st.divider()

# ==========================================
# 4. 核心功能分頁 (Tabs)
# ==========================================
tab1, tab2, tab3 = st.tabs(["安全診斷", "智慧充電", "服務中心"])

# --- 分頁一：安全診斷 (直擊電子門把與低壓電池痛點) ---
with tab1:
    st.subheader("車輛健康狀態監測")
    
    # 模擬 12V 低壓電池預警系統
    health = st.session_state.battery_12v_health
    
    if health <= 20:
        st.error(f"嚴重警告：12V 低壓電池健康度極低 ({health}%)！")
        st.warning("為避免電子門把斷電卡死，系統已強制解除車門電子鎖定。請立即預約進廠更換低壓電池。")
        
        # 應急教學 (呼應報告建議的物理備援)
        with st.expander("緊急狀況：如何使用物理機械門把開門？", expanded=True):
            st.write("1. 在車門把手前方（靠近車窗開關處）尋找機械釋放撥塊。")
            st.write("2. 用力向上拉起撥塊，即可在全車斷電狀態下開啟車門。")
            st.button("立即呼叫道路救援", type="primary")
    else:
        st.success(f"12V 低壓電池狀態良好 (健康度: {health}%)")
        st.info("電子門把與車載系統供電正常。")
        
    st.divider()
    col1, col2 = st.columns(2)
    col1.metric("主電池剩餘電量", "68%", "-2%")
    col2.metric("胎壓狀態", "正常", "38 PSI")

# --- 分頁二：智慧充電 (呼應區域設施數據) ---
with tab2:
    st.subheader("區域充電站導航")
    
    # 根據使用者所在區域，提供不同的數據洞察
    region_info = df_charge[df_charge['Region'] == current_region].iloc[0]
    stations = region_info['Charging_Stations']
    
    st.markdown(f"您當前位於 **{current_region}**，該區共有約 **{stations/1e6:.1f} 百萬** 座充電站。")
    
    if current_region in ['Middle East', 'Europe']:
        st.success("該區充電基礎設施極為密集，無須擔心續航焦慮。")
    else:
        st.warning("該區充電站密度適中，建議長途旅行前預先規劃超充站路線。")
        
    destination = st.text_input("輸入目的地以規劃充電路線：", placeholder="例如：台北101")
    if st.button("開始規劃"):
        with st.spinner('正在計算最佳超充站路線...'):
            time.sleep(1.5)
            st.toast("路線規劃完成！已傳送至車載導航。")

# --- 分頁三：服務中心 (CRM 與 OTA 危機處理) ---
with tab3:
    st.subheader("遠端更新與客戶服務")
    
    st.info(f"OTA 狀態：{st.session_state.ota_status}")
    
    st.write("本次更新 (v11.2) 包含：")
    st.write("- 升級低壓電池健康度高頻監測演算法。")
    st.write("- 優化極端環境下的車門解鎖邏輯。")
    
    if st.button("立即執行 OTA 更新"):
        st.session_state.ota_status = "系統已是最新版本 (v11.2)"
        st.toast("更新安裝中，請勿發動車輛...")
        st.rerun() # 重新載入畫面更新狀態
        
    st.divider()
    st.write("需要協助嗎？")
    col_a, col_b = st.columns(2)
    col_a.button("線上文字客服")
    col_b.button("預約進廠維修")

st.markdown("---")
st.caption("Tesla Guardian App - B2C Customer Relationship Management Demo")