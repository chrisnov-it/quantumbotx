# Adding New Trading Strategies

<cite>
**Referenced Files in This Document**   
- [base_strategy.py](file://core/strategies/base_strategy.py)
- [strategy_map.py](file://core/strategies/strategy_map.py)
- [validation.py](file://core/utils/validation.py)
- [logger.py](file://core/utils/logger.py)
- [engine.py](file://core/backtesting/engine.py)
- [ma_crossover.py](file://core/strategies/ma_crossover.py)
- [bollinger_squeeze.py](file://core/strategies/bollinger_squeeze.py)
</cite>

## Table of Contents
1. [Introduction](#introduction)
2. [Strategy Implementation Requirements](#strategy-implementation-requirements)
3. [Registering a New Strategy](#registering-a-new-strategy)
4. [Complete Strategy Example: Moving Average Envelope](#complete-strategy-example-moving-average-envelope)
5. [Best Practices for Strategy Design](#best-practices-for-strategy-design)
6. [Testing Strategies with Backtesting Engine](#testing-strategies-with-backtesting-engine)
7. [Common Pitfalls and Performance Optimization](#common-pitfalls-and-performance-optimization)

## Introduction
This document provides comprehensive guidance for developing custom trading strategies within the quantumbotx system. It details the process of extending the BaseStrategy class, implementing required methods, registering new strategies, and following best practices for robust strategy development. The documentation includes a complete example of a Moving Average Envelope strategy and covers testing procedures, risk management, and performance optimization techniques.

## Strategy Implementation Requirements

The quantumbotx system uses an object-oriented architecture where all trading strategies inherit from the `BaseStrategy` abstract base class. Contrary to the initial documentation objective, strategies do not implement `init`, `on_tick`, or `on_bar` methods. Instead, they must implement the `analyze_df` method for backtesting and potentially an `analyze` method for real-time execution.

The `BaseStrategy` class defines the contract that all strategies must follow:

```python
class BaseStrategy(ABC):
    def __init__(self, bot_instance, params: dict = {}):
        self.bot = bot_instance
        self.params = params

    @abstractmethod
    def analyze(self, df):
        raise NotImplementedError("Setiap strategi harus mengimplementasikan metode `analyze(df)`.")

    @classmethod
    def get_definable_params(cls):
        return []
```

Strategies must implement the `analyze_df` method which processes a pandas DataFrame containing price data and returns the same DataFrame with a 'signal' column containing 'BUY', 'SELL', or 'HOLD' values. The method should be vectorized for performance in backtesting scenarios.

**Section sources**
- [base_strategy.py](file://core/strategies/base_strategy.py#L4-L28)

## Registering a New Strategy

To make a new strategy available in the system, it must be registered in the `STRATEGY_MAP` dictionary within `strategy_map.py`. This dictionary maps strategy identifiers (strings) to their corresponding class implementations.

The registration process involves two steps:
1. Import the strategy class at the top of `strategy_map.py`
2. Add an entry to the `STRATEGY_MAP` dictionary with a unique identifier and the class reference

```python
from .new_strategy import NewStrategy

STRATEGY_MAP = {
    # existing strategies...
    'NEW_STRATEGY': NewStrategy,
}
```

The strategy identifier should follow the naming convention of uppercase letters and underscores. This identifier is used throughout the system to reference the strategy in configuration, backtesting, and execution contexts.

**Section sources**
- [strategy_map.py](file://core/strategies/strategy_map.py#L14-L26)

## Complete Strategy Example: Moving Average Envelope

Below is a complete implementation of a Moving Average Envelope strategy. This strategy creates upper and lower bands around a moving average and generates signals when the price crosses these bands.

```python
# core/strategies/ma_envelope.py

import pandas as pd
import numpy as np
import logging
from core.strategies.base_strategy import BaseStrategy
import core.utils.ta as ta

logger = logging.getLogger("QuantumBotX")

class MAEnvelopeStrategy(BaseStrategy):
    """
    Moving Average Envelope strategy that generates signals when price
    crosses above or below bands set at a percentage distance from a moving average.
    
    When the price crosses above the upper band, it generates a BUY signal.
    When the price crosses below the lower band, it generates a SELL signal.
    """
    
    def __init__(self, bot_instance, params: dict = {}):
        super().__init__(bot_instance, params)
        self.validate_parameters()
    
    def validate_parameters(self):
        """Validate strategy parameters using the system's validation utility."""
        errors = []
        
        # Validate required parameters
        envelope_pct = self.params.get('envelope_pct', 2.0)
        ma_period = self.params.get('ma_period', 20)
        
        if not isinstance(envelope_pct, (int, float)) or envelope_pct <= 0:
            errors.append("Envelope percentage must be a positive number.")
            
        if not isinstance(ma_period, int) or ma_period <= 0:
            errors.append("MA period must be a positive integer.")
        
        if errors:
            error_msg = "MA Envelope Strategy validation errors: " + "; ".join(errors)
            logger.error(error_msg)
            raise ValueError(error_msg)
    
    @classmethod
    def get_definable_params(cls):
        """
        Return list of parameters that can be configured by users.
        This enables UI integration for parameter customization.
        """
        return [
            {'name': 'ma_period', 'label': 'MA Period', 'type': 'int', 'default': 20, 'min': 2, 'max': 100},
            {'name': 'envelope_pct', 'label': 'Envelope Percentage', 'type': 'float', 'default': 2.0, 'min': 0.1, 'max': 10.0},
            {'name': 'ma_type', 'label': 'MA Type', 'type': 'select', 'options': ['sma', 'ema', 'wma'], 'default': 'sma'}
        ]
    
    def analyze(self, df):
        """
        Real-time analysis method for single bar processing.
        This method is called by the trading bot during live execution.
        
        Args:
            df: DataFrame with a single row of market data
            
        Returns:
            Dictionary with signal, price, and explanation
        """
        try:
            # Extract parameters
            ma_period = self.params.get('ma_period', 20)
            envelope_pct = self.params.get('envelope_pct', 2.0)
            ma_type = self.params.get('ma_type', 'sma')
            
            # Get current price
            current_price = df['close'].iloc[-1]
            
            # Calculate moving average based on type
            if ma_type == 'ema':
                ma_value = ta.ema(df['close'], length=ma_period).iloc[-1]
            elif ma_type == 'wma':
                ma_value = ta.wma(df['close'], length=ma_period).iloc[-1]
            else:  # sma
                ma_value = ta.sma(df['close'], length=ma_period).iloc[-1]
            
            # Calculate envelope bands
            upper_band = ma_value * (1 + envelope_pct / 100)
            lower_band = ma_value * (1 - envelope_pct / 100)
            
            # Generate signal
            signal = "HOLD"
            explanation = f"Price: {current_price:.5f}, MA: {ma_value:.5f}, Upper: {upper_band:.5f}, Lower: {lower_band:.5f}. No signal."
            
            # Check for BUY signal (price crosses above upper band)
            if current_price > upper_band:
                signal = "BUY"
                explanation = f"BUY signal: Price {current_price:.5f} crossed above upper band {upper_band:.5f}. MA: {ma_value:.5f}."
            
            # Check for SELL signal (price crosses below lower band)
            elif current_price < lower_band:
                signal = "SELL"
                explanation = f"SELL signal: Price {current_price:.5f} crossed below lower band {lower_band:.5f}. MA: {ma_value:.5f}."
            
            logger.info(f"MA Envelope analysis - {explanation}")
            
            return {
                "signal": signal,
                "price": current_price,
                "explanation": explanation,
                "indicators": {
                    "ma_value": round(ma_value, 5),
                    "upper_band": round(upper_band, 5),
                    "lower_band": round(lower_band, 5),
                    "envelope_pct": envelope_pct,
                    "ma_period": ma_period
                }
            }
            
        except Exception as e:
            error_msg = f"MA Envelope strategy analysis error: {str(e)}"
            logger.error(error_msg)
            return {
                "signal": "HOLD",
                "price": df['close'].iloc[-1] if len(df) > 0 else 0,
                "explanation": error_msg,
                "indicators": {}
            }
    
    def analyze_df(self, df):
        """
        Vectorized analysis method for backtesting.
        Processes the entire DataFrame at once for optimal performance.
        
        Args:
            df: DataFrame with historical market data
            
        Returns:
            DataFrame with added 'signal' column
        """
        try:
            # Extract parameters
            ma_period = self.params.get('ma_period', 20)
            envelope_pct = self.params.get('envelope_pct', 2.0)
            ma_type = self.params.get('ma_type', 'sma')
            
            # Validate data
            if df is None or df.empty or len(df) < ma_period:
                df['signal'] = 'HOLD'
                return df
            
            # Calculate moving average
            if ma_type == 'ema':
                df['ma_value'] = ta.ema(df['close'], length=ma_period)
            elif ma_type == 'wma':
                df['ma_value'] = ta.wma(df['close'], length=ma_period)
            else:  # sma
                df['ma_value'] = ta.sma(df['close'], length=ma_period)
            
            # Calculate envelope bands
            df['upper_band'] = df['ma_value'] * (1 + envelope_pct / 100)
            df['lower_band'] = df['ma_value'] * (1 - envelope_pct / 100)
            
            # Generate signals using vectorized operations
            price = df['close']
            upper = df['upper_band']
            lower = df['lower_band']
            
            # BUY when price crosses above upper band
            buy_signal = price > upper
            
            # SELL when price crosses below lower band
            sell_signal = price < lower
            
            # HOLD when no condition is met
            hold_signal = ~(buy_signal | sell_signal)
            
            # Assign signals
            df['signal'] = np.where(buy_signal, 'BUY', np.where(sell_signal, 'SELL', 'HOLD'))
            
            logger.info(f"MA Envelope backtest analysis completed. BUY signals: {sum(buy_signal)}, SELL signals: {sum(sell_signal)}")
            
            return df
            
        except Exception as e:
            error_msg = f"MA Envelope strategy backtest analysis error: {str(e)}"
            logger.error(error_msg)
            df['signal'] = 'HOLD'
            return df
```

After creating this file, register the strategy in `strategy_map.py`:

```python
from .ma_envelope import MAEnvelopeStrategy

STRATEGY_MAP = {
    # existing strategies...
    'MA_ENVELOPE': MAEnvelopeStrategy,
}
```

**Section sources**
- [ma_crossover.py](file://core/strategies/ma_crossover.py#L47-L60)
- [bollinger_squeeze.py](file://core/strategies/bollinger_squeeze.py#L60-L87)

## Best Practices for Strategy Design

### Risk Management and Parameter Validation
Implement comprehensive parameter validation to prevent invalid configurations that could lead to excessive risk or system errors. Use the provided validation utilities and extend them as needed.

```python
def validate_parameters(self):
    """Example of comprehensive parameter validation"""
    errors = []
    
    # Validate numerical parameters
    risk_percent = self.params.get('risk_percent', 1.0)
    if not isinstance(risk_percent, (int, float)) or risk_percent <= 0 or risk_percent > 10:
        errors.append("Risk percentage must be a positive number between 0.1 and 10.")
    
    # Validate time-based parameters
    timeframe = self.params.get('timeframe', 'H1')
    valid_timeframes = ['M1', 'M5', 'M15', 'M30', 'H1', 'H4', 'D1']
    if timeframe not in valid_timeframes:
        errors.append(f"Timeframe must be one of: {', '.join(valid_timeframes)}")
    
    if errors:
        logger.error(f"Strategy validation failed: {errors}")
        raise ValueError(f"Invalid parameters: {errors}")
```

### Logging Best Practices
Use structured logging to provide visibility into strategy behavior during both development and production:

```python
# Use appropriate log levels
logger.debug("Detailed calculation steps for debugging")
logger.info("Strategy executed successfully with BUY signal")
logger.warning("Unusual market condition detected")
logger.error("Strategy execution failed due to data error")
```

### Strategy Design Patterns
Follow these design principles for robust strategy implementation:

1. **Separation of Concerns**: Keep signal generation logic separate from risk management and execution logic
2. **Statelessness**: Design strategies to be stateless when possible to simplify testing and reduce bugs
3. **Parameterization**: Make all key values configurable through parameters rather than hardcoding
4. **Error Handling**: Implement comprehensive error handling to prevent strategy crashes

**Section sources**
- [validation.py](file://core/utils/validation.py#L1-L20)
- [logger.py](file://core/utils/logger.py#L1-L25)

## Testing Strategies with Backtesting Engine

The backtesting engine in `core/backtesting/engine.py` allows you to test new strategies against historical data. The engine simulates trades based on strategy signals and calculates performance metrics.

### Backtesting Workflow
1. Prepare historical data in a pandas DataFrame with columns: 'time', 'open', 'high', 'low', 'close', 'volume'
2. Configure strategy parameters
3. Call the `run_backtest` function with the strategy ID, parameters, and data
4. Analyze the results including equity curve, trade history, and performance metrics

```python
from core.backtesting.engine import run_backtest

# Example backtesting usage
result = run_backtest(
    strategy_id='MA_ENVELOPE',
    params={
        'ma_period': 20,
        'envelope_pct': 2.0,
        'risk_percent': 1.0,
        'sl_pips': 2.0,
        'tp_pips': 4.0
    },
    historical_data_df=historical_data,
    symbol_name='EURUSD'
)

# Analyze results
if 'error' in result:
    print(f"Backtest error: {result['error']}")
else:
    print(f"Final capital: {result['final_capital']}")
    print(f"Total trades: {len(result['trades'])}")
    print(f"Win rate: {result['win_rate']:.2%}")
    print(f"Max drawdown: {result['max_drawdown']:.2%}")
```

The backtesting engine automatically handles:
- Position sizing based on risk parameters
- Stop-loss and take-profit execution
- Trade logging and performance calculation
- Special handling for volatile instruments like XAUUSD
- ATR-based volatility adjustments

**Section sources**
- [engine.py](file://core/backtesting/engine.py#L0-L199)

## Common Pitfalls and Performance Optimization

### Common Pitfalls
1. **Lookahead Bias**: Using future data in signal generation. Always use `.shift(1)` when referencing current values to ensure signals are generated before the price movement.
2. **Overfitting**: Creating strategies that perform well on historical data but fail in live trading. Use walk-forward optimization and out-of-sample testing.
3. **Curve Fitting**: Optimizing parameters to fit historical noise rather than genuine market patterns.
4. **Ignoring Transaction Costs**: Not accounting for spreads, commissions, and slippage in backtesting.

### Performance Optimization
For computationally intensive calculations, use these optimization techniques:

1. **Vectorized Operations**: Use pandas and numpy vectorized operations instead of loops
```python
# Good: Vectorized operation
buy_signal = df['close'] > df['ma_value']

# Avoid: Looping through data
signals = []
for i in range(len(df)):
    if df['close'].iloc[i] > df['ma_value'].iloc[i]:
        signals.append('BUY')
    else:
        signals.append('HOLD')
```

2. **Efficient Indicator Calculation**: Use pandas_ta library methods which are optimized
```python
# Use built-in methods
df.ta.sma(length=20, append=True)
df.ta.rsi(length=14, append=True)

# Instead of manual calculation
df['sma'] = df['close'].rolling(20).mean()
```

3. **Memory Management**: Process data in chunks for very large datasets
4. **Caching**: Cache expensive calculations when possible
5. **Parallel Processing**: For multiple strategy evaluations, use multiprocessing

### Thread Safety Considerations
When accessing shared data in multi-threaded environments:
1. Use thread-safe data structures
2. Implement proper locking mechanisms
3. Avoid shared mutable state when possible
4. Use immutable data patterns

The quantumbotx system handles most threading concerns at the framework level, but custom strategies should still follow these principles when accessing shared resources.

**Section sources**
- [bollinger_squeeze.py](file://core/strategies/bollinger_squeeze.py#L60-L87)
- [turtle_breakout.py](file://core/strategies/turtle_breakout.py#L70-L118)
- [engine.py](file://core/backtesting/engine.py#L0-L199)