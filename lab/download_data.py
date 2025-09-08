# download_data.py - Enhanced MT5 Data Downloader for QuantumBotX Backtesting
import MetaTrader5 as mt5
import pandas as pd
import os
import sys
from datetime import datetime
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

# --- Popular Trading Symbols for Indonesian Market + Index Trading ---
POPULAR_SYMBOLS = {
    # Forex Major Pairs (Standard)
    'EURUSD': mt5.TIMEFRAME_H1,
    'GBPUSD': mt5.TIMEFRAME_H1,
    'USDJPY': mt5.TIMEFRAME_H1,
    'AUDUSD': mt5.TIMEFRAME_H1,
    'USDCAD': mt5.TIMEFRAME_H1,
    'USDCHF': mt5.TIMEFRAME_H1,
    'NZDUSD': mt5.TIMEFRAME_H1,
    'EURGBP': mt5.TIMEFRAME_H1,
    'EURJPY': mt5.TIMEFRAME_H1,
    'GBPJPY': mt5.TIMEFRAME_H1,
    
    # Forex Major Pairs (FBS Demo with 'w' suffix)
    'EURUSDw': mt5.TIMEFRAME_H1,
    'GBPUSDw': mt5.TIMEFRAME_H1,
    'USDJPYw': mt5.TIMEFRAME_H1,
    'AUDUSDw': mt5.TIMEFRAME_H1,
    'USDCADw': mt5.TIMEFRAME_H1,
    'USDCHFw': mt5.TIMEFRAME_H1,
    'NZDUSDw': mt5.TIMEFRAME_H1,
    'EURGBPw': mt5.TIMEFRAME_H1,
    'EURJPYw': mt5.TIMEFRAME_H1,
    'GBPJPYw': mt5.TIMEFRAME_H1,
    
    # Indonesian Focus
    'USDIDR': mt5.TIMEFRAME_H1,  # Important for Indonesian traders
    'USDIDRw': mt5.TIMEFRAME_H1, # FBS variant
    
    # Stock Indices (US Markets)
    'US30': mt5.TIMEFRAME_H1,    # Dow Jones Industrial Average
    'US100': mt5.TIMEFRAME_H1,   # NASDAQ 100
    'US500': mt5.TIMEFRAME_H1,   # S&P 500
    'NAS100': mt5.TIMEFRAME_H1,  # Alternative NASDAQ name
    'SPX500': mt5.TIMEFRAME_H1,  # Alternative S&P 500 name
    'DJ30': mt5.TIMEFRAME_H1,    # Alternative Dow Jones name
    
    # European Indices
    'DE30': mt5.TIMEFRAME_H1,    # DAX (Germany)
    'DAX30': mt5.TIMEFRAME_H1,   # Alternative DAX name
    'UK100': mt5.TIMEFRAME_H1,   # FTSE 100 (UK)
    'FTSE100': mt5.TIMEFRAME_H1, # Alternative FTSE name
    'FR40': mt5.TIMEFRAME_H1,    # CAC 40 (France)
    'CAC40': mt5.TIMEFRAME_H1,   # Alternative CAC name
    'ES35': mt5.TIMEFRAME_H1,    # IBEX 35 (Spain)
    'IT40': mt5.TIMEFRAME_H1,    # MIB 40 (Italy)
    
    # Asian Indices
    'JP225': mt5.TIMEFRAME_H1,   # Nikkei 225 (Japan)
    'N225': mt5.TIMEFRAME_H1,    # Alternative Nikkei name
    'HK50': mt5.TIMEFRAME_H1,    # Hang Seng (Hong Kong)
    'AUS200': mt5.TIMEFRAME_H1,  # ASX 200 (Australia)
    
    # Precious Metals (High volatility - needs special handling)
    'XAUUSD': mt5.TIMEFRAME_H1,  # Gold - very popular
    'XAGUSD': mt5.TIMEFRAME_H1,  # Silver
    'XAUUSDw': mt5.TIMEFRAME_H1, # FBS Gold variant
    'XAGUSDw': mt5.TIMEFRAME_H1, # FBS Silver variant
    'GOLD': mt5.TIMEFRAME_H1,    # Alternative Gold symbol
    'SILVER': mt5.TIMEFRAME_H1,  # Alternative Silver symbol
    
    # Energy Commodities
    'USOIL': mt5.TIMEFRAME_H1,   # Crude Oil (US)
    'UKOIL': mt5.TIMEFRAME_H1,   # Brent Oil (UK)
    'WTI': mt5.TIMEFRAME_H1,     # West Texas Intermediate
    'BRENT': mt5.TIMEFRAME_H1,   # Brent Crude
    'NGAS': mt5.TIMEFRAME_H1,    # Natural Gas
    
    # Crypto (if available on broker)
    'BTCUSD': mt5.TIMEFRAME_H1,
    'ETHUSD': mt5.TIMEFRAME_H1,
    'LTCUSD': mt5.TIMEFRAME_H1,
    'ADAUSD': mt5.TIMEFRAME_H1,
    'DOTUSD': mt5.TIMEFRAME_H1,
}

# --- Custom Symbols (Add your broker-specific symbols here) ---
CUSTOM_SYMBOLS = {
    # Add any additional symbols your broker offers
    # Format: 'SYMBOL_NAME': mt5.TIMEFRAME_H1,
    # Examples:
    # 'EURAUD': mt5.TIMEFRAME_H1,
    # 'GBPCAD': mt5.TIMEFRAME_H1,
    # 'CADJPY': mt5.TIMEFRAME_H1,
    # 'CHFJPY': mt5.TIMEFRAME_H1,
}

def add_custom_symbol(symbol_name, timeframe=mt5.TIMEFRAME_H1):
    """
    Add a custom symbol to download list
    Usage: add_custom_symbol('EURAUD', mt5.TIMEFRAME_H1)
    """
    CUSTOM_SYMBOLS[symbol_name] = timeframe
    print(f"✅ Added {symbol_name} to custom download list")

def download_custom_symbol(symbol_name, timeframe=mt5.TIMEFRAME_H1, start_date=None, end_date=None):
    """
    Download a single custom symbol immediately
    """
    if start_date is None:
        start_date = datetime(2020, 1, 1)
    if end_date is None:
        end_date = datetime.now()
    
    print(f"\n🎯 Manual Download: {symbol_name}")
    return download_symbol_data(symbol_name, timeframe, start_date, end_date)

def download_symbol_data(symbol, timeframe, start_date, end_date, data_dir="backtest_data"):
    """
    Download historical data for a specific symbol
    Compatible with QuantumBotX backtesting engine
    Enhanced for index trading and broker-specific symbol variants
    """
    # Ensure data directory exists
    os.makedirs(data_dir, exist_ok=True)
    
    print(f"\n📊 Downloading {symbol} data...")
    
    # Get symbol info first
    symbol_info = mt5.symbol_info(symbol)  # pyright: ignore
    if symbol_info is None:
        print(f"❌ Symbol {symbol} not found on this broker")
        
        # Suggest alternative symbol names for common cases
        suggestions = []
        if symbol.endswith('w'):
            base_symbol = symbol[:-1]
            suggestions.append(base_symbol)
        elif not symbol.endswith('w') and symbol in ['EURUSD', 'GBPUSD', 'USDJPY', 'AUDUSD', 'USDCAD', 'USDCHF']:
            suggestions.append(symbol + 'w')
        
        if symbol == 'US30':
            suggestions.extend(['DJ30', 'DOW30', 'DJIA'])
        elif symbol == 'US100':
            suggestions.extend(['NAS100', 'NASDAQ100', 'NDX'])
        elif symbol == 'US500':
            suggestions.extend(['SPX500', 'SP500', 'SPX'])
        elif symbol == 'DE30':
            suggestions.extend(['DAX30', 'GER30', 'DAX'])
        elif symbol == 'XAUUSD':
            suggestions.extend(['GOLD', 'XAUUSDw'])
        
        if suggestions:
            print(f"💡 Try these alternatives: {', '.join(suggestions)}")
        
        return None
    
    if not symbol_info.visible:
        # Try to enable the symbol
        if not mt5.symbol_select(symbol, True):  # pyright: ignore
            print(f"❌ Failed to enable symbol {symbol}")
            return None
        print(f"✅ Enabled symbol {symbol} in Market Watch")
    
    # Show symbol details for indices and special instruments
    if any(idx in symbol.upper() for idx in ['US30', 'US100', 'US500', 'DE30', 'UK100', 'JP225']):
        print(f"📈 Index detected: {symbol} (Point value: {symbol_info.point}, Contract size: {symbol_info.trade_contract_size})")
    elif 'XAU' in symbol.upper() or 'GOLD' in symbol.upper():
        print(f"🥇 Gold detected: {symbol} (Spread typically higher, use conservative settings)")
    elif symbol.endswith('w'):
        print(f"🔧 FBS variant detected: {symbol} (Micro lot broker format)")
    
    # Download the data
    rates = mt5.copy_rates_range(symbol, timeframe, start_date, end_date)  # pyright: ignore
    
    if rates is None or len(rates) == 0:
        print(f"❌ No data available for {symbol}")
        print(f"💡 Check if {symbol} was available during the requested date range")
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
    # Clean symbol name for filename (remove 'w' suffix for file naming consistency)
    clean_symbol = symbol.replace('w', '') if symbol.endswith('w') else symbol
    filename = f"{clean_symbol}_{timeframe_str}_data.csv"
    file_path = os.path.join(data_dir, filename)
    
    # Save to CSV
    df.to_csv(file_path, index=False)
    
    print(f"✅ {symbol}: {len(df)} bars saved to {file_path}")
    print(f"   📅 Date range: {df['time'].min()} to {df['time'].max()}")
    
    # Special notes for different instrument types
    if any(idx in symbol.upper() for idx in ['US30', 'US100', 'US500', 'DE30']):
        print("   📊 INDEX: Suitable for INDEX_MOMENTUM and INDEX_BREAKOUT_PRO strategies")
    elif 'XAU' in symbol.upper() or 'GOLD' in symbol.upper():
        print("   ⚠️  GOLD: Volatile instrument - QuantumBotX will apply conservative risk settings")
    elif symbol.endswith('w'):
        print(f"   🔧 FBS Format: Saved as {clean_symbol} for consistency")
    
    return file_path

def main():
    """Main function to download data for multiple symbols"""
    
    # --- Initialize MT5 ---
    if not mt5.initialize(login=ACCOUNT, password=PASSWORD, server=SERVER):  # pyright: ignore
        error = mt5.last_error() # pyright: ignore
        print(f"❌ Failed to initialize MT5! Error: {error}")
        print("\n🔧 Troubleshooting:")
        print("   1. Check if MT5 terminal is running")
        print("   2. Verify credentials in .env file")
        print("   3. Ensure the account is not already logged in elsewhere")
        print("   4. Check internet connection")
        mt5.shutdown() # pyright: ignore
        return
    
    account_info = mt5.account_info() # pyright: ignore
    print("✅ Successfully connected to MT5")
    print(f"📡 Server: {account_info.server}")
    print(f"👤 Account: {account_info.login}")
    print(f"💰 Balance: ${account_info.balance:,.2f}")
    print(f"🏢 Company: {account_info.company}")
    
    # Detect broker type for better symbol selection
    server_name = account_info.server.upper()
    broker_type = "Unknown"
    
    if 'FBS' in server_name or 'DEMO' in server_name:
        broker_type = "FBS Demo"
        print(f"🔧 Detected: {broker_type} - Will prioritize 'w' suffix symbols")
    elif 'XM' in server_name:
        broker_type = "XM Global"
        print(f"🔧 Detected: {broker_type} - Will use standard symbol names")
    elif 'EXNESS' in server_name:
        broker_type = "Exness"
        print(f"🔧 Detected: {broker_type} - Will use 'm' suffix for some symbols")
    else:
        print(f"🔧 Broker: {server_name} - Will try all symbol variants")
    
    # --- Download Parameters ---
    start_date = datetime(2020, 1, 1)  # 4+ years of data
    end_date = datetime.now()
    
    print(f"\n📊 Downloading data from {start_date.date()} to {end_date.date()}")
    
    downloaded_files = []
    failed_symbols = []
    index_files = []
    forex_files = []
    commodity_files = []
    
    # Download data for all popular symbols
    all_symbols = {**POPULAR_SYMBOLS, **CUSTOM_SYMBOLS}  # Merge popular and custom symbols
    
    if CUSTOM_SYMBOLS:
        print(f"\n🎯 Custom symbols added: {list(CUSTOM_SYMBOLS.keys())}")
    
    for symbol, timeframe in all_symbols.items():
        try:
            file_path = download_symbol_data(symbol, timeframe, start_date, end_date)
            if file_path:
                downloaded_files.append(file_path)
                
                # Categorize files for better organization
                if any(idx in symbol.upper() for idx in ['US30', 'US100', 'US500', 'DE30', 'UK100', 'JP225']):
                    index_files.append(file_path)
                elif symbol.upper() in ['EURUSD', 'GBPUSD', 'USDJPY', 'AUDUSD'] or symbol.upper().replace('W', '') in ['EURUSD', 'GBPUSD', 'USDJPY', 'AUDUSD']:
                    forex_files.append(file_path)
                elif 'XAU' in symbol.upper() or 'OIL' in symbol.upper():
                    commodity_files.append(file_path)
            else:
                failed_symbols.append(symbol)
        except Exception as e:
            print(f"❌ Error downloading {symbol}: {e}")
            failed_symbols.append(symbol)
    
    # Cleanup
    mt5.shutdown() # pyright: ignore
    
    # Enhanced Summary
    print("\n🎉 Download Complete!")
    print(f"✅ Successfully downloaded: {len(downloaded_files)} files")
    print(f"❌ Failed downloads: {len(failed_symbols)} symbols")
    
    if index_files:
        print(f"\n📈 Index Data ({len(index_files)} files):")
        for file_path in index_files:
            filename = os.path.basename(file_path)
            print(f"   • {filename} - Use with INDEX_MOMENTUM or INDEX_BREAKOUT_PRO")
    
    if forex_files:
        print(f"\n💱 Forex Data ({len(forex_files)} files):")
        for file_path in forex_files[:5]:  # Show first 5
            filename = os.path.basename(file_path)
            print(f"   • {filename}")
        if len(forex_files) > 5:
            print(f"   • ... and {len(forex_files) - 5} more forex pairs")
    
    if commodity_files:
        print(f"\n🥇 Commodity Data ({len(commodity_files)} files):")
        for file_path in commodity_files:
            filename = os.path.basename(file_path)
            print(f"   • {filename} - Use conservative settings")
    
    if failed_symbols:
        print(f"\n⚠️  Failed symbols ({len(failed_symbols)}):")
        for symbol in failed_symbols[:10]:  # Show first 10
            print(f"   • {symbol}")
        if len(failed_symbols) > 10:
            print(f"   • ... and {len(failed_symbols) - 10} more symbols")
    
    print("\n💡 QuantumBotX Strategy Recommendations:")
    if index_files:
        print("   📈 For INDEX trading:")
        print("      • Beginners: Try INDEX_MOMENTUM strategy first")
        print("      • Advanced: Use INDEX_BREAKOUT_PRO for institutional patterns")
        print("      • Best symbols: US30, US100, US500, DE30")
    
    if forex_files:
        print("   💱 For FOREX trading:")
        print("      • Beginners: Start with MA_CROSSOVER on EURUSD")
        print("      • Intermediate: Try RSI_CROSSOVER strategy")
        print("      • Advanced: Use PULSE_SYNC for multi-indicator analysis")
    
    if commodity_files:
        print("   🥇 For COMMODITIES:")
        print("      • XAUUSD: Use TURTLE_BREAKOUT with conservative settings")
        print("      • Oil: Apply trend-following strategies during trending markets")
    
    print("\n🔧 Setup Instructions:")
    print("   1. Upload CSV files via QuantumBotX web interface")
    print("   2. Start with demo accounts before live trading")
    print("   3. Use lot size 0.01 for initial testing")
    print("   4. Index strategies work best during market hours")
    
    print("\n👨‍💻 Manual Symbol Download:")
    print("   # To download additional symbols, modify the CUSTOM_SYMBOLS dictionary")
    print("   # Or use the helper functions:")
    print("   # add_custom_symbol('EURAUD')")
    print("   # download_custom_symbol('EURAUD')")
    
    print(f"\n🔌 Connected to: {SERVER} (Account: {ACCOUNT})")
    print(f"🔄 Broker Type: {broker_type}")
    
    # Show sample usage for manual downloads
    print("\n📚 Sample Manual Usage:")
    print("   from download_data import download_custom_symbol, add_custom_symbol")
    print("   add_custom_symbol('EURAUD')  # Add to list")
    print("   download_custom_symbol('GBPCAD')  # Download immediately")
    
if __name__ == "__main__":
    main()