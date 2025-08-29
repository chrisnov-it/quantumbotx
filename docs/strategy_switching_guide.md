# QuantumBotX Automatic Strategy Switching Guide

## Overview

The Automatic Strategy Switching system is an advanced feature of QuantumBotX that automatically evaluates and switches between different strategy/instrument combinations based on their performance and current market conditions. This ensures your trading bots are always using the most profitable and suitable strategies for the current market environment.

## How It Works

### 1. Performance Evaluation
The system continuously evaluates all configured strategy/instrument combinations using:
- **Profitability Score**: Based on net profit, win rate, and profit factor
- **Risk Control Score**: Based on maximum drawdown and risk/reward ratio
- **Consistency Score**: Based on trade frequency and profit consistency
- **Activity Level Score**: Based on the number of trades generated
- **Market Fit Score**: Based on strategy compatibility with instrument type and market conditions

### 2. Market Condition Detection
The system analyzes each instrument to determine:
- **Market Condition**: Trending vs. ranging markets
- **Volatility Regime**: High vs. low volatility periods
- **Session Status**: Active trading sessions

### 3. Automatic Switching
Based on the composite performance scores and market conditions, the system:
- Switches to the highest-performing strategy/instrument combination
- Respects cooldown periods to prevent excessive switching
- Maintains a history of all switches for review

## Dashboard Features

### Strategy Switcher Dashboard
Access the dashboard through the "Strategy Switcher" link in the sidebar.

#### Current Status
- **Active Strategy**: The currently active strategy
- **Active Symbol**: The currently active trading instrument
- **Last Switch**: Timestamp of the last strategy switch
- **Cooldown Status**: Indicates if switching is currently in cooldown

#### Strategy Performance Rankings
Shows all strategy/instrument combinations ranked by their composite performance scores:
- **Rank**: Position in the rankings
- **Strategy/Symbol**: The strategy and instrument combination
- **Composite Score**: Overall performance score (0-1)
- **Profitability**: Profitability component score
- **Risk Control**: Risk management component score
- **Market Fit**: Compatibility with market conditions

#### Recent Strategy Switches
Displays a history of recent strategy switches with details:
- **Action**: Type of switch (Initial setup or strategy switch)
- **From/To**: Previous and new strategy/instrument combinations
- **Reason**: Reason for the switch
- **Score**: Performance score of the new combination
- **Improvement**: Performance improvement from the switch

#### Monitored Instruments & Strategies
Lists all instruments and strategies being monitored by the system.

## Trading Bot Integration

### Enabling Strategy Switching
When creating or editing a trading bot, you can enable automatic strategy switching:

1. Navigate to the Trading Bots page
2. Click "Create Bot" or edit an existing bot
3. Check the "Aktifkan Automatic Strategy Switching" checkbox
4. Save the bot configuration

When enabled, the bot will automatically switch to the best-performing strategy/instrument combination as determined by the strategy switcher system.

## API Endpoints

The strategy switching system provides REST API endpoints for integration:

### Status Endpoints
- `GET /api/strategy-switcher/status` - Get current strategy switcher status
- `GET /api/strategy-switcher/recent-switches` - Get recent strategy switches

### Evaluation Endpoints
- `POST /api/strategy-switcher/evaluate` - Manually trigger strategy evaluation
- `POST /api/strategy-switcher/manual-trigger` - Manually trigger strategy evaluation and switch

### Data Endpoints
- `GET /api/strategy-switcher/rankings` - Get current strategy performance rankings
- `GET /api/strategy-switcher/market-conditions` - Get current market conditions
- `GET /api/strategy-switcher/configuration` - Get strategy switcher configuration

### Configuration Endpoints
- `GET /api/strategy-switcher/configuration` - Get current configuration
- `PUT /api/strategy-switcher/configuration` - Update configuration

## Configuration

### Monitored Instruments
The system monitors a configurable list of instruments including:
- Indices (US500, US30, DE30, etc.)
- Forex pairs (EURUSD, GBPUSD, etc.)
- Gold (XAUUSD)
- Cryptocurrencies (BTCUSD, etc.)

### Test Strategies
The system evaluates a configurable list of strategies:
- INDEX_BREAKOUT_PRO
- MA_CROSSOVER
- RSI_CROSSOVER
- TURTLE_BREAKOUT
- QUANTUMBOTX_HYBRID

### Settings
- **Switching Cooldown**: 24 hours (minimum time between switches)
- **Performance Evaluation Period**: 500 bars
- **Minimum Performance Score**: 0.6 (minimum score to consider switching)
- **Switch Threshold**: 0.1 (minimum score improvement to trigger switch)

## Best Practices

### For Optimal Performance
1. **Diversify Instruments**: Monitor a variety of instruments to find the best opportunities
2. **Regular Evaluation**: The system automatically evaluates performance, but you can manually trigger evaluations
3. **Review Switches**: Regularly review the switch history to understand system behavior
4. **Adjust Settings**: Fine-tune configuration parameters based on your trading preferences

### Monitoring Recommendations
1. **Check Dashboard Regularly**: Review the strategy switcher dashboard for insights
2. **Review Notifications**: Pay attention to strategy switch notifications
3. **Analyze Performance**: Compare manual vs. automatic strategy selection performance
4. **Adjust Parameters**: Modify strategy parameters based on market conditions

## Troubleshooting

### Common Issues
1. **No Switches Occurring**: Check if all monitored instruments have data files
2. **Poor Performance**: Review strategy parameters and market conditions
3. **Frequent Switching**: Increase the switching cooldown period or switch threshold

### Data Requirements
The system requires historical data files in the `lab/backtest_data` directory:
- Format: CSV files with time, open, high, low, close, volume columns
- Naming: `{SYMBOL}_H1_data.csv` (e.g., EURUSD_H1_data.csv)
- Content: Sufficient historical data for backtesting (minimum 500 bars)

## Conclusion

The Automatic Strategy Switching system provides a powerful way to optimize your trading performance by automatically selecting the best strategy/instrument combinations based on real-time performance analysis and market conditions. By enabling this feature on your trading bots, you can ensure they're always using the most profitable approaches without manual intervention.