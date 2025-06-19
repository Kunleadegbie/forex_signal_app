
### 📄 `app.py` (Streamlit-Ready & Secure Secrets Usage)

import streamlit as st
import pandas as pd
import requests
from ta.momentum import RSIIndicator
from ta.trend import MACD, SMAIndicator, EMAIndicator
from ta.volatility import BollingerBands
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Fetch secrets from Streamlit Cloud / local secrets.toml
API_KEY = st.secrets["API_KEY"]
EMAIL_USERNAME = st.secrets["EMAIL_USERNAME"]
EMAIL_PASSWORD = st.secrets["EMAIL_PASSWORD"]
EMAIL_SUBSCRIBER = st.secrets["EMAIL_SUBSCRIBER"]

# Constants
API_URL = f"https://api.twelvedata.com/time_series?symbol=EUR/USD&interval=1min&apikey={API_KEY}"
CURRENCY_PAIR = "EUR/USD"
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

def fetch_forex_data():
    try:
        response = requests.get(API_URL)
        data = response.json()

        # Check for API errors
        if "values" not in data:
            st.error(f"API Error: {data.get('message', 'No values found.')}")
            return None

        # Create DataFrame from values
        df = pd.DataFrame(data["values"])
        df["close"] = df["close"].astype(float)
        df["datetime"] = pd.to_datetime(df["datetime"])
        df = df.sort_values("datetime")

        return df

    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return None

def calculate_indicators(data):
    indicators = {}
    indicators["RSI"] = RSIIndicator(data["close"]).rsi()
    indicators["MACD"] = MACD(data["close"]).macd()
    bb = BollingerBands(data["close"])
    indicators["Bollinger High"] = bb.bollinger_hband()
    indicators["Bollinger Low"] = bb.bollinger_lband()
    indicators["SMA 20"] = SMAIndicator(data["close"], window=20).sma_indicator()
    indicators["EMA 20"] = EMAIndicator(data["close"], window=20).ema_indicator()
    return indicators

def analyze_signals(data, indicators):
    latest_close = data["close"].iloc[-1]
    signals = []

    rsi = indicators["RSI"].iloc[-1]
    signals.append("RSI indicates BUY" if rsi < 30 else "RSI indicates SELL" if rsi > 70 else "RSI neutral")

    macd = indicators["MACD"].iloc[-1]
    signals.append("MACD indicates BUY" if macd > 0 else "MACD indicates SELL")

    upper_band = indicators["Bollinger High"].iloc[-1]
    lower_band = indicators["Bollinger Low"].iloc[-1]
    signals.append("Price below Bollinger Bands: BUY" if latest_close < lower_band else "Price above Bollinger Bands: SELL" if latest_close > upper_band else "Price within Bollinger Bands")

    # Determine overall recommendation
    if any("BUY" in s for s in signals):
        trade_decision = "BUY"
    elif any("SELL" in s for s in signals):
        trade_decision = "SELL"
    else:
        trade_decision = "HOLD"

    return signals, trade_decision

def send_email(subject, body, recipient=EMAIL_SUBSCRIBER):
    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(EMAIL_USERNAME, EMAIL_PASSWORD)

        msg = MIMEMultipart()
        msg["From"] = EMAIL_USERNAME
        msg["To"] = recipient
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))
        server.sendmail(EMAIL_USERNAME, recipient, msg.as_string())
        server.quit()
        st.success(f"Trade signal sent to {recipient}!")
    except Exception as e:
        st.error(f"Failed to send email: {e}")

def main():
    st.title("📊 Forex Trading Signals - EUR/USD (via Twelve Data API)")
    st.sidebar.header("Trading Options")

    st.write("""
    Live forex trading signals for EUR/USD using RSI, MACD, Bollinger Bands, SMA, and EMA.
    Powered by **Twelve Data API**.
    """)

    num_points = st.sidebar.slider("Number of Data Points to Display", 10, 200, 100)

    st.subheader("📈 Live Forex Data (EUR/USD)")
    data = fetch_forex_data()
    if data is not None:
        st.dataframe(data[["datetime", "close"]].tail(num_points))

        indicators = calculate_indicators(data)
        signals, trade_decision = analyze_signals(data, indicators)

        st.subheader("📌 Trading Signals")
        for signal in signals:
            st.write(f"- {signal}")

        st.subheader("💡 Trade Recommendation")
        st.write(f"**{trade_decision}**")

        latest_close = data["close"].iloc[-1]

        # Set risk management levels based on trade decision
        if trade_decision == "BUY":
            take_profit = latest_close * 1.01
            stop_loss = latest_close * 0.99
        elif trade_decision == "SELL":
            take_profit = latest_close * 0.99
            stop_loss = latest_close * 1.01
        else:  # HOLD or unknown
            take_profit = latest_close
            stop_loss = latest_close

        st.subheader("🎯 Risk Management")
        st.write(f"Stop Loss: {stop_loss:.6f}")
        st.write(f"Take Profit: {take_profit:.6f}")

        email_subject = f"Forex Trade Alert - {trade_decision}"
        email_body = (
            f"Trade Signal: {trade_decision}\n"
            f"Latest Price: {latest_close}\n"
            f"Take Profit: {take_profit:.6f}\n"
            f"Stop Loss: {stop_loss:.6f}\n\n"
            f"Signals:\n" + "\n".join(signals)
        )
        send_email(email_subject, email_body)

    else:
        st.write("No data available at the moment.")

if __name__ == "__main__":
    main()
