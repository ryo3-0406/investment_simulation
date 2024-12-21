import streamlit as st
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import plotly.graph_objects as go

# Streamlitでの入力フォーム
st.title("NISA iDeCo 年利シミュレーション")
st.sidebar.header("シミュレーション設定")

# デフォルト値
initial_investment = st.sidebar.number_input("初期投資額（円）", value=0, step=10000)
monthly_investment = st.sidebar.number_input("毎月の積立額（円）", value=5000, step=1000)
years = st.sidebar.number_input("運用期間（年）", value=35, step=1)
annual_rate_mean = st.sidebar.slider("平均年利 (%)", min_value=0.0, max_value=20.0, value=8.0, step=0.1) / 100
annual_rate_std = st.sidebar.slider("年利の標準偏差 (%)", min_value=0.0, max_value=20.0, value=4.0, step=0.1) / 100
n_sims = st.sidebar.number_input("シミュレーション回数", value=500, step=50)
start_date = st.sidebar.date_input("開始年月", value=datetime(2025, 1, 1))

# 計算用変数
months = int(years * 12)
monthly_rate_mean = (1 + annual_rate_mean) ** (1 / 12) - 1
monthly_rate_std = annual_rate_std / np.sqrt(12)

# 開始日付をdatetime型に変換
dates = [start_date + timedelta(days=30 * i) for i in range(months)]

# シミュレーション実行
results = []
for _ in range(n_sims):
    balance = initial_investment
    balances = []
    for month in range(months):
        monthly_rate = np.random.normal(monthly_rate_mean, monthly_rate_std)
        balance = balance * (1 + monthly_rate) + monthly_investment
        balances.append(balance)
    results.append(balances)

# 結果をデータフレームに変換
results_df = pd.DataFrame(results).T

# 元金の計算
principal = [(initial_investment + monthly_investment * month) for month in range(1, months + 1)]

# 単位変換をしない（純粋な日本円表示）
mean_series = results_df.mean(axis=1)
std_series = results_df.std(axis=1)

# Plotlyによるインタラクティブグラフ
fig = go.Figure()

# 個別シミュレーションをプロット
for i in range(n_sims):
    fig.add_trace(go.Scatter(
        x=dates, y=results_df[i], mode='lines', line=dict(color='blue', width=0.5), opacity=0.1, showlegend=False
    ))

# 平均値をプロット
fig.add_trace(go.Scatter(
    x=dates, y=mean_series, mode='lines', name="シミュレーション平均",
    line=dict(color='red', width=3)
))

# 標準偏差を範囲としてプロット
fig.add_trace(go.Scatter(
    x=dates, y=mean_series + std_series, mode='lines', name="標準偏差上限",
    line=dict(color='red', width=1, dash='dot'), showlegend=False
))
fig.add_trace(go.Scatter(
    x=dates, y=mean_series - std_series, mode='lines', name="標準偏差下限",
    line=dict(color='red', width=1, dash='dot'), showlegend=False, fill='tonexty', fillcolor='rgba(255, 0, 0, 0.2)'
))

# 元金をプロット
fig.add_trace(go.Scatter(
    x=dates, y=principal, mode='lines', name="元金の単純積み上げ",
    line=dict(color='green', width=2, dash='dash')
))

# グラフレイアウトのカスタマイズ
fig.update_layout(
    title="シミュレーション結果",
    xaxis_title="年月",
    yaxis_title="金額（円）",
    title_font=dict(size=24),
    xaxis=dict(
        tickformat="%Y-%m",
        tickangle=45,
        showgrid=True,
        gridcolor="rgba(200, 200, 200, 0.3)"
    ),
    yaxis=dict(
        showgrid=True,
        gridcolor="rgba(200, 200, 200, 0.3)",
        tickformat=",.0f",  # 金額をシンプルな数値に
        title_font=dict(size=16),  # 軸ラベルのフォントサイズ
        tickfont=dict(size=14)  # 目盛りラベルのフォントサイズ
    ),
    legend=dict(
        orientation="h", yanchor="bottom", y=-0.3, xanchor="center", x=0.5,
        bgcolor="rgba(255,255,255,0.8)"
    ),
    template="plotly_white",
    height=700,
    margin=dict(l=20, r=20, t=50, b=50)  # マージン調整
)

# グラフをStreamlitで表示
st.plotly_chart(fig, use_container_width=True)

# 結果の統計
final_balances = results_df.iloc[-1]
mean_balance = final_balances.mean()
std_balance = final_balances.std()
median_balance = final_balances.median()

def format_currency(value):

    return f"{int(value):,} 円"


# 表示部分
st.write(f"平均最終残高: {format_currency(mean_balance)}")
st.write(f"元金積み上げ最終結果: {format_currency(principal[-1])}")
st.write(f"標準偏差: {format_currency(std_balance)}")
st.write(f"中央値: {format_currency(median_balance)}")
