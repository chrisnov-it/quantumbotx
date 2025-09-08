# ❓ QuantumBotX FAQ

Frequently asked questions about using QuantumBotX.

## 🚀 General Questions

### What is QuantumBotX?
QuantumBotX is an AI-powered, modular trading bot platform designed for MetaTrader 5 (MT5). It provides professional trading strategies with beginner-friendly features, educational tools, and cultural awareness.

### Do I need programming knowledge to use QuantumBotX?
No programming knowledge is required! QuantumBotX is designed to be user-friendly with a web-based interface. However, basic computer skills are helpful.

### Which brokers are supported?
QuantumBotX works with any broker that supports MetaTrader 5, including:
- XM Global
- Exness
- Alpari
- MetaQuotes (demo)
- And many others

The system automatically migrates symbols between brokers.

### Can I use QuantumBotX with a demo account?
Yes! In fact, we strongly recommend starting with a demo account to learn the system without risking real money.

## 💰 Trading Questions

### How much money do I need to start?
You can start with as little as $100, but we recommend at least $1,000 for more flexibility. For demo accounts, no real money is required.

### What markets can I trade?
QuantumBotX supports multiple markets:
- **Forex**: EURUSD, GBPUSD, USDJPY, etc.
- **Gold**: XAUUSD
- **Indices**: US30, US500, DE30, etc.
- **Cryptocurrencies**: BTCUSD, ETHUSD (with special weekend mode)

### How does the risk management work?
QuantumBotX uses ATR (Average True Range) based position sizing:
- Automatically calculates lot sizes based on market volatility
- Caps risk at 1-2% per trade
- Provides special protection for volatile instruments like Gold
- Includes emergency brake system to skip dangerous trades

### What are the recommended settings for beginners?
For beginners, we recommend:
- Risk per trade: 1.0%
- Stop Loss: 2.0 x ATR
- Take Profit: 4.0 x ATR
- Timeframe: H1 (1 hour)
- Starting strategy: MA_CROSSOVER
- Lot size: 0.01 (micro lots)

## 🤖 Bot Management

### How many bots can I run simultaneously?
You can run up to 4 bots simultaneously, which is optimal for most retail traders.

### Can I modify bot settings while it's running?
Yes, you can modify most settings while the bot is running. However, for safety reasons, some core parameters require the bot to be stopped first.

### How do I know if my bot is working correctly?
Monitor these indicators:
- Check the dashboard for active bot status
- Review trade history in the "History" section
- Monitor notifications for important events
- Use the AI Mentor for performance analysis

### What happens if my computer shuts down?
If your computer shuts down, all active bots will stop. When you restart the application, you'll need to manually restart your bots. We recommend using a reliable computer or VPS for live trading.

## 📊 Strategy Questions

### Which strategy should I start with?
Beginners should start with:
1. **MA_CROSSOVER** (Week 1-2): Simple moving average strategy
2. **RSI_CROSSOVER** (Week 3-4): Momentum-based strategy
3. **TURTLE_BREAKOUT** (Week 5-6): Breakout trading strategy

### How do I know which strategy works best for a market?
The system provides automatic recommendations:
- **EURUSD/GBPUSD**: Trend-following strategies like MA_CROSSOVER
- **XAUUSD**: Breakout strategies like TURTLE_BREAKOUT or QUANTUM_VELOCITY
- **BTCUSD/ETHUSD**: Crypto-optimized strategies like QUANTUMBOTX_CRYPTO
- **Indices**: INDEX_BREAKOUT_PRO for professional index trading

### Can I create my own strategies?
Yes, experienced users can create custom strategies by extending the strategy classes. However, this requires Python programming knowledge.

### How do I backtest a strategy?
1. Go to the "Backtester" page
2. Select your strategy and market
3. Choose a historical data period
4. Run the backtest
5. Review performance metrics like profit factor and drawdown

## 🧪 Backtesting & Data

### Do I need an internet connection for backtesting?
No! Backtesting works completely offline and does not require an internet connection or MT5 terminal. All you need is historical data in CSV format stored in the `lab/backtest_data` directory.

### How do I get historical data for backtesting?
QuantumBotX provides a data download script in the `lab/download_data.py` directory that can automatically download historical data from your MT5 account:

1. Ensure MT5 terminal is running and you're logged in
2. Configure your MT5 credentials in the `.env` file
3. Run the download script:
   ```bash
   python lab/download_data.py
   ```
4. The script will download data for popular symbols and save CSV files to `lab/backtest_data/`

### What format should backtesting data be in?
Backtesting data should be in CSV format with the following columns:
- `time`: Timestamp in any standard format
- `open`: Opening price
- `high`: Highest price
- `low`: Lowest price
- `close`: Closing price
- `volume`: Trading volume

Files should be named using the pattern: `{SYMBOL}_{TIMEFRAME}_data.csv` (e.g., `EURUSD_H1_data.csv`)

### Can I use my own data for backtesting?
Yes! You can use your own historical data by placing CSV files in the `lab/backtest_data` directory with the proper naming convention. This is useful if you have data from other sources or want to test specific market conditions.

### How much historical data do I need?
For meaningful backtesting results, we recommend at least 500 bars (about 2 years of H1 data) for most strategies. More data generally leads to more reliable results, especially for strategies that use longer timeframes or lookback periods.

## 🛡️ Safety & Risk Management

### Is QuantumBotX safe to use?
QuantumBotX includes multiple safety features:
- ATR-based position sizing automatically adapts to market volatility
- Special protection for Gold (XAUUSD) prevents account blowouts
- Emergency brake system skips dangerous trades
- Parameter validation prevents unsafe configurations

### What happens if I lose connection to MT5?
If connection to MT5 is lost, the system will:
1. Log the error in the application logs
2. Stop all active bots
3. Attempt to reconnect automatically
4. Require manual restart of bots after reconnection

### How do I protect my account from large losses?
Follow these risk management principles:
- Never risk more than 2% of your account per trade
- Always use stop losses
- Start with micro lots (0.01)
- Demo trade for at least 30 days before going live
- Monitor your bots regularly

## 🎓 Learning & Education

### Do I need prior trading experience?
No prior experience is required. QuantumBotX includes a progressive learning path that takes you from absolute beginner to advanced trader over several months.

### What educational resources are available?
QuantumBotX provides:
- **AI Mentor**: Personalized trading advice and education
- **Strategy explanations**: Plain English descriptions of all parameters
- **Progressive learning path**: Structured curriculum from beginner to expert
- **ATR education**: Understanding volatility-based risk management
- **Beginner defaults**: Safe parameter settings for all strategies

### How long does it take to learn?
The structured learning path is designed to take 3 months:
- Month 1: Basic strategies and concepts
- Month 2: Intermediate strategies and market analysis
- Month 3: Advanced strategies and portfolio management

## 🌙 Cultural Features

### What holidays are supported?
QuantumBotX automatically detects and adapts to:
- **Christmas**: December 20 - January 6
- **Ramadan**: Islamic holy month (dates vary yearly)
- **Eid al-Fitr**: Celebration at the end of Ramadan
- **New Year**: December 30 - January 3

### How do holiday modes affect trading?
Holiday modes automatically:
- Reduce risk during distracted periods
- Pause trading during prayer times (Ramadan)
- Apply culturally-appropriate UI themes
- Provide relevant greetings and reminders

### Can I disable holiday modes?
Holiday modes are automatically activated based on calendar dates and cannot be manually disabled. This ensures cultural sensitivity and appropriate risk management during holiday periods.

## 🔧 Technical Questions

### What are the system requirements?
- **Operating System**: Windows 10 or later (MT5 requirement)
- **Python**: 3.10 or later
- **RAM**: 4GB minimum, 8GB recommended
- **Storage**: 500MB free space
- **Internet**: Stable connection required

### How do I update QuantumBotX?
1. Pull the latest changes from the repository:
   ```bash
   git pull origin main
   ```
2. Update dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Restart the application

### Where are logs stored?
Application logs are stored in the `logs/` directory:
- `app.log`: Main application logs
- Historical logs are automatically rotated

### How do I report bugs or issues?
Please report issues through the GitHub repository's issue tracker with:
- Detailed description of the problem
- Steps to reproduce
- Screenshots if applicable
- Log files if relevant

## 📱 Mobile & Remote Access

### Can I access QuantumBotX from my phone?
The web interface is mobile-responsive and can be accessed from any device with a web browser. However, the application must be running on a computer with MT5.

### Is there a mobile app?
Currently, there is no dedicated mobile app. The web interface works well on mobile devices.

### Can I run QuantumBotX on a VPS?
Yes, QuantumBotX can run on a Virtual Private Server (VPS), which is recommended for live trading to ensure 24/7 operation.