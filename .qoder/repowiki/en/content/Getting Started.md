# Getting Started

<cite>
**Referenced Files in This Document**   
- [README.md](file://README.md)
- [requirements.txt](file://requirements.txt)
- [package.json](file://package.json)
- [init_db.py](file://init_db.py)
- [run.py](file://run.py)
- [core/__init__.py](file://core/__init__.py)
- [core/utils/mt5.py](file://core/utils/mt5.py)
- [core/strategies/beginner_defaults.py](file://core/strategies/beginner_defaults.py) - *Updated in recent commit*
- [core/strategies/strategy_selector.py](file://core/strategies/strategy_selector.py) - *Updated in recent commit*
- [core/education/atr_education.py](file://core/education/atr_education.py) - *Added in recent commit*
</cite>

## Update Summary
**Changes Made**   
- Added new section: **Beginner Onboarding Experience** to introduce the new educational features
- Enhanced **Troubleshooting Common Issues** with beginner-focused safety tips and parameter validation
- Updated **Configure Environment Variables** to include educational context for risk management
- Added references to new beginner education files and their integration points
- Incorporated ATR-based risk management explanations and protection features

## Table of Contents
1. [Python Environment Setup](#python-environment-setup)
2. [Install Python Dependencies](#install-python-dependencies)
3. [Install Node.js Dependencies](#install-nodejs-dependencies)
4. [Configure Environment Variables](#configure-environment-variables)
5. [Initialize the Database](#initialize-the-database)
6. [Start the Flask Application](#start-the-flask-application)
7. [Beginner Onboarding Experience](#beginner-onboarding-experience)
8. [Troubleshooting Common Issues](#troubleshooting-common-issues)

## Python Environment Setup

To begin using QuantumBotX, you must first set up a dedicated Python environment. This ensures dependency isolation and prevents conflicts with other projects.

1. Open your terminal or command prompt.
2. Navigate to the project root directory:
   ```bash
   cd 
   ```
3. Create a virtual environment named `venv`:
   ```bash
   python -m venv venv
   ```
4. Activate the virtual environment:
   - On Windows:
     ```bash
     .\venv\Scripts\activate
     ```
   - On macOS/Linux:
     ```bash
     source venv/bin/activate
     ```
   After activation, you should see `(venv)` in your command prompt, indicating the virtual environment is active.

**Section sources**
- [README.md](file://README.md#L50-L55)

## Install Python Dependencies

With the virtual environment activated, install all required Python packages listed in `requirements.txt`.

1. Run the following command:
   ```bash
   pip install -r requirements.txt
   ```

This installs essential libraries including:
- `Flask`: Web framework for the dashboard
- `MetaTrader5`: Official MT5 Python API
- `pandas` and `pandas_ta`: Data analysis and technical indicators
- `python-dotenv`: Environment variable management
- `sqlite3`: Database operations

Ensure your internet connection is stable during installation. If you encounter permission errors, run your terminal as an administrator or use the `--user` flag.

**Section sources**
- [requirements.txt](file://requirements.txt#L1-L23)
- [README.md](file://README.md#L60-L62)

## Install Node.js Dependencies

QuantumBotX uses Node.js for frontend asset management. Although the frontend is pre-built, installing Node.js dependencies ensures compatibility and enables future customization.

1. Ensure Node.js and npm are installed on your system. Verify with:
   ```bash
   node --version
   npm --version
   ```
2. Install all dependencies from `package.json`:
   ```bash
   npm install
   ```
   This command installs frontend libraries such as TailwindCSS and Chart.js, which power the responsive UI and data visualizations.

Note: The application will function without this step if you only intend to use the existing frontend assets.

**Section sources**
- [package.json](file://package.json)

## Configure Environment Variables

Proper configuration of environment variables is critical for connecting to your MetaTrader 5 account and securing the application.

1. Copy the example environment file:
   ```bash
   copy .env.example .env
   ```
   **Note**: The repository does not contain `.env.example`. Based on `run.py` and `README.md`, create a new `.env` file in the project root.

2. Create a `.env` file with the following content:
   ```env
   MT5_LOGIN=your_mt5_account_number
   MT5_PASSWORD=your_mt5_password
   MT5_SERVER=your_broker_server_name
   SECRET_KEY=your_flask_secret_key_here
   DB_NAME=bots.db
   FLASK_DEBUG=False
   FLASK_HOST=127.0.0.1
   FLASK_PORT=5000
   ```
   Replace the placeholder values with your actual MT5 credentials. The `SECRET_KEY` should be a strong random string used for session security.

**Important**: Never commit `.env` to version control. It contains sensitive information.

**Section sources**
- [README.md](file://README.md#L75-L85)
- [run.py](file://run.py#L8-L10)

## Initialize the Database

QuantumBotX uses SQLite to store bot configurations, trade history, and backtest results. Initialize the database schema using the provided script.

1. Run the database initialization script:
   ```bash
   python init_db.py
   ```
2. To overwrite an existing database, use:
   ```bash
   python init_db.py --force
   ```

The script creates four tables:
- `users`: Stores admin user credentials
- `bots`: Stores trading bot configurations
- `trade_history`: Logs all bot actions and trades
- `backtest_results`: Stores historical backtest performance data

A default admin user is created with:
- **Email**: `admin@quantumbotx.com`
- **Password**: `admin`

**Section sources**
- [init_db.py](file://init_db.py#L1-L137)
- [core/db/connection.py](file://core/db/connection.py#L4-L5)

## Start the Flask Application

After completing setup, launch the QuantumBotX application.

1. Ensure the virtual environment is active and MT5 terminal is running.
2. Start the Flask server:
   ```bash
   python run.py
   ```
3. Open your browser and navigate to:
   ```
   http://127.0.0.1:5000
   ```

### Expected Output
```
INFO:root:Koneksi MT5 berhasil diinisialisasi dari run.py.
INFO:root:Aplikasi QuantumBotX dimulai dalam mode PRODUKSI.
 * Running on http://127.0.0.1:5000
```

The application automatically:
- Loads environment variables
- Connects to MT5 using credentials from `.env`
- Initializes all active bots
- Registers API routes and web pages
- Sets up graceful shutdown via `atexit`

**Section sources**
- [run.py](file://run.py#L1-L52)
- [core/__init__.py](file://core/__init__.py#L20-L137)

## Beginner Onboarding Experience

QuantumBotX now includes a comprehensive onboarding experience for beginners with a progressive learning path and educational guidance. This system helps new traders start safely and learn effectively.

### Beginner-Friendly Strategy Defaults

The system provides optimized defaults for beginners across multiple strategies:

**Recommended Beginner Strategies:**
- **MA_CROSSOVER**: Simple trend following with fast_period=10, slow_period=30
- **RSI_CROSSOVER**: Momentum trading with rsi_period=14, rsi_ma_period=7
- **TURTLE_BREAKOUT**: Breakout trading with entry_period=15, exit_period=8

These defaults are designed to provide faster feedback and quicker learning cycles for beginners.

### Progressive Learning Path

Follow this structured 3-month learning path:

1. **Week 1-2: Foundation** - Start with MA_CROSSOVER to learn basic trend following
2. **Week 3-4: Momentum** - Move to RSI_CROSSOVER to understand momentum concepts
3. **Week 5-6: Breakouts** - Learn breakout trading with TURTLE_BREAKOUT
4. **Month 2: Intermediate** - Study mean reversion with BOLLINGER_REVERSION
5. **Month 3: Advanced** - Master multi-indicator analysis with PULSE_SYNC

### ATR-Based Risk Management Education

The system includes automatic ATR (Average True Range) based risk management:

- **ATR Concept**: Measures average daily price movement
- **EURUSD**: Typical ATR = 50 pips (stable market)
- **XAUUSD**: Typical ATR = $15 (very high volatility)
- **Automatic Protection**: System caps risk at 1% for volatile instruments like gold

### Quick Start Guide for Absolute Beginners

1. **Choose Your First Strategy**: Start with MA_CROSSOVER (simplest and most educational)
2. **Set Safe Parameters**: Use lot size: 0.01, Stop Loss: 50 pips, Take Profit: 100 pips
3. **Start with Demo**: Trade demo account for at least 1 month before going live
4. **Track Everything**: Keep a detailed trading journal recording entry/exit reasons
5. **Gradual Progression**: Master one strategy before trying others (aim for 60%+ win rate)

### Safety Tips for Beginners

- 🛡️ NEVER risk more than 2% of your account per trade
- 📊 ALWAYS backtest strategies before live trading
- 💰 Start with micro lots (0.01) while learning
- 📈 Demo trade for at least 30 days before going live
- 🎯 Set stop losses on EVERY trade - no exceptions
- 📚 Focus on learning, not making money initially
- 💡 Use economic calendar to avoid high-impact news
- 🎨 Master ONE strategy before trying others

**Section sources**
- [core/strategies/beginner_defaults.py](file://core/strategies/beginner_defaults.py#L1-L310)
- [core/strategies/strategy_selector.py](file://core/strategies/strategy_selector.py#L1-L204)
- [core/education/atr_education.py](file://core/education/atr_education.py#L1-L273)

## Troubleshooting Common Issues

### Missing Dependencies
**Symptom**: `ModuleNotFoundError` when starting the app.
**Solution**: Ensure the virtual environment is activated and reinstall dependencies:
```bash
pip install -r requirements.txt
```

### MT5 Terminal Connectivity Problems
**Symptom**: "Gagal inisialisasi MT5" or login failure.
**Solutions**:
1. Ensure the MetaTrader 5 desktop terminal is installed and running.
2. Verify your MT5 credentials in `.env` are correct.
3. Confirm the broker server name matches exactly (case-sensitive).
4. Check that the MT5 terminal allows automated trading in settings.

### Database Initialization Errors
**Symptom**: "Database error" or inability to create tables.
**Solutions**:
1. Ensure no other process is using `bots.db`.
2. Use `--force` to remove and recreate the database:
   ```bash
   python init_db.py --force
   ```
3. Verify write permissions in the project directory.

### Flask Application Fails to Start
**Symptom**: Port conflict or binding errors.
**Solution**: Change the port in `.env`:
```env
FLASK_PORT=5001
```

### Bot Fails to Start
**Symptom**: Bot status shows "Error" in the dashboard.
**Solution**: Check `logs/app.log` for detailed error messages. Common causes include invalid strategy parameters or symbol not found in MT5.

### Beginner Strategy Configuration Issues
**Symptom**: Strategy parameters are too aggressive for learning.
**Solutions**:
1. Use beginner defaults from `beginner_defaults.py`
2. Validate parameters using the strategy selector:
   ```python
   from core.strategies.strategy_selector import StrategySelector
   selector = StrategySelector()
   validation = selector.validate_parameters('MA_CROSSOVER', {'fast_period': 50})
   ```
3. Follow the recommended learning path in the Beginner Onboarding section
4. Start with demo trading and small lot sizes (0.01)

### ATR Risk Management Warnings
**Symptom**: System warns about unsafe risk parameters.
**Solutions**:
1. For beginners: Keep risk percentage ≤ 2%
2. For gold (XAUUSD) trading: Risk is automatically capped at 1%
3. Use recommended ATR multipliers: SL at 2x ATR, TP at 4x ATR
4. The system automatically protects against catastrophic losses on volatile instruments

**Section sources**
- [core/utils/mt5.py](file://core/utils/mt5.py#L16-L22)
- [init_db.py](file://init_db.py#L30-L40)
- [run.py](file://run.py#L25-L35)
- [core/strategies/beginner_defaults.py](file://core/strategies/beginner_defaults.py#L1-L310)
- [core/strategies/strategy_selector.py](file://core/strategies/strategy_selector.py#L1-L204)
- [core/education/atr_education.py](file://core/education/atr_education.py#L1-L273)