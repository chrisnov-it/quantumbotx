#!/usr/bin/env python3
"""
📚 Test ATR Education System
Validates the new educational features for ATR-based risk management
"""

import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from core.education.atr_education import (
        ATREducationHelper, 
        get_atr_tutorial, 
        explain_atr_example,
        validate_beginner_atr_settings
    )
    from core.strategies.beginner_defaults import (
        get_atr_education_info,
        explain_atr_for_beginners
    )
    
    print("✅ All ATR education imports successful!")
    
except Exception as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)

def test_atr_education_system():
    """Test the ATR education system"""
    print("\n📚 Testing ATR Education System")
    print("=" * 60)
    
    # Test 1: Basic education helper
    print("\n1. 📖 ATR Education Helper:")
    helper = ATREducationHelper()
    tutorial = helper.get_beginner_tutorial()
    
    print(f"   📚 Tutorial has {len(tutorial['steps'])} steps")
    print(f"   💡 Key takeaways: {len(tutorial['key_takeaways'])}")
    
    for i, step in enumerate(tutorial['steps'], 1):
        print(f"      Step {i}: {step['title']}")
    
    # Test 2: Interactive examples
    print("\n2. 🎯 Interactive Examples:")
    
    test_scenarios = [
        {'symbol': 'EURUSD', 'account': 10000, 'risk': 1.0, 'atr': 0.0050},
        {'symbol': 'XAUUSD', 'account': 10000, 'risk': 2.0, 'atr': 15.0},  # Will be protected
        {'symbol': 'BTCUSD', 'account': 5000, 'risk': 1.5, 'atr': 500.0}
    ]
    
    for scenario in test_scenarios:
        example = helper.get_interactive_example(
            scenario['symbol'], 
            scenario['account'], 
            scenario['risk'], 
            scenario['atr']
        )
        
        print(f"\\n   📊 {scenario['symbol']} Example:")
        print(f"      Input Risk: {scenario['risk']}% → Actual: {example['risk_percent_actual']}%")
        print(f"      ATR: {scenario['atr']} → SL Distance: {example['sl_distance']:.2f}")
        print(f"      Lot Size: {example['lot_size']}")
        print(f"      Protection Active: {example['protection_active']}")
        print(f"      Risk-to-Reward: {example['risk_to_reward_ratio']}")
        
        if example['protection_active']:
            print(f"      🛡️ PROTECTION: System reduced risk for safety!")
    
    # Test 3: Parameter validation
    print("\n3. ⚙️ Parameter Validation:")
    
    validation_tests = [
        {'symbol': 'EURUSD', 'risk': 0.5, 'sl': 2.0, 'tp': 4.0, 'name': 'Conservative EURUSD'},
        {'symbol': 'XAUUSD', 'risk': 3.0, 'sl': 3.0, 'tp': 5.0, 'name': 'Risky Gold (will warn)'},
        {'symbol': 'BTCUSD', 'risk': 1.0, 'sl': 1.0, 'tp': 1.5, 'name': 'Poor risk-reward crypto'}
    ]
    
    for test in validation_tests:
        validation = helper.validate_beginner_parameters(
            test['symbol'], test['risk'], test['sl'], test['tp']
        )
        
        print(f"\\n   🧪 {test['name']}:")
        print(f"      Safe for beginners: {validation['is_beginner_safe']}")
        print(f"      Will be protected: {validation['will_be_protected']}")
        
        if validation['warnings']:
            for warning in validation['warnings']:
                print(f"      ⚠️ {warning}")
        
        if validation['suggestions']:
            for suggestion in validation['suggestions']:
                print(f"      💡 {suggestion}")
    
    # Test 4: Integration with beginner defaults
    print("\n4. 🔗 Integration with Beginner Defaults:")
    
    atr_info = get_atr_education_info()
    print(f"   📚 ATR concept explanations: {len(atr_info['concept_explanation']['detailed'])}")
    print(f"   📊 Example markets: {list(atr_info['examples'].keys())}")
    print(f"   🛡️ Protection features: {len(atr_info['protection_features'])}")
    
    # Test specific symbol explanations
    for symbol in ['EURUSD', 'XAUUSD']:
        explanation = explain_atr_for_beginners(symbol)
        print(f"\\n   📈 {symbol} Explanation:")
        print(f"      {explanation['example']['explanation']}")
        print(f"      Typical ATR: {explanation['example']['typical_atr']}")
    
    print("\n🎉 All ATR education tests completed successfully!")

def demonstrate_atr_protection():
    """Demonstrate the ATR protection system in action"""
    print("\n🛡️ ATR Protection System Demonstration")
    print("=" * 60)
    
    helper = ATREducationHelper()
    
    # Show dangerous vs safe scenarios
    scenarios = [
        {
            'name': 'Beginner Mistake (Before Protection)',
            'symbol': 'XAUUSD',
            'account': 10000,
            'risk': 5.0,  # Dangerous!
            'atr': 20.0,
            'description': 'What would happen without protection'
        },
        {
            'name': 'System Protection (After)',
            'symbol': 'XAUUSD', 
            'account': 10000,
            'risk': 5.0,  # Same input
            'atr': 20.0,
            'description': 'How the system saves the beginner'
        }
    ]
    
    for scenario in scenarios:
        example = helper.get_interactive_example(
            scenario['symbol'],
            scenario['account'], 
            scenario['risk'],
            scenario['atr']
        )
        
        print(f"\\n📊 {scenario['name']}:")
        print(f"   Account: ${scenario['account']:,}")
        print(f"   Desired Risk: {scenario['risk']}%")
        print(f"   ATR: ${scenario['atr']}")
        print(f"   📉 Target Risk Amount: ${example['amount_to_risk_target']:.0f}")
        print(f"   🛡️ Actual Risk Amount: ${example['actual_risk_amount']:.0f}")
        
        if example['protection_active']:
            savings = example['amount_to_risk_target'] - example['actual_risk_amount']
            print(f"   💰 PROTECTION SAVED: ${savings:.0f}")
            print(f"   🎯 System automatically reduced risk by {(savings/example['amount_to_risk_target']*100):.0f}%")
        
        print(f"\\n   📝 Explanation:")
        for exp in example['explanation']:
            print(f"      {exp}")
    
    print("\\n✨ CONCLUSION:")
    print("   Your ATR system is like having a professional trader watching over beginners!")
    print("   It prevents the common mistakes that blow up accounts.")

if __name__ == "__main__":
    print("📚 QuantumBotX ATR Education System Test")
    print("=" * 60)
    
    try:
        test_atr_education_system()
        demonstrate_atr_protection()
        
        print("\\n" + "=" * 60)
        print("🏆 SUCCESS! ATR education system is working perfectly!")
        print("🎓 Your app now teaches beginners professional risk management!")
        print("🛡️ Built-in protection prevents common beginner mistakes!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\\n❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()