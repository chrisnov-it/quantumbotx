# download_data.py - Enhanced MT5 Data Downloader for QuantumBotX Backtesting
import MetaTrader5 as mt5
import pandas as pd
import os
import sys
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables from .env file
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(project_root, '.env'))

# --- MT5 Credentials from Environment ---
ACCOUNT = int(os.getenv('MT5_LOGIN', '0'))
PASSWORD = os.getenv('MT5_PASSWORD', '')
SERVER = os.getenv('MT5_SERVER', '')

# Validate credentials
if not all([ACCOUNT, PASSWORD, SERVER]):
    print("❌ MT5 credentials not found in .env file!")
    print("📝 Please configure the following in your .env file:")
    print("   MT5_LOGIN=your_account_number")
    print("   MT5_PASSWORD=your_password")
    print("   MT5_SERVER=your_server_name")
    print("\n💡 Tip: Check the .env file in the project root directory")
    sys.exit(1)

# --- Popular Trading Symbols for Indonesian Market ---
POPULAR_SYMBOLS = {
    # Forex Major Pairs
    'EURUSD': mt5.TIMEFRAME_H1,
    'GBPUSD': mt5.TIMEFRAME_H1,
    'USDJPY': mt5.TIMEFRAME_H1,
    'AUDUSD': mt5.TIMEFRAME_H1,
    'USDCAD': mt5.TIMEFRAME_H1,
    'USDCHF': mt5.TIMEFRAME_H1,
    
    # Indonesian Focus
    'USDIDR': mt5.TIMEFRAME_H1,  # Important for Indonesian traders
    
    # Precious Metals (High volatility - needs special handling)
    'XAUUSD': mt5.TIMEFRAME_H1,  # Gold - very popular
    'XAGUSD': mt5.TIMEFRAME_H1,  # Silver
    
    # Crypto (if available)
    'BTCUSD': mt5.TIMEFRAME_H1,
    'ETHUSD': mt5.TIMEFRAME_H1,
    
    # Oil
    'USOIL': mt5.TIMEFRAME_H1,
    'UKOIL': mt5.TIMEFRAME_H1,
}

def download_symbol_data(symbol, timeframe, start_date, end_date, data_dir="backtest_data"):
    """
    Download historical data for a specific symbol
    Compatible with QuantumBotX backtesting engine
    """
    # Ensure data directory exists
    os.makedirs(data_dir, exist_ok=True)
    
    print(f"\n📊 Downloading {symbol} data...")
    
    # Get symbol info first
    symbol_info = mt5.symbol_info(symbol)
    if symbol_info is None:
        print(f"❌ Symbol {symbol} not found on this broker")
        return None
    
    if not symbol_info.visible:
        # Try to enable the symbol
        if not mt5.symbol_select(symbol, True):
            print(f"❌ Failed to enable symbol {symbol}")
            return None
    
    # Download the data
    rates = mt5.copy_rates_range(symbol, timeframe, start_date, end_date)
    
    if rates is None or len(rates) == 0:
        print(f"❌ No data available for {symbol}")
        return None
    
    # Convert to DataFrame
    df = pd.DataFrame(rates)
    df['time'] = pd.to_datetime(df['time'], unit='s')
    
    # Rename columns to match QuantumBotX backtesting engine expectations
    df = df.rename(columns={
        'time': 'time',
        'open': 'open', 
        'high': 'high',
        'low': 'low',
        'close': 'close',
        'tick_volume': 'volume'
    })
    
    # Remove unnecessary columns and ensure proper order
    df = df[['time', 'open', 'high', 'low', 'close', 'volume']]
    
    # Get timeframe string for filename
    timeframe_map = {
        mt5.TIMEFRAME_M1: 'M1',
        mt5.TIMEFRAME_M5: 'M5', 
        mt5.TIMEFRAME_M15: 'M15',
        mt5.TIMEFRAME_M30: 'M30',
        mt5.TIMEFRAME_H1: 'H1',
        mt5.TIMEFRAME_H4: 'H4',
        mt5.TIMEFRAME_D1: 'D1',
        mt5.TIMEFRAME_W1: 'W1',
        mt5.TIMEFRAME_MN1: 'MN1'
    }
    
    timeframe_str = timeframe_map.get(timeframe, 'H1')
    
    # Create filename compatible with backtesting engine
    filename = f"{symbol}_{timeframe_str}_data.csv"
    file_path = os.path.join(data_dir, filename)
    
    # Save to CSV
    df.to_csv(file_path, index=False)
    
    print(f"✅ {symbol}: {len(df)} bars saved to {file_path}")
    print(f"   📅 Date range: {df['time'].min()} to {df['time'].max()}")
    
    # Special note for XAUUSD (Gold)
    if 'XAU' in symbol.upper():
        print(f"   ⚠️  WARNING: {symbol} is a volatile instrument - QuantumBotX will apply conservative risk settings")
    
    return file_path

def main():
    """Main function to download data for multiple symbols"""
    
    # --- Initialize MT5 ---
    if not mt5.initialize(login=ACCOUNT, password=PASSWORD, server=SERVER):
        error = mt5.last_error()
        print(f"❌ Failed to initialize MT5! Error: {error}")
        print("\n🔧 Troubleshooting:")
        print("   1. Check if MT5 terminal is running")
        print("   2. Verify credentials in .env file")
        print("   3. Ensure the account is not already logged in elsewhere")
        print("   4. Check internet connection")
        mt5.shutdown()
        return
    
    account_info = mt5.account_info()
    print(f"✅ Successfully connected to MT5")
    print(f"📡 Server: {account_info.server}")
    print(f"👤 Account: {account_info.login}")
    print(f"💰 Balance: ${account_info.balance:,.2f}")
    print(f"🏢 Company: {account_info.company}")
    
    # --- Download Parameters ---
    start_date = datetime(2020, 1, 1)  # 4+ years of data
    end_date = datetime.now()
    
    print(f"\n📊 Downloading data from {start_date.date()} to {end_date.date()}")
    
    downloaded_files = []
    failed_symbols = []
    
    # Download data for all popular symbols
    for symbol, timeframe in POPULAR_SYMBOLS.items():
        try:
            file_path = download_symbol_data(symbol, timeframe, start_date, end_date)
            if file_path:
                downloaded_files.append(file_path)
            else:
                failed_symbols.append(symbol)
        except Exception as e:
            print(f"❌ Error downloading {symbol}: {e}")
            failed_symbols.append(symbol)
    
    # Cleanup
    mt5.shutdown()
    
    # Summary
    print(f"\n🎉 Download Complete!")
    print(f"✅ Successfully downloaded: {len(downloaded_files)} files")
    print(f"❌ Failed downloads: {len(failed_symbols)} symbols")
    
    if downloaded_files:
        print("\n📁 Downloaded files:")
        for file_path in downloaded_files:
            print(f"   • {file_path}")
    
    if failed_symbols:
        print("\n⚠️  Failed symbols:")
        for symbol in failed_symbols:
            print(f"   • {symbol}")
    
    print("\n💡 Tips for QuantumBotX Backtesting:")
    print("   1. Upload CSV files via the web interface")
    print("   2. XAUUSD will automatically use conservative settings")
    print("   3. Start with simple strategies like MA_CROSSOVER")
    print("   4. Use USDIDR data for Indonesian market focus")
    print(f"\n🔧 Connected to: {SERVER} (Account: {ACCOUNT})")
    
if __name__ == "__main__":
    main()