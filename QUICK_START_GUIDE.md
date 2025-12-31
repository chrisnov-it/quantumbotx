# QuantumBotX - Quick Start Guide

## Setup Your Broker

- **Option A: MetaTrader 5 (Forex/Gold)**
  - Download MT5 from: <https://www.metatrader5.com/>
  - Install and keep it running in the background.
  
- **Option B: Crypto Exchange (Binance/Bybit)**
  - Create an account on your preferred exchange.
  - For testing, use **Binance Futures Testnet**.

⚠️ **Note:** MT5 is only required if you choose to trade Forex/Gold via `MT5` broker type.

2. **Configure Your Settings**
   - Copy `.env.example` to `.env`
   - Edit `.env` with your MT5 credentials:

     ```ini
     MT5_LOGIN=your_account_number
     MT5_PASSWORD=your_password
     MT5_SERVER=your_server_name
     ```

3. **Verify Connection**
   - To test MT5: `python test_mt5_connection.py`
   - To test Crypto: `python test_ccxt.py`
   - To simulate without Internet: `python visual_simulation.py`

4. **Start the Application**
   - Double-click `start.bat` (Windows)
   - Open <http://127.0.0.1:5000>

- **Windows 10/11** (Native MT5 support)
- **Linux/MacOS/Docker** (CCXT/Crypto support only)
- **Python 3.10 - 3.13**
- **4GB RAM minimum**
- **Stable internet connection**

## Daily Use

1. Start MetaTrader 5 first
2. Run `start.bat`
3. Open your web browser to <http://127.0.0.1:5000>

## Troubleshooting

- Make sure MetaTrader 5 is running
- Check your .env file has correct credentials
- If the app won't start, try running `python run.py` directly

## Support

If you need help, check the README.md file or contact support.
