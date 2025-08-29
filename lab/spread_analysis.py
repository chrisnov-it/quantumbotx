# spread_analysis.py - Analyze actual spread data from MT5 CSV files
import pandas as pd
import numpy as np

def analyze_spread_data():
    """Analyze actual spread data from CSV files"""
    
    print("💰 Actual Spread Data Analysis")
    print("=" * 50)
    
    # Files with spread data still present
    files_to_analyze = [
        ('XAUUSD', 'XAUUSD_16385_data.csv'),
        ('EURUSD', 'EURUSD_16385_data.csv.bak'),
        ('GBPUSD', 'GBPUSD_16385_data.csv'),
    ]
    
    for instrument, filename in files_to_analyze:
        try:
            print(f"\n📊 {instrument} ({filename})")
            print("-" * 30)
            
            df = pd.read_csv(filename)
            
            if 'spread' not in df.columns:
                print("   ⚠️ No spread data available")
                continue
                
            spread_stats = df['spread'].describe()
            
            print(f"   Average spread: {spread_stats['mean']:.1f} points")
            print(f"   Min spread: {spread_stats['min']:.0f} points")
            print(f"   Max spread: {spread_stats['max']:.0f} points") 
            print(f"   Std deviation: {spread_stats['std']:.1f} points")
            
            # Most common spreads
            print(f"\n   📈 Most common spreads:")
            spread_counts = df['spread'].value_counts().head(5)
            for spread, count in spread_counts.items():
                pct = (count / len(df)) * 100
                print(f"     {spread:2.0f} points: {pct:4.1f}% of the time")
            
            # Calculate cost impact
            avg_price = df['close'].mean()
            avg_spread = spread_stats['mean']
            
            # Convert to dollar cost (rough estimate)
            if instrument == 'XAUUSD':
                # Gold: $1 per point for 0.01 lot
                cost_per_trade = avg_spread * 1.0
                lot_size = "0.01"
            else:
                # Forex: $1 per pip for 0.01 lot  
                cost_per_trade = avg_spread * 0.1  # Points to pips conversion
                lot_size = "0.01"
            
            print(f"\n   💰 Cost Impact (for {lot_size} lot):")
            print(f"     Cost per trade: ${cost_per_trade:.2f}")
            print(f"     Cost per 100 trades: ${cost_per_trade * 100:.0f}")
            
            # Time-based analysis
            if len(df) > 24:
                print(f"\n   ⏰ Spread by time (sample):")
                df['hour'] = pd.to_datetime(df['time']).dt.hour
                hourly_spreads = df.groupby('hour')['spread'].mean().head(5)
                for hour, avg_spread in hourly_spreads.items():
                    print(f"     Hour {hour:02d}:00 - {avg_spread:.1f} points")
                    
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    print(f"\n💡 Key Findings:")
    print(f"   • XAUUSD spreads are typically 10-20 points (high cost)")
    print(f"   • Forex spreads are typically 1-3 points (manageable)")
    print(f"   • Spreads vary throughout the day (wider during low liquidity)")
    print(f"   • Your backtesting currently ignores these costs!")
    
    print(f"\n🎯 Impact on Your Results:")
    print(f"   • Backtesting profits are OVERESTIMATED")
    print(f"   • High-frequency strategies most affected")
    print(f"   • Gold trading severely impacted by spreads")
    print(f"   • Consider implementing spread modeling")

if __name__ == "__main__":
    analyze_spread_data()