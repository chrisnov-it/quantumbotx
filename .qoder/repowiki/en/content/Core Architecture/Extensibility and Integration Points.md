# Extensibility and Integration Points

<cite>
**Referenced Files in This Document**   
- [base_strategy.py](file://core\strategies\base_strategy.py)
- [strategy_map.py](file://core\strategies\strategy_map.py)
- [api_bots.py](file://core\routes\api_bots.py)
- [models.py](file://core\db\models.py)
- [queries.py](file://core\db\queries.py)
- [init_db.py](file://init_db.py)
- [trade.py](file://core\mt5\trade.py)
- [api_profile.py](file://core\routes\api_profile.py)
</cite>

## Table of Contents
1. [Introduction](#introduction)
2. [Strategy Extensibility](#strategy-extensibility)
3. [API Endpoint Extension](#api-endpoint-extension)
4. [Database Schema Extension](#database-schema-extension)
5. [MT5 Integration Enhancement](#mt5-integration-enhancement)
6. [Conclusion](#conclusion)

## Introduction
This document provides comprehensive guidance on the extensibility points within the quantumbotx trading system. It details how developers can extend the platform's functionality through custom trading strategies, new API endpoints, database schema modifications, and enhanced MetaTrader 5 (MT5) integration. The documentation includes step-by-step examples, code snippets, and considerations for backward compatibility, testing, and deployment.

## Strategy Extensibility

The quantumbotx platform enables extensibility through a well-defined strategy pattern that allows developers to create new trading algorithms by subclassing the `BaseStrategy` class and registering them in the strategy map.

### Base Strategy Architecture
The `BaseStrategy` class serves as an abstract base class that defines the contract for all trading strategies. It uses Python's Abstract Base Class (ABC) pattern to enforce implementation of the core `analyze` method.

```python
# core/strategies/base_strategy.py
from abc import ABC, abstractmethod

class BaseStrategy(ABC):
    """
    Abstract base class for all trading strategies.
    Each strategy must inherit from this class and implement the `analyze` method.
    """
    def __init__(self, bot_instance, params: dict = {}):
        self.bot = bot_instance
        self.params = params

    @abstractmethod
    def analyze(self, df):
        """
        Core method that must be overridden by each derived strategy.
        This method must return a dictionary containing the analysis results.
        Accepts DataFrame as input.
        """
        raise NotImplementedError("Each strategy must implement the `analyze(df)` method.")

    @classmethod
    def get_definable_params(cls):
        """
        Class method that returns a list of parameters that can be set by the user.
        Each derived strategy should override this if it has parameters.
        """
        return []
```

### Strategy Registration Process
Strategies are registered and accessed through the `strategy_map.py` file, which maintains a dictionary mapping strategy identifiers to their corresponding classes. This pattern enables dynamic strategy loading and provides a centralized registry.

```python
# core/strategies/strategy_map.py
from .ma_crossover import MACrossoverStrategy
from .quantumbotx_hybrid import QuantumBotXHybridStrategy
from .rsi_crossover import RSICrossoverStrategy
from .bollinger_reversion import BollingerBandsStrategy
from .bollinger_squeeze import BollingerSqueezeStrategy

STRATEGY_MAP = {
    'MA_CROSSOVER': MACrossoverStrategy,
    'QUANTUMBOTX_HYBRID': QuantumBotXHybridStrategy,
    'RSI_CROSSOVER': RSICrossoverStrategy,
    'BOLLINGER_REVERSION': BollingerBandsStrategy,
    'BOLLINGER_SQUEEZE': BollingerSqueezeStrategy,
    # Additional strategies...
}
```

### Step-by-Step: Creating a New Strategy
To add a new trading strategy, follow these steps:

1. **Create a new strategy file** in the `core/strategies/` directory:
```python
# core/strategies/my_new_strategy.py
from .base_strategy import BaseStrategy

class MyNewStrategy(BaseStrategy):
    """
    Custom trading strategy based on a unique algorithm.
    """
    name = "My New Strategy"
    description = "A custom strategy with specific market logic."
    
    @classmethod
    def get_definable_params(cls):
        return [
            {"name": "period", "type": "int", "default": 14, "min": 5, "max": 50},
            {"name": "threshold", "type": "float", "default": 0.5, "min": 0.1, "max": 2.0}
        ]
    
    def analyze(self, df):
        """
        Implements the core trading logic.
        Returns a dictionary with signal and analysis data.
        """
        # Extract parameters
        period = self.params.get('period', 14)
        threshold = self.params.get('threshold', 0.5)
        
        # Calculate custom indicator
        df['custom_indicator'] = df['close'].rolling(period).mean() / df['close']
        
        # Generate signal based on threshold
        current_value = df['custom_indicator'].iloc[-1]
        if current_value < (1 - threshold):
            signal = 'BUY'
            reason = f'Indicator value {current_value:.3f} below buy threshold'
        elif current_value > (1 + threshold):
            signal = 'SELL'
            reason = f'Indicator value {current_value:.3f} above sell threshold'
        else:
            signal = 'HOLD'
            reason = f'Indicator value {current_value:.3f} within threshold range'
        
        return {
            'signal': signal,
            'reason': reason,
            'indicator_value': current_value,
            'timestamp': df.index[-1].isoformat()
        }
```

2. **Register the strategy** in `strategy_map.py`:
```python
# Add import at the top
from .my_new_strategy import MyNewStrategy

# Add to STRATEGY_MAP dictionary
STRATEGY_MAP = {
    # Existing strategies...
    'MY_NEW_STRATEGY': MyNewStrategy,
}
```

3. **Verify API exposure** through the `/api/strategies` endpoint:
```python
# The strategy will automatically appear in the API response
{
    "id": "MY_NEW_STRATEGY",
    "name": "My New Strategy",
    "description": "A custom strategy with specific market logic."
}
```

### Backward Compatibility and Testing
When adding new strategies, consider the following:

- **Parameter defaults**: Always provide sensible default values in `get_definable_params()` to ensure backward compatibility
- **Error handling**: Implement robust error handling in the `analyze` method to prevent bot crashes
- **Unit testing**: Create test files (e.g., `my_new_strategy_test.py`) to validate strategy logic
- **Backtesting**: Verify the strategy's performance using historical data before deployment

**Section sources**
- [base_strategy.py](file://core\strategies\base_strategy.py#L1-L28)
- [strategy_map.py](file://core\strategies\strategy_map.py#L1-L26)

## API Endpoint Extension

The quantumbotx platform uses Flask blueprints to organize and extend API endpoints. This modular approach allows for clean separation of concerns and easy addition of new functionality.

### Blueprint Architecture
The application registers multiple blueprints in the main application factory (`__init__.py`), each responsible for a specific domain of functionality:

```python
# core/__init__.py (simplified)
from .routes.api_bots import api_bots
from .routes.api_profile import api_profile
from .routes.api_portfolio import api_portfolio

app.register_blueprint(api_bots)
app.register_blueprint(api_profile)
app.register_blueprint(api_portfolio)
```

### Step-by-Step: Adding a New API Endpoint
To introduce a new API endpoint, follow these steps:

1. **Create a new route file** in the `core/routes/` directory:
```python
# core/routes/api_analytics.py
from flask import Blueprint, jsonify, request
from core.db import queries
from core.utils.mt5 import get_rates_mt5
import pandas_ta as ta

api_analytics = Blueprint('api_analytics', __name__)

@api_analytics.route('/api/analytics/volatility', methods=['GET'])
def get_volatility_analysis():
    """
    Provides volatility analysis for a given symbol and timeframe.
    """
    try:
        symbol = request.args.get('symbol', 'EURUSD')
        timeframe_str = request.args.get('timeframe', 'H1')
        
        # Map timeframe string to MT5 constant
        timeframe_map = {
            'M1': mt5.TIMEFRAME_M1, 'M5': mt5.TIMEFRAME_M5, 'M15': mt5.TIMEFRAME_M15,
            'H1': mt5.TIMEFRAME_H1, 'H4': mt5.TIMEFRAME_H4, 'D1': mt5.TIMEFRAME_D1
        }
        timeframe = timeframe_map.get(timeframe_str.upper(), mt5.TIMEFRAME_H1)
        
        # Get historical data
        df = get_rates_mt5(symbol, timeframe, 100)
        if df is None or df.empty:
            return jsonify({"error": f"Failed to fetch data for {symbol}"}), 404
        
        # Calculate volatility metrics
        df.ta.atr(length=14, append=True)
        df.ta.bbands(close=df['close'], length=20, std=2, append=True)
        
        # Prepare response data
        latest = df.iloc[-1]
        volatility_data = {
            'symbol': symbol,
            'timeframe': timeframe_str,
            'current_price': float(latest['close']),
            'atr': float(latest['ATRr_14']) if 'ATRr_14' in latest else None,
            'bb_upper': float(latest['BBU_20_2.0']) if 'BBU_20_2.0' in latest else None,
            'bb_lower': float(latest['BBL_20_2.0']) if 'BBL_20_2.0' in latest else None,
            'bb_width': (float(latest['BBU_20_2.0']) - float(latest['BBL_20_2.0'])) / float(latest['close']) if 'BBU_20_2.0' in latest and 'BBL_20_2.0' in latest else None,
            'timestamp': df.index[-1].isoformat()
        }
        
        return jsonify(volatility_data)
        
    except Exception as e:
        return jsonify({"error": f"Failed to calculate volatility: {str(e)}"}), 500
```

2. **Register the blueprint** in the main application (`core/__init__.py`):
```python
# Add import at the top
from .routes.api_analytics import api_analytics

# Add registration
app.register_blueprint(api_analytics)
```

3. **Verify the new endpoint** is accessible:
```bash
curl "http://localhost:5000/api/analytics/volatility?symbol=EURUSD&timeframe=H1"
```

### Example: Profile Management Endpoint
The `api_profile.py` file demonstrates a complete implementation of CRUD operations for user profile management:

```python
# core/routes/api_profile.py
from flask import Blueprint, jsonify, request
import sqlite3
from werkzeug.security import generate_password_hash

api_profile = Blueprint('api_profile', __name__)

@api_profile.route('/api/profile', methods=['GET'])
def get_profile():
    conn = get_db()
    user = conn.execute('SELECT id, name, email, strftime("%d %b %Y", join_date) as join_date FROM users WHERE id = ?', (1,)).fetchone()
    conn.close()
    if user is None:
        return jsonify({'error': 'User not found'}), 404
    return jsonify(dict(user))

@api_profile.route('/api/profile', methods=['PUT'])
def update_profile():
    data = request.json
    name = data.get('name')
    password = data.get('password')

    if not name:
        return jsonify({'error': 'Name cannot be empty'}), 400

    conn = get_db()
    if password:
        conn.execute('UPDATE users SET name = ?, password_hash = ? WHERE id = ?', (name, generate_password_hash(password), 1))
    else:
        conn.execute('UPDATE users SET name = ? WHERE id = ?', (name, 1))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Profile updated successfully.'})
```

### Best Practices for API Extension
- **Consistent naming**: Follow existing naming conventions for routes and response formats
- **Error handling**: Implement comprehensive error handling with appropriate HTTP status codes
- **Input validation**: Validate all input parameters to prevent injection attacks
- **Documentation**: Include docstrings that describe the endpoint's purpose and parameters
- **Authentication**: Consider security requirements and implement appropriate authentication

**Section sources**
- [api_bots.py](file://core\routes\api_bots.py#L1-L167)
- [api_profile.py](file://core\routes\api_profile.py#L1-L38)

## Database Schema Extension

The quantumbotx platform uses SQLite for data persistence, with a schema defined in the `init_db.py` file. The database layer consists of models, connections, and queries that provide a structured approach to data storage and retrieval.

### Current Database Schema
The database schema is initialized through the `init_db.py` script, which creates the following tables:

```python
# init_db.py
# Table: users
sql_create_users_table = """
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    join_date DATETIME DEFAULT CURRENT_TIMESTAMP
);
"""

# Table: bots
sql_create_bots_table = """
CREATE TABLE IF NOT EXISTS bots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    market TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'Paused',
    lot_size REAL NOT NULL DEFAULT 0.01,
    sl_pips INTEGER NOT NULL DEFAULT 100,
    tp_pips INTEGER NOT NULL DEFAULT 200,
    timeframe TEXT NOT NULL DEFAULT 'H1',
    check_interval_seconds INTEGER NOT NULL DEFAULT 60,
    strategy TEXT NOT NULL,
    strategy_params TEXT
);
"""

# Table: trade_history
sql_create_history_table = """
CREATE TABLE IF NOT EXISTS trade_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    bot_id INTEGER NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    action TEXT NOT NULL,
    details TEXT,
    is_notification INTEGER NOT NULL DEFAULT 0,
    is_read INTEGER NOT NULL DEFAULT 0,
    FOREIGN KEY (bot_id) REFERENCES bots (id) ON DELETE CASCADE
);
"""

# Table: backtest_results
sql_create_backtest_results_table = """
CREATE TABLE IF NOT EXISTS backtest_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    strategy_name TEXT NOT NULL,
    data_filename TEXT NOT NULL,
    total_profit_usd REAL NOT NULL,
    total_trades INTEGER NOT NULL,
    win_rate_percent REAL NOT NULL,
    max_drawdown_percent REAL NOT NULL,
    wins INTEGER NOT NULL,
    losses INTEGER NOT NULL,
    equity_curve TEXT, -- Stored as JSON
    trade_log TEXT,    -- Stored as JSON
    parameters TEXT    -- Stored as JSON
);
"""
```

### Step-by-Step: Extending the Database Schema
To extend the database schema for additional data storage needs, follow these steps:

1. **Modify the `init_db.py` file** to include the new table:
```python
# Add new table for strategy performance metrics
sql_create_strategy_metrics_table = """
CREATE TABLE IF NOT EXISTS strategy_performance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    strategy_id TEXT NOT NULL,
    period_start DATETIME NOT NULL,
    period_end DATETIME NOT NULL,
    total_trades INTEGER NOT NULL,
    winning_trades INTEGER NOT NULL,
    losing_trades INTEGER NOT NULL,
    total_profit REAL NOT NULL,
    max_drawdown REAL NOT NULL,
    sharpe_ratio REAL,
    sortino_ratio REAL,
    profit_factor REAL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(strategy_id, period_start, period_end)
);
"""

# In the main() function, add the table creation
if conn is not None:
    # ... existing table creations
    print("\nCreating 'strategy_performance' table...")
    create_table(conn, sql_create_strategy_metrics_table)
```

2. **Create corresponding query functions** in `queries.py`:
```python
# core/db/queries.py
def save_strategy_performance(metrics_data):
    """Save strategy performance metrics to the database."""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO strategy_performance 
                (strategy_id, period_start, period_end, total_trades, winning_trades, 
                losing_trades, total_profit, max_drawdown, sharpe_ratio, sortino_ratio, profit_factor)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                metrics_data['strategy_id'],
                metrics_data['period_start'],
                metrics_data['period_end'],
                metrics_data['total_trades'],
                metrics_data['winning_trades'],
                metrics_data['losing_trades'],
                metrics_data['total_profit'],
                metrics_data['max_drawdown'],
                metrics_data.get('sharpe_ratio'),
                metrics_data.get('sortino_ratio'),
                metrics_data.get('profit_factor')
            ))
            conn.commit()
            return cursor.lastrowid
    except sqlite3.Error as e:
        logger.error(f"Failed to save strategy performance: {e}", exc_info=True)
        return None

def get_strategy_performance(strategy_id, limit=10):
    """Retrieve performance metrics for a specific strategy."""
    try:
        with get_db_connection() as conn:
            performance = conn.execute('''
                SELECT * FROM strategy_performance 
                WHERE strategy_id = ? 
                ORDER BY period_start DESC 
                LIMIT ?
            ''', (strategy_id, limit)).fetchall()
            return [dict(row) for row in performance]
    except sqlite3.Error as e:
        logger.error(f"Database error when retrieving strategy performance: {e}")
        return []
```

3. **Update the models.py file** to include the new functionality:
```python
# core/db/models.py
def log_strategy_performance(bot_id, strategy_id, performance_data):
    """Log strategy performance metrics."""
    try:
        with sqlite3.connect('bots.db') as conn:
            cursor = conn.cursor()
            # Insert into strategy_performance table
            cursor.execute('''
                INSERT INTO strategy_performance 
                (strategy_id, period_start, period_end, total_trades, winning_trades, 
                losing_trades, total_profit, max_drawdown)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                strategy_id,
                performance_data['period_start'],
                performance_data['period_end'],
                performance_data['total_trades'],
                performance_data['winning_trades'],
                performance_data['losing_trades'],
                performance_data['total_profit'],
                performance_data['max_drawdown']
            ))
            conn.commit()
    except Exception as e:
        print(f"[DB ERROR] Failed to log strategy performance: {e}")
```

4. **Create API endpoints** to expose the new data:
```python
# In a new or existing route file
@api_analytics.route('/api/analytics/performance/<strategy_id>', methods=['GET'])
def get_strategy_performance_api(strategy_id):
    """Retrieve performance metrics for a specific strategy."""
    try:
        limit = request.args.get('limit', 10, type=int)
        performance = queries.get_strategy_performance(strategy_id, limit)
        return jsonify(performance)
    except Exception as e:
        return jsonify({"error": f"Failed to retrieve performance data: {str(e)}"}), 500
```

### Migration Strategy
When extending the database schema in a production environment:

- **Backward compatibility**: Ensure new schema changes do not break existing functionality
- **Data migration**: Plan for migration of existing data if table structures change
- **Testing**: Test schema changes thoroughly in a staging environment
- **Rollback plan**: Have a rollback strategy in case of issues
- **Versioning**: Consider implementing database versioning for complex migrations

**Section sources**
- [models.py](file://core\db\models.py#L1-L20)
- [queries.py](file://core\db\queries.py#L1-L174)
- [init_db.py](file://init_db.py#L1-L114)

## MT5 Integration Enhancement

The quantumbotx platform integrates with MetaTrader 5 (MT5) through a dedicated module that handles trading operations, market data retrieval, and account management. This integration can be enhanced to support new order types, market data requests, and advanced trading features.

### Current MT5 Integration
The core MT5 functionality is implemented in the `trade.py` file, which provides functions for trade execution, lot size calculation, and position management.

```python
# core/mt5/trade.py
def calculate_lot_size(account_currency, symbol, risk_percent, sl_price, entry_price):
    """Calculate appropriate lot size based on risk."""
    try:
        # Get account and symbol information
        account_info = mt5.account_info()
        if account_info is None:
            logger.error("Failed to get account information.")
            return None

        symbol_info = mt5.symbol_info(symbol)
        if symbol_info is None:
            logger.error(f"Failed to get info for symbol {symbol}.")
            return None

        # Calculate risk amount
        balance = account_info.balance
        amount_to_risk = balance * (risk_percent / 100.0)
        sl_pips_distance = abs(entry_price - sl_price)
        
        # Calculate value per lot
        lot_value_check = mt5.order_calc_profit(
            mt5.ORDER_TYPE_BUY, symbol, 1.0, entry_price, sl_price
        )
        if lot_value_check is None or lot_value_check == 0:
            logger.error(f"Failed to calculate profit/loss for {symbol}")
            return None

        # Calculate lot size
        loss_for_one_lot = abs(lot_value_check)
        lot_size = amount_to_risk / loss_for_one_lot

        # Adjust for broker limitations
        volume_step = symbol_info.volume_step
        min_volume = symbol_info.volume_min
        max_volume = symbol_info.volume_max

        lot_size = math.floor(lot_size / volume_step) * volume_step
        lot_size = round(lot_size, len(str(volume_step).split('.')[1]) if '.' in str(volume_step) else 0)

        if lot_size < min_volume:
            logger.warning(f"Calculated lot size ({lot_size}) below minimum ({min_volume}). Using minimum lot.")
            return min_volume
        
        if lot_size > max_volume:
            logger.warning(f"Calculated lot size ({lot_size}) above maximum ({max_volume}). Using maximum lot.")
            return max_volume

        return lot_size

    except Exception as e:
        logger.error(f"Error calculating lot size: {e}", exc_info=True)
        return None
```

### Step-by-Step: Enhancing MT5 Integration
To enhance the MT5 integration with new order types or market data requests, follow these steps:

1. **Add support for new order types** in `trade.py`:
```python
# core/mt5/trade.py
def place_pending_order(symbol, order_type, price, risk_percent, sl_pips, tp_pips, magic_id, expiration_hours=24):
    """
    Place a pending order (Buy Limit, Buy Stop, Sell Limit, Sell Stop).
    """
    try:
        # Validate order type
        valid_pending_types = [
            mt5.ORDER_TYPE_BUY_LIMIT, mt5.ORDER_TYPE_BUY_STOP,
            mt5.ORDER_TYPE_SELL_LIMIT, mt5.ORDER_TYPE_SELL_STOP
        ]
        if order_type not in valid_pending_types:
            return None, "Invalid pending order type"

        # Get symbol info
        symbol_info = mt5.symbol_info(symbol)
        if symbol_info is None:
            return None, f"Symbol {symbol} not found"

        digits = symbol_info.digits

        # Calculate lot size based on risk
        account_info = mt5.account_info()
        if account_info is None:
            return None, "Failed to get account info"

        # For pending orders, we need to estimate SL/TP distance
        # This could be based on ATR or fixed pips
        sl_distance = sl_pips * symbol_info.point
        tp_distance = tp_pips * symbol_info.point

        sl_level = round(price - sl_distance if order_type in [mt5.ORDER_TYPE_BUY_LIMIT, mt5.ORDER_TYPE_BUY_STOP] else price + sl_distance, digits)
        tp_level = round(price + tp_distance if order_type in [mt5.ORDER_TYPE_BUY_LIMIT, mt5.ORDER_TYPE_BUY_STOP] else price - tp_distance, digits)

        # Calculate lot size
        lot_size = calculate_lot_size(
            account_info.currency, symbol, risk_percent, 
            sl_level, price
        )
        if lot_size is None:
            return None, "Failed to calculate lot size."

        # Set expiration time
        from datetime import datetime, timedelta
        expiration_time = datetime.now() + timedelta(hours=expiration_hours)

        # Create order request
        request = {
            "action": mt5.TRADE_ACTION_PENDING,
            "symbol": symbol,
            "volume": lot_size,
            "type": order_type,
            "price": price,
            "sl": sl_level,
            "tp": tp_level,
            "magic": magic_id,
            "comment": "QuantumBotX Pending Order",
            "type_time": mt5.ORDER_TIME_SPECIFIED,
            "type_filling": mt5.ORDER_FILLING_RETURN,
            "expiration": int(expiration_time.timestamp())
        }

        # Send order
        result = mt5.order_send(request)
        if result.retcode != mt5.TRADE_RETCODE_DONE:
            logger.error(f"Pending order FAILED, retcode={result.retcode}, comment: {result.comment}")
            return None, result.comment
        
        logger.info(f"Pending order SUCCESSFUL: Lot={lot_size}, Price={price}, SL={sl_level}, TP={tp_level}")
        return result, "Pending order placed successfully"

    except Exception as e:
        logger.error(f"Exception in place_pending_order: {e}", exc_info=True)
        return None, str(e)
```

2. **Add new market data requests** for advanced indicators:
```python
# core/mt5/trade.py
def get_advanced_market_data(symbol, timeframe, count=100):
    """
    Get market data with advanced technical indicators pre-calculated.
    """
    try:
        # Get base price data
        df = get_rates_mt5(symbol, timeframe, count)
        if df is None or df.empty:
            return None

        # Calculate advanced indicators
        df.ta.sma(length=20, append=True)  # Simple Moving Average
        df.ta.ema(length=50, append=True)  # Exponential Moving Average
        df.ta.rsi(length=14, append=True)  # Relative Strength Index
        df.ta.macd(append=True)            # MACD
        df.ta.bbands(close=df['close'], length=20, std=2, append=True)  # Bollinger Bands
        df.ta.atr(length=14, append=True)  # Average True Range

        # Add candlestick pattern recognition
        df.ta.cdl_pattern(name="all", append=True)

        # Calculate volatility
        df['volatility'] = df['close'].rolling(10).std() / df['close'].rolling(10).mean()

        # Add trend detection
        df['trend'] = 'SIDEWAYS'
        sma_20 = df['SMA_20'].iloc[-1]
        sma_50 = df['SMA_50'].iloc[-1]
        current_price = df['close'].iloc[-1]
        
        if current_price > sma_20 > sma_50:
            df['trend'] = 'UPTREND'
        elif current_price < sma_20 < sma_50:
            df['trend'] = 'DOWNTREND'

        return df

    except Exception as e:
        logger.error(f"Error getting advanced market data: {e}", exc_info=True)
        return None
```

3. **Update the utility functions** to support new features:
```python
# core/utils/mt5.py
# Add new timeframe constants if needed
TIMEFRAME_MAP = {
    "M1": mt5.TIMEFRAME_M1, "M2": mt5.TIMEFRAME_M2, "M3": mt5.TIMEFRAME_M3,
    "M5": mt5.TIMEFRAME_M5, "M15": mt5.TIMEFRAME_M15, "M30": mt5.TIMEFRAME_M30,
    "H1": mt5.TIMEFRAME_H1, "H2": mt5.TIMEFRAME_H2, "H4": mt5.TIMEFRAME_H4,
    "D1": mt5.TIMEFRAME_D1, "W1": mt5.TIMEFRAME_W1, "MN1": mt5.TIMEFRAME_MN1
}

# Add function to get symbol fundamentals
def get_symbol_fundamentals(symbol):
    """
    Get fundamental data for a symbol if available.
    """
    try:
        # This would connect to a fundamental data provider
        # For now, return mock data
        fundamentals = {
            "symbol": symbol,
            "pe_ratio": None,
            "eps": None,
            "dividend_yield": None,
            "market_cap": None,
            "beta": None,
            "last_updated": datetime.now().isoformat()
        }
        
        # Special handling for forex pairs
        forex_pairs = ['EURUSD', 'GBPUSD', 'USDJPY', 'AUDUSD', 'USDCAD']
        if symbol in forex_pairs:
            # Get interest rate differentials
            base_currency = symbol[:3]
            quote_currency = symbol[3:]
            fundamentals['base_rate'] = 0.0  # Would be retrieved from economic data
            fundamentals['quote_rate'] = 0.0
            fundamentals['rate_differential'] = 0.0
        
        return fundamentals
        
    except Exception as e:
        logger.error(f"Error getting symbol fundamentals: {e}", exc_info=True)
        return None
```

4. **Create API endpoints** to expose new MT5 features:
```python
# In api_chart.py or a new file
@api_chart.route('/api/chart/advanced-data')
def api_advanced_chart_data():
    """Provide chart data with advanced technical indicators."""
    symbol = request.args.get('symbol', 'EURUSD')
    timeframe_str = request.args.get('timeframe', 'H1')
    
    # Map timeframe
    timeframe = TIMEFRAME_MAP.get(timeframe_str.upper(), mt5.TIMEFRAME_H1)
    
    # Get advanced market data
    df = get_advanced_market_data(symbol, timeframe, 100)
    if df is None or df.empty:
        return jsonify({"error": "Failed to fetch advanced data"}), 500
    
    # Prepare response
    last_50_rows = df.tail(50)
    chart_data = {
        "labels": [ts.strftime('%H:%M') for ts in last_50_rows.index],
        "price": last_50_rows['close'].tolist(),
        "sma_20": last_50_rows['SMA_20'].tolist(),
        "sma_50": last_50_rows['SMA_50'].tolist(),
        "rsi": last_50_rows['RSI_14'].tolist(),
        "macd": last_50_rows['MACDh_12_26_9'].tolist(),
        "bb_upper": last_50_rows['BBU_20_2.0'].tolist(),
        "bb_lower": last_50_rows['BBL_20_2.0'].tolist(),
        "atr": last_50_rows['ATRr_14'].tolist()
    }
    
    return jsonify(chart_data)
```

### Best Practices for MT5 Integration
- **Error handling**: Implement comprehensive error handling for all MT5 API calls
- **Rate limiting**: Respect MT5 API rate limits to avoid connection issues
- **Connection management**: Properly initialize and shutdown MT5 connections
- **Logging**: Log all trading operations for audit and debugging purposes
- **Testing**: Test new features in a demo account before using with real funds
- **Security**: Never expose API credentials in client-side code

**Section sources**
- [trade.py](file://core\mt5\trade.py#L1-L152)
- [utils/mt5.py](file://core\utils\mt5.py#L1-L65)

## Conclusion
The quantumbotx platform provides multiple extensibility points that allow developers to customize and enhance its functionality. By following the patterns established in the codebase, developers can:

1. **Add new trading strategies** by subclassing `BaseStrategy` and registering them in `strategy_map.py`
2. **Introduce new API endpoints** using Flask blueprints in the routes directory
3. **Extend the database schema** in `init_db.py` and corresponding query functions in `queries.py`
4. **Enhance MT5 integration** with new order types, market data requests, and advanced trading features

When extending the platform, it's important to maintain backward compatibility, implement thorough testing, and follow the existing code patterns and conventions. The modular architecture of quantumbotx makes it possible to incrementally add new features while maintaining system stability and performance.

For production deployments, always test new extensions in a staging environment and have a rollback plan in place. The platform's design allows for continuous improvement and adaptation to changing market conditions and trading requirements.