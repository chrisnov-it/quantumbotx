#!/usr/bin/env python3
# quick_ai_mentor_demo.py
"""
🚀 Quick AI Mentor Demo - Add Sample Data
Creates sample trading sessions to demonstrate the AI Mentor features
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from datetime import date, timedelta
from core.db.models import create_trading_session, log_trade_for_ai_analysis

def create_sample_data():
    """Create sample trading sessions for AI mentor demo"""
    print("\n🤖 Creating sample AI mentor data...")
    
    # Create today's session
    today = date.today()
    session_id = create_trading_session(
        session_date=today,
        emotions='tenang',
        market_conditions='trending',
        notes='Sample trading session untuk demo AI Mentor'
    )
    
    if session_id > 0:
        print(f"✅ Created today's session: {session_id}")
        
        # Add some sample trades
        sample_trades = [
            {'bot_id': 1, 'symbol': 'EURUSD', 'profit': 25.50, 'lot_size': 0.01, 'sl_used': True, 'tp_used': True, 'risk': 1.0, 'strategy': 'MA_CROSSOVER'},
            {'bot_id': 2, 'symbol': 'XAUUSD', 'profit': -15.20, 'lot_size': 0.01, 'sl_used': True, 'tp_used': False, 'risk': 1.0, 'strategy': 'QUANTUM_VELOCITY'},
            {'bot_id': 3, 'symbol': 'BTCUSD', 'profit': 45.80, 'lot_size': 0.01, 'sl_used': True, 'tp_used': True, 'risk': 0.5, 'strategy': 'QUANTUMBOTX_CRYPTO'}
        ]
        
        for trade in sample_trades:
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
        
        print(f"✅ Added {len(sample_trades)} sample trades")
    
    # Create yesterday's session
    yesterday = today - timedelta(days=1)
    yesterday_session = create_trading_session(
        session_date=yesterday,
        emotions='serakah',
        market_conditions='volatile',
        notes='Trading agresif kemarin, kurang sabar'
    )
    
    if yesterday_session > 0:
        print(f"✅ Created yesterday's session: {yesterday_session}")
        
        # Add yesterday's trades
        yesterday_trades = [
            {'bot_id': 1, 'symbol': 'EURUSD', 'profit': -35.20, 'lot_size': 0.02, 'sl_used': False, 'tp_used': False, 'risk': 2.0, 'strategy': 'MA_CROSSOVER'},
            {'bot_id': 2, 'symbol': 'GBPUSD', 'profit': 15.50, 'lot_size': 0.01, 'sl_used': True, 'tp_used': True, 'risk': 1.0, 'strategy': 'RSI_CROSSOVER'}
        ]
        
        for trade in yesterday_trades:
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
    
    print("\n🎉 Sample AI Mentor data created successfully!")
    print("📱 Visit http://localhost:5000/ai-mentor to see the results!")

if __name__ == "__main__":
    create_sample_data()