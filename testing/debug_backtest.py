#!/usr/bin/env python3
"""
Debug script for backtesting history issues
This script will help identify problems with profit calculations and data display
"""

import sqlite3
import json
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def check_database():
    """Check the database structure and data"""
    try:
        conn = sqlite3.connect('bots.db')
        cursor = conn.cursor()
        
        # Check if table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='backtest_results'")
        table_exists = cursor.fetchone()
        
        if not table_exists:
            print("❌ ERROR: backtest_results table does not exist!")
            return False
            
        print("✅ backtest_results table exists")
        
        # Check table schema
        cursor.execute("PRAGMA table_info(backtest_results)")
        columns = cursor.fetchall()
        print("\n📋 Database Schema:")
        for col in columns:
            print(f"  - {col[1]} ({col[2]})")
        
        # Check data count
        cursor.execute("SELECT COUNT(*) FROM backtest_results")
        count = cursor.fetchone()[0]
        print(f"\n📊 Total records: {count}")
        
        if count == 0:
            print("❌ No backtest data found!")
            return False
        
        # Check recent records
        cursor.execute("""
            SELECT id, strategy_name, total_profit_usd, total_trades, 
                   equity_curve, trade_log, timestamp
            FROM backtest_results 
            ORDER BY timestamp DESC 
            LIMIT 3
        """)
        
        records = cursor.fetchall()
        print("\n🔍 Sample Records:")
        
        for i, record in enumerate(records, 1):
            id_, strategy, profit, trades, equity, trade_log, timestamp = record
            print(f"\n  Record {i}:")
            print(f"    ID: {id_}")
            print(f"    Strategy: {strategy}")
            print(f"    Total Profit USD: {profit}")
            print(f"    Total Trades: {trades}")
            print(f"    Timestamp: {timestamp}")
            
            # Check JSON fields
            try:
                equity_data = json.loads(equity) if equity else []
                print(f"    Equity Curve Length: {len(equity_data)}")
                if equity_data:
                    print(f"    Initial Capital: {equity_data[0]}")
                    print(f"    Final Capital: {equity_data[-1]}")
                    print(f"    Calculated Profit: {equity_data[-1] - equity_data[0]}")
            except json.JSONDecodeError:
                print(f"    ❌ ERROR: Invalid equity_curve JSON")
            
            try:
                trade_data = json.loads(trade_log) if trade_log else []
                print(f"    Trade Log Length: {len(trade_data)}")
                if trade_data:
                    total_trade_profit = sum(t.get('profit', 0) for t in trade_data)
                    print(f"    Sum of Trade Profits: {total_trade_profit}")
            except json.JSONDecodeError:
                print(f"    ❌ ERROR: Invalid trade_log JSON")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Database Error: {e}")
        return False

def check_api_response():
    """Test the API response format"""
    try:
        from core.db.queries import get_all_backtest_history
        
        print("\n🌐 Testing API Response:")
        history = get_all_backtest_history()
        
        if not history:
            print("❌ No data returned from get_all_backtest_history()")
            return False
            
        print(f"✅ Returned {len(history)} records")
        
        # Check first record structure
        first_record = history[0]
        print(f"\n📋 First Record Structure:")
        for key, value in first_record.items():
            value_type = type(value).__name__
            if isinstance(value, str) and len(value) > 100:
                value_preview = value[:100] + "..."
            else:
                value_preview = value
            print(f"  - {key}: {value_preview} ({value_type})")
        
        return True
        
    except Exception as e:
        print(f"❌ API Error: {e}")
        return False

def simulate_simple_backtest():
    """Run a simple backtest to verify the engine works"""
    try:
        import pandas as pd
        import numpy as np
        from core.backtesting.engine import run_backtest
        
        print("\n🧪 Testing Backtest Engine:")
        
        # Create simple test data
        dates = pd.date_range('2023-01-01', periods=100, freq='H')
        price = 1950 + np.cumsum(np.random.randn(100) * 0.5)
        
        df = pd.DataFrame({
            'time': dates,
            'XAUUSD_open': price,
            'XAUUSD_high': price + np.random.rand(100) * 2,
            'XAUUSD_low': price - np.random.rand(100) * 2,
            'XAUUSD_close': price,
            'XAUUSD_volume': np.random.randint(1000, 5000, 100)
        })
        
        # Set proper column names for the engine
        df = df.rename(columns={
            'XAUUSD_open': 'open',
            'XAUUSD_high': 'high', 
            'XAUUSD_low': 'low',
            'XAUUSD_close': 'close',
            'XAUUSD_volume': 'volume'
        })
        
        params = {
            'lot_size': 2.0,  # 2% risk
            'sl_pips': 2.0,   # 2x ATR for SL
            'tp_pips': 4.0    # 4x ATR for TP
        }
        
        # Test with MA_CROSSOVER strategy
        result = run_backtest('MA_CROSSOVER', params, df)
        
        if 'error' in result:
            print(f"❌ Backtest Error: {result['error']}")
            return False
            
        print("✅ Backtest completed successfully!")
        print(f"  Strategy: {result.get('strategy_name', 'Unknown')}")
        print(f"  Total Trades: {result.get('total_trades', 0)}")
        print(f"  Total Profit USD: {result.get('total_profit_usd', 0)}")
        print(f"  Final Capital: {result.get('final_capital', 0)}")
        print(f"  Win Rate: {result.get('win_rate_percent', 0)}%")
        print(f"  Equity Curve Length: {len(result.get('equity_curve', []))}")
        print(f"  Trades Length: {len(result.get('trades', []))}")
        
        return True
        
    except Exception as e:
        print(f"❌ Backtest Engine Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main diagnostic function"""
    print("🔍 QuantumBotX Backtest History Diagnostic")
    print("=" * 50)
    
    # Check database
    db_ok = check_database()
    
    # Check API
    api_ok = check_api_response()
    
    # Test engine
    engine_ok = simulate_simple_backtest()
    
    print("\n" + "=" * 50)
    print("📊 DIAGNOSTIC SUMMARY:")
    print(f"  Database: {'✅ OK' if db_ok else '❌ FAILED'}")
    print(f"  API: {'✅ OK' if api_ok else '❌ FAILED'}")
    print(f"  Engine: {'✅ OK' if engine_ok else '❌ FAILED'}")
    
    if all([db_ok, api_ok, engine_ok]):
        print("\n🎉 All systems appear to be working!")
        print("   If you're still seeing issues in the web interface:")
        print("   1. Check browser console for JavaScript errors")
        print("   2. Verify Chart.js is loading properly")
        print("   3. Check network requests in browser dev tools")
    else:
        print("\n❌ Issues detected. Check the output above for details.")

if __name__ == "__main__":
    main()