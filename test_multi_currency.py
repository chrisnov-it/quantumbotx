#!/usr/bin/env python3
"""
Multi-Currency Strategy Performance Tester
Tests QuantumBotX Hybrid strategy on different currency pairs to compare performance
"""

import sys
import os
import pandas as pd
import numpy as np

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def create_forex_data(symbol, base_price, volatility, periods=1000):
    """Create realistic forex data for testing"""
    dates = pd.date_range('2023-01-01', periods=periods, freq='h')
    
    # Different volatility characteristics for different pairs
    if 'USD' in symbol and 'JPY' in symbol:
        # JPY pairs have larger price movements
        price_changes = np.random.randn(periods) * volatility * 0.5
    elif 'XAU' in symbol:
        # Gold has much higher volatility
        price_changes = np.random.randn(periods) * volatility * 3.0
    else:
        # Standard forex pairs
        price_changes = np.random.randn(periods) * volatility
    
    # Add trending behavior
    trend = np.linspace(0, volatility * 10, periods) * (1 if np.random.random() > 0.5 else -1)
    prices = base_price + np.cumsum(price_changes) + trend * 0.1
    
    # Ensure prices stay reasonable
    prices = np.clip(prices, base_price * 0.8, base_price * 1.2)
    
    df = pd.DataFrame({
        'time': dates,
        'open': prices,
        'high': prices + np.random.uniform(0, volatility * 0.5, periods),
        'low': prices - np.random.uniform(0, volatility * 0.5, periods),
        'close': prices + np.random.uniform(-volatility * 0.2, volatility * 0.2, periods),
        'volume': np.random.randint(100, 1000, periods)
    })
    
    # Ensure OHLC integrity
    df['high'] = df[['high', 'close', 'open']].max(axis=1)
    df['low'] = df[['low', 'close', 'open']].min(axis=1)
    
    return df

def test_strategy_on_pair(symbol, base_price, volatility):
    """Test QuantumBotX Hybrid strategy on a specific currency pair"""
    from core.backtesting.engine import run_backtest
    
    print(f"\\n📈 Testing {symbol}")
    print("=" * 50)
    
    # Create test data
    df = create_forex_data(symbol, base_price, volatility)
    
    print(f"📊 Data range: ${df['close'].min():.5f} - ${df['close'].max():.5f}")
    print(f"📊 Average volatility: {df['close'].std():.5f}")
    
    # Standard parameters for QuantumBotX Hybrid
    params = {
        'lot_size': 1.0,        # 1% risk
        'sl_pips': 2.0,         # 2x ATR for SL
        'tp_pips': 4.0,         # 4x ATR for TP
        'adx_period': 14,
        'adx_threshold': 25,
        'ma_fast_period': 20,
        'ma_slow_period': 50,
        'bb_length': 20,
        'bb_std': 2.0,
        'trend_filter_period': 200
    }
    
    try:
        # Run backtest with symbol name for proper detection
        result = run_backtest('QUANTUMBOTX_HYBRID', params, df, symbol_name=symbol)
        
        if 'error' in result:
            print(f"❌ Error: {result['error']}")
            return None
        
        # Extract metrics
        profit = result.get('total_profit_usd', 0)
        trades = result.get('total_trades', 0)
        final_capital = result.get('final_capital', 10000)
        drawdown = result.get('max_drawdown_percent', 0)
        win_rate = result.get('win_rate_percent', 0)
        wins = result.get('wins', 0)
        losses = result.get('losses', 0)
        
        # Calculate additional metrics
        profit_percentage = (profit / 10000) * 100
        avg_profit_per_trade = profit / trades if trades > 0 else 0
        
        print(f"📊 Results:")
        print(f"   Total Profit: ${profit:,.2f} ({profit_percentage:+.2f}%)")
        print(f"   Total Trades: {trades}")
        print(f"   Final Capital: ${final_capital:,.2f}")
        print(f"   Max Drawdown: {drawdown:.2f}%")
        print(f"   Win Rate: {win_rate:.2f}%")
        print(f"   Wins/Losses: {wins}/{losses}")
        print(f"   Avg Profit/Trade: ${avg_profit_per_trade:.2f}")
        
        # Risk assessment
        is_safe = (
            abs(profit) < 5000 and      # Reasonable profit/loss range
            drawdown < 25 and           # Acceptable drawdown
            final_capital > 7500 and    # Account preservation
            trades >= 5                 # Sufficient trade sample
        )
        
        performance_rating = "UNKNOWN"
        if trades == 0:
            performance_rating = "NO TRADES"
        elif profit > 1000 and win_rate > 60 and drawdown < 10:
            performance_rating = "EXCELLENT"
        elif profit > 500 and win_rate > 50 and drawdown < 15:
            performance_rating = "GOOD"
        elif profit > 0 and drawdown < 20:
            performance_rating = "FAIR"
        elif abs(profit) < 1000 and drawdown < 25:
            performance_rating = "POOR"
        else:
            performance_rating = "DANGEROUS"
        
        status = "✅ SAFE" if is_safe else "⚠️ RISKY"
        print(f"\\n{status} | Performance: {performance_rating}")
        
        return {
            'symbol': symbol,
            'profit': profit,
            'profit_percentage': profit_percentage,
            'trades': trades,
            'final_capital': final_capital,
            'drawdown': drawdown,
            'win_rate': win_rate,
            'wins': wins,
            'losses': losses,
            'avg_profit_per_trade': avg_profit_per_trade,
            'is_safe': is_safe,
            'performance_rating': performance_rating,
            'volatility': df['close'].std()
        }
        
    except Exception as e:
        print(f"❌ Exception: {e}")
        import traceback
        traceback.print_exc()
        return None

def main():
    """Main testing function"""
    print("🌍 Multi-Currency Strategy Performance Analysis")
    print("=" * 70)
    print("Testing QuantumBotX Hybrid Strategy on Different Currency Pairs")
    print("=" * 70)
    
    # Define currency pairs to test
    test_pairs = [
        # Major Forex Pairs
        ('EURUSD', 1.1000, 0.0015),    # EUR/USD - low volatility
        ('GBPUSD', 1.2500, 0.0020),    # GBP/USD - medium volatility
        ('USDJPY', 110.00, 0.5000),    # USD/JPY - different price range
        ('USDCHF', 0.9200, 0.0018),    # USD/CHF - low volatility
        ('AUDUSD', 0.7300, 0.0025),    # AUD/USD - commodity currency
        ('NZDUSD', 0.6800, 0.0030),    # NZD/USD - higher volatility
        
        # Cross Pairs
        ('EURGBP', 0.8800, 0.0012),    # EUR/GBP - very low volatility
        ('EURJPY', 120.00, 0.6000),    # EUR/JPY - cross pair
        
        # Commodity/Metals
        ('XAUUSD', 1950.0, 12.000),    # Gold - high volatility (our problem child)
        ('USDCAD', 1.3500, 0.0022),    # USD/CAD - oil-related
    ]
    
    results = []
    
    for symbol, base_price, volatility in test_pairs:
        result = test_strategy_on_pair(symbol, base_price, volatility)
        if result:
            results.append(result)
    
    # Analysis summary
    print("\\n" + "=" * 70)
    print("📊 COMPREHENSIVE ANALYSIS SUMMARY")
    print("=" * 70)
    
    if not results:
        print("❌ No successful tests completed")
        return
    
    # Sort by performance
    results.sort(key=lambda x: x['profit'], reverse=True)
    
    print("\\n🏆 Performance Ranking:")
    print("Symbol    | Profit      | Trades | Win Rate | Drawdown | Rating")
    print("-" * 65)
    
    for result in results:
        symbol = result['symbol']
        profit = result['profit']
        trades = result['trades']
        win_rate = result['win_rate']
        drawdown = result['drawdown']
        rating = result['performance_rating']
        
        print(f"{symbol:9} | ${profit:9.2f} | {trades:6} | {win_rate:7.1f}% | {drawdown:7.1f}% | {rating}")
    
    # Statistical analysis
    profitable_pairs = [r for r in results if r['profit'] > 0]
    safe_pairs = [r for r in results if r['is_safe']]
    
    print(f"\\n📈 Statistics:")
    print(f"   Total Pairs Tested: {len(results)}")
    print(f"   Profitable Pairs: {len(profitable_pairs)} ({len(profitable_pairs)/len(results)*100:.1f}%)")
    print(f"   Safe Pairs: {len(safe_pairs)} ({len(safe_pairs)/len(results)*100:.1f}%)")
    
    avg_profit = sum(r['profit'] for r in results) / len(results)
    avg_win_rate = sum(r['win_rate'] for r in results) / len(results)
    avg_drawdown = sum(r['drawdown'] for r in results) / len(results)
    
    print(f"   Average Profit: ${avg_profit:.2f}")
    print(f"   Average Win Rate: {avg_win_rate:.1f}%")
    print(f"   Average Drawdown: {avg_drawdown:.1f}%")
    
    # Best and worst performers
    if results:
        best = results[0]
        worst = results[-1]
        
        print(f"\\n🥇 Best Performer: {best['symbol']}")
        print(f"   Profit: ${best['profit']:,.2f} ({best['profit_percentage']:+.2f}%)")
        print(f"   Win Rate: {best['win_rate']:.1f}%")
        print(f"   Rating: {best['performance_rating']}")
        
        print(f"\\n🥉 Worst Performer: {worst['symbol']}")
        print(f"   Profit: ${worst['profit']:,.2f} ({worst['profit_percentage']:+.2f}%)")
        print(f"   Win Rate: {worst['win_rate']:.1f}%")
        print(f"   Rating: {worst['performance_rating']}")
    
    # XAUUSD specific analysis
    xauusd_result = next((r for r in results if r['symbol'] == 'XAUUSD'), None)
    if xauusd_result:
        print(f"\\n🥇 XAUUSD Analysis:")
        print(f"   Previous Issue: -$15,231.28 loss, 152.31% drawdown")
        print(f"   Current Result: ${xauusd_result['profit']:,.2f} profit/loss, {xauusd_result['drawdown']:.2f}% drawdown")
        
        if abs(xauusd_result['profit']) < 15231.28:
            improvement = ((15231.28 - abs(xauusd_result['profit'])) / 15231.28) * 100
            print(f"   Improvement: {improvement:.1f}% reduction in risk")
        
        if xauusd_result['is_safe']:
            print("   ✅ XAUUSD is now trading safely with the new protection!")
        else:
            print("   ⚠️ XAUUSD still needs attention")
    
    print("\\n💡 Conclusions:")
    if len(safe_pairs) >= len(results) * 0.8:
        print("   ✅ Strategy performs well across most currency pairs")
    elif len(profitable_pairs) >= len(results) * 0.6:
        print("   🟡 Strategy shows promise but needs optimization")
    else:
        print("   ❌ Strategy may need significant improvements")
    
    print("   • Test with real historical data for validation")
    print("   • Consider pair-specific parameter optimization")
    print("   • Monitor real trading performance closely")

if __name__ == "__main__":
    main()