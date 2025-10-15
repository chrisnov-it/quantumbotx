# QuantumBotX - Quick Start Guide

## First Time Setup

1. **Install MetaTrader 5** (Required)
   - Download from: https://www.metatrader5.com/
   - Install and create a demo account
   - Keep MT5 running in the background
   - ⚠️ **IMPORTANT:** MetaTrader 5 must be running for QuantumBotX to work

2. **Configure Your Settings**
   - Copy `.env.example` to `.env`
   - Edit `.env` with your MT5 credentials:
     ```ini
     MT5_LOGIN=your_account_number
     MT5_PASSWORD=your_password
     MT5_SERVER=your_server_name
     ```

3. **Start the Application**
   - Double-click `start.bat` (Windows)
   - Open http://127.0.0.1:5000 in your browser

## ✅ System Requirements

- **Windows 7 SP1 or later** (64-bit recommended)
- **MetaTrader 5** (must be installed separately)
- **4GB RAM minimum** (8GB recommended)
- **500MB free disk space**
- **Internet connection** for initial setup
- **❌ Python NOT required** (already bundled in the installer)

## Daily Use

1. Start MetaTrader 5 first
2. Run `start.bat`
3. Open your web browser to http://127.0.0.1:5000

## Troubleshooting

- Make sure MetaTrader 5 is running
- Check your .env file has correct credentials
- If the app won't start, try running `python run.py` directly

## Support

If you need help, check the README.md file or contact support.
