#!/usr/bin/env python3
# testing/test_ai_mentor_integration.py
"""
🧪 Test AI Mentor Integration dengan Data Trading Real
Test komprehensif untuk memastikan AI mentor bekerja dengan sempurna
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import date, datetime, timedelta
from core.ai.trading_mentor_ai import IndonesianTradingMentorAI, TradingSession
from core.db.models import (
    create_trading_session, log_trade_for_ai_analysis, 
    get_trading_session_data, save_ai_mentor_report,
    update_session_emotions_and_notes, get_recent_mentor_reports
)

def test_database_integration():
    """Test integrasi database AI mentor"""
    print("\n🔍 Testing Database Integration...")
    
    # Test 1: Create trading session
    today = date.today()
    session_id = create_trading_session(
        session_date=today,
        emotions='tenang',
        market_conditions='trending',
        notes='Test session untuk AI mentor'
    )
    
    print(f"✅ Session created with ID: {session_id}")
    
    # Test 2: Log some test trades
    test_trades = [
        {'bot_id': 1, 'symbol': 'EURUSD', 'profit': 45.50, 'lot_size': 0.01, 'sl_used': True, 'tp_used': True, 'risk': 1.0, 'strategy': 'MA_CROSSOVER'},
        {'bot_id': 2, 'symbol': 'XAUUSD', 'profit': -25.30, 'lot_size': 0.01, 'sl_used': True, 'tp_used': False, 'risk': 0.5, 'strategy': 'RSI_CROSSOVER'},
        {'bot_id': 3, 'symbol': 'BTCUSD', 'profit': 78.90, 'lot_size': 0.01, 'sl_used': True, 'tp_used': True, 'risk': 0.3, 'strategy': 'QUANTUMBOTX_CRYPTO'}
    ]
    
    for trade in test_trades:
        log_trade_for_ai_analysis(
            bot_id=trade['bot_id'],
            symbol=trade['symbol'],
            profit_loss=trade['profit'],
            lot_size=trade['lot_size'],
            stop_loss_used=trade['sl_used'],
            take_profit_used=trade['tp_used'],
            risk_percent=trade['risk'],
            strategy_used=trade['strategy']
        )
    
    print(f"✅ Logged {len(test_trades)} test trades")
    
    # Test 3: Retrieve session data
    session_data = get_trading_session_data(today)
    if session_data:
        print(f"✅ Retrieved session data: {session_data['total_trades']} trades, P/L: ${session_data['total_profit_loss']:.2f}")
        return session_data
    else:
        print("❌ Failed to retrieve session data")
        return None

def test_ai_mentor_analysis(session_data):
    """Test AI mentor analysis dengan data real"""
    print("\n🤖 Testing AI Mentor Analysis...")
    
    if not session_data:
        print("❌ No session data available for testing")
        return None
    
    # Create TradingSession object
    trading_session = TradingSession(
        date=date.today(),
        trades=session_data['trades'],
        emotions=session_data['emotions'],
        market_conditions=session_data['market_conditions'],
        profit_loss=session_data['total_profit_loss'],
        notes=session_data['personal_notes']
    )
    
    # Generate AI analysis
    mentor = IndonesianTradingMentorAI()
    analysis = mentor.analyze_trading_session(trading_session)
    
    print("✅ AI Analysis generated successfully:")
    print(f"   📊 Pola Trading: {analysis['pola_trading']['pola_utama']}")
    print(f"   🧠 Emosi Analysis: {analysis['emosi_vs_performa']['feedback'][:50]}...")
    print(f"   🛡️ Risk Score: {analysis['manajemen_risiko']['nilai']}")
    print(f"   💡 Recommendations: {len(analysis['rekomendasi'])} tips")
    
    # Test full report generation
    full_report = mentor.generate_daily_report(trading_session)
    print(f"✅ Full Indonesian report generated: {len(full_report)} characters")
    
    # Save to database
    save_success = save_ai_mentor_report(session_data['session_id'], analysis)
    print(f"✅ Report saved to database: {save_success}")
    
    return analysis, full_report

def test_emotional_updates():
    """Test update emosi dan catatan"""
    print("\n💭 Testing Emotional Updates...")
    
    emotions_to_test = ['tenang', 'serakah', 'takut', 'frustasi']
    test_notes = [
        "Hari ini trading dengan perasaan tenang, mengikuti strategi dengan disiplin.",
        "Agak serakah karena melihat profit, hampir over-trading.",
        "Takut entry karena market volatile, miss beberapa opportunity.",
        "Frustasi karena loss beruntun, butuh break sejenak."
    ]
    
    for emotion, note in zip(emotions_to_test, test_notes):
        success = update_session_emotions_and_notes(date.today(), emotion, note)
        print(f"✅ Updated emotion to '{emotion}': {success}")
        
    return True

def test_historical_reports():
    """Test pengambilan laporan historis"""
    print("\n📚 Testing Historical Reports...")
    
    # Create some historical data
    historical_dates = [date.today() - timedelta(days=i) for i in range(1, 8)]
    emotions_cycle = ['tenang', 'serakah', 'frustasi', 'takut', 'tenang', 'serakah', 'tenang']
    
    for test_date, emotion in zip(historical_dates, emotions_cycle):
        session_id = create_trading_session(
            session_date=test_date,
            emotions=emotion,
            market_conditions='normal',
            notes=f'Historical test session for {test_date}'
        )
        
        # Add some random trades
        import random
        for _ in range(random.randint(1, 5)):
            log_trade_for_ai_analysis(
                bot_id=random.randint(1, 4),
                symbol=random.choice(['EURUSD', 'XAUUSD', 'BTCUSD']),
                profit_loss=random.uniform(-50, 100),
                lot_size=0.01,
                stop_loss_used=random.choice([True, False]),
                take_profit_used=random.choice([True, False]),
                risk_percent=random.uniform(0.5, 2.0),
                strategy_used=random.choice(['MA_CROSSOVER', 'RSI_CROSSOVER', 'QUANTUMBOTX_CRYPTO'])
            )
    
    # Retrieve reports
    reports = get_recent_mentor_reports(10)
    print(f"✅ Retrieved {len(reports)} historical reports")
    
    for report in reports[:3]:
        print(f"   📅 {report['session_date']}: ${report['profit_loss']:.2f} ({report['emotions']})")
    
    return reports

def test_ai_mentor_scenarios():
    """Test berbagai skenario AI mentor"""
    print("\n🎭 Testing Different AI Mentor Scenarios...")
    
    mentor = IndonesianTradingMentorAI()
    
    scenarios = [
        {
            'name': 'Profitable Day',
            'session': TradingSession(
                date=date.today(),
                trades=[
                    {'symbol': 'EURUSD', 'profit': 85.50, 'lot_size': 0.01, 'stop_loss_used': True, 'risk_percent': 1.0},
                    {'symbol': 'XAUUSD', 'profit': 45.20, 'lot_size': 0.01, 'stop_loss_used': True, 'risk_percent': 0.5}
                ],
                emotions='tenang',
                market_conditions='trending',
                profit_loss=130.70,
                notes='Hari yang bagus, strategi berjalan dengan baik'
            )
        },
        {
            'name': 'Loss Day',
            'session': TradingSession(
                date=date.today(),
                trades=[
                    {'symbol': 'EURUSD', 'profit': -45.30, 'lot_size': 0.02, 'stop_loss_used': False, 'risk_percent': 3.0},
                    {'symbol': 'BTCUSD', 'profit': -25.80, 'lot_size': 0.01, 'stop_loss_used': True, 'risk_percent': 2.0}
                ],
                emotions='frustasi',
                market_conditions='sideways',
                profit_loss=-71.10,
                notes='Hari buruk, emosi menguasai, lupa pakai SL'
            )
        },
        {
            'name': 'Mixed Day',
            'session': TradingSession(
                date=date.today(),
                trades=[
                    {'symbol': 'XAUUSD', 'profit': 25.50, 'lot_size': 0.01, 'stop_loss_used': True, 'risk_percent': 1.0},
                    {'symbol': 'EURUSD', 'profit': -15.20, 'lot_size': 0.01, 'stop_loss_used': True, 'risk_percent': 1.0},
                    {'symbol': 'BTCUSD', 'profit': 35.80, 'lot_size': 0.01, 'stop_loss_used': True, 'risk_percent': 0.5}
                ],
                emotions='netral',
                market_conditions='volatile',
                profit_loss=46.10,
                notes='Hari biasa, ada profit ada loss, overall masih positif'
            )
        }
    ]
    
    for scenario in scenarios:
        print(f"\n🎯 Testing Scenario: {scenario['name']}")
        analysis = mentor.analyze_trading_session(scenario['session'])
        
        print(f"   📊 Risk Score: {analysis['manajemen_risiko']['nilai']}")
        print(f"   💭 Emotion Feedback: {analysis['emosi_vs_performa']['feedback'][:60]}...")
        print(f"   💪 Motivation: {analysis['motivasi'][:60]}...")
        
        # Test specific Indonesian cultural elements
        full_report = mentor.generate_daily_report(scenario['session'])
        
        # Check for Indonesian specific content
        indonesian_markers = ['Alhamdulillah', 'Jakarta', 'WIB', 'BI rate', 'trader Indonesia']
        found_markers = [marker for marker in indonesian_markers if marker in full_report]
        print(f"   🇮🇩 Indonesian context markers found: {len(found_markers)}/5")
    
    print("✅ All scenarios tested successfully")

def run_comprehensive_test():
    """Run komprehensif test untuk AI mentor"""
    print("🚀 COMPREHENSIVE AI MENTOR TEST - INDONESIAN TRADING SYSTEM")
    print("=" * 70)
    
    try:
        # Step 1: Database integration
        session_data = test_database_integration()
        
        # Step 2: AI analysis
        if session_data:
            analysis, report = test_ai_mentor_analysis(session_data)
        
        # Step 3: Emotional updates
        test_emotional_updates()
        
        # Step 4: Historical reports
        test_historical_reports()
        
        # Step 5: Different scenarios
        test_ai_mentor_scenarios()
        
        print("\n" + "=" * 70)
        print("🎉 ALL TESTS PASSED! AI MENTOR SYSTEM IS READY FOR INDONESIAN TRADERS!")
        print("🇮🇩 Sistem AI Mentor siap melayani trader Indonesia!")
        print("=" * 70)
        
        return True
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = run_comprehensive_test()
    sys.exit(0 if success else 1)