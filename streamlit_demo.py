import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import random

# Page configuration
st.set_page_config(
    page_title="QuantumBotX Trading Bot Demo",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Header
st.title("🤖 QuantumBotX - AI Trading Bot Demo")
st.markdown("*Experience the power of algorithmic trading without risking real money*")

# Portfolio Overview
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Balance", "$10,000", "+2.3%")
with col2:
    st.metric("Active Strategies", "4", "+1")
with col3:
    st.metric("Total Profit", "$234.56", "+5.2%")
with col4:
    st.metric("Bots Running", "3", "Online")

# Demo Data Generation
def generate_demo_data():
    # Generate realistic trading data
    symbols = ['EURUSD', 'GBPUSD', 'XAUUSD', 'BTCUSD']
    strategies = ['MA Crossover', 'RSI Momentum', 'Quantum Velocity', 'Ichimoku Cloud']
    data = []

    base_date = datetime.now() - timedelta(days=30)

    for i in range(30):
        for symbol in symbols[:2]:  # Only EURUSD and GBPUSD for demo
            profit = random.uniform(-50, 150) if random.random() > 0.3 else random.uniform(-100, 200)
            data.append({
                'date': (base_date + timedelta(days=i)).strftime('%Y-%m-%d'),
                'symbol': symbol,
                'strategy': random.choice(strategies),
                'profit': round(profit, 2),
                'status': 'Closed' if random.random() > 0.2 else 'Open'
            })

    return pd.DataFrame(data)

# Strategy Showcase
st.header("🎯 Featured Trading Strategies")

col1, col2 = st.columns(2)

with col1:
    st.subheader("📈 MA Crossover Strategy")
    st.write("""
    **Perfect for beginners!** This classic strategy identifies trend changes using moving average crossovers.
    - Uses 50 & 200 period moving averages
    - Works beautifully in trending markets
    - Risk management: 1% per trade
    - EURUSD & GBPUSD optimized
    """)

    # Example chart placeholder
    chart_data = pd.DataFrame({
        'Price': [1.0850, 1.0875, 1.0920, 1.0885, 1.0910, 1.0935, 1.0960, 1.0945],
        'SMA50': [1.0800, 1.0815, 1.0830, 1.0845, 1.0860, 1.0875, 1.0890, 1.0905],
        'SMA200': [1.0750, 1.0765, 1.0780, 1.0795, 1.0810, 1.0825, 1.0840, 1.0855]
    })
    st.line_chart(chart_data)

with col2:
    st.subheader("🎪 Bollinger Band Reversal")
    st.write("""
    **Advanced mean reversion strategy** that profits from price returning to the mean.
    - Uses Bollinger Bands for entry signals
    - RSI confirmation for momentum timing
    - Excellent in ranging markets
    - Perfect for FOREX pairs
    """)

    # Bollinger bands visualization
    bb_data = pd.DataFrame({
        'Price': [1.0850, 1.0835, 1.0860, 1.0825, 1.0875, 1.0800, 1.0885, 1.0840],
        'Upper BB': [1.0910, 1.0925, 1.0900, 1.0935, 1.0920, 1.0945, 1.0930, 1.0915],
        'Lower BB': [1.0790, 1.0775, 1.0800, 1.0765, 1.0780, 1.0755, 1.0770, 1.0785]
    })
    st.line_chart(bb_data)

# Live Demo Section
st.header("📊 Live Bot Performance")

# Demo trading data
demo_data = generate_demo_data()

# Filter options
col1, col2, col3 = st.columns(3)
with col1:
    symbol_filter = st.selectbox("Filter by Symbol:", ["All"] + demo_data['symbol'].unique().tolist())
with col2:
    strategy_filter = st.selectbox("Filter by Strategy:", ["All"] + demo_data['strategy'].unique().tolist())
with col3:
    status_filter = st.selectbox("Filter by Status:", ["All"] + demo_data['status'].unique().tolist())

# Apply filters
filtered_data = demo_data.copy()
if symbol_filter != "All":
    filtered_data = filtered_data[filtered_data['symbol'] == symbol_filter]
if strategy_filter != "All":
    filtered_data = filtered_data[filtered_data['strategy'] == strategy_filter]
if status_filter != "All":
    filtered_data = filtered_data[filtered_data['status'] == status_filter]

# Display trades table
st.dataframe(
    filtered_data.sort_values('date', ascending=False),
    use_container_width=True
)

# Performance Summary
st.subheader("📈 Performance Summary")

col1, col2, col3, col4 = st.columns(4)

with col1:
    total_trades = len(filtered_data)
    st.metric("Total Trades", total_trades)

with col2:
    profitable_trades = len(filtered_data[filtered_data['profit'] > 0])
    win_rate = (profitable_trades / total_trades * 100) if total_trades > 0 else 0
    st.metric("Win Rate", ".1f")

with col3:
    avg_profit = filtered_data['profit'].mean()
    st.metric("Avg Profit/Trade", ".2f")

with col4:
    total_profit = filtered_data['profit'].sum()
    st.metric("Total P&L", ".2f")

# Features Showcase
st.header("🚀 Key Features")

feature_col1, feature_col2 = st.columns(2)

with feature_col1:
    st.subheader("🛡️ Risk Management")
    st.write("""
    - **ATR-Based Sizing**: Dynamic position sizing that adapts to volatility
    - **1% Risk Rule**: Conservative approach protects your capital
    - **XAUUSD Protection**: Special safeguards for gold trading
    - **Emergency Brake**: Auto-halting during extreme market conditions
    """)

    st.subheader("🎓 AI Educational System")
    st.write("""
    - **Strategy Complexity Ratings**: 2-12 scale for beginners to experts
    - **Day-by-Day Learning**: Progressive experience from Week 1 to Month 3
    - **AI Mentor**: Indonesian AI mentor with cultural intelligence
    - **Parameter Explanations**: Every setting explained in plain language
    """)

with feature_col2:
    st.subheader("📊 Multi-Asset Trading")
    st.write("""
    - **FOREX**: EURUSD, GBPUSD, JPY pairs with trend-following
    - **Gold**: Ultra-conservative XAUUSD with ATR limits
    - **Crypto**: BTCUSD/ETHUSD with 24/7 weekend trading
    - **Indices**: US500, US30 with momentum strategies
    - **Multi-Broker**: XM Global, FBS, IC Markets support
    """)

    st.subheader("🌟 Unique Features")
    st.write("""
    - **Strategy Switcher**: AI automatically selects best strategy
    - **Holiday Detection**: Christmas & Ramadan mode activation
    - **Cultural Awareness**: Islamic finance features and Zakat calculator
    - **Live Dashboard**: Real-time monitoring and performance tracking
    """)

# Call to Action
st.header("🎯 Ready to Start Your Trading Journey?")

st.info("""
**QuantumBotX Demo Limitations:**
- This is a *simulation* of the actual trading bot
- Real trading requires Windows + MetaTrader 5 terminal
- All data shown is generated for demonstration purposes
- The actual bot provides live MT5 integration and real-time trading
""")

st.markdown("""
### How to Get Started:
1. **Download the full application** from our GitHub repository
2. **Install MetaTrader 5** on your Windows computer
3. **Set up your demo account** with any MT5 broker
4. **Configure and start trading** with $50 minimum deposit

### System Requirements:
- Windows 10/11 (64-bit)
- MetaTrader 5 terminal
- Python 3.10 or higher
- At least 4GB RAM
""")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p><strong>QuantumBotX</strong> - Making Algorithmic Trading Accessible for Everyone</p>
    <p>Developed with ❤️ by Chrisnov IT Solutions</p>
    <p><a href='https://github.com/rebarakaz/quantumbotx' target='_blank'>View on GitHub</a> • <a href='#' target='_blank'>Documentation</a></p>
</div>
""", unsafe_allow_html=True)
