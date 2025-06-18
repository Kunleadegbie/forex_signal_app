# Forex Signal App 📊📈

A Streamlit app for generating forex trading signals for the EUR/USD currency pair using technical indicators like RSI, MACD, Bollinger Bands, SMA, and EMA.

## 📦 Setup Instructions

1. Clone the repo:

2. Install dependencies:

3. Add a `.streamlit/secrets.toml` file with:
```toml
API_KEY = "your_api_key"
EMAIL_USERNAME = "your_email"
EMAIL_PASSWORD = "your_app_password"
EMAIL_SUBSCRIBER = "subscriber_email"

4. Run the app:

arduino
Copy
Edit
streamlit run app.py
📌 Notes
Secrets are managed securely via .streamlit/secrets.toml

Uses ta library for technical indicators

Sends trade signal alerts via Gmail SMTP

Built for Streamlit Cloud deployment




