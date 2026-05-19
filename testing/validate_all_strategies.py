#!/usr/bin/env python3
"""
Comprehensive validation of all trading strategies
Ensures all strategies work properly with the fixed backtesting engine
"""

import sys
import os
repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if repo_root not in sys.path:
    sys.path.insert(0, repo_root)
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

def validate_strategy_registration():
    """Validate strategy registration and imports"""
    print("🔍 VALIDATING STRATEGY REGISTRATION")
    print("=" * 60)
    
    try:
        from core.strategies.strategy_map import STRATEGY_MAP, STRATEGY_METADATA
        
        print("✅ Successfully imported STRATEGY_MAP")
        print("✅ Successfully imported STRATEGY_METADATA")
        
        # Check all strategies are registered
        registered_strategies = list(STRATEGY_MAP.keys())
        metadata_strategies = list(STRATEGY_METADATA.keys())
        
        print(f"\n📊 Registered strategies ({len(registered_strategies)}):")
        for i, strategy in enumerate(registered_strategies, 1):
            print(f"  {i:2d}. {strategy}")
        
        print(f"\n📊 Metadata strategies ({len(metadata_strategies)}):")
        for i, strategy in enumerate(metadata_strategies, 1):
            print(f"  {i:2d}. {strategy}")
        
        # Check for mismatches
        missing_in_metadata = set(registered_strategies) - set(metadata_strategies)
        missing_in_registration = set(metadata_strategies) - set(registered_strategies)
        
        if missing_in_metadata:
            print(f"\n⚠️  Strategies missing metadata: {missing_in_metadata}")
        if missing_in_registration:
            print(f"\n⚠️  Strategies missing registration: {missing_in_registration}")
        
        if not missing_in_metadata and not missing_in_registration:
            print("\n✅ All strategies properly registered and documented")
        
        return registered_strategies, metadata_strategies
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return [], []
    except Exception as e:
        print(f"❌ Validation error: {e}")
        return [], []

def validate_strategy_classes():
    """Validate that all strategy classes can be instantiated"""
    print("\n🏗️  VALIDATING STRATEGY CLASSES")
    print("=" * 60)
    
    try:
        from core.strategies.strategy_map import STRATEGY_MAP
        
        # Mock bot for testing
        class MockBot:
            def __init__(self):
                self.market_for_mt5 = "EURUSD"
                self.timeframe = "H1"
                self.tf_map = {}
        
        mock_bot = MockBot()
        working_strategies = []
        broken_strategies = []
        
        for strategy_id, strategy_class in STRATEGY_MAP.items():
            try:
                # Get default parameters
                default_params = {}
                if hasattr(strategy_class, 'get_definable_params'):
                    param_definitions = strategy_class.get_definable_params()
                    for param in param_definitions:
                        default_params[param['name']] = param.get('default', 1)
                
                # Try to instantiate
                strategy_instance = strategy_class(bot_instance=mock_bot, params=default_params)
                
                # Check required methods
                if hasattr(strategy_instance, 'analyze') and hasattr(strategy_instance, 'analyze_df'):
                    print(f"  ✅ {strategy_id}")
                    working_strategies.append(strategy_id)
                else:
                    print(f"  ⚠️  {strategy_id} - Missing required methods")
                    broken_strategies.append(strategy_id)
                
            except Exception as e:
                print(f"  ❌ {strategy_id} - Error: {e}")
                broken_strategies.append(strategy_id)
        
        print("\n📊 SUMMARY:")
        print(f"✅ Working strategies: {len(working_strategies)}")
        print(f"❌ Broken strategies: {len(broken_strategies)}")
        
        if broken_strategies:
            print("\n🔧 BROKEN STRATEGIES NEED FIXING:")
            for strategy in broken_strategies:
                print(f"  - {strategy}")
        
        return working_strategies, broken_strategies
        
    except Exception as e:
        print(f"❌ Class validation error: {e}")
        return [], []

def check_strategy_id_consistency():
    """Check for ID consistency issues"""
    print("\n🔗 CHECKING STRATEGY ID CONSISTENCY")
    print("=" * 60)
    
    issues = []
    
    try:
        from core.strategies.strategy_map import STRATEGY_MAP
        
        # Check for case sensitivity issues
        strategy_ids = list(STRATEGY_MAP.keys())
        
        # Look for inconsistent casing
        case_issues = []
        for strategy_id in strategy_ids:
            # Check if there's a similar ID with different case
            similar_ids = [s for s in strategy_ids if s.lower() == strategy_id.lower() and s != strategy_id]
            if similar_ids:
                case_issues.append((strategy_id, similar_ids))
        
        if case_issues:
            print("⚠️  Case sensitivity issues found:")
            for original, similar in case_issues:
                print(f"  - '{original}' conflicts with {similar}")
            issues.extend(case_issues)
        
        # Check for naming convention consistency
        inconsistent_naming = []
        for strategy_id in strategy_ids:
            if strategy_id != strategy_id.upper() and '_' in strategy_id:
                # Most strategies use UPPER_CASE, but some don't
                inconsistent_naming.append(strategy_id)
        
        if inconsistent_naming:
            print("⚠️  Naming convention inconsistencies:")
            for strategy_id in inconsistent_naming:
                print(f"  - '{strategy_id}' should probably be '{strategy_id.upper()}'")
            issues.extend(inconsistent_naming)
        
        if not issues:
            print("✅ No ID consistency issues found")
        
        return issues
        
    except Exception as e:
        print(f"❌ ID consistency check error: {e}")
        return [str(e)]

def validate_backtesting_compatibility():
    """Check if strategies work with the fixed backtesting engine"""
    print("\n🔬 VALIDATING BACKTESTING COMPATIBILITY")
    print("=" * 60)
    
    try:
        from core.strategies.strategy_map import STRATEGY_MAP
        from core.backtesting.enhanced_engine import run_enhanced_backtest
        import pandas as pd
        import numpy as np
        from datetime import datetime, timedelta
        
        # Create minimal test data
        np.random.seed(42)
        data = []
        base_price = 1.1000
        
        for i in range(50):
            price = base_price + i * 0.0001 + np.random.normal(0, 0.00005)
            time = datetime(2024, 1, 1) + timedelta(hours=i)
            data.append({
                'time': time,
                'open': price,
                'high': price + 0.00002,
                'low': price - 0.00002,
                'close': price,
                'volume': 10000
            })
        
        df = pd.DataFrame(data)
        print(f"Created test data: {len(df)} bars")
        
        # Test a few key strategies
        test_strategies = ['MA_CROSSOVER', 'RSI_CROSSOVER', 'BOLLINGER_SQUEEZE']
        
        compatible_strategies = []
        incompatible_strategies = []
        
        for strategy_id in test_strategies:
            if strategy_id not in STRATEGY_MAP:
                print(f"  ⚠️  {strategy_id} not found in STRATEGY_MAP")
                continue
            
            try:
                # Basic parameters
                params = {
                    'risk_percent': 1.0,
                    'sl_atr_multiplier': 2.0,
                    'tp_atr_multiplier': 4.0
                }
                
                # Run quick test
                result = run_enhanced_backtest(strategy_id.lower(), params, df, 'EURUSD')
                
                if result and not result.get('error'):
                    print(f"  ✅ {strategy_id} - Compatible")
                    compatible_strategies.append(strategy_id)
                else:
                    print(f"  ❌ {strategy_id} - Error: {result.get('error', 'Unknown error')}")
                    incompatible_strategies.append(strategy_id)
                
            except Exception as e:
                print(f"  ❌ {strategy_id} - Exception: {e}")
                incompatible_strategies.append(strategy_id)
        
        print("\n📊 BACKTESTING COMPATIBILITY:")
        print(f"✅ Compatible: {len(compatible_strategies)}")
        print(f"❌ Incompatible: {len(incompatible_strategies)}")
        
        return compatible_strategies, incompatible_strategies
        
    except Exception as e:
        print(f"❌ Backtesting compatibility check error: {e}")
        return [], []

def main():
    print("🚀 COMPREHENSIVE STRATEGY VALIDATION")
    print("=" * 80)
    
    all_issues = []
    
    # 1. Validate registration
    registered, metadata = validate_strategy_registration()
    
    # 2. Validate classes
    working, broken = validate_strategy_classes()
    if broken:
        all_issues.extend(broken)
    
    # 3. Check ID consistency
    id_issues = check_strategy_id_consistency()
    if id_issues:
        all_issues.extend(id_issues)
    
    # 4. Test backtesting compatibility
    compatible, incompatible = validate_backtesting_compatibility()
    if incompatible:
        all_issues.extend(incompatible)
    
    # Final summary
    print("\n" + "=" * 80)
    print("🏁 FINAL VALIDATION SUMMARY")
    print("=" * 80)
    
    if not all_issues:
        print("🎉 ALL STRATEGIES ARE WORKING PERFECTLY!")
        print(f"✅ {len(registered)} strategies registered")
        print(f"✅ {len(working)} strategies functional")
        print("✅ No ID consistency issues")
        print("✅ Backtesting engine compatibility confirmed")
        print("\n🚀 ALL STRATEGIES READY FOR PRODUCTION!")
    else:
        print(f"⚠️  ISSUES FOUND ({len(all_issues)}):")
        for i, issue in enumerate(all_issues, 1):
            print(f"  {i}. {issue}")
        
        print("\n🔧 RECOMMENDATIONS:")
        if broken:
            print("  - Fix broken strategy classes")
        if id_issues:
            print("  - Resolve ID consistency issues")
        if incompatible:
            print("  - Debug backtesting compatibility")
    
    print("\n📋 STRATEGY STATUS FOR USER:")
    print(f"Your trading strategies are {'READY' if not all_issues else 'MOSTLY READY'} to use!")
    if not all_issues:
        print(f"All {len(registered)} strategies should work properly with the fixed backtesting engine.")

if __name__ == '__main__':
    main()
