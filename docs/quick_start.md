# 🚀 QuantumBotX Quick Start Guide

Get up and running with QuantumBotX in under 10 minutes!

## 📋 Before You Begin

**Requirements:**
- Windows computer (MT5 requirement)
- MetaTrader 5 terminal installed and running
- Python 3.10 or later
- MT5 account (demo is fine to start)

## ⏱️ 5-Minute Setup

### Step 1: Download QuantumBotX
```bash
git clone https://github.com/rebarakaz/quantumbotx.git
cd quantumbotx
```

### Step 2: Set Up Python Environment
```bash
python -m venv venv
# Windows:
.\venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Configure MT5 Connection
```bash
cp .env.example .env
```

Edit `.env` with your MT5 credentials:
```
MT5_LOGIN=your_account_number
MT5_PASSWORD=your_password
MT5_SERVER=your_broker_server
```

### Step 5: Start QuantumBotX
```bash
python run.py
```

## 🌐 Access the Dashboard

Open your web browser and go to:
```
http://127.0.0.1:5000
```

## 🤖 Create Your First Bot (3 Minutes)

### 1. Navigate to Trading Bots
Click "Trading Bots" in the left sidebar

### 2. Click "Buat Bot Baru"
Fill in these beginner settings:

**Basic Info:**
- **Nama Bot**: My First Bot
- **Pasar**: EURUSD (or any pair you want to trade)
- **Risk per Trade**: 1.0 (%)
- **SL (ATR Multiplier)**: 2.0
- **TP (ATR Multiplier)**: 4.0
- **Timeframe**: H1
- **Interval Cek**: 60

**Strategy Settings:**
- **Strategi**: MA_CROSSOVER
- **Fast Period**: 10
- **Slow Period**: 30

### 3. Click "Buat Bot"

### 4. Start Your Bot
Click the "▶️ Start" button next to your new bot

## 📊 Monitor Your Bot

### Dashboard View
- Check your bot status on the main dashboard
- View real-time performance metrics
- Monitor active trades

### Trade History
- Go to "History" to see all executed trades
- Review profit/loss for each trade

## 🧪 Quick Backtesting (Optional)

Before going live, you can test your strategy with historical data:

### Get Historical Data
1. Ensure MT5 terminal is running and you're logged in
2. Run the data download script:
   ```bash
   python lab/download_data.py
   ```
   
This will download data for popular symbols to `lab/backtest_data/`

### Run a Backtest
1. Go to "Backtester" in the dashboard
2. Select "MA_CROSSOVER" strategy
3. Choose "EURUSD" market
4. Click "Run Backtest"
5. Review results before live trading

## 🎯 Success Tips

### First Week Goals
1. **Observe Only**: Let your bot run for a week without interference
2. **Learn the Interface**: Familiarize yourself with all dashboard features
3. **Check Daily**: Review performance each day
4. **Ask AI Mentor**: Use the AI Mentor for questions and explanations

### Common Beginner Mistakes
- ❌ Changing settings too frequently
- ❌ Running too many bots at once
- ❌ Not using stop losses
- ❌ Trading live without demo experience

### Best Practices
- ✅ Start with demo account
- ✅ Use micro lots (0.01)
- ✅ Monitor bots daily
- ✅ Keep a simple trading journal
- ✅ Follow the progressive learning path
- ✅ Test strategies with backtesting first

## 🆘 Need Help?

### Quick Troubleshooting
1. **MT5 Connection Issues**: Ensure MT5 terminal is running
2. **Login Problems**: Verify credentials in `.env` file
3. **Bot Not Trading**: Check if market is open and bot is started
4. **Performance Concerns**: Use backtester before going live

### Getting More Help
- **AI Mentor**: Click the AI button on dashboard for instant help
- **Documentation**: Check `docs/` folder for detailed guides
- **Strategy Explanations**: Every parameter has plain English descriptions

## 🎉 Next Steps

After your first week:
1. **Run Backtest**: Test your strategy with historical data
2. **Try Different Markets**: Experiment with GBPUSD or XAUUSD
3. **Explore Other Strategies**: Try RSI_CROSSOVER next
4. **Join Learning Path**: Follow the structured 3-month curriculum

## 🛡️ Important Reminders

- **Demo First**: Always demo trade for at least 30 days
- **Small Risk**: Never risk more than 2% per trade
- **Stop Losses**: Always use stop losses
- **Emotional Control**: Treat demo like real money
- **Continuous Learning**: Use AI Mentor regularly

---

**Congratulations!** You've successfully set up and started your first trading bot. Remember, successful trading is about consistency and risk management, not huge profits. Take your time to learn the system and build good habits.