# Test the enhanced download functionality
import sys
import os
from dotenv import load_dotenv

# Add project root to path and load environment
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)
load_dotenv(os.path.join(project_root, '.env'))

# Import the enhanced download script
from download_data import download_symbol_data, POPULAR_SYMBOLS
import MetaTrader5 as mt5
from datetime import datetime, timedelta

# Get credentials from environment
ACCOUNT = int(os.getenv('MT5_LOGIN', '0'))
PASSWORD = os.getenv('MT5_PASSWORD', '')
SERVER = os.getenv('MT5_SERVER', '')

def test_enhanced_download():
    """Test the enhanced download functionality"""
    
    # Initialize MT5
    if not mt5.initialize(login=ACCOUNT, password=PASSWORD, server=SERVER):
        print("❌ Failed to initialize MT5!", mt5.last_error())
        return
    
    print("✅ Successfully connected to XM MT5")
    print(f"📡 Server: {mt5.account_info().server}")
    print(f"👤 Account: {mt5.account_info().login}")
    
    # Test download for one symbol
    symbol = "EURUSD"
    timeframe = mt5.TIMEFRAME_H1
    
    # Download just 1 week of recent data for testing
    end_date = datetime.now()
    start_date = end_date - timedelta(days=7)
    
    print(f"\n📊 Testing download for {symbol}...")
    print(f"📅 Date range: {start_date.date()} to {end_date.date()}")
    
    file_path = download_symbol_data(symbol, timeframe, start_date, end_date, "test_data")
    
    if file_path:
        print(f"🎉 Test successful! File created: {file_path}")
        
        # Check file content
        import pandas as pd
        df = pd.read_csv(file_path)
        print(f"📈 Data preview:")
        print(f"   Rows: {len(df)}")
        print(f"   Columns: {list(df.columns)}")
        print(f"   Date range: {df['time'].min()} to {df['time'].max()}")
        print(f"\n   Sample data:")
        print(df.head(3).to_string())
        
    else:
        print("❌ Test failed")
    
    # Cleanup
    mt5.shutdown()
    
    # Show available symbols info
    print(f"\n💡 Enhanced script supports {len(POPULAR_SYMBOLS)} symbols:")
    for symbol in list(POPULAR_SYMBOLS.keys())[:10]:  # Show first 10
        print(f"   • {symbol}")
    if len(POPULAR_SYMBOLS) > 10:
        print(f"   ... and {len(POPULAR_SYMBOLS) - 10} more")

if __name__ == "__main__":
    test_enhanced_download()