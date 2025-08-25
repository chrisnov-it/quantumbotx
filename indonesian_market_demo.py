#!/usr/bin/env python3
"""
Indonesian Market Trading Demo for QuantumBotX
Showcasing opportunities in Indonesian financial markets
"""

import sys
import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def demo_indonesian_market_overview():
    """Overview of Indonesian trading opportunities"""
    print("🇮🇩 Indonesian Market Trading Opportunities")
    print("=" * 60)
    print("Welcome to the Indonesian Financial Markets!")
    print("=" * 60)
    
    market_segments = {
        'IDX Stocks (Jakarta Stock Exchange)': {
            'description': 'Local Indonesian companies',
            'examples': ['BBCA.JK (BCA)', 'BBRI.JK (BRI)', 'TLKM.JK (Telkom)'],
            'trading_hours': '09:00-16:00 WIB (GMT+7)',
            'currency': 'IDR (Indonesian Rupiah)',
            'min_lot': '100 shares',
            'opportunities': ['Banking sector growth', 'Infrastructure development', 'Consumer goods expansion']
        },
        'USD/IDR Forex': {
            'description': 'Indonesian Rupiah currency trading',
            'examples': ['USDIDR', 'EURIDR', 'JPYIDR'],
            'trading_hours': '24/5 (Global forex hours)',
            'currency': 'IDR pairs',
            'min_lot': 'Varies by broker',
            'opportunities': ['Commodity-driven moves', 'Central bank policy', 'Tourism recovery']
        },
        'International Markets via Indonesian Brokers': {
            'description': 'Global markets through local brokers',
            'examples': ['XAUUSD', 'US stocks', 'Major forex pairs'],
            'trading_hours': 'Varies by market',
            'currency': 'USD typically',
            'min_lot': 'Standard international',
            'opportunities': ['Global diversification', 'USD income', 'Hedge against IDR']
        }
    }
    
    print("\\n📊 Indonesian Market Segments:")
    for i, (segment, details) in enumerate(market_segments.items(), 1):
        print(f"\\n{i}. {segment}")
        print(f"   📝 Description: {details['description']}")
        print(f"   📈 Examples: {', '.join(details['examples'])}")
        print(f"   ⏰ Hours: {details['trading_hours']}")
        print(f"   💰 Currency: {details['currency']}")
        print(f"   🎯 Opportunities: {', '.join(details['opportunities'][:2])}")

def demo_indonesian_brokers():
    """Showcase Indonesian brokers with demo accounts"""
    print("\\n🏢 Indonesian Brokers with Demo Accounts")
    print("=" * 60)
    
    brokers = [
        {
            'name': 'Indopremier Securities (IPOT)',
            'type': 'Local Indonesian Broker',
            'specialties': ['IDX Stocks', 'Local bonds', 'Indonesian mutual funds'],
            'demo_account': 'Yes - Full IDX access',
            'advantages': ['Local market expertise', 'IDR-based trading', 'Indonesian customer service'],
            'website': 'https://www.indopremier.com/',
            'best_for': 'Indonesian stock market and local investments'
        },
        {
            'name': 'XM Indonesia',
            'type': 'International Broker (Indonesia Office)',
            'specialties': ['Forex', 'CFDs', 'Commodities', 'Crypto CFDs'],
            'demo_account': 'Yes - $10,000 virtual',
            'advantages': ['Global markets', 'MT4/MT5 platform', 'Indonesian support'],
            'website': 'https://www.xm.com/id/',
            'best_for': 'Forex and international markets'
        },
        {
            'name': 'OctaFX Indonesia',
            'type': 'International Broker (Popular in Indonesia)',
            'specialties': ['Forex', 'Metals', 'Indices', 'Energies'],
            'demo_account': 'Yes - Unlimited time',
            'advantages': ['Tight spreads', 'Fast execution', 'Indonesian community'],
            'website': 'https://www.octafx.com/id/',
            'best_for': 'Professional forex trading'
        },
        {
            'name': 'HSBC Indonesia',
            'type': 'International Bank',
            'specialties': ['Forex', 'Asian currencies', 'Trade finance'],
            'demo_account': 'Available for qualified clients',
            'advantages': ['Banking integration', 'Asian market focus', 'Multi-currency'],
            'website': 'Contact local HSBC branch',
            'best_for': 'Currency hedging and international business'
        }
    ]
    
    print("\\n🎯 Recommended Brokers for Indonesian Traders:")
    for i, broker in enumerate(brokers, 1):
        print(f"\\n{i}. {broker['name']}")
        print(f"   🏢 Type: {broker['type']}")
        print(f"   📈 Specialties: {', '.join(broker['specialties'][:3])}")
        print(f"   🧪 Demo Account: {broker['demo_account']}")
        print(f"   ⭐ Best For: {broker['best_for']}")
        print(f"   🌐 Website: {broker['website']}")

def demo_idx_stocks_trading():
    """Demo trading Indonesian stocks"""
    print("\\n📈 IDX Stock Trading Simulation")
    print("=" * 60)
    
    # Simulate some popular Indonesian stocks
    idx_stocks = [
        {'symbol': 'BBCA.JK', 'name': 'Bank Central Asia', 'price': 9150, 'sector': 'Banking'},
        {'symbol': 'BBRI.JK', 'name': 'Bank Rakyat Indonesia', 'price': 4520, 'sector': 'Banking'},
        {'symbol': 'TLKM.JK', 'name': 'Telkom Indonesia', 'price': 3280, 'sector': 'Telecommunications'},
        {'symbol': 'ASII.JK', 'name': 'Astra International', 'price': 6750, 'sector': 'Automotive'},
        {'symbol': 'UNVR.JK', 'name': 'Unilever Indonesia', 'price': 7100, 'sector': 'Consumer Goods'},
    ]
    
    print("\\n🏦 Popular IDX Stocks (Simulated Prices):")
    print("Symbol     | Company                    | Price (IDR) | Sector")
    print("-" * 70)
    
    total_portfolio_value = 0
    
    for stock in idx_stocks:
        # Simulate small price movements
        current_price = stock['price'] * (1 + np.random.uniform(-0.02, 0.02))
        change_pct = ((current_price - stock['price']) / stock['price']) * 100
        
        # Simulate trading with 1000 IDR capital per stock
        shares_affordable = int(100000 / current_price)  # 100k IDR investment
        position_value = shares_affordable * current_price
        total_portfolio_value += position_value
        
        color = "📈" if change_pct > 0 else "📉" if change_pct < 0 else "➡️"
        
        print(f"{stock['symbol']:10} | {stock['name']:25} | {current_price:8.0f} {color} | {stock['sector']}")
    
    print(f"\\n💼 Simulated Portfolio Value: {total_portfolio_value:,.0f} IDR")
    print(f"💰 Equivalent in USD: ${total_portfolio_value/15400:.2f} (assuming 1 USD = 15,400 IDR)")

def demo_usd_idr_trading():
    """Demo USD/IDR forex trading"""
    print("\\n💱 USD/IDR Forex Trading Simulation")
    print("=" * 60)
    
    # Current USD/IDR around 15,400
    base_rate = 15400
    
    # Simulate daily USD/IDR movements
    days = 30
    dates = pd.date_range(end=datetime.now(), periods=days, freq='D')
    
    # IDR volatility (typically 0.5-1% daily)
    daily_changes = np.random.randn(days) * 0.008  # 0.8% daily volatility
    rates = base_rate * (1 + daily_changes).cumprod()
    
    print(f"\\n📊 USD/IDR Rate Simulation (Last {days} days):")
    print(f"Starting Rate: {base_rate:,.0f} IDR per USD")
    print(f"Ending Rate: {rates[-1]:,.0f} IDR per USD")
    print(f"Total Change: {((rates[-1] - base_rate) / base_rate) * 100:+.2f}%")
    
    # Trading simulation
    position_size = 10000  # $10,000 USD position
    entry_rate = rates[0]
    exit_rate = rates[-1]
    
    if rates[-1] > rates[0]:  # USD strengthened
        pnl_usd = position_size * ((exit_rate - entry_rate) / entry_rate)
        direction = "USD strengthened"
    else:  # USD weakened
        pnl_usd = position_size * ((exit_rate - entry_rate) / entry_rate)
        direction = "USD weakened"
    
    pnl_idr = pnl_usd * exit_rate
    
    print(f"\\n💹 Trading Simulation:")
    print(f"Position: Long ${position_size:,} USD vs IDR")
    print(f"Entry Rate: {entry_rate:,.0f} IDR/USD")
    print(f"Exit Rate: {exit_rate:,.0f} IDR/USD")
    print(f"Market Move: {direction}")
    print(f"P&L: ${pnl_usd:+,.2f} USD (or {pnl_idr:+,.0f} IDR)")

def demo_strategy_performance_indonesia():
    """Test strategies on Indonesian markets"""
    print("\\n🤖 Strategy Performance on Indonesian Markets")
    print("=" * 60)
    
    from core.brokers.indonesian_brokers import IndopremierBroker
    
    # Create Indonesian broker instance
    broker = IndopremierBroker(demo=True)
    
    # Test symbols
    test_symbols = [
        ('BBCA.JK', 'Bank Central Asia'),
        ('USDIDR', 'USD/IDR Forex'),
        ('XAUIDR', 'Gold in IDR')
    ]
    
    print("\\n📈 Testing QuantumBotX Strategies on Indonesian Markets:")
    
    for symbol, name in test_symbols:
        try:
            # Get simulated market data
            df = broker.get_market_data(symbol, broker.timeframe_map[broker.Timeframe.H1] if hasattr(broker, 'timeframe_map') else 'H1', 500)
            
            if not df.empty:
                # Calculate basic metrics
                volatility = (df['close'].std() / df['close'].mean()) * 100
                price_range = f"{df['close'].min():.0f} - {df['close'].max():.0f}"
                
                # Assess suitability for different strategies
                if volatility < 2:
                    strategy_rec = "Bollinger Reversion (Low volatility)"
                elif volatility > 5:
                    strategy_rec = "Conservative MA Crossover (High volatility)"
                else:
                    strategy_rec = "QuantumBotX Hybrid (Moderate volatility)"
                
                print(f"\\n📊 {symbol} ({name}):")
                print(f"   Price Range: {price_range}")
                print(f"   Volatility: {volatility:.1f}%")
                print(f"   Recommended Strategy: {strategy_rec}")
                print(f"   Data Points: {len(df)} bars")
            else:
                print(f"\\n❌ {symbol}: No data available")
                
        except Exception as e:
            print(f"\\n❌ {symbol}: Error - {e}")

def demo_regulatory_compliance():
    """Indonesian regulatory information"""
    print("\\n⚖️ Indonesian Regulatory Compliance")
    print("=" * 60)
    
    regulatory_info = {
        'Primary Regulator': {
            'name': 'OJK (Otoritas Jasa Keuangan)',
            'role': 'Financial Services Authority',
            'website': 'https://www.ojk.go.id/',
            'oversight': 'Banks, capital markets, insurance, pension funds'
        },
        'Stock Exchange': {
            'name': 'IDX (Indonesia Stock Exchange)',
            'location': 'Jakarta',
            'website': 'https://www.idx.co.id/',
            'trading_currency': 'Indonesian Rupiah (IDR)'
        },
        'Key Regulations': [
            'Foreign investment limits in certain sectors',
            'Tax obligations for trading profits',
            'Anti-money laundering (AML) requirements',
            'Know Your Customer (KYC) procedures'
        ],
        'Tax Considerations': [
            'Capital gains tax on stock trading',
            'Forex trading taxation rules',
            'Withholding tax on foreign investments',
            'Professional trader vs investor classification'
        ]
    }
    
    print("\\n🏛️ Regulatory Framework:")
    print(f"Primary Regulator: {regulatory_info['Primary Regulator']['name']}")
    print(f"Stock Exchange: {regulatory_info['Stock Exchange']['name']}")
    
    print("\\n⚠️ Important Considerations:")
    for consideration in regulatory_info['Key Regulations'][:3]:
        print(f"  • {consideration}")
    
    print("\\n💰 Tax Implications:")
    for tax_item in regulatory_info['Tax Considerations'][:3]:
        print(f"  • {tax_item}")
    
    print("\\n📝 Recommendation:")
    print("  • Consult with Indonesian tax advisor")
    print("  • Understand local broker regulations")
    print("  • Keep detailed trading records")
    print("  • Consider professional trader registration if applicable")

def main():
    """Main Indonesian market demo"""
    print("🇮🇩 SELAMAT DATANG! Welcome to Indonesian Market Trading!")
    print("Your QuantumBotX system now supports Indonesian markets!")
    print()
    
    # Run all demos
    demo_indonesian_market_overview()
    demo_indonesian_brokers()
    demo_idx_stocks_trading()
    demo_usd_idr_trading()
    demo_strategy_performance_indonesia()
    demo_regulatory_compliance()
    
    print("\\n" + "=" * 60)
    print("🎯 NEXT STEPS FOR INDONESIAN TRADING")
    print("=" * 60)
    
    next_steps = [
        {
            'step': '1. Choose Your Indonesian Broker',
            'recommendation': 'Start with XM Indonesia demo (easiest setup)',
            'action': 'Sign up for demo account at xm.com/id/'
        },
        {
            'step': '2. Add Indonesian Configuration',
            'recommendation': 'Update .env file with Indonesian broker credentials',
            'action': 'Add XM_INDONESIA_LOGIN and XM_INDONESIA_PASSWORD'
        },
        {
            'step': '3. Test IDX Stocks Strategy',
            'recommendation': 'Start with banking stocks (BBCA, BBRI, BMRI)',
            'action': 'Run backtests on Indonesian blue-chip stocks'
        },
        {
            'step': '4. Explore USD/IDR Trading',
            'recommendation': 'Great for Indonesian traders to earn USD',
            'action': 'Test forex strategies on USD/IDR pair'
        },
        {
            'step': '5. Regulatory Compliance',
            'recommendation': 'Understand Indonesian tax obligations',
            'action': 'Consult with local financial advisor'
        }
    ]
    
    for step_info in next_steps:
        print(f"\\n{step_info['step']}")
        print(f"   💡 Recommendation: {step_info['recommendation']}")
        print(f"   🎯 Action: {step_info['action']}")
    
    print("\\n🎉 AMAZING OPPORTUNITY!")
    print("=" * 60)
    print("You're now building a trading system that covers:")
    print("✅ Global Forex (MT5, cTrader, XM)")
    print("✅ Cryptocurrency (Binance)")  
    print("✅ US Stocks (Interactive Brokers)")
    print("✅ Social Trading (TradingView)")
    print("✅ Indonesian Markets (Local brokers)") 
    print()
    print("🌏 FROM INDONESIA TO THE WORLD!")
    print("Your trading system now spans the entire globe! 🚀")

if __name__ == "__main__":
    main()