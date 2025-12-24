# 🤖 QuantumBotX — AI-Powered Modular Trading Bot for MT5

Welcome to **QuantumBotX**, your personal, modular, and smart trading assistant built with Python and MetaTrader5 (MT5).

---

## 🚀 Quick Start with MT5 Integration

**New to QuantumBotX?** Follow these 3 simple steps:

### ⚡ Step 1: Install MT5 Integration

```bash
# Automatically detect, install, and configure MT5
python install_mt5_integration.py

# This will:
# ✅ Check Python compatibility
# ✅ Install MetaTrader5 library
# ✅ Verify MT5 platform installation
# ✅ Create .env configuration template
# ✅ Generate connection test script
```

### 🏦 Step 2: Setup MT5 Platform

```bash
# 1. Download MT5 from: https://www.metatrader5.com/en/download
# 2. Install with default settings
# 3. Launch MT5 and create/login to demo account
# 4. Keep MT5 running - it's required for data downloads
```

### ⚙️ Step 3: Configure & Test

```bash
# Edit your .env file with MT5 credentials:
# MT5_LOGIN=your_account_number
# MT5_PASSWORD=your_password
# MT5_SERVER=FBS-Demo

# Test your MT5 connection:
python test_mt5_connection.py

# Download market data (or use web interface):
python lab/download_data.py

# Start trading interface:
python run.py
```

### ❓ Need Help?

- 📖 **Full Guide**: Check `MT5_SETUP_GUIDE.md`
- 🧪 **Quick Test**: `python test_mt5_connection.py`
- 🔧 **Manual Config**: Edit `.env` file directly

---

## 🎯 Key Features

### 📊 **Professional Backtesting**

- **MT5 Data Integration**: Download 50+ instruments directly from brokers
- **Realistic Modeling**: Spread, slippage, and commission simulation
- **Strategy Testing**: 16+ strategies with custom parameters
- **Performance Analytics**: Equity curves, drawdown analysis, risk metrics

### 🧠 **Smart Bot Management**

- **Real-Time Monitoring**: Live bot status with auto-refresh
- **Risk Protection**: Ultra-safe position sizing, especially for gold/XAUUSD
- **Strategy Switching**: Automated strategy adaptation to market conditions
- **Multi-Broker Support**: XM Global, FBS, Exness, IC Markets, Pepperstone

### 🔍 **Market Analysis**

- **Live Data Analysis**: Real-time signals from MT5 market data
- **Multi-Timeframe**: Daily, H1, M15 analysis for comprehensive signals
- **Holiday Detection**: Automatic Christmas/Ramadan mode activation
- **AI Mentor**: Personalized trading guidance in Indonesian

### 🔐 **Safety First**

- **Conservative Defaults**: Beginner-safe settings out of the box
- **Account Protection**: Emergency brakes and risk limits
- **Testing Mode**: Demo account support before live trading
- **Clean Architecture**: Modular design for reliability

---

## 🗂️ Data Download Features

### Available Instruments

- **Forex**: EURUSD, GBPUSD, AUDUSD, JPY pairs, major crosses
- **Gold**: XAUUSD with ultra-conservative risk management
- **Indices**: US30, US100, US500 (S&P 500), DE30, UK100
- **Commodities**: Oil (USOIL, UKOIL), Natural Gas
- **Crypto**: BTCUSD, ETHUSD (if supported by broker)
- **Exotic Pairs**: Currency pairs for advanced traders

### Data Quality

- ✅ **4+ Years** of historical data
- ✅ **OHLCV Format**: Open, High, Low, Close, Volume
- ✅ **Broker Aliasing**: Automatic XAUUSD/USDIDR variant detection
- ✅ **Timeframes**: H1 (recommended), M1, M5, M15, H4, D1

### Download Methods

1. **Web Interface**: Click "Download Data MT5" button on backtesting page
2. **Command Line**: `python lab/download_data.py`
3. **Automatic Installer**: `python install_mt5_integration.py`

---

## 🧪 Technical Stack

- **Python 3.10+** with async capabilities
- **Flask** web framework with real-time updates
- **MetaTrader5** direct broker integration
- **pandas-ta** for technical analysis
- **Chart.js** for interactive visualizations
- **SQLite** with migration support

---

## 🧠 AI Mentor Features

- **Indonesian Language**: Guidance in Bahasa Indonesia
- **Emotional Intelligence**: Understanding trader psychology
- **Performance Analysis**: Trade pattern recognition
- **Risk Assessment**: Personalized risk tolerance evaluation
- **Strategy Recommendations**: Matching strategies to trader level
- **Motivational Support**: Contextual encouragement

---

## 📚 Educational Framework

### Beginner Path (Month 1)

- **Week 1**: MA Crossover on EURUSD
- **Week 2**: Bollinger Bands for range trading
- **Week 3**: Basic risk management practices
- **Week 4**: Understanding ATR-based position sizing

### Intermediate Path (Month 2-3)

- **Strategy Rotation**: Multiple approaches per market
- **Parameter Optimization**: Finding edge through testing
- **Market Analysis**: Understanding different market regimes
- **Risk Scaling**: Position sizing based on confidence

### Advanced Mastery (Month 4+)

- **Strategy Combination**: Multi-strategy portfolios
- **Market Timing**: When to trade what
- **Risk Management**: Advanced portfolio protection
- **Psychology**: Maintaining discipline

---

## ⚠️ Important Disclaimers

**Trading Risks:**

- FX trading involves substantial risk and may not be suitable for all
- High leverage can amplify losses
- Past performance ≠ future results
- Never trade with money you can't afford to lose

**Software Usage:**

- For educational/research purposes
- Test thoroughly on demo accounts first
- Creator not responsible for trading losses
- Use at your own risk

---

## 🤝 Support & Community

- **Documentation**: Full setup guides in `/docs`
- **Issues**: GitHub Issues for bugs/features
- **Discussions**: Community support forum
- **Updates**: Check changelog for improvements

---

## 📈 What's Next?

### Current Features ✅

- ✅ MT5 Integration with 50+ instruments
- ✅ 16 Trading strategies with risk management
- ✅ AI mentor in Indonesian
- ✅ Professional backtesting engine
- ✅ Holiday-aware trading modes
- ✅ Ultra-conservative gold/XAUUSD protection

### Coming Soon 🚧

- 🔄 Telegram notifications
- 🔄 Advanced portfolio analytics
- 🔄 Multi-broker arbitrage
- 🔄 Custom strategy builder
- 🔄 Community marketplace

---

## ☕ Support Development

Enjoy QuantumBotX? Consider supporting future development:

[img src="https://www.paypalobjects.com/en_US/i/btn/btn_donate_SM.gif" alt="Donate with PayPal"](https://www.paypal.com/paypalme/rebarakaz)

---

Happy Trading! 🎯📊🏆
