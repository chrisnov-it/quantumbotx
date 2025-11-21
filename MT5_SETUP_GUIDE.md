/** eslint-disable markdown/fenced-code-language */
# 🚀 QuantumBotX MT5 Integration Guide

> **Get Historical Market Data for Advanced Backtesting**

## 📋 Prerequisites

**Required Software:**
- ✅ [MetaTrader 5 Platform](https://www.metatrader5.com/en/download) (Latest version)
- ✅ Python 3.8+ (Already included with QuantumBotX)
- ✅ Active MT5 Demo or Live Account

---

## ⚡ Quick Setup (3 Steps)

### Step 1: Install MT5 Platform
```text
1. Download MT5 from: https://www.metatrader5.com/en/download
2. Install in default location: C:\Program Files\MetaTrader 5
3. Launch MT5 and login to your account (demo recommended)
4. Keep MT5 running in background for data downloads
```

### Step 2: Configure QuantumBotX Settings
```bash
# Copy and edit your .env file
cp .env.example .env

# Edit .env with your MT5 credentials:
MT5_LOGIN=12345678      # Your MT5 account number
MT5_PASSWORD=YourPass    # Your MT5 password
MT5_SERVER=FBS-Demo     # Your broker server
```

### Step 3: Install MT5 Python Library
**Windows Command:**
```bash
# Open Command Prompt as Administrator
pip install MetaTrader5

# Alternative (from Requirements):
pip install -r requirements.txt
```

---

## 🔧 Manual MT5 Library Installation

If standard installation fails:

### Method A: Wheel File (Recommended)
```bash
# Download the wheel file manually
pip install MetaTrader5-5.0.45-cp38-cp38-win_amd64.whl

# Or download from: https://pypi.org/project/MetaTrader5/#files
```

### Method B: Conda Environment
```bash
# Create dedicated environment
conda create -n qb_mt5 python=3.9
conda activate qb_mt5

# Install MT5
conda install MetaTrader5 -c conda-forge
```

---

## 🌐 Supported Brokers

**Pre-configured for:**
- ✅ FBS Markets (FBS-Demo)
- ✅ XM Global (XMGlobal-Real/live server names)
- ✅ IC Markets (ICMarkets-Demo)
- ✅ Pepperstone (Pepperstone-Demo)

**For other brokers:**
```env
# Add to your .env file:
MT5_SERVER=YourBroker-ServerName
```

---

## 🗂️ Data Download Features

### Automatic Symbol Detection
- **Forex:** EURUSD, GBPUSD, AUDUSD, JPY pairs, etc.
- **Gold:** XAUUSD (ultra-conservative risk management)
- **Indices:** US30, US100, US500 (S&P 500, Dow Jones)
- **Commodities:** Oil, Natural Gas
- **Crypto:** BTCUSD, ETHUSD (if supported)
- **Exotic Pairs:** Currency pairs not in default list

### What Gets Downloaded
- ✅ OHLCV data (Open, High, Low, Close, Volume)
- ✅ Multiple timeframes (H1 recommended for backtesting)
- ✅ Last 4+ years of historical data
- ✅ Automatic broker symbol aliasing
- ✅ Indonesian market focus (USDIDR)
- ✅ European indices (DE30, UK100)

---

## 🚦 Testing Your Setup

### Test 1: MT5 Connection
```bash
# Run the download script directly
python lab/download_data.py
```
**Expected Output:**
```text
✅ Successfully connected to MT5
📡 Server: FBS-Demo
👤 Account: 12345678
💰 Balance: $10,000.00

📊 Downloading data from 2020-01-01 to 2025-09-24
📊 Downloading EURUSD data...
✅ EURUSD: 15000 bars saved to lab/backtest_data/EURUSD_H1_data.csv
```

### Test 2: Web Interface
```text
1. Start QuantumBotX: python run.py
2. Open: http://localhost:5000/backtest
3. Click: "Download Data MT5" button
4. Should show: "Downloaded X files successfully"
```

---

## 🐛 Troubleshooting

### Error: "MetaTrader5 module not found"
```bash
# Windows installation fix
pip uninstall MetaTrader5
pip install --no-cache-dir MetaTrader5

# Or use specific wheel:
pip install MetaTrader5-5.0.34-cp39-cp39-win_amd64.whl
```

### Error: "Failed to initialize MT5"
```text
✅ Check MT5 is running
✅ Verify account credentials in .env
✅ Try Demo account first
✅ Check broker server name matches exactly
```

### Error: "Symbol not found"
```text
✅ MT5 shows: "Enable Auto Trading" in algo settings
✅ Check if symbol is visible in MT5 Market Watch
✅ Some symbols need manual activation in MT5
✅ Broker may not offer certain instruments
```

### Error: "Download timed out"
```text
✅ Reduce download period in script if needed
✅ Check internet connection stability
✅ Some brokers are faster than others
✅ Account may have download rate limits
```

---

## 🔄 Advanced Configuration

### Custom Symbol List
Add to your `.env` file:
```env
CUSTOM_MT5_SYMBOLS=GBPAUD,NZDCAD,USDMXN,HK50,AUS200
```

### Proxy Settings (if needed)
```env
MT5_PROXY_HOST=your.proxy.host
MT5_PROXY_PORT=8080
MT5_PROXY_USER=username
MT5_PROXY_PASS=password
```

### Log Level Control
```env
BACKTEST_LOG_LEVEL=DEBUG  # For troubleshooting
```

---

## 📊 Data Quality Verification

After download, check your CSV files:
```python
import pandas as pd
df = pd.read_csv('lab/backtest_data/EURUSD_H1_data.csv')
print(f"Rows: {len(df)}")
print(f"Date range: {df['time'].min()} to {df['time'].max()}")
print(f"Latest close: {df['close'].iloc[-1]}")
```

**Expected Output:**
```text
Rows: 15800+ (4+ years of H1 data)
Date range: 2020-01-01 to current_date
Latest close: matches MT5 current price
```

---

## 🎯 Next Steps After Setup

1. **Run Initial Downloads:** Get historical data for major symbols
2. **Test Backtesting:** Upload CSV files and test strategies
3. **Create Bots:** Use analysis features with real data
4. **Monitor Performance:** Track equity curves and metrics

---

## 📞 Support

**Common Issues:**
- MT5 needs to remain logged in during downloads
- Some brokers require manual symbol activation
- Demo accounts sometimes have download limits
- VPN may be needed for some broker connections

**Help Resources:**
- MT5 Official Documentation: https://www.metatrader5.com
- QuantumBotX Issue Tracker: Check GitHub issues
- Community: Join Discord/Telegram for support

---

*Happy Trading! 🎯📈*
