# app.py

import streamlit as st
import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt

st.title("📈 Мій інвестиційний портфель")

uploaded = st.file_uploader("Завантаж CSV з портфелем", type="csv")
if uploaded is not None:
    df = pd.read_csv(uploaded)
    df["Ticker"] = df["Ticker"].str.strip().str.upper()

    st.subheader("Поточні ціни та вартість позицій")
    tickers = df["Ticker"].tolist()
    data = yf.download(tickers, period="1d", threads=True, progress=False)

    latest = data["Close"].iloc[-1]
    df["Current Price"] = df["Ticker"].map(latest)
    df["Current Value"] = df["Quantity"] * df["Current Price"]
    df["Invested"] = df["Quantity"] * df["Purchase Price"]
    df["PnL $"] = df["Current Value"] - df["Invested"]
    df["PnL %"] = df["PnL $"] / df["Invested"] * 100

    st.dataframe(df.style.format({
        "Current Price": "${:.2f}",
        "Current Value": "${:,.2f}",
        "Invested": "${:,.2f}",
        "PnL $": "${:,.2f}",
        "PnL %": "{:.2f}%"
    }))

    st.subheader("Динаміка вартості портфеля")
    invested_total = df["Invested"].sum()
    current_total = df["Current Value"].sum()
    pnl_total = current_total - invested_total
    pnl_pct = pnl_total / invested_total * 100

    col1, col2 = st.columns(2)
    col1.metric("Загальна інвестиція", f"${invested_total:,.2f}")
    col2.metric("Загальна KP", f"${current_total:,.2f}", f"{pnl_pct:.2f}%")

    # Графік
    fig, ax = plt.subplots()
    ax.bar(df["Ticker"], df["Current Value"], label="Current Value", color="green")
    ax.bar(df["Ticker"], df["Invested"], label="Invested", alpha=0.6)
    ax.set_ylabel("USD")
    ax.set_title("Порівняння: інвестовано vs поточна вартість")
    ax.legend()
    plt.xticks(rotation=45)
    st.pyplot(fig)

    st.subheader("Сповіщення")
    threshold = st.slider("Сповіщати, якщо зміна ± % від покупки перевищує:", 5, 100, 20)
    alerts = df[(df["PnL %"].abs() >= threshold)]
    if not alerts.empty:
        st.write("⚠️ Наступні позиції перевищили поріг:")
        st.table(alerts[["Ticker", "PnL %", "PnL $"]])
    else:
        st.write("Наразі жодного попередження.")
else:
    st.info("Завантаж CSV-файл з твоїм портфелем, щоб почати аналіз.")
