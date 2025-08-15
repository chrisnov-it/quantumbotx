# 🤖 QuantumBotX — AI-Powered Modular Trading Bot for MT5

!MIT License
!Python Version
!Framework
!Made with Love

Welcome to **QuantumBotX**, your personal, modular, and smart trading assistant built with Python and MetaTrader5 (MT5).
Designed to be elegant, powerful, and flexible — whether you're a scalper, swing trader, or a strategy researcher.

---

## 🚀 Features

- ✅ **Modular Strategy System**: Easily create and plug in your own trading strategies.
- ✅ **Comprehensive Backtester**: Test your strategies against historical data with detailed performance metrics and visualizations.
- ✅ **Real-Time Analysis**: Live dashboard with data visualization using Chart.js.
- ✅ **Adaptive Logic**: Comes with a Hybrid strategy that adapts to trending or ranging markets.
- ✅ **Automated Trading**: Full position handling (entry, exit, SL, TP) using bot-specific magic numbers.
- ✅ **Persistent Logging**: All activities and trades are logged to a local SQLite database.
- ✅ **Modern Web UI**: Clean and responsive dashboard built with Flask and TailwindCSS.
- ✅ **Multi-Timeframe Support**: Analyze and trade on any standard timeframe from M1 to D1.
- ✅ **Live/Demo Ready**: Tested and ready for both demo and live trading accounts.

---

## 📦 Tech Stack

- `Python 3.10+`
- `Flask` & `TailwindCSS`
- `MetaTrader5` Python Integration
- `pandas` & `pandas-ta` for data analysis
- `Chart.js` for data visualization
- `SQLite` for database

---

## 🧠 Strategy Examples

| Strategy | Description | Best For |
|---|---|---|
| `Moving Average Crossover` | Classic Golden/Death Cross. | Trending markets (e.g., Indices, XAUUSD). |
| `Bollinger Bands Reversion` | Mean reversion based on price touching the bands. | Ranging/Volatile markets (e.g., EURUSD). |
| `QuantumBotX Hybrid` | Adaptive strategy using ADX to switch between MA Crossover and Bollinger Bands. | All-weather performance. |

---

## 📈 Roadmap

- [ ] **Advanced Strategy**: `MACD_STOCH_FILTER` for more precise, filtered entries.
- [ ] **Telegram Notifications**: Get real-time alerts for trades and errors.
- [ ] **Portfolio Analytics**: Deeper insights into your trading performance.

---

## 🔐 Environment Variables (`.env`)

Rename `.env.example` to `.env`, and fill in the following:

```env
MT5_LOGIN="your_mt5_login"
MT5_PASSWORD="your_password"
MT5_SERVER="your_broker_server"
SECRET_KEY="any_flask_secret_key"
DB_NAME=bots.db
```

> **Note:** The API keys for Alpha Vantage, CMC, and Finnhub are deprecated and can be ignored.

---

## 🧪 Local Setup (Dev Mode)

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/rebarakaz/quantumbotx.git
    cd quantumbotx
    ```
2.  **Set up Python virtual environment:**
    ```bash
    python -m venv venv
    # On Windows
    .\venv\Scripts\activate
    # On macOS/Linux
    source venv/bin/activate
    ```
3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
4.  **Configure your environment:**
    ```bash
    cp .env.example .env
    # Now, edit the .env file with your MT5 credentials
    ```
5.  **Run the application:**
    ```bash

    python run.py
    ```

> **Important:** You must have the MetaTrader 5 terminal installed and running on the same machine.

---

## ⚠️ Disclaimer

Trading foreign exchange on margin carries a high level of risk and may not be suitable for all investors. The high degree of leverage can work against you as well as for you. Before deciding to trade, you should carefully consider your investment objectives, level of experience, and risk appetite.

This software is provided "as is" for educational and research purposes. The author is not responsible for any financial losses incurred from using this bot. **Always test thoroughly on a demo account before using on a live account.**

---

## 📈 Screenshot

![QuantumBotX Dashboard Preview](static/img/dashboard-preview.png)

---

## 🧠 Author

Developed with 💖 by **Chrisnov IT Solutions**
Concept, Logic & Execution: `@reynov` aka BabyDev

---

## ☕ Support This Project

If you like this project, give it a ⭐ on GitHub, or buy me a coffee to support future versions:

[<img src="https://www.paypalobjects.com/en_US/i/btn/btn_donate_SM.gif" alt="Donate with PayPal" />](https://www.paypal.com/paypalme/rebarakaz)

---

## 📝 License

This project is licensed under the MIT License - see the LICENSE.md file for details.
