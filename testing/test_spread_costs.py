#!/usr/bin/env python3
"""
Test the enhanced engine's spread cost calculations
Focus on the specific issue: Are spread costs destroying profitability?
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_spread_calculations():
    """Test spread cost calculations specifically"""
    print("💰 TESTING SPREAD COST CALCULATIONS")
    print("=" * 60)
    
    # Import the enhanced engine components
    from core.backtesting.enhanced_engine import EnhancedBacktestEngine, InstrumentConfig
    
    # Test EURUSD configuration
    eurusd_config = InstrumentConfig.get_config('EURUSD')
    print(f"EURUSD Config: {eurusd_config}")
    
    # Test spread calculation
    engine = EnhancedBacktestEngine(enable_spread_costs=True)
    
    # Realistic EURUSD trade
    lot_size = 0.5  # Half a lot
    spread_pips = eurusd_config['typical_spread_pips']
    
    spread_cost = engine.calculate_spread_cost(lot_size, spread_pips, eurusd_config)
    
    print(f"\nSpread calculation test:")
    print(f"Lot size: {lot_size}")
    print(f"Spread pips: {spread_pips}")
    print(f"Calculated spread cost: ${spread_cost:.2f}")
    
    # Manual calculation verification
    # For forex: $1 per pip per 0.01 lot (micro lot)
    expected_cost = spread_pips * 1.0 * (lot_size / 0.01)
    print(f"Expected spread cost: ${expected_cost:.2f}")
    
    if abs(spread_cost - expected_cost) < 0.01:
        print("✅ Spread calculation correct")
    else:
        print(f"❌ Spread calculation error! Expected: ${expected_cost:.2f}, Got: ${spread_cost:.2f}")
        return False
    
    # Test different lot sizes
    print(f"\nSpread costs for different lot sizes:")
    for lot in [0.01, 0.1, 0.5, 1.0, 2.0]:
        cost = engine.calculate_spread_cost(lot, spread_pips, eurusd_config)
        print(f"  {lot} lots: ${cost:.2f}")
        
        # Check if cost is reasonable (should be proportional)
        if cost > 100:  # Over $100 spread cost is suspicious for forex
            print(f"  ❌ WARNING: Very high spread cost for {lot} lots!")
    
    return True

def test_realistic_prices():
    """Test realistic entry/exit price calculations"""
    print(f"\n📊 TESTING REALISTIC PRICE CALCULATIONS")
    print("=" * 60)
    
    from core.backtesting.enhanced_engine import EnhancedBacktestEngine, InstrumentConfig
    
    engine = EnhancedBacktestEngine()
    config = InstrumentConfig.get_config('EURUSD')
    
    # Test parameters
    close_price = 1.1000
    spread_pips = config['typical_spread_pips']
    pip_size = config['pip_size']
    slippage_pips = config.get('slippage_pips', 0.5)
    
    print(f"Test parameters:")
    print(f"Close price: {close_price}")
    print(f"Spread: {spread_pips} pips")
    print(f"Pip size: {pip_size}")
    print(f"Slippage: {slippage_pips} pips")
    
    # Test BUY entry
    buy_entry = engine.calculate_realistic_entry_price('BUY', close_price, spread_pips, pip_size, slippage_pips)
    sell_entry = engine.calculate_realistic_entry_price('SELL', close_price, spread_pips, pip_size, slippage_pips)
    
    print(f"\nRealistic entry prices:")
    print(f"BUY entry: {buy_entry:.5f} (should be higher than close)")
    print(f"SELL entry: {sell_entry:.5f} (should be lower than close)")
    
    # Calculate expected values
    spread_cost = spread_pips * pip_size
    expected_buy = close_price + (spread_cost / 2) + (slippage_pips * pip_size)
    expected_sell = close_price - (spread_cost / 2) - (slippage_pips * pip_size)
    
    print(f"\nExpected values:")
    print(f"Expected BUY: {expected_buy:.5f}")
    print(f"Expected SELL: {expected_sell:.5f}")
    
    # Verify calculations
    if abs(buy_entry - expected_buy) < 0.00001 and abs(sell_entry - expected_sell) < 0.00001:
        print("✅ Entry price calculations correct")
    else:
        print("❌ Entry price calculation error!")
        return False
    
    # Test exit prices
    tp_price = close_price + 0.0020  # 20 pips profit target
    sl_price = close_price - 0.0010  # 10 pips stop loss
    
    buy_tp_exit = engine.calculate_realistic_exit_price('BUY', tp_price, spread_pips, pip_size, slippage_pips)
    buy_sl_exit = engine.calculate_realistic_exit_price('BUY', sl_price, spread_pips, pip_size, slippage_pips)
    
    print(f"\nExit prices for BUY position:")
    print(f"TP exit: {buy_tp_exit:.5f} (at {tp_price:.5f} target)")
    print(f"SL exit: {buy_sl_exit:.5f} (at {sl_price:.5f} target)")
    
    # The exit should be worse than the target due to spread/slippage
    if buy_tp_exit < tp_price and buy_sl_exit < sl_price:
        print("✅ Exit price calculations correct (accounts for spread/slippage)")
        return True
    else:
        print("❌ Exit price calculation error!")
        return False

def test_gold_vs_forex():
    """Compare Gold vs Forex configurations"""
    print(f"\n🥇 TESTING GOLD vs FOREX CONFIGURATIONS")
    print("=" * 60)
    
    from core.backtesting.enhanced_engine import InstrumentConfig
    
    eurusd_config = InstrumentConfig.get_config('EURUSD')
    xauusd_config = InstrumentConfig.get_config('XAUUSD')
    
    print("EURUSD Configuration:")
    for key, value in eurusd_config.items():
        print(f"  {key}: {value}")
    
    print("\nXAUUSD Configuration:")
    for key, value in xauusd_config.items():
        print(f"  {key}: {value}")
    
    # Test spread costs comparison
    from core.backtesting.enhanced_engine import EnhancedBacktestEngine
    engine = EnhancedBacktestEngine()
    
    lot_size = 0.1
    
    eurusd_spread = engine.calculate_spread_cost(lot_size, eurusd_config['typical_spread_pips'], eurusd_config)
    gold_spread = engine.calculate_spread_cost(lot_size, xauusd_config['typical_spread_pips'], xauusd_config)
    
    print(f"\nSpread costs for {lot_size} lots:")
    print(f"EURUSD: ${eurusd_spread:.2f}")
    print(f"XAUUSD: ${gold_spread:.2f}")
    
    if gold_spread > eurusd_spread * 5:  # Gold should be higher but not excessively
        print(f"⚠️  WARNING: Gold spread cost is {gold_spread/eurusd_spread:.1f}x higher than EURUSD!")
        if gold_spread > 100:  # Over $100 for 0.1 lot
            print("❌ CRITICAL: Gold spread costs are destroying profitability!")
            return False
    
    return True

def test_full_trade_simulation():
    """Simulate a complete trade with all costs"""
    print(f"\n🔄 FULL TRADE SIMULATION WITH COSTS")
    print("=" * 60)
    
    from core.backtesting.enhanced_engine import EnhancedBacktestEngine, InstrumentConfig
    
    # Test EURUSD trade
    config = InstrumentConfig.get_config('EURUSD')
    engine = EnhancedBacktestEngine()
    
    # Trade parameters
    capital = 10000.0
    risk_percent = 1.0  # 1%
    atr_value = 0.0010  # 10 pips
    sl_atr_multiplier = 2.0
    tp_atr_multiplier = 4.0
    
    # Calculate position size
    lot_size = engine.calculate_position_size('EURUSD', capital, risk_percent, atr_value * sl_atr_multiplier, atr_value, config)
    
    # Entry and exit
    close_price = 1.1000
    entry_price = engine.calculate_realistic_entry_price('BUY', close_price, config['typical_spread_pips'], config['pip_size'])
    
    sl_target = entry_price - (atr_value * sl_atr_multiplier)
    tp_target = entry_price + (atr_value * tp_atr_multiplier)
    
    sl_exit = engine.calculate_realistic_exit_price('BUY', sl_target, config['typical_spread_pips'], config['pip_size'])
    tp_exit = engine.calculate_realistic_exit_price('BUY', tp_target, config['typical_spread_pips'], config['pip_size'])
    
    # Calculate profits
    profit_multiplier = lot_size * config['contract_size']
    sl_profit = (sl_exit - entry_price) * profit_multiplier
    tp_profit = (tp_exit - entry_price) * profit_multiplier
    
    # Spread cost
    spread_cost = engine.calculate_spread_cost(lot_size, config['typical_spread_pips'], config)
    
    print(f"Trade Simulation:")
    print(f"Capital: ${capital:,.2f}")
    print(f"Risk: {risk_percent}%")
    print(f"Lot size: {lot_size:.2f}")
    print(f"Entry price: {entry_price:.5f}")
    print(f"SL target: {sl_target:.5f} → exit: {sl_exit:.5f}")
    print(f"TP target: {tp_target:.5f} → exit: {tp_exit:.5f}")
    print(f"Spread cost: ${spread_cost:.2f}")
    
    print(f"\nTrade outcomes:")
    print(f"If SL hit: ${sl_profit:.2f} - ${spread_cost:.2f} = ${sl_profit - spread_cost:.2f}")
    print(f"If TP hit: ${tp_profit:.2f} - ${spread_cost:.2f} = ${tp_profit - spread_cost:.2f}")
    
    # Check if spread cost is reasonable
    amount_to_risk = capital * (risk_percent / 100.0)
    spread_as_percent_of_risk = (spread_cost / amount_to_risk) * 100
    
    print(f"\nSpread cost analysis:")
    print(f"Amount risked: ${amount_to_risk:.2f}")
    print(f"Spread cost: ${spread_cost:.2f} ({spread_as_percent_of_risk:.1f}% of risk)")
    
    if spread_as_percent_of_risk > 20:  # If spread costs more than 20% of risk
        print("❌ CRITICAL: Spread costs are too high relative to risk!")
        print("   This could explain the poor backtest performance.")
        return False
    elif spread_as_percent_of_risk > 10:
        print("⚠️  WARNING: Spread costs are high")
        return True
    else:
        print("✅ Spread costs are reasonable")
        return True

def main():
    print("🔍 ENHANCED ENGINE SPREAD COST ANALYSIS")
    print("=" * 70)
    
    all_tests_passed = True
    
    # Test 1: Spread calculations
    if not test_spread_calculations():
        all_tests_passed = False
    
    # Test 2: Realistic prices
    if not test_realistic_prices():
        all_tests_passed = False
    
    # Test 3: Gold vs Forex comparison
    if not test_gold_vs_forex():
        all_tests_passed = False
    
    # Test 4: Full trade simulation
    if not test_full_trade_simulation():
        all_tests_passed = False
    
    print(f"\n🏁 ANALYSIS COMPLETE")
    print("=" * 70)
    
    if all_tests_passed:
        print("✅ All spread cost tests passed")
        print("🤔 The issue might be:")
        print("   - Strategy generating too many losing signals")
        print("   - Data quality issues")
        print("   - Parameter interpretation differences")
        print("   - Currency conversion issues")
    else:
        print("❌ ISSUES FOUND in spread cost calculations!")
        print("💡 RECOMMENDATION: Fix the identified spread cost issues")
    
    print(f"\n📋 NEXT ACTIONS:")
    print("1. Check if web interface is passing wrong parameters")
    print("2. Compare enhanced vs original engine side by side")
    print("3. Test with original engine to isolate the issue")
    print("4. Check database for parameter storage issues")

if __name__ == '__main__':
    main()