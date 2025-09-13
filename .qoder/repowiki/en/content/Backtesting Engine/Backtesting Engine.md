# Backtesting Engine

<cite>
**Referenced Files in This Document**   
- [engine.py](file://core/backtesting/engine.py) - *Updated with enhanced XAUUSD protections and ATR-based risk management*
- [api_backtest.py](file://core/routes/api_backtest.py) - *Enhanced with realistic cost modeling and improved data handling*
- [backtesting.html](file://templates/backtesting.html) - *Updated with enhanced engine UI indicators*
- [backtesting.js](file://static/js/backtesting.js) - *Enhanced with detailed results display and cost breakdown*
- [backtesting_analyzer.html](file://testing/backtesting_analyzer.html) - *Added for system analysis and validation*
</cite>

## Update Summary
**Changes Made**   
- Updated Trading Costs Modeling section with enhanced spread cost and slippage simulation details
- Added Enhanced Backtesting Engine section for new realistic execution features
- Updated API Interface section with enhanced parameter mapping and result structure
- Enhanced Backtest Configuration section with new parameter names and engine configuration
- Added comprehensive source tracking for all updated sections
- Fixed outdated information about profit calculation and risk management

## Table of Contents
1. [Backtesting Methodology](#backtesting-methodology)
2. [Backtesting Workflow](#backtesting-workflow)
3. [Key Performance Metrics](#key-performance-metrics)
4. [Trading Costs Modeling](#trading-costs-modeling)
5. [Enhanced Backtesting Engine](#enhanced-backtesting-engine)
6. [Backtest Configuration and Execution](#backtest-configuration-and-execution)
7. [API Interface](#api-interface)
8. [Backtest History Visualization](#backtest-history-visualization)
9. [Limitations and Best Practices](#limitations-and-best-practices)
10. [Performance Optimization](#performance-optimization)

## Backtesting Methodology

The backtesting engine in quantumbotx implements an event-driven simulation framework that processes historical market data to evaluate trading strategy performance. The core methodology is implemented in `engine.py` and follows a structured four-step process.

### Historical Data Loading and Preparation
The backtesting process begins with loading historical data from a CSV file into a pandas DataFrame. The data must contain standard OHLC (Open, High, Low, Close) columns along with a timestamp column. The engine automatically parses the time column and prepares the data for analysis.

```python
df = pd.read_csv(file, parse_dates=['time'])
```

The system includes enhanced symbol detection logic to accurately identify the trading instrument, particularly for XAUUSD (Gold). This detection uses multiple methods:
- Direct symbol name parameter
- Filename parsing (e.g., "XAUUSD_H1_data.csv" → "XAUUSD")
- Column name analysis
- Strategy bot metadata

### Event-Driven Simulation
The backtesting engine operates on an event-driven model where each historical price bar triggers potential trading decisions. The simulation loop processes each bar sequentially, checking for entry and exit conditions.

``mermaid
flowchart TD
Start([Start Backtest]) --> Initialize["Initialize State Variables<br/>Capital, Trades, Equity Curve"]
Initialize --> Precompute["Precompute Indicators<br/>ATR, Strategy Signals"]
Precompute --> Loop["For Each Price Bar"]
Loop --> CheckPosition{"In Position?"}
CheckPosition --> |Yes| CheckExit["Check Stop Loss/Take Profit<br/>Conditions"]
CheckExit --> |Triggered| CloseTrade["Close Trade<br/>Update Capital & Metrics"]
CloseTrade --> UpdateState["Update Equity Curve<br/>Max Drawdown"]
CheckExit --> |Not Triggered| ContinueLoop
CheckPosition --> |No| CheckSignal{"Check Strategy Signal<br/>(BUY/SELL)"}
CheckSignal --> |Signal Present| EnterTrade["Enter Trade<br/>Calculate Position Size"]
EnterTrade --> UpdateState
CheckSignal --> |No Signal| ContinueLoop
UpdateState --> ContinueLoop
ContinueLoop --> NextBar["Next Price Bar"]
NextBar --> EndLoop{"End of Data?"}
EndLoop --> |No| Loop
EndLoop --> |Yes| CalculateResults["Calculate Final Performance Metrics"]
CalculateResults --> ReturnResults["Return Backtest Results"]
```

**Diagram sources**
- [engine.py](file://core/backtesting/engine.py#L90-L157)

**Section sources**
- [engine.py](file://core/backtesting/engine.py#L90-L157)

The simulation handles both long (BUY) and short (SELL) positions, with position exits triggered by either stop loss (SL) or take profit (TP) conditions being met. The engine uses the low price for BUY stop loss checks and high price for SELL stop loss checks to ensure realistic execution conditions.

## Backtesting Workflow

The complete backtesting workflow spans from strategy selection through result visualization, integrating frontend and backend components.

### Strategy Selection and Configuration
Users begin by selecting a trading strategy from a dropdown menu populated with available strategies. The strategy selection triggers the loading of strategy-specific parameters, which are then displayed in the configuration panel.

``mermaid
sequenceDiagram
participant User as "User"
participant Frontend as "Frontend (backtesting.html)"
participant API as "API Server"
participant Engine as "Backtesting Engine"
User->>Frontend : Select strategy from dropdown
Frontend->>API : GET /api/strategies
API-->>Frontend : Return list of strategies
Frontend->>API : GET /api/strategies/{strategy_id}/params
API-->>Frontend : Return strategy parameters
Frontend->>User : Display strategy parameters
User->>Frontend : Configure parameters and upload data
Frontend->>API : POST /api/backtest/run with form data
API->>Engine : Call run_backtest() function
Engine-->>API : Return backtest results
API-->>Frontend : Return JSON results
Frontend->>User : Display results and equity curve
```

**Diagram sources**
- [backtesting.html](file://templates/backtesting.html)
- [backtesting.js](file://static/js/backtesting.js)
- [api_backtest.py](file://core/routes/api_backtest.py)

**Section sources**
- [backtesting.html](file://templates/backtesting.html)
- [backtesting.js](file://static/js/backtesting.js)

### Result Visualization
After backtest execution, results are visualized through multiple components:
- Summary metrics display (profit, drawdown, win rate, etc.)
- Equity curve chart showing capital growth over time
- Trade log displaying the last 20 trades with entry/exit prices and profits

The equity curve is rendered using Chart.js, providing an interactive visualization of the strategy's performance. The frontend JavaScript handles the dynamic updating of the results container, replacing the loading spinner with the complete results display.

## Key Performance Metrics

The backtesting engine calculates several key performance metrics that provide comprehensive insights into strategy performance.

### Metric Calculation
The following metrics are calculated at the conclusion of the backtest:

```python
# Calculate key metrics
total_profit = capital - initial_capital
wins = len([t for t in trades if t['profit'] > 0])
losses = len(trades) - wins
win_rate = (wins / len(trades) * 100) if trades else 0
```

**Section sources**
- [engine.py](file://core/backtesting/engine.py#L262-L288)

The primary metrics include:

**:Total Profit USD**
- The net profit in USD terms from the backtest
- Calculated as final capital minus initial capital ($10,000)
- Represents the absolute performance of the strategy

**:Max Drawdown Percent**
- The maximum peak-to-trough decline in the equity curve
- Calculated as (peak_equity - current_equity) / peak_equity
- Measures the largest historical loss, indicating risk exposure

**:Win Rate Percent**
- The percentage of winning trades out of total trades
- Calculated as (wins / total_trades) * 100
- Indicates the strategy's consistency in generating profitable trades

**:Total Trades**
- The total number of trades executed during the backtest
- Provides context for evaluating other metrics
- Higher trade counts generally provide more statistically significant results

**:Final Capital**
- The ending account balance after all trades
- Starting capital is fixed at $10,000
- Shows the compounded growth (or decline) of the account

### Significance of Metrics
These metrics work together to provide a balanced assessment of strategy performance. While total profit indicates overall profitability, max drawdown reveals the risk involved in achieving that profit. A high win rate suggests consistency, but must be evaluated alongside profit factor (average win/average loss) to ensure profitability isn't driven by infrequent large wins.

The equity curve provides visual insight into performance consistency, with smooth upward trends indicating stable performance, while jagged curves suggest higher volatility and risk.

## Trading Costs Modeling

The backtesting engine incorporates sophisticated modeling of trading costs and risk management parameters, with special considerations for volatile instruments like XAUUSD (Gold).

### Position Sizing and Risk Management
The engine implements dynamic position sizing based on account equity and volatility (ATR - Average True Range). The risk is expressed as a percentage of account capital, with different calculation methods for standard forex pairs and XAUUSD.

For standard forex instruments:
- Risk per trade = account capital × (risk_percent / 100)
- Contract size = 100,000 (standard lot)
- Position size calculated based on stop loss distance in price terms

For XAUUSD, the system implements extreme conservative measures due to the instrument's high volatility:

```python
# XAUUSD EXTREME PROTECTION
if is_gold:
    if risk_percent <= 0.25:
        lot_size = 0.01
    elif risk_percent <= 0.5:
        lot_size = 0.01
    elif risk_percent <= 0.75:
        lot_size = 0.02
    elif risk_percent <= 1.0:
        lot_size = 0.02
    else:
        lot_size = 0.03  # MAXIMUM for any XAUUSD trade
```

**Section sources**
- [engine.py](file://core/backtesting/engine.py#L182-L204)

This fixed lot size approach prevents excessive risk exposure during volatile gold market conditions. The system caps the maximum lot size at 0.03 regardless of the requested risk percentage, implementing multiple safety layers.

Additionally, the system includes ATR-based volatility adjustments:
- If ATR > 30.0 (extreme volatility): lot size = 0.01
- If ATR > 20.0 (high volatility): lot_size = base_lot_size * 0.5
- Otherwise: use base lot size

An emergency brake prevents trades where estimated risk exceeds 5% of account capital.

### Slippage and Commission Modeling
While explicit slippage and commission parameters are not directly modeled in the current implementation, their effects are indirectly accounted for through the stop loss mechanism and conservative profit calculations.

The profit calculation incorporates the spread effect by using the close price for entry and the exact stop loss/take profit levels for exit:

```python
# Profit calculation
if position_type == 'BUY':
    profit = (exit_price - entry_price) * profit_multiplier
else: # SELL
    profit = (entry_price - exit_price) * profit_multiplier
```

**Section sources**
- [engine.py](file://core/backtesting/engine.py#L121-L157)

For XAUUSD, the system uses a contract size of 100 (vs. 100,000 for standard forex), reflecting the different pip value structure of gold trading. This ensures accurate profit calculations that account for the instrument's specific characteristics.

## Enhanced Backtesting Engine

The enhanced backtesting engine provides more realistic simulation capabilities with advanced cost modeling and execution simulation features.

### Realistic Cost Modeling
The enhanced engine incorporates realistic trading costs that significantly impact strategy performance:

**:Spread Costs**
- Models actual spread costs based on instrument-specific parameters
- Deducts spread costs from trade profits
- Uses typical spread values (e.g., 2.0 pips for EUR/USD, higher for exotic pairs)
- Total spread costs are calculated as: `total_trades × spread_pips × pip_value × lot_size`

**:Slippage Simulation**
- Simulates order execution slippage based on market volatility
- Applies random slippage within realistic bounds
- Increases slippage during high volatility periods
- Models both positive and negative slippage occurrences

**:Realistic Execution**
- Simulates bid/ask price differences in trade execution
- Uses mid-price for signal generation but bid/ask for execution
- Models partial fills for large order sizes
- Incorporates order book depth simulation

### Instrument-Specific Configuration
The enhanced engine applies instrument-specific risk parameters:

```python
engine_config = {
    'enable_spread_costs': True,
    'enable_slippage': True,
    'enable_realistic_execution': True
}
```

**Section sources**
- [api_backtest.py](file://core/routes/api_backtest.py#L50-L60)
- [backtesting.js](file://static/js/backtesting.js#L150-L200)

The system automatically configures parameters based on the trading instrument:
- **Max Risk Percent**: 2.0% for most instruments, reduced for volatile assets
- **Typical Spread Pips**: Instrument-specific spread values
- **Max Lot Size**: Safety limits to prevent excessive position sizing

## Backtest Configuration and Execution

The backtesting system provides a flexible configuration interface that allows users to customize various parameters for their simulations.

### Configuration Parameters
Users can configure the following parameters through the web interface:

**:Strategy Selection**
- Dropdown menu with all available strategies from strategy_map.py
- Currently includes MA_CROSSOVER, RSI_CROSSOVER, BOLLINGER_REVERSION, and others

**:Historical Data Upload**
- CSV file upload with OHLCV (Open, High, Low, Close, Volume) data
- Must include a 'time' column with parseable timestamps
- Filename used for symbol detection (e.g., XAUUSD_H1_data.csv)

**:Risk Management Parameters**
- **SL (ATR Multiplier)**: Stop loss distance as multiple of ATR (default: 2.0)
- **TP (ATR Multiplier)**: Take profit distance as multiple of ATR (default: 4.0)
- **Risk Percent**: Risk percentage of account capital (replaces 'lot_size' parameter)

**:Strategy-Specific Parameters**
- Dynamically loaded based on selected strategy
- Examples include moving average periods, RSI thresholds, Bollinger Band settings

### Execution Example
Here's a concrete example of backtest configuration and execution:

```python
# Example backtest configuration
params = {
    'risk_percent': 2.0,    # 2% risk per trade
    'sl_atr_multiplier': 2.0,     # 2x ATR for stop loss
    'tp_atr_multiplier': 4.0,     # 4x ATR for take profit
    'ma_period': 20,    # Strategy-specific parameter
    'rsi_period': 14    # Strategy-specific parameter
}

# Execute backtest
results = run_backtest(
    strategy_id='MA_CROSSOVER',
    params=params,
    historical_data_df=df,
    symbol_name='XAUUSD'
)
```

The system processes this configuration by:
1. Validating the strategy ID against the STRATEGY_MAP
2. Creating a strategy instance with the provided parameters
3. Pre-computing technical indicators including ATR
4. Running the event-driven simulation
5. Calculating performance metrics
6. Returning structured results

## API Interface

The backtesting system exposes a RESTful API interface that enables programmatic access to backtesting functionality.

### API Endpoints
The API is implemented in `api_backtest.py` and provides two main endpoints:

**:POST /api/backtest/run**
- **Purpose**: Execute a backtest simulation
- **Request Format**: multipart/form-data
- **Parameters**:
  - **file**: CSV file with historical data (required)
  - **strategy**: Strategy ID (required)
  - **params**: JSON string with backtest parameters (optional)
- **Response**: JSON object with backtest results or error message
- **Status Codes**: 200 (success), 400 (bad request), 500 (server error)

**:GET /api/backtest/history**
- **Purpose**: Retrieve historical backtest results
- **Request Format**: None (query parameters accepted)
- **Response**: Array of backtest result objects
- **Status Codes**: 200 (success), 500 (server error)

### API Implementation
The API implementation follows a clean separation of concerns:

``mermaid
classDiagram
class APIBacktest {
+run_backtest_route()
+get_history_route()
}
class BacktestingEngine {
+run_backtest()
}
class Database {
+save_backtest_result()
+get_all_backtest_history()
}
APIBacktest --> BacktestingEngine : "calls"
APIBacktest --> Database : "calls"
Database --> APIBacktest : "returns"
BacktestingEngine --> APIBacktest : "returns"
```

**Diagram sources**
- [api_backtest.py](file://core/routes/api_backtest.py)

**Section sources**
- [api_backtest.py](file://core/routes/api_backtest.py)

The `run_backtest_route` function handles file upload, parameter parsing, and backtest execution, while the `get_history_route` function retrieves and processes stored backtest results from the database. Both endpoints include comprehensive error handling and data validation.

Results are automatically saved to the database when a backtest completes successfully, enabling historical analysis and comparison of different strategy configurations.

The API includes enhanced data validation to ensure data integrity:
- Sanitizes NaN/Inf values before saving to database
- Preserves original `total_profit_usd` field name
- Implements robust JSON parsing with fallbacks
- Adds comprehensive error handling for malformed data

## Backtest History Visualization

The backtesting system now includes a comprehensive history visualization feature that allows users to review and analyze past backtest results.

### History Interface
The history interface is accessible via `/backtest_history` and consists of two main components:

**:History List**
- Displays all saved backtest results in chronological order
- Shows strategy name, market, timestamp, and profit for each backtest
- Clickable items that reveal detailed information

**:Detail View**
- Shows comprehensive results for a selected backtest
- Includes summary metrics, equity curve chart, parameters, and trade log
- Interactive elements for exploring historical results

### Frontend Implementation
The frontend implementation in `backtest_history.js` provides complete functionality for displaying historical results:

```javascript
function showDetail(item) {
    // Display basic information
    detailId.textContent = item.id || 'N/A';
    detailTimestamp.textContent = formatTimestamp(item.timestamp);
    
    // Display summary metrics
    detailSummary.innerHTML = createSummaryHtml(item);
    
    // Display equity chart
    displayEquityChart(item.equity_curve);
    
    // Display parameters
    displayParameters(item.parameters);
    
    // Display trade log
    displayTradeLog(item.trade_log);
}
```

**Section sources**
- [backtest_history.js](file://static/js/backtest_history.js#L150-L200)
- [backtest_history.html](file://templates/backtest_history.html)

The system includes robust error handling and data validation:
- Graceful degradation for missing or malformed data
- Comprehensive error handling for JSON parsing
- Console logging for debugging purposes
- Responsive design with loading states

### Data Processing Pipeline
The complete data processing pipeline ensures data integrity from calculation to display:

1. **Calculation**: Engine calculates metrics and validates for NaN/Inf values
2. **Sanitization**: API sanitizes results before saving to database
3. **Storage**: Results saved to SQLite database with JSON fields
4. **Retrieval**: API retrieves and processes stored results
5. **Parsing**: Frontend safely parses JSON fields with fallbacks
6. **Display**: Interactive visualization of all results components

This end-to-end validation ensures that users can reliably review and analyze their backtesting history with confidence in data accuracy.

## Limitations and Best Practices

### Historical Backtesting Limitations
While historical backtesting provides valuable insights, it has several inherent limitations that users should understand:

**:Overfitting Risk**
- Strategies can be excessively optimized to historical data
- May perform poorly on out-of-sample data or in live markets
- Solution: Use walk-forward optimization and out-of-sample testing

**:Market Condition Changes**
- Historical periods may not reflect current market regimes
- Volatility, correlations, and market structure can change
- Solution: Test across multiple market conditions and time periods

**:Data Quality Issues**
- Historical data may have gaps, errors, or survivorship bias
- Corporate actions (splits, dividends) may not be properly adjusted
- Solution: Use high-quality data sources and validate data integrity

**:Execution Assumptions**
- Backtests assume perfect execution at specified prices
- Real markets involve slippage, partial fills, and rejections
- Solution: Incorporate realistic execution models and transaction costs

### Best Practices for Result Interpretation
To derive meaningful insights from backtesting results, follow these best practices:

**:Focus on Risk-Adjusted Returns**
- Don't just look at total profit; consider drawdown and win rate
- A strategy with lower profit but much smaller drawdown may be preferable
- Use multiple metrics to evaluate performance holistically

**:Validate Statistical Significance**
- Ensure sufficient sample size (number of trades)
- Generally, 30+ trades are needed for basic statistical reliability
- More trades provide greater confidence in results

**:Test Across Market Regimes**
- Evaluate performance in trending, ranging, and volatile markets
- A robust strategy should perform reasonably well across conditions
- Avoid strategies that only work in specific market environments

**:Consider Forward Testing**
- Paper trade or forward test successful backtests before live deployment
- This provides real-world validation of strategy performance
- Helps identify issues not apparent in historical testing

## Performance Optimization

### Large Dataset Handling
The backtesting engine is designed to handle large historical datasets efficiently, but performance considerations are important for optimal operation.

**:Data Loading Optimization**
- Use properly formatted CSV files with appropriate data types
- Ensure the time column is parseable and sorted chronologically
- Consider using more efficient formats like Parquet for very large datasets

**:Memory Management**
- The engine loads the entire dataset into memory for processing
- For extremely large datasets, consider processing in chunks or using streaming approaches
- Monitor system memory usage during backtests with large datasets

**:Computational Efficiency**
- The current implementation uses a simple loop through price bars
- For strategies requiring complex calculations, pre-compute indicators when possible
- Consider vectorized operations using pandas for indicator calculations

### Optimization Recommendations
To optimize backtest performance with large datasets:

**:Use Appropriate Timeframes**
- Higher frequency data (e.g., 1-minute) creates much larger datasets than lower frequency (e.g., daily)
- Use the minimum timeframe resolution necessary for your strategy
- Consider testing on smaller timeframes first before scaling up

**:Filter Data When Possible**
- If testing a specific period, filter the dataset to that range before backtesting
- Remove unnecessary columns from the CSV file
- Use only the data required for your specific strategy

**:Leverage Caching**
- Store pre-processed data with indicators already calculated
- Cache strategy parameter combinations that are frequently tested
- Implement result caching to avoid re-running identical backtests

**:Parallel Processing**
- For testing multiple parameter combinations, consider running backtests in parallel
- Use multiprocessing to utilize multiple CPU cores
- Be mindful of memory usage when running multiple backtests simultaneously

The current implementation provides a solid foundation for backtesting, with opportunities for further optimization based on specific use cases and performance requirements.