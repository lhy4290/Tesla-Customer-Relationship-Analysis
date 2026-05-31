import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# ==========================================
# 解決「豆腐塊」中文亂碼的關鍵設定
# ==========================================
# 設定支援中文的字體 (Windows 預設為微軟正黑體)
# 如果你是用 Mac，請將 'Microsoft JhengHei' 改成 'PingFang TC' 或 'Arial Unicode MS'
plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei'] 
plt.rcParams['axes.unicode_minus'] = False # 確保圖表中的負號能正常顯示
# ==========================================

# 1. 網頁基本設定 (必須放在腳本最前面)
st.set_page_config(
    page_title="Tesla 市場情報",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. 載入資料並使用快取 (提升網頁載入速度)
@st.cache_data
def load_data():
    df = pd.read_csv('tesla_deliveries_dataset_2015_2025.csv')
    return df

df = load_data()

# 3. 側邊欄設計 (Filters)
st.sidebar.title("控制面板")
st.sidebar.markdown("請選擇您要分析的維度：")

# 建立年份滑桿
min_year, max_year = int(df['Year'].min()), int(df['Year'].max())
selected_years = st.sidebar.slider("選擇年份區間", min_year, max_year, (min_year, max_year))

# 建立車型多選框
models = df['Model'].unique().tolist()
selected_models = st.sidebar.multiselect("選擇車型", models, default=models)

# 4. 根據側邊欄選擇過濾數據
filtered_df = df[
    (df['Year'] >= selected_years[0]) & 
    (df['Year'] <= selected_years[1]) &
    (df['Model'].isin(selected_models))
]

# 5. 主畫面標題與商業洞察
st.title("Tesla 產銷與市場情報")
st.markdown("提供管理層即時監控全球供應鏈效率、定價策略與基礎設施發展狀況。")

# 6. 核心 KPI 區塊
st.subheader("核心營運指標 (KPI)")
col1, col2, col3 = st.columns(3)

total_deliveries = filtered_df['Estimated_Deliveries'].sum()
total_production = filtered_df['Production_Units'].sum()
avg_price = filtered_df['Avg_Price_USD'].mean()
delivery_rate = (total_deliveries / total_production) * 100 if total_production > 0 else 0

col1.metric("總交車量 (輛)", f"{total_deliveries:,.0f}")
col2.metric("平均產銷匹配率", f"{delivery_rate:.1f}%")
col3.metric("平均售價 (USD)", f"${avg_price:,.0f}")

st.divider() # 分隔線

# 7. 視覺化圖表區
# 統一設定深色主題風格，搭配 Streamlit 黑底
custom_dark_params = {
    "axes.facecolor": "#0e1117", "figure.facecolor": "#0e1117",
    "text.color": "#fafafa", "axes.labelcolor": "#fafafa",
    "xtick.color": "#fafafa", "ytick.color": "#fafafa",
    "grid.color": "#333333"
}
sns.set_theme(style="darkgrid", rc=custom_dark_params)

# --- 圖表一：產銷走勢圖 (全寬) ---
st.subheader("全球產銷規模與效率走勢")
yearly_data = filtered_df.groupby('Year')[['Production_Units', 'Estimated_Deliveries']].sum().reset_index()

fig_trend, ax1 = plt.subplots(figsize=(12, 4))
ax1.plot(yearly_data['Year'], yearly_data['Production_Units'] / 1e6, marker='o', color='#4ca3dd', label='Production volume (millions)')
ax1.plot(yearly_data['Year'], yearly_data['Estimated_Deliveries'] / 1e6, marker='s', color='#ff9e42', label='Estimated Deliveries (millions)')
ax1.set_ylabel('Quantity (Millions)')
ax1.set_xlabel('Year')
ax1.legend(loc='upper left', facecolor='#262730', labelcolor='white')

# 修正：移除 theme=None
st.pyplot(fig_trend, use_container_width=True)

st.divider() # 加一條分隔線讓版面更乾淨

# --- 圖表二與三：並排顯示 (區域市場 & 車型市佔) ---
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("區域市場基礎設施分析")
    region_data = filtered_df.groupby('Region')[['Estimated_Deliveries', 'Charging_Stations']].sum().reset_index()
    region_data = region_data.sort_values(by='Estimated_Deliveries', ascending=False)
    
    fig_region, ax_reg = plt.subplots(figsize=(6, 5))
    
    # 強制將畫布與圖表背景設定為「純白色」
    fig_region.patch.set_facecolor('#ffffff') 
    ax_reg.set_facecolor('#ffffff')           
    
    # 畫出長條圖
    sns.barplot(data=region_data, x='Region', y='Estimated_Deliveries', palette='Blues_r', ax=ax_reg)
    
    # 配合白底，強制將所有文字與刻度設定為「黑色」
    ax_reg.set_xlabel('Region', color='black', fontweight='bold', fontsize=12)
    ax_reg.set_ylabel('Total Deliveries', color='black', fontweight='bold', fontsize=12)
    ax_reg.tick_params(colors='black') 
    
    for spine in ax_reg.spines.values():
        spine.set_color('#333333')
        
    plt.tight_layout() 
    
    # 修正：移除 theme=None，並可直接傳入 facecolor='white' 確保白底
    st.pyplot(fig_region, use_container_width=True, facecolor='white') 

with col_right:
    st.subheader("產品線交付市佔率")
    model_share = filtered_df.groupby('Model')['Estimated_Deliveries'].sum().reset_index()
    
    fig_pie, ax_pie = plt.subplots(figsize=(6, 4))
    
    # 強制將畫布背景設定為「純白色」
    fig_pie.patch.set_facecolor('#ffffff')
    
    colors = sns.color_palette('pastel')[0:len(model_share)]
    
    wedges, texts, autotexts = ax_pie.pie(
        model_share['Estimated_Deliveries'], labels=model_share['Model'], 
        autopct='%1.1f%%', startangle=140, colors=colors, 
        pctdistance=0.77, 
        textprops={'color': 'black', 'fontsize': 11, 'fontweight': 'bold'} 
    )
    
    # 環狀圖中間的圓圈改回「純白色」
    centre_circle = plt.Circle((0,0), 0.55, fc='#ffffff')
    ax_pie.add_artist(centre_circle)
    
    for autotext in autotexts:
        autotext.set_color('#000000')      
        autotext.set_fontsize(12)          
        autotext.set_fontweight('bold')
        
    plt.tight_layout() 
    
    # 修正：移除 theme=None，並可直接傳入 facecolor='white' 確保白底
    st.pyplot(fig_pie, use_container_width=True, facecolor='white')

# 洞察文字區塊
col_cap1, col_cap2 = st.columns(2)
with col_cap1:
    st.info("💡 洞察：基礎設施(充電站)密集的區域，其交車量表現呈現高度正相關。")
with col_cap2:
    st.info("💡 洞察：核心車型呈現高度均勻的市佔分佈，展現健康的產品矩陣。")

st.markdown("---")
st.markdown("© 2026 數據分析實習專案 | 資料來源: Tesla Global Deliveries and Production Dataset")