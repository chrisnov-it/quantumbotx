# Strategy Framework

<cite>
**Referenced Files in This Document**   
- [base_strategy.py](file://core/strategies/base_strategy.py) - *Updated in recent commit*
- [strategy_map.py](file://core/strategies/strategy_map.py) - *Updated with strategy metadata and difficulty ratings*
- [beginner_defaults.py](file://core/strategies/beginner_defaults.py) - *Added in recent commit for beginner-friendly defaults*
- [strategy_selector.py](file://core/strategies/strategy_selector.py) - *Added in recent commit for strategy guidance*
- [atr_education.py](file://core/education/atr_education.py) - *Added in recent commit for ATR education*
- [ma_crossover.py](file://core/strategies/ma_crossover.py)
- [rsi_crossover.py](file://core/strategies/rsi_crossover.py)
- [bollinger_reversion.py](file://core/strategies/bollinger_reversion.py)
- [bollinger_squeeze.py](file://core/strategies/bollinger_squeeze.py)
- [ichimoku_cloud.py](file://core/strategies/ichimoku_cloud.py)
- [quantumbotx_hybrid.py](file://core/strategies/quantumbotx_hybrid.py)
</cite>

## Update Summary
**Changes Made**   
- Added comprehensive educational framework for beginners with strategy complexity ratings
- Introduced strategy difficulty levels (BEGINNER, INTERMEDIATE, ADVANCED, EXPERT) and metadata
- Added beginner-friendly default parameters and explanations for each strategy
- Implemented progressive learning path and strategy recommendations based on experience level
- Enhanced strategy selection with the StrategySelector class for guided onboarding
- Added ATR-based risk management education system for beginner traders
- Updated STRATEGY_MAP with comprehensive metadata including difficulty, complexity scores, and market type recommendations

## Table of Contents
1. [Introduction](#introduction)
2. [BaseStrategy Abstract Interface](#basestrategy-abstract-interface)
3. [Strategy Registration and Dynamic Loading](#strategy-registration-and-dynamic-loading)
4. [Available Strategies](#available-strategies)
   - [MA Crossover Strategy](#ma-crossover-strategy)
   - [RSI Crossover Strategy](#rsi-crossover-strategy)
   - [Bollinger Bands Reversion Strategy](#bollinger-bands-reversion-strategy)
   - [Bollinger Squeeze Breakout Strategy](#bollinger-squeeze-breakout-strategy)
   - [Ichimoku Cloud Strategy](#ichimoku-cloud-strategy)
   - [QuantumbotX Hybrid Strategy](#quantumbotx-hybrid-strategy)
5. [Strategy Implementation and Configuration Examples](#strategy-implementation-and-configuration-examples)
6. [Market Data Flow and Signal Generation](#market-data-flow-and-signal-generation)
7. [Strategy Evaluation and Parameter Optimization](#strategy-evaluation-and-parameter-optimization)
8. [Common Development Issues and Debugging](#common-development-issues-and-debugging)
9. [Beginner Education Framework](#beginner-education-framework)
10. [Strategy Complexity and Difficulty Ratings](#strategy-complexity-and-difficulty-ratings)

## Introduction
The QuantumbotX strategy framework provides a modular and extensible architecture for implementing algorithmic trading strategies. Built around an abstract base class and a centralized registration system, it enables developers to create, register, and dynamically load trading strategies. This document details the core components of the framework, including the `BaseStrategy` interface, the `STRATEGY_MAP` registration mechanism, and the implementation logic of each available strategy. It also covers how strategies process market data, generate trading signals, and integrate with the broader trading bot system. The framework has been enhanced with a comprehensive educational system for beginners, including strategy difficulty ratings, beginner-friendly defaults, and a progressive learning path.

## BaseStrategy Abstract Interface

The `BaseStrategy` class serves as the foundation for all trading strategies in the QuantumbotX framework. Defined in `base_strategy.py`, it is an abstract base class that enforces a consistent interface across all strategy implementations.

```python
class BaseStrategy(ABC):
    def __init__(self, bot_instance, params: dict = {}):
        self.bot = bot_instance
        self.params = params

    @abstractmethod
    def analyze(self, df):
        raise NotImplementedError("Each strategy must implement the `analyze(df)` method.")

    @classmethod
    def get_definable_params(cls):
        return []
```

### Key Components of BaseStrategy

- **Initialization (`__init__`)**: Accepts a `bot_instance` reference and a dictionary of parameters. These are stored as instance attributes for use in analysis.
- **Abstract Method (`analyze`)**: Must be implemented by all concrete strategies. It takes a pandas DataFrame containing market data and returns a dictionary with the trading signal, price, and explanation.
- **Class Method (`get_definable_params`)**: Returns a list of configurable parameters for the strategy, used in UI rendering and configuration. Strategies override this to expose their tunable settings.

### Inheritance Requirements
All concrete strategies must:
1. Inherit from `BaseStrategy`
2. Implement the `analyze` method
3. Optionally override `get_definable_params` to define user-configurable parameters
4. Define `name` and `description` class attributes for identification

**Section sources**
- [base_strategy.py](file://core/strategies/base_strategy.py#L4-L28)

## Strategy Registration and Dynamic Loading

The strategy registration system is managed through the `STRATEGY_MAP` dictionary in `strategy_map.py`. This map enables dynamic loading and instantiation of strategies by their unique identifiers.

```python
STRATEGY_MAP = {
    'MA_CROSSOVER': MACrossoverStrategy,
    'QUANTUMBOTX_HYBRID': QuantumBotXHybridStrategy,
    'QUANTUMBOTX_CRYPTO': QuantumBotXCryptoStrategy,
    'RSI_CROSSOVER': RSICrossoverStrategy,
    'BOLLINGER_REVERSION': BollingerBandsStrategy,
    'BOLLINGER_SQUEEZE': BollingerSqueezeStrategy,
    # ... additional strategies
}
```

### Registration Process
1. Each strategy class is imported at the top of `strategy_map.py`
2. The class is mapped to a unique string identifier in `STRATEGY_MAP`
3. The system uses this map to instantiate strategies dynamically when requested

### Dynamic Loading Mechanism
When a strategy is selected (e.g., via API or UI), the system:
1. Receives a strategy ID (e.g., "MA_CROSSOVER")
2. Looks up the corresponding class in `STRATEGY_MAP`
3. Instantiates the class with the provided parameters and bot instance
4. Returns the ready-to-use strategy object

This design enables:
- Easy addition of new strategies (just import and add to map)
- Runtime strategy selection
- Clean separation between strategy definition and usage
- Centralized management of all available strategies

The web interface (via JavaScript in `backtesting.js` and `trading_bots.js`) fetches available strategies from `/api/strategies`, which likely queries the `STRATEGY_MAP` to generate the response.

``mermaid
flowchart TD
A["User selects strategy ID"] --> B["API receives strategy ID"]
B --> C["Look up class in STRATEGY_MAP"]
C --> D{"Class found?"}
D --> |Yes| E["Instantiate strategy with params"]
D --> |No| F["Return error"]
E --> G["Strategy ready for analysis"]
```

**Diagram sources**
- [strategy_map.py](file://core/strategies/strategy_map.py#L1-L27)

**Section sources**
- [strategy_map.py](file://core/strategies/strategy_map.py#L1-L27)
- [backtesting.js](file://static/js/backtesting.js#L12-L44)
- [trading_bots.js](file://static/js/trading_bots.js#L18-L52)

## Available Strategies

This section details each available trading strategy, including its logic, parameters, and optimal market conditions.

### MA Crossover Strategy

**Name**: Moving Average Crossover  
**Description**: Generates signals based on crossovers between two moving averages. Ideal for trending markets.

#### Logic
- Calculates two Simple Moving Averages (SMA) with different periods
- **BUY signal**: Fast MA crosses above slow MA (Golden Cross)
- **SELL signal**: Fast MA crosses below slow MA (Death Cross)

#### Parameters
- **fast_period**: Period for the fast MA (default: 20)
- **slow_period**: Period for the slow MA (default: 50)

#### Optimal Conditions
- Strong trending markets
- Higher timeframes (H1, H4, D1)
- Avoids choppy or ranging markets

```python
def analyze(self, df):
    # Implementation details...
    if prev["ma_fast"] <= prev["ma_slow"] and last["ma_fast"] > last["ma_slow"]:
        signal = "BUY"
    elif prev["ma_fast"] >= prev["ma_slow"] and last["ma_fast"] < last["ma_slow"]:
        signal = "SELL"
```

**Section sources**
- [ma_crossover.py](file://core/strategies/ma_crossover.py#L1-L60)

### RSI Crossover Strategy

**Name**: RSI Crossover  
**Description**: Momentum-based strategy using RSI crossover with its moving average, validated by a long-term trend filter.

#### Logic
- Calculates RSI and its moving average
- Applies a long-term SMA trend filter
- **BUY signal**: Uptrend + RSI crosses above its MA
- **SELL signal**: Downtrend + RSI crosses below its MA

#### Parameters
- **rsi_period**: RSI calculation period (default: 14)
- **rsi_ma_period**: MA period for RSI smoothing (default: 10)
- **trend_filter_period**: SMA period for trend filtering (default: 50)

#### Optimal Conditions
- Markets with clear momentum
- Medium-term trends
- Avoids overbought/oversold extremes without confirmation

**Section sources**
- [rsi_crossover.py](file://core/strategies/rsi_crossover.py#L1-L84)

### Bollinger Bands Reversion Strategy

**Name**: Bollinger Bands Reversion  
**Description**: Mean reversion strategy based on price touching Bollinger Bands, with long-term trend filtering.

#### Logic
- Calculates Bollinger Bands with customizable length and standard deviation
- Uses a long-term SMA as trend filter
- **BUY signal**: Uptrend + price touches lower band
- **SELL signal**: Downtrend + price touches upper band

#### Parameters
- **bb_length**: Length for Bollinger Bands (default: 20)
- **bb_std**: Standard deviation multiplier (default: 2.0)
- **trend_filter_period**: SMA period for trend filter (default: 200)

#### Optimal Conditions
- Range-bound markets
- High volatility environments
- Counter-trend opportunities in established trends

**Section sources**
- [bollinger_reversion.py](file://core/strategies/bollinger_reversion.py#L1-L75)

### Bollinger Squeeze Breakout Strategy

**Name**: Bollinger Squeeze Breakout  
**Description**: Identifies low volatility periods (squeeze) as precursors to strong breakout moves.

#### Logic
- Monitors Bollinger Band width
- Detects "squeeze" when bandwidth falls below a threshold
- **BUY signal**: Breakout above upper band during squeeze
- **SELL signal**: Breakout below lower band during squeeze
- Uses RSI to avoid overbought/oversold entries

#### Parameters
- **bb_length**: Bollinger Bands length (default: 20)
- **bb_std**: Standard deviation (default: 2.0)
- **squeeze_window**: Window for average bandwidth (default: 10)
- **squeeze_factor**: Multiplier for squeeze threshold (default: 0.7)
- **rsi_period**: RSI period for confirmation (default: 14)

#### Optimal Conditions
- Pre-breakout consolidation phases
- News-driven volatility expansions
- High-momentum assets

**Section sources**
- [bollinger_squeeze.py](file://core/strategies/bollinger_squeeze.py#L1-L88)

### Ichimoku Cloud Strategy

**Name**: Ichimoku Cloud  
**Description**: Comprehensive trading system using the full Ichimoku Kinko Hyo framework.

#### Logic
- Calculates all Ichimoku components (Tenkan-sen, Kijun-sen, Senkou Span A/B)
- **BUY signal**: Tenkan/Kijun Golden Cross + price above cloud
- **SELL signal**: Tenkan/Kijun Death Cross + price below cloud
- Optional cloud filter can be disabled

#### Parameters
- **tenkan_period**: Tenkan-sen period (default: 9)
- **kijun_period**: Kijun-sen period (default: 26)
- **senkou_period**: Senkou Span B period (default: 52)
- **use_cloud_filter**: Whether to require cloud confirmation (default: True)

#### Optimal Conditions
- All market conditions
- Multiple timeframe analysis
- Trend confirmation and support/resistance

**Section sources**
- [ichimoku_cloud.py](file://core/strategies/ichimoku_cloud.py#L1-L124)

### QuantumbotX Hybrid Strategy

**Name**: QuantumbotX Hybrid  
**Description**: Proprietary strategy combining multiple indicators with adaptive logic based on market regime.

#### Logic
- Uses ADX to determine market regime (trending vs. ranging)
- In trending markets: Uses MA crossover signals
- In ranging markets: Uses Bollinger Bands reversion signals
- All signals filtered by long-term trend direction

#### Parameters
- **adx_period**: ADX calculation period (default: 14)
- **adx_threshold**: Threshold to distinguish trending/ranging (default: 25)
- **ma_fast_period**: Fast MA period (default: 20)
- **ma_slow_period**: Slow MA period (default: 50)
- **bb_length**: Bollinger Bands length (default: 20)
- **bb_std**: Bollinger Bands standard deviation (default: 2.0)
- **trend_filter_period**: Long-term trend filter period (default: 200)

#### Optimal Conditions
- All market conditions
- Adaptive to changing volatility
- Robust across different asset classes

**Section sources**
- [quantumbotx_hybrid.py](file://core/strategies/quantumbotx_hybrid.py#L1-L113)

## Strategy Implementation and Configuration Examples

### Creating a Custom Strategy
```python
from core.strategies.base_strategy import BaseStrategy

class MyCustomStrategy(BaseStrategy):
    name = "My Custom Strategy"
    description = "A simple example strategy."
    
    @classmethod
    def get_definable_params(cls):
        return [
            {"name": "threshold", "label": "Signal Threshold", "type": "number", "default": 50}
        ]
    
    def analyze(self, df):
        if len(df) < 10:
            return {"signal": "HOLD", "price": None, "explanation": "Insufficient data"}
        
        last_price = df.iloc[-1]["close"]
        signal = "BUY" if last_price > self.params.get("threshold", 50) else "SELL"
        
        return {
            "signal": signal,
            "price": last_price,
            "explanation": f"Price {last_price} compared to threshold"
        }
```

### Registering a New Strategy
Add to `strategy_map.py`:
```python
from .my_custom_strategy import MyCustomStrategy

STRATEGY_MAP = {
    # ... existing strategies
    'MY_CUSTOM': MyCustomStrategy,
}
```

### Strategy Configuration
Strategies expose their parameters via `get_definable_params()`, which is used by the UI to render configuration forms. Each parameter includes:
- **name**: Internal identifier
- **label**: User-friendly display name
- **type**: Input type (number, boolean, etc.)
- **default**: Default value
- **step**: Step increment for number inputs

## Market Data Flow and Signal Generation

### Data Flow Architecture
``mermaid
flowchart LR
A[Market Data Source] --> B[Data Preprocessing]
B --> C[Strategy Engine]
C --> D[analyze method]
D --> E[Signal Generation]
E --> F[Trading Bot Execution]
```

### Signal Generation Process
1. Market data (OHLCV) is loaded into a pandas DataFrame
2. The DataFrame is passed to the strategy's `analyze` method
3. The strategy calculates indicators and applies its logic
4. A signal dictionary is returned with:
   - **signal**: BUY, SELL, or HOLD
   - **price**: Current market price
   - **explanation**: Human-readable rationale
5. The trading bot acts on the signal according to risk management rules

### Backtesting vs Live Trading
- **Live Trading**: Uses `analyze(df)` method on recent data
- **Backtesting**: Uses `analyze_df(df)` method on historical data for vectorized performance

**Section sources**
- [ma_crossover.py](file://core/strategies/ma_crossover.py#L30-L60)
- [rsi_crossover.py](file://core/strategies/rsi_crossover.py#L30-L84)

## Strategy Evaluation and Parameter Optimization

### Performance Evaluation Metrics
- **Win Rate**: Percentage of profitable trades
- **Profit Factor**: Gross profit / Gross loss
- **Maximum Drawdown**: Largest peak-to-trough decline
- **Sharpe Ratio**: Risk-adjusted return
- **Expectancy**: Average profitability per trade

### Parameter Optimization
Use the `analyze_df` method for backtesting across parameter combinations:
```python
# Example: Grid search for MA Crossover
best_result = None
for fast in range(10, 30, 5):
    for slow in range(40, 60, 5):
        strategy = MACrossoverStrategy(bot, {"fast_period": fast, "slow_period": slow})
        results = strategy.analyze_df(historical_data)
        # Calculate performance metrics
        # Track best performing combination
```

### Best Practices
- Use walk-forward optimization to avoid overfitting
- Test across multiple market conditions
- Validate results on out-of-sample data
- Consider transaction costs in evaluation
- Monitor strategy performance decay over time

## Common Development Issues and Debugging

### Common Issues
1. **Insufficient Data**: Strategy requires more bars than available
   - *Solution*: Check data length before analysis
2. **Indicator Calculation Errors**: NaN values in results
   - *Solution*: Use `dropna()` and validate indicator columns
3. **Parameter Validation**: Invalid parameter values
   - *Solution*: Implement parameter validation in `__init__`
4. **Indexing Errors**: Incorrect DataFrame indexing
   - *Solution*: Use `.iloc[-1]` for last row, `.iloc[-2]` for previous

### Debugging Techniques
- **Logging**: Add debug logs to track indicator values and decision logic
- **Visualization**: Plot indicators and signals using matplotlib
- **Unit Testing**: Test edge cases and boundary conditions
- **Step-by-Step Execution**: Use debugger to trace signal generation
- **Data Validation**: Verify input DataFrame structure and completeness

### Error Handling
Always include robust error handling in the `analyze` method:
```python
def analyze(self, df):
    if df is None or df.empty:
        return {"signal": "HOLD", "price": None, "explanation": "No data"}
    
    # Additional validation...
    
    try:
        # Analysis logic
        pass
    except Exception as e:
        return {"signal": "HOLD", "price": None, "explanation": f"Error: {str(e)}"}
```

**Section sources**
- [ma_crossover.py](file://core/strategies/ma_crossover.py#L20-L30)
- [ichimoku_cloud.py](file://core/strategies/ichimoku_cloud.py#L20-L40)

## Beginner Education Framework

The QuantumbotX framework includes a comprehensive educational system designed to help new traders learn algorithmic trading concepts safely and effectively.

### ATR-Based Risk Management Education
The system implements an advanced ATR (Average True Range) based risk management system with automatic protections for volatile instruments like gold (XAUUSD).

**Key Features:**
- **ATR Calculation**: Measures average daily price movement for each instrument
- **Risk Percentage**: Limits maximum loss per trade (recommended: 1-2%)
- **Dynamic Position Sizing**: Automatically calculates appropriate lot sizes
- **Gold Protection System**: Special safeguards for highly volatile gold trading
- **Volatility-Adaptive Parameters**: Adjusts stop loss and take profit distances based on current market conditions

### Strategy Selector for Beginners
The `StrategySelector` class provides guided onboarding for new traders:

```python
class StrategySelector:
    """Helper class to guide beginners in strategy selection"""
    
    def get_beginner_dashboard(self) -> dict:
        """Get complete beginner-friendly dashboard"""
        return {
            'recommended_strategies': self._get_beginner_strategies(),
            'learning_path': self._get_learning_path(),
            'quick_start_guide': self._get_quick_start_guide(),
            'safety_tips': self._get_safety_tips()
        }
```

### Progressive Learning Path
New traders are guided through a structured learning progression:

1. **Week 1-2: Foundation** - MA Crossover strategy
2. **Week 3-4: Momentum** - RSI Crossover strategy  
3. **Week 5-6: Breakouts** - Turtle Breakout strategy
4. **Month 2: Intermediate** - Bollinger Reversion strategy
5. **Month 3: Advanced** - Pulse Sync strategy

### Safety Features for Beginners
- Automatic risk capping for volatile instruments
- Special gold protection prevents account blowouts
- Dynamic position sizing based on market volatility
- Emergency brake system skips dangerous trades
- Real-time risk calculation and logging

**Section sources**
- [beginner_defaults.py](file://core/strategies/beginner_defaults.py#L1-L311)
- [strategy_selector.py](file://core/strategies/strategy_selector.py#L1-L205)
- [atr_education.py](file://core/education/atr_education.py#L1-L274)

## Strategy Complexity and Difficulty Ratings

The framework includes a comprehensive strategy rating system to help users select appropriate strategies based on their experience level.

### Strategy Metadata
Each strategy is classified with difficulty ratings and complexity scores:

```python
STRATEGY_METADATA = {
    # BEGINNER FRIENDLY
    'MA_CROSSOVER': {
        'difficulty': 'BEGINNER',
        'complexity_score': 2,
        'recommended_for_beginners': True,
        'description': 'Simple trend following - perfect first strategy',
        'market_types': ['FOREX', 'GOLD', 'CRYPTO'],
        'learning_priority': 1
    },
    
    # INTERMEDIATE
    'BOLLINGER_REVERSION': {
        'difficulty': 'INTERMEDIATE',
        'complexity_score': 3,
        'recommended_for_beginners': False,
        'description': 'Mean reversion - good for ranging markets',
        'market_types': ['FOREX'],
        'learning_priority': 4
    },
    
    # ADVANCED
    'MERCY_EDGE': {
        'difficulty': 'ADVANCED',
        'complexity_score': 6,
        'recommended_for_beginners': False,
        'description': 'AI-enhanced multi-timeframe analysis',
        'market_types': ['FOREX', 'GOLD'],
        'learning_priority': 9
    },
    
    # EXPERT
    'QUANTUMBOTX_HYBRID': {
        'difficulty': 'EXPERT',
        'complexity_score': 8,
        'recommended_for_beginners': False,
        'description': 'Multi-asset adaptive strategy',
        'market_types': ['FOREX', 'GOLD', 'CRYPTO'],
        'learning_priority': 11
    }
}
```

### Difficulty Levels
- **BEGINNER (Complexity 1-3)**: Simple strategies with few parameters, ideal for learning
- **INTERMEDIATE (Complexity 4-6)**: Moderate complexity, requires understanding of multiple indicators
- **ADVANCED (Complexity 7-9)**: Complex strategies with multiple parameters and conditions
- **EXPERT (Complexity 10-12)**: Highly sophisticated strategies for experienced traders

### Experience-Based Recommendations
The system provides tailored strategy recommendations based on user experience:

```python
STRATEGY_RECOMMENDATIONS = {
    'ABSOLUTE_BEGINNER': [
        'MA_CROSSOVER',
        'TURTLE_BREAKOUT'
    ],
    
    'BEGINNER': [
        'MA_CROSSOVER',
        'RSI_CROSSOVER',
        'TURTLE_BREAKOUT'
    ],
    
    'INTERMEDIATE': [
        'MA_CROSSOVER',
        'RSI_CROSSOVER', 
        'BOLLINGER_REVERSION',
        'PULSE_SYNC'
    ],
    
    'ADVANCED': [
        'QUANTUM_VELOCITY',
        'MERCY_EDGE',
        'ICHIMOKU_CLOUD'
    ],
    
    'EXPERT': [
        'QUANTUMBOTX_CRYPTO',
        'QUANTUMBOTX_HYBRID',
        'DYNAMIC_BREAKOUT'
    ]
}
```

### Beginner-Friendly Defaults
Each strategy includes optimized default parameters for beginners:

```python
BEGINNER_DEFAULTS = {
    'MA_CROSSOVER': {
        'difficulty': 'BEGINNER',
        'recommended': True,
        'description': 'Simple trend following - When fast line crosses slow line',
        'params': {
            'fast_period': 10,
            'slow_period': 30
        },
        'explanation': {
            'fast_period': 'Fast moving average (10 = responds quickly to price changes)',
            'slow_period': 'Slow moving average (30 = shows main trend direction)'
        }
    }
}
```

**Section sources**
- [strategy_map.py](file://core/strategies/strategy_map.py#L20-L165)
- [beginner_defaults.py](file://core/strategies/beginner_defaults.py#L1-L311)
- [strategy_selector.py](file://core/strategies/strategy_selector.py#L1-L205)