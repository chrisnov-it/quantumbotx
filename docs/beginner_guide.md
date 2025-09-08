# 🎓 QuantumBotX Beginner's Guide

Welcome to QuantumBotX, your personal AI-powered trading assistant! This guide will help you get started with the platform, understand its core concepts, and begin your journey toward automated trading success.

## 🚀 Getting Started

### What is QuantumBotX?
QuantumBotX is an intelligent, modular trading bot platform built for MetaTrader 5 (MT5). It combines professional trading strategies with beginner-friendly features, educational tools, and cultural awareness to create a comprehensive trading experience.

### Key Features for Beginners:
- 🎯 **Progressive Learning Path**: Structured learning from Week 1 to Month 3
- 📚 **Strategy Difficulty Ratings**: 2-12 complexity scale with automatic recommendations
- 🛡️ **Beginner Safeguards**: Parameter validation prevents dangerous settings
- 🎓 **Educational Framework**: Every setting explained in plain English
- 🤖 **ATR-Based Risk Management**: Automatic position sizing that adapts to market volatility

## 🛠️ Installation & Setup

### Prerequisites
1. **MetaTrader 5 Terminal**: Must be installed and running on your computer
2. **MT5 Account**: Demo or live account with your broker
3. **Python 3.10+**: Required for running the application

### Installation Steps
1. Clone the repository:
   ```bash
   git clone https://github.com/rebarakaz/quantumbotx.git
   cd quantumbotx
   ```

2. Create a Python virtual environment:
   ```bash
   python -m venv venv
   # On Windows
   .\venv\Scripts\activate
   # On macOS/Linux
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure your environment:
   ```bash
   cp .env.example .env
   # Edit the .env file with your MT5 credentials
   ```

5. Run the application:
   ```bash
   python run.py
   ```

## 🎮 Navigating the Dashboard

Once the application is running, open your web browser and go to `http://127.0.0.1:5000` to access the dashboard.

### Main Navigation
- **Dashboard**: Overview of your trading performance and statistics
- **Trading Bots**: Create, manage, and monitor your trading bots
- **Backtester**: Test strategies with historical data
- **AI Mentor**: Get personalized trading advice and education
- **Strategy Switcher**: Automatic strategy optimization system
- **Portfolio**: Track your overall trading performance
- **Market Data**: View real-time market information

## 🤖 Creating Your First Trading Bot

### Step 1: Choose a Strategy
For beginners, we recommend starting with these simple strategies:
- **MA_CROSSOVER**: Simple moving average crossover (Complexity: 2/10)
- **RSI_CROSSOVER**: Relative Strength Index momentum strategy (Complexity: 3/10)
- **TURTLE_BREAKOUT**: Breakout trading strategy (Complexity: 2/10)

### Step 2: Set Up Your Bot
1. Navigate to the "Trading Bots" page
2. Click "Buat Bot Baru"
3. Fill in the basic information:
   - **Bot Name**: Give your bot a descriptive name
   - **Market**: Choose your trading pair (e.g., EURUSD, XAUUSD)
   - **Risk per Trade**: Start with 1.0% (never exceed 2%)
   - **SL/TP Multipliers**: Use the default ATR-based values (2.0 for SL, 4.0 for TP)
   - **Timeframe**: H1 (1 hour) is recommended for beginners
   - **Check Interval**: 60 seconds is fine for most strategies

### Step 3: Configure Strategy Parameters
For your first bot, use the beginner-friendly defaults:
- **MA_CROSSOVER**: Fast period 10, Slow period 30
- **RSI_CROSSOVER**: RSI period 14, MA period 7
- **TURTLE_BREAKOUT**: Entry period 15, Exit period 8

### Step 4: Start Trading
1. Save your bot configuration
2. Click the "Start" button to begin trading
3. Monitor your bot's performance on the dashboard

## 📊 Understanding Risk Management

### ATR-Based Position Sizing
QuantumBotX uses Average True Range (ATR) to automatically adjust your position size based on market volatility:

- **Low Volatility**: Larger positions (safe markets)
- **High Volatility**: Smaller positions (protects your capital)

### Special Protections
- **Gold (XAUUSD) Protection**: Ultra-conservative settings automatically applied
- **Crypto Protection**: Weekend mode and volatility filters for cryptocurrencies
- **Emergency Brake**: System automatically skips dangerous trades

## 🎓 Learning Path for Beginners

### Week 1-2: Foundation
- **Strategy**: MA_CROSSOVER
- **Focus**: Learn basic trend following
- **Practice**: Demo trading with 0.01 lots
- **Goal**: Understand moving averages and crossovers

### Week 3-4: Momentum
- **Strategy**: RSI_CROSSOVER
- **Focus**: Learn momentum analysis
- **Practice**: Combine with moving averages
- **Goal**: Understand RSI and momentum concepts

### Week 5-6: Breakouts
- **Strategy**: TURTLE_BREAKOUT
- **Focus**: Learn breakout trading
- **Practice**: Practice entry/exit timing
- **Goal**: Identify support/resistance levels

## 🧪 Backtesting Your Strategies

Before trading live, always backtest your strategies. Backtesting allows you to test your strategies on historical data to see how they would have performed.

### How Backtesting Works
Backtesting in QuantumBotX works completely offline - you don't need an internet connection or MT5 terminal running. All you need is historical data in CSV format.

### Getting Historical Data
QuantumBotX provides a convenient script to download historical data from your MT5 account:

1. Ensure MT5 terminal is running and you're logged in
2. Configure your MT5 credentials in the `.env` file
3. Run the download script:
   ```bash
   python lab/download_data.py
   ```
   
This script will automatically download data for popular symbols and save CSV files to the `lab/backtest_data/` directory.

### Manual Data Download
If you prefer to download data manually or have data from other sources:

1. Navigate to the `lab/backtest_data` directory
2. Place your CSV files there with the naming convention: `{SYMBOL}_{TIMEFRAME}_data.csv` (e.g., `EURUSD_H1_data.csv`)
3. Ensure your CSV files have the required columns: time, open, high, low, close, volume

### Running a Backtest
1. Go to the "Backtester" page in the dashboard
2. Select your strategy and market
3. Choose a historical data period
4. Run the backtest
5. Review the results:
   - Profit factor (aim for >1.5)
   - Win rate (aim for >55%)
   - Maximum drawdown (<30% is acceptable)
   - Total trades executed

### Interpreting Backtest Results
- **Profit Factor**: The ratio of gross profits to gross losses (>1.5 is good)
- **Win Rate**: Percentage of winning trades (>55% is acceptable)
- **Maximum Drawdown**: Largest peak-to-trough decline (<30% is acceptable)
- **Sharpe Ratio**: Risk-adjusted return (higher is better)

## 🎯 Best Practices for Success

### For Demo Trading
1. **Treat Demo Like Real Money**: Make emotional decisions as if you were risking real capital
2. **Keep a Trading Journal**: Record every trade and your reasoning
3. **Focus on One Strategy**: Master it completely before trying others
4. **Review Every Trade**: Analyze both wins and losses

### Risk Management Rules
1. **Never risk more than 2%** of your account per trade
2. **Always use stop losses** - no exceptions
3. **Maintain a 1:2 risk-reward ratio** minimum
4. **Diversify across markets** but not strategies

### Moving to Live Trading
1. **Demo for at least 30 days** with consistent profitability
2. **Start with micro lots** (0.01) even with a live account
3. **Monitor emotions** - fear and greed are your biggest enemies
4. **Gradually increase position size** only after consistent profits

## 🌙 Cultural Features

QuantumBotX automatically adapts to religious holidays:

### Ramadan Trading Mode
- Automatically activates during Islamic holy month
- Respects prayer times with trading pauses
- Includes Zakat calculator and charity tracker
- Features patience reminders and optimal trading hours

### Christmas Trading Mode
- Activates during Christmas period
- Reduces risk during holiday season
- Applies special UI themes and decorations

## 🆘 Getting Help

### AI Mentor
The AI Mentor provides personalized trading advice:
- Click the AI button on the dashboard
- Ask questions about strategies or market conditions
- Get educational explanations for trading concepts

### Error Handling
If you encounter issues:
1. Check the application logs in the `logs/` directory
2. Ensure MT5 terminal is running
3. Verify your `.env` configuration
4. Restart the application if needed

## 📈 Next Steps

After mastering the basics:
1. **Explore Advanced Strategies**: Try BOLLINGER_REVERSION and PULSE_SYNC
2. **Use Strategy Switcher**: Enable automatic strategy optimization
3. **Customize Parameters**: Fine-tune strategies for specific markets
4. **Expand to Multiple Markets**: Trade Forex, Gold, and Crypto

Remember: Trading involves significant risk. Always start with demo accounts and never risk money you cannot afford to lose. QuantumBotX is designed to help you learn and trade more effectively, but success depends on your discipline and risk management.