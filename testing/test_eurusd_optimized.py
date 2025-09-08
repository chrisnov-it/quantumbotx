#!/usr/bin/env python3
# test_eurusd_optimized.py - EURUSD Optimized for Current Market Conditions

import sys
import os
import pandas as pd

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_optimized_eurusd_strategies():
    """Test ultra-conservative EURUSD strategies for current market conditions"""
    
    print("🎯 EURUSD Optimized Strategy Testing")
    print("=" * 70)
    print("💡 Based on analysis: EURUSD is in sideways/ranging market")
    print("🔧 Using ultra-conservative parameters + mean reversion approach")
    
    try:
        from core.backtesting.enhanced_engine import run_enhanced_backtest
        from core.strategies.strategy_map import STRATEGY_MAP
        
        # Load EURUSD data
        csv_file = 'lab/backtest_data/EURUSD_H1_data.csv'
        df = pd.read_csv(csv_file, parse_dates=['time'])
        
        # Use recent data but smaller sample for current conditions
        test_df = df.tail(1500).copy()  # Last 1500 bars = ~2 months
        print(f"📊 Testing period: {test_df['time'].min()} to {test_df['time'].max()}")
        print(f"Data points: {len(test_df)} bars")
        
        # ULTRA-CONSERVATIVE strategies optimized for ranging EURUSD
        optimized_strategies = [
            {
                'name': 'ULTRA-CONSERVATIVE MA_CROSSOVER',
                'strategy_id': 'MA_CROSSOVER',
                'params': {
                    'fast_period': 5,   # Very fast for quick entries
                    'slow_period': 15,  # Short slow period for ranging market
                    'risk_percent': 0.3,  # Ultra low risk
                    'sl_atr_multiplier': 1.5,  # Tight stop loss
                    'tp_atr_multiplier': 2.5   # Conservative take profit
                }
            },
            {
                'name': 'SCALPING MA_CROSSOVER',
                'strategy_id': 'MA_CROSSOVER',
                'params': {
                    'fast_period': 3,   # Very fast scalping
                    'slow_period': 8,   # Quick signals
                    'risk_percent': 0.2,  # Micro risk
                    'sl_atr_multiplier': 1.2,  # Very tight SL
                    'tp_atr_multiplier': 2.0   # Quick profit taking
                }
            },
            {
                'name': 'MEAN REVERSION RSI',
                'strategy_id': 'RSI_CROSSOVER',
                'params': {
                    'rsi_period': 7,    # Faster RSI for ranging
                    'rsi_ma_period': 3, # Very fast smoothing
                    'trend_filter_period': 20,  # Shorter trend filter
                    'risk_percent': 0.4,
                    'sl_atr_multiplier': 1.5,
                    'tp_atr_multiplier': 2.5
                }
            },
            {
                'name': 'MICRO BREAKOUT',
                'strategy_id': 'TURTLE_BREAKOUT', 
                'params': {
                    'entry_period': 8,  # Very short breakout period
                    'exit_period': 4,   # Quick exit
                    'risk_percent': 0.3,
                    'sl_atr_multiplier': 1.3,
                    'tp_atr_multiplier': 2.0
                }
            },
            {
                'name': 'BOLLINGER REVERSION (If Available)',
                'strategy_id': 'BOLLINGER_REVERSION',
                'params': {
                    'bb_period': 20,
                    'bb_std': 2.0,
                    'risk_percent': 0.4,
                    'sl_atr_multiplier': 1.5,
                    'tp_atr_multiplier': 2.5
                }
            }
        ]
        
        engine_config = {
            'enable_spread_costs': True,
            'enable_slippage': True,
            'enable_realistic_execution': True
        }
        
        results = []
        
        for strategy_config in optimized_strategies:
            print(f"\n🧪 Testing: {strategy_config['name']}")
            print("-" * 50)
            
            strategy_id = strategy_config['strategy_id']
            params = strategy_config['params']
            
            # Check if strategy exists
            if strategy_id not in STRATEGY_MAP:
                print(f"❌ Strategy {strategy_id} not found - skipping")
                continue
            
            print(f"Ultra-Conservative Parameters: {params}")
            
            # Run backtest
            result = run_enhanced_backtest(
                strategy_id,
                params,
                test_df,
                symbol_name='EURUSD',
                engine_config=engine_config
            )
            
            if 'error' in result:
                print(f"❌ Error: {result['error']}")
                continue
            
            # Extract metrics
            total_trades = result.get('total_trades', 0)
            gross_profit = result.get('total_profit_usd', 0)
            spread_costs = result.get('total_spread_costs', 0)
            net_profit = result.get('net_profit_after_costs', 0)
            win_rate = result.get('win_rate_percent', 0)
            max_drawdown = result.get('max_drawdown_percent', 0)
            
            print(f"📊 Ultra-Conservative Results:")
            print(f"  Trades: {total_trades}")
            print(f"  Win Rate: {win_rate:.1f}%")
            print(f"  Net Profit: ${net_profit:.2f}")
            print(f"  Max Drawdown: {max_drawdown:.2f}%")
            print(f"  Spread Costs: ${spread_costs:.2f}")
            
            # Ultra-conservative assessment
            if total_trades > 0:
                profit_per_trade = net_profit / total_trades
                print(f"  Profit/Trade: ${profit_per_trade:.2f}")
                
                # Quality for ultra-conservative approach
                quality_score = 0
                if net_profit > -50:  # Loss tolerance
                    quality_score += 1
                if max_drawdown < 10:  # Very low drawdown
                    quality_score += 2
                if win_rate > 30:  # Decent win rate
                    quality_score += 1
                if total_trades >= 10:  # Sufficient trades
                    quality_score += 1
                
                if quality_score >= 4:
                    print(f"  🏆 EXCELLENT: Ultra-conservative approach working!")
                elif quality_score >= 3:
                    print(f"  ✅ GOOD: Acceptable for ranging market")
                elif quality_score >= 2:
                    print(f"  ⚠️ FAIR: Needs minor adjustments")
                else:
                    print(f"  ❌ POOR: Strategy not suitable")
            else:
                print(f"  ❌ No trades - too conservative")
            
            results.append({
                'name': strategy_config['name'],
                'trades': total_trades,
                'net_profit': net_profit,
                'win_rate': win_rate,
                'max_drawdown': max_drawdown,
                'quality_score': quality_score if total_trades > 0 else 0
            })
        
        # Find best ultra-conservative approach
        print(f"\n🎯 EURUSD Ultra-Conservative Ranking")
        print("=" * 70)
        
        # Sort by quality score, then by net profit
        results.sort(key=lambda x: (x['quality_score'], x['net_profit']), reverse=True)
        
        for i, result in enumerate(results):
            if result['trades'] > 0:
                emoji = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣"][min(i, 4)]
                print(f"{emoji} {result['name']}")
                print(f"    Profit: ${result['net_profit']:.2f} | Win Rate: {result['win_rate']:.1f}% | Drawdown: {result['max_drawdown']:.1f}% | Score: {result['quality_score']}/5")
        
        # Recommendation
        if results and results[0]['quality_score'] >= 3:
            best = results[0]
            print(f"\n🎉 RECOMMENDED FOR CURRENT EURUSD CONDITIONS:")
            print(f"   Strategy: {best['name']}")
            print(f"   Why it works: Ultra-conservative approach for ranging market")
            print(f"   Expected: ${best['net_profit']:.2f} profit with {best['max_drawdown']:.1f}% max drawdown")
            
            # Create optimized bot parameters
            print(f"\n🤖 OPTIMIZED BOT PARAMETERS FOR EURUSD:")
            for strategy_config in optimized_strategies:
                if strategy_config['name'] == best['name']:
                    print(f"   Strategy: {strategy_config['strategy_id']}")
                    for param, value in strategy_config['params'].items():
                        print(f"   {param}: {value}")
                    break
            
            print(f"\n💡 LONDON SESSION TIPS:")
            print(f"   • Use smaller position sizes during 1-4 PM London")
            print(f"   • Take profits quickly in ranging market")
            print(f"   • Monitor for breakout setups at session open")
            print(f"   • Current conditions favor mean reversion over trend following")
            
            return True
        else:
            print(f"\n⚠️ DIFFICULT MARKET CONDITIONS:")
            print(f"   • EURUSD appears to be in challenging ranging phase")
            print(f"   • Consider waiting for clearer trend signals")
            print(f"   • Focus on indices (like US500) which showed better performance")
            print(f"   • Or test with M15/M30 timeframes for more opportunities")
            
            return False
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def suggest_alternative_pairs():
    """Suggest alternative forex pairs based on current analysis"""
    
    print(f"\n🌍 Alternative Forex Pairs for London Session")
    print("=" * 50)
    
    # Check what data we have available
    data_dir = 'lab/backtest_data'
    forex_pairs = []
    
    for file in os.listdir(data_dir):
        if file.endswith('_H1_data.csv'):
            symbol = file.replace('_H1_data.csv', '')
            if symbol in ['GBPUSD', 'EURGBP', 'GBPJPY', 'EURJPY', 'USDCHF']:
                forex_pairs.append(symbol)
    
    print(f"📊 Available Forex Pairs for London Session:")
    for pair in forex_pairs:
        if 'GBP' in pair:
            print(f"  🇬🇧 {pair} - High volatility during London session")
        elif 'EUR' in pair:
            print(f"  🇪🇺 {pair} - European focus, good London activity")
        else:
            print(f"  💱 {pair} - Cross-pair opportunity")
    
    print(f"\n💡 RECOMMENDATIONS based on current market:")
    print(f"   1. 🇬🇧 GBPUSD - Higher volatility than EURUSD")
    print(f"   2. 🇪🇺 EURGBP - Cross-pair, different dynamics")
    print(f"   3. 🥇 Continue with US500 - Your winning strategy!")
    print(f"   4. 🚀 Wait for EURUSD breakout signals")

if __name__ == "__main__":
    print("🎯 EURUSD Market Condition Optimization")
    print("=" * 80)
    
    success = test_optimized_eurusd_strategies()
    suggest_alternative_pairs()
    
    if success:
        print(f"\n✅ OPTIMIZATION COMPLETE!")
        print(f"🎯 Found ultra-conservative approach for current EURUSD conditions")
    else:
        print(f"\n💡 STRATEGIC RECOMMENDATION:")
        print(f"🏆 Stick with US500 + Set 3 parameters (your winning combination!)")
        print(f"⏰ Monitor EURUSD for better trend opportunities")
        print(f"🔄 Consider testing GBPUSD for higher London volatility")