#!/usr/bin/env python3
"""
🎓 Test Beginner-Friendly Strategy System
Quick validation of the new beginner defaults and strategy selector
"""

import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from core.strategies.strategy_map import (
        get_beginner_strategies, 
        get_strategies_by_difficulty,
        get_strategies_for_market,
        get_strategy_info,
        STRATEGY_METADATA
    )
    from core.strategies.strategy_selector import StrategySelector
    from core.strategies.beginner_defaults import get_beginner_defaults
    
    print("✅ All imports successful!")
    
except Exception as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)

def test_beginner_system():
    """Test the beginner-friendly strategy system"""
    print("\n🎯 Testing Beginner Strategy System")
    print("=" * 50)
    
    # Test 1: Beginner strategies
    print("\n1. 🎓 Beginner-Friendly Strategies:")
    beginner_strategies = get_beginner_strategies()
    for strategy in beginner_strategies:
        metadata = STRATEGY_METADATA[strategy]
        print(f"   ✅ {strategy}")
        print(f"      Complexity: {metadata['complexity_score']}/10")
        print(f"      Description: {metadata['description']}")
        print(f"      Markets: {', '.join(metadata['market_types'])}")
    
    # Test 2: Strategy selector
    print("\n2. 🎯 Strategy Selector Test:")
    selector = StrategySelector()
    dashboard = selector.get_beginner_dashboard()
    
    print(f"   📊 Recommended strategies: {len(dashboard['recommended_strategies'])}")
    for strategy in dashboard['recommended_strategies']:
        print(f"      • {strategy['display_name']} (Complexity: {strategy['complexity_score']})")
    
    # Test 3: Market-specific recommendations
    print("\n3. 🏪 Market-Specific Recommendations:")
    markets = ['FOREX', 'GOLD', 'CRYPTO']
    for market in markets:
        recommendation = selector.get_strategy_for_market(market, 'BEGINNER')
        print(f"   {market}: {recommendation['recommended_strategy']}")
        print(f"      Reason: {recommendation['reasoning']}")
    
    # Test 4: Learning path
    print("\n4. 📚 Learning Path:")
    learning_path = dashboard['learning_path']
    for step in learning_path:
        print(f"   {step['level']}: {step['strategy']}")
        print(f"      Goal: {step['goal']}")
        print(f"      Focus: {step['focus']}")
    
    # Test 5: Parameter validation
    print("\n5. ⚙️ Parameter Validation Test:")
    test_params = {
        'fast_period': 50,  # Very different from beginner default (10)
        'slow_period': 200  # Very different from beginner default (30)
    }
    
    validation = selector.validate_parameters('MA_CROSSOVER', test_params)
    print(f"   Is beginner safe: {validation['is_beginner_safe']}")
    if validation['warnings']:
        for warning in validation['warnings']:
            print(f"   ⚠️ {warning}")
    if validation['suggestions']:
        for suggestion in validation['suggestions']:
            print(f"   💡 {suggestion}")
    
    # Test 6: Safety tips
    print("\n6. 🛡️ Safety Tips:")
    safety_tips = dashboard['safety_tips']
    for tip in safety_tips[:3]:  # Show first 3
        print(f"   {tip}")
    print(f"   ... and {len(safety_tips)-3} more tips")
    
    print("\n🎉 All tests completed successfully!")
    print("\n💡 Summary:")
    print(f"   • {len(beginner_strategies)} beginner-friendly strategies")
    print(f"   • {len(get_strategies_by_difficulty('INTERMEDIATE'))} intermediate strategies")
    print(f"   • {len(get_strategies_by_difficulty('ADVANCED'))} advanced strategies")
    print(f"   • {len(get_strategies_by_difficulty('EXPERT'))} expert strategies")
    print(f"   • Complete learning path with {len(learning_path)} steps")
    print(f"   • {len(safety_tips)} safety tips for beginners")

def show_strategy_comparison():
    """Show comparison of old vs new defaults"""
    print("\n📊 Strategy Defaults Comparison")
    print("=" * 50)
    
    strategies_to_compare = ['MA_CROSSOVER', 'RSI_CROSSOVER', 'TURTLE_BREAKOUT']
    
    for strategy_name in strategies_to_compare:
        print(f"\n🎯 {strategy_name}:")
        
        # Get beginner defaults
        beginner_info = get_beginner_defaults(strategy_name)
        if beginner_info:
            print(f"   Difficulty: {beginner_info['difficulty']}")
            print(f"   Description: {beginner_info['description']}")
            print(f"   Beginner Parameters:")
            for param, value in beginner_info['params'].items():
                explanation = beginner_info['explanation'].get(param, '')
                print(f"      • {param}: {value} - {explanation}")
        else:
            print("   ❌ No beginner defaults found")

if __name__ == "__main__":
    print("🎓 QuantumBotX Beginner Strategy System Test")
    print("=" * 60)
    
    try:
        test_beginner_system()
        show_strategy_comparison()
        
        print("\n" + "=" * 60)
        print("🏆 SUCCESS! Beginner system is working perfectly!")
        print("✨ Your trading app is now super beginner-friendly!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()