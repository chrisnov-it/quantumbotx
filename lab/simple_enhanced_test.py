# simple_enhanced_test.py - Simple test of enhanced backtesting concepts
import pandas as pd
import numpy as np

def demonstrate_enhanced_concepts():
    """Demonstrate the enhanced backtesting concepts without full engine"""
    
    print("🚀 Enhanced Backtesting Concepts Demo")
    print("=" * 50)
    
    # 1. Instrument Configuration
    print("\n1️⃣ Instrument-Specific Configuration")
    print("-" * 30)
    
    instruments = {
        'EURUSD': {
            'spread_pips': 1.5,
            'slippage_pips': 0.3,
            'max_risk': 2.0,
            'type': 'Forex Major'
        },
        'XAUUSD': {
            'spread_pips': 15.0,
            'slippage_pips': 2.0,
            'max_risk': 1.0,
            'type': 'Precious Metal'
        },
        'GBPUSD': {
            'spread_pips': 2.5,
            'slippage_pips': 0.5,
            'max_risk': 2.0,
            'type': 'Forex Major'
        }
    }
    
    for symbol, config in instruments.items():
        print(f"📊 {symbol} ({config['type']}):")
        print(f"   💸 Spread: {config['spread_pips']} pips")
        print(f"   ⚡ Slippage: {config['slippage_pips']} pips")
        print(f"   🔒 Max Risk: {config['max_risk']}%")
    
    # 2. Spread Cost Calculation
    print(f"\n2️⃣ Spread Cost Impact Analysis")
    print("-" * 30)
    
    trade_scenarios = [
        {'instrument': 'EURUSD', 'lot_size': 0.1, 'trades_per_month': 20},
        {'instrument': 'XAUUSD', 'lot_size': 0.02, 'trades_per_month': 10},
        {'instrument': 'GBPUSD', 'lot_size': 0.1, 'trades_per_month': 15}
    ]
    
    print("Monthly spread cost analysis:")
    total_monthly_cost = 0
    
    for scenario in trade_scenarios:
        symbol = scenario['instrument']
        config = instruments[symbol]
        lot_size = scenario['lot_size']
        trades = scenario['trades_per_month']
        
        # Calculate spread cost per trade
        # Forex: $1 per pip per 0.01 lot
        # Gold: $1 per point per 0.01 lot
        dollar_per_pip = 1.0  # For 0.01 lot
        cost_per_trade = config['spread_pips'] * dollar_per_pip * (lot_size / 0.01)
        monthly_cost = cost_per_trade * trades
        total_monthly_cost += monthly_cost
        
        print(f"📈 {symbol}:")
        print(f"   Lot size: {lot_size}")
        print(f"   Trades/month: {trades}")
        print(f"   Cost/trade: ${cost_per_trade:.2f}")
        print(f"   Monthly cost: ${monthly_cost:.2f}")
    
    print(f"\n💰 Total monthly spread cost: ${total_monthly_cost:.2f}")
    print(f"💡 This is pure cost deduction from profits!")
    
    # 3. ATR-based Position Sizing Demo
    print(f"\n3️⃣ ATR-based Position Sizing")
    print("-" * 30)
    
    # Simulate ATR values for different market conditions
    market_conditions = {
        'Low Volatility': {'atr': 0.0015, 'description': 'Quiet market'},
        'Normal Volatility': {'atr': 0.0035, 'description': 'Average conditions'},
        'High Volatility': {'atr': 0.0080, 'description': 'News events'},
        'Extreme Volatility': {'atr': 0.0150, 'description': 'Market panic'}
    }
    
    capital = 10000
    risk_percent = 1.0  # 1% risk per trade
    sl_atr_multiplier = 2.0  # Stop loss at 2x ATR
    
    print(f"Position sizing for EURUSD (Capital: ${capital}, Risk: {risk_percent}%):")
    
    for condition, data in market_conditions.items():
        atr = data['atr']
        description = data['description']
        
        # Calculate position size
        amount_to_risk = capital * (risk_percent / 100)
        sl_distance = atr * sl_atr_multiplier
        contract_size = 100000  # Standard lot
        
        risk_per_lot = sl_distance * contract_size
        if risk_per_lot > 0:
            lot_size = amount_to_risk / risk_per_lot
            lot_size = min(lot_size, 10.0)  # Cap at reasonable size
        else:
            lot_size = 0
        
        print(f"🌊 {condition} (ATR: {atr:.4f}):")
        print(f"   SL Distance: {sl_distance:.4f} ({sl_distance*10000:.1f} pips)")
        print(f"   Lot Size: {lot_size:.3f}")
        print(f"   Risk: ${amount_to_risk:.0f}")
        print(f"   Scenario: {description}")
    
    # 4. Gold Protection Demo
    print(f"\n4️⃣ Gold (XAUUSD) Protection System")
    print("-" * 30)
    
    gold_scenarios = [
        {'risk_percent': 0.5, 'atr': 8.0, 'condition': 'Low risk, normal volatility'},
        {'risk_percent': 1.0, 'atr': 12.0, 'condition': 'Medium risk, normal volatility'},
        {'risk_percent': 2.0, 'atr': 25.0, 'condition': 'High risk, high volatility'},
        {'risk_percent': 2.0, 'atr': 35.0, 'condition': 'High risk, extreme volatility'}
    ]
    
    print("Gold position sizing with protection:")
    
    for scenario in gold_scenarios:
        risk = scenario['risk_percent']
        atr = scenario['atr']
        condition = scenario['condition']
        
        # Apply gold protection rules
        protected_risk = min(risk, 1.0)  # Cap at 1% for gold
        
        # Base lot size (ultra-conservative)
        if protected_risk <= 0.25:
            base_lot = 0.01
        elif protected_risk <= 0.5:
            base_lot = 0.01
        elif protected_risk <= 0.75:
            base_lot = 0.02
        else:
            base_lot = 0.02  # Never above 0.02 for gold
        
        # ATR-based reduction
        if atr > 30.0:
            final_lot = 0.01  # Extreme volatility
            protection = "EXTREME volatility protection"
        elif atr > 20.0:
            final_lot = max(0.01, base_lot * 0.5)  # High volatility
            protection = "HIGH volatility protection"
        else:
            final_lot = base_lot
            protection = "Normal volatility"
        
        # Final cap
        final_lot = min(final_lot, 0.03)
        
        print(f"🥇 Risk: {risk}%, ATR: {atr:.1f}")
        print(f"   Original risk: {risk}% → Protected: {protected_risk}%")
        print(f"   Base lot: {base_lot} → Final: {final_lot}")
        print(f"   Protection: {protection}")
        print(f"   Scenario: {condition}")
        print()
    
    # 5. Realistic vs Perfect Execution
    print(f"\n5️⃣ Perfect vs Realistic Execution")
    print("-" * 30)
    
    example_trade = {
        'signal': 'BUY',
        'close_price': 1.1000,
        'target_profit': 1.1050,
        'stop_loss': 1.0950,
        'lot_size': 0.1
    }
    
    # Perfect execution (old way)
    perfect_entry = example_trade['close_price']
    perfect_exit = example_trade['target_profit']
    perfect_profit = (perfect_exit - perfect_entry) * 100000 * example_trade['lot_size']
    
    # Realistic execution (new way)
    spread_pips = 1.5
    slippage_pips = 0.3
    pip_size = 0.0001
    
    spread_cost = spread_pips * pip_size
    slippage_cost = slippage_pips * pip_size
    
    realistic_entry = perfect_entry + (spread_cost / 2) + slippage_cost  # Buy at ask + slippage
    realistic_exit = perfect_exit - (spread_cost / 2) - slippage_cost    # Sell at bid - slippage
    realistic_profit = (realistic_exit - realistic_entry) * 100000 * example_trade['lot_size']
    
    # Spread cost deduction
    spread_cost_dollar = spread_pips * 1.0 * (example_trade['lot_size'] / 0.01)
    
    print(f"Example BUY trade (EURUSD, {example_trade['lot_size']} lot):")
    print(f"📊 Target: {example_trade['close_price']:.4f} → {example_trade['target_profit']:.4f}")
    print()
    print(f"💫 Perfect Execution:")
    print(f"   Entry: {perfect_entry:.4f}")
    print(f"   Exit: {perfect_exit:.4f}")
    print(f"   Profit: ${perfect_profit:.2f}")
    print()
    print(f"🎯 Realistic Execution:")
    print(f"   Entry: {realistic_entry:.4f} (spread + slippage)")
    print(f"   Exit: {realistic_exit:.4f} (spread + slippage)")
    print(f"   Gross Profit: ${realistic_profit:.2f}")
    print(f"   Spread Cost: ${spread_cost_dollar:.2f}")
    print(f"   Net Profit: ${realistic_profit:.2f}")
    print()
    print(f"📉 Difference: ${realistic_profit - perfect_profit:.2f}")
    print(f"📈 Impact: {((perfect_profit - realistic_profit) / perfect_profit * 100):.1f}% reduction")
    
    print(f"\n💡 Summary of Enhanced Features:")
    print(f"   ✅ Instrument-specific configurations")
    print(f"   ✅ Realistic spread and slippage modeling")
    print(f"   ✅ ATR-based dynamic position sizing")
    print(f"   ✅ Special gold market protections")
    print(f"   ✅ Emergency brake systems")
    print(f"   ✅ More accurate profit/loss calculations")
    
    print(f"\n🎯 Why This Matters:")
    print(f"   • Your old backtesting was too optimistic")
    print(f"   • Spread costs can consume 10-30% of profits")
    print(f"   • Gold trading needs special protection")
    print(f"   • ATR-based sizing prevents account blowouts")
    print(f"   • Realistic execution prepares you for live trading")

if __name__ == "__main__":
    demonstrate_enhanced_concepts()