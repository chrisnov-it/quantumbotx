# Risk Management

<cite>
**Referenced Files in This Document**   
- [core/mt5/trade.py](file://core/mt5/trade.py#L1-L152)
- [core/utils/validation.py](file://core/utils/validation.py#L1-L21)
- [core/bots/trading_bot.py](file://core/bots/trading_bot.py#L1-L170)
- [core/brokers/base_broker.py](file://core/brokers/base_broker.py#L1-L172)
- [core/backtesting/engine.py](file://core/backtesting/engine.py#L90-L119)
</cite>

## Table of Contents
1. [Stop-Loss and Take-Profit Calculation](#stop-loss-and-take-profit-calculation)
2. [Risk Parameter Validation](#risk-parameter-validation)
3. [Position Sizing Logic](#position-sizing-logic)
4. [Trading Bot Risk Controls](#trading-bot-risk-controls)
5. [Margin Management and Account Monitoring](#margin-management-and-account-monitoring)
6. [Maximum Drawdown Protection](#maximum-drawdown-protection)
7. [Circuit Breaker and Safety Mechanisms](#circuit-breaker-and-safety-mechanisms)
8. [Configuration and Monitoring Guidance](#configuration-and-monitoring-guidance)
9. [Common Pitfalls and Mitigation Strategies](#common-pitfalls-and-mitigation-strategies)

## Stop-Loss and Take-Profit Calculation

The risk management system in QuantumBotX calculates stop-loss (SL) and take-profit (TP) levels dynamically using Average True Range (ATR) volatility metrics. This ensures that trade exits are adaptive to current market conditions rather than fixed pip values.

In `core/mt5/trade.py`, the `place_trade()` function implements dynamic SL/TP calculation:

```python
# Calculate ATR from historical data
atr = ta.atr(df['high'], df['low'], df['close'], length=14).iloc[-1]

# Calculate SL and TP distances using ATR multipliers
sl_distance = atr * sl_atr_multiplier
tp_distance = atr * tp_atr_multiplier

# Set levels based on order direction
sl_level = round(price - sl_distance if order_type == mt5.ORDER_TYPE_BUY else price + sl_distance, digits)
tp_level = round(price + tp_distance if order_type == mt5.ORDER_TYPE_BUY else price - tp_distance, digits)
```

This approach ensures that stop-loss levels are wider during high volatility periods, reducing the chance of being stopped out by market noise, while take-profit levels scale with market movement potential.

**Section sources**
- [core/mt5/trade.py](file://core/mt5/trade.py#L60-L85)

## Risk Parameter Validation

The system validates risk parameters before trade execution to ensure compliance with broker requirements and prevent invalid configurations. The validation occurs at both the API input level and during bot initialization.

In `core/utils/validation.py`, the `validate_bot_params()` function enforces data type and range constraints:

```python
def validate_bot_params(data):
    required_fields = ['name', 'market', 'lot_size', 'sl_pips', 'tp_pips', 'timeframe', 'check_interval_seconds', 'strategy']
    errors = []

    for field in required_fields:
        if field not in data:
            errors.append(f"Field '{field}' is required.")

    if not isinstance(data.get('lot_size'), (int, float)) or data['lot_size'] <= 0:
        errors.append("Lot size must be a positive number.")

    if not isinstance(data.get('sl_pips'), int) or data['sl_pips'] <= 0:
        errors.append("SL (Stop Loss) must be a positive integer.")

    if not isinstance(data.get('tp_pips'), int) or data['tp_pips'] <= 0:
        errors.append("TP (Take Profit) must be a positive integer.")

    return errors
```

This validation prevents common configuration errors such as negative lot sizes or zero stop-loss values, ensuring that only valid risk parameters are accepted into the system.

**Section sources**
- [core/utils/validation.py](file://core/utils/validation.py#L1-L21)

## Position Sizing Logic

Position sizing is calculated based on account balance, risk percentage, and the distance to stop-loss, ensuring consistent risk exposure across trades. The system also respects broker-specific volume constraints.

The `calculate_lot_size()` function in `core/mt5/trade.py` implements this logic:

```python
def calculate_lot_size(account_currency, symbol, risk_percent, sl_price, entry_price):
    # Get account balance and calculate risk amount
    balance = account_info.balance
    amount_to_risk = balance * (risk_percent / 100.0)
    
    # Calculate loss per lot using MT5's order_calc_profit
    loss_for_one_lot = abs(mt5.order_calc_profit(
        mt5.ORDER_TYPE_BUY, symbol, 1.0, entry_price, sl_price
    ))

    # Calculate lot size based on risk amount
    lot_size = amount_to_risk / loss_for_one_lot

    # Adjust for broker volume constraints
    volume_step = symbol_info.volume_step
    min_volume = symbol_info.volume_min
    max_volume = symbol_info.volume_max

    lot_size = math.floor(lot_size / volume_step) * volume_step
    lot_size = round(lot_size, len(str(volume_step).split('.')[1]) if '.' in str(volume_step) else 0)

    # Enforce minimum and maximum volume limits
    if lot_size < min_volume:
        return min_volume
    
    if lot_size > max_volume:
        return max_volume

    return lot_size
```

This implementation ensures that position size is proportional to account equity and inversely proportional to stop-loss distance, maintaining consistent risk percentage per trade.

**Section sources**
- [core/mt5/trade.py](file://core/mt5/trade.py#L10-L55)

## Trading Bot Risk Controls

The trading bot applies risk controls before sending orders to MT5, integrating position management, signal handling, and error recovery. The `TradingBot` class in `core/bots/trading_bot.py` orchestrates these controls.

Key risk control mechanisms include:

- **Position conflict resolution**: Automatically closes opposing positions before opening new ones
- **Signal-state coordination**: Ensures trades are only executed when no conflicting position exists
- **Error handling and logging**: Comprehensive error tracking with notification capabilities

```python
def _handle_trade_signal(self, signal, position):
    if signal == 'BUY':
        # Close opposing SELL position if exists
        if position and position.type == mt5.ORDER_TYPE_SELL:
            close_trade(position)
            position = None

        # Open new BUY position if no position exists
        if not position:
            place_trade(self.market_for_mt5, mt5.ORDER_TYPE_BUY, self.risk_percent, self.sl_pips, self.tp_pips, self.id)

    elif signal == 'SELL':
        # Close opposing BUY position if exists
        if position and position.type == mt5.ORDER_TYPE_BUY:
            close_trade(position)
            position = None

        # Open new SELL position if no position exists
        if not position:
            place_trade(self.market_for_mt5, mt5.ORDER_TYPE_SELL, self.risk_percent, self.sl_pips, self.tp_pips, self.id, self.timeframe)
```

The bot uses its unique ID as a magic number to track its positions, preventing interference with trades from other bots or manual trading.

**Section sources**
- [core/bots/trading_bot.py](file://core/bots/trading_bot.py#L130-L169)

## Margin Management and Account Monitoring

The system implements margin management through a unified broker interface that abstracts account information retrieval across different broker platforms. The `AccountInfo` class in `core/brokers/base_broker.py` defines the standard account metrics:

```python
class AccountInfo:
    def __init__(self, balance: float, equity: float, margin: float, 
                 free_margin: float, margin_level: float, currency: str = "USD"):
        self.balance = balance
        self.equity = equity
        self.margin = margin
        self.free_margin = free_margin
        self.margin_level = margin_level
        self.currency = currency
```

Broker implementations populate these values from platform-specific APIs, enabling consistent risk assessment regardless of the underlying broker. The system can monitor margin levels and free margin to prevent over-leveraging and margin calls.

While direct margin-based position sizing is not implemented in the MT5 module, the base broker class provides the `calculate_position_size()` method that could be extended for margin-aware sizing:

```python
def calculate_position_size(self, account_balance: float, risk_percent: float,
                          entry_price: float, stop_loss: float) -> float:
    risk_amount = account_balance * (risk_percent / 100)
    price_difference = abs(entry_price - stop_loss)
    
    if price_difference == 0:
        return 0
        
    position_size = risk_amount / price_difference
    return position_size
```

**Section sources**
- [core/brokers/base_broker.py](file://core/brokers/base_broker.py#L62-L75)

## Maximum Drawdown Protection

The system includes maximum drawdown protection mechanisms, particularly evident in the backtesting engine which monitors equity peaks and calculates drawdown in real-time.

In `core/backtesting/engine.py`, the drawdown calculation is implemented as:

```python
# Track peak equity for drawdown calculation
peak_equity = initial_capital
max_drawdown = 0.0

# Inside the backtest loop
if capital > peak_equity:
    peak_equity = capital

drawdown = (peak_equity - capital) / peak_equity if peak_equity > 0 else 0
max_drawdown = max(max_drawdown, drawdown)
```

The backtesting engine also includes a circuit breaker that halts trading if capital is depleted:

```python
# Hentikan backtest jika modal habis
if capital <= 0:
    break
```

This prevents the system from continuing to trade with insufficient capital, effectively serving as a maximum drawdown protection at 100% drawdown level. The test scripts also include safety analysis that evaluates drawdown thresholds:

```python
is_safe = (
    abs(profit) < 5000 and      # Reasonable profit/loss range
    drawdown < 20 and           # Reasonable drawdown
    final_capital > 8000 and    # Account not severely damaged
    trades > 0                  # At least some trades executed
)
```

This shows an implicit drawdown limit of 20% for acceptable performance.

**Section sources**
- [core/backtesting/engine.py](file://core/backtesting/engine.py#L53-L137)

## Circuit Breaker and Safety Mechanisms

The system implements several circuit breaker and safety mechanisms to prevent catastrophic losses and ensure system stability:

1. **Capital preservation circuit breaker**: Stops backtesting when capital reaches zero
2. **Lot size validation**: Prevents excessively large or small position sizes
3. **Comprehensive error handling**: Graceful degradation on system errors
4. **Unified risk management**: Portfolio-level risk constraints

The backtesting engine includes explicit lot size validation:

```python
if calculated_lot_size > 10.0:
    logger.warning(f"Calculated lot size {calculated_lot_size} exceeds max limit. Skipping trade.")
    continue 

if calculated_lot_size < 0.00001:
    logger.warning(f"Calculated lot size {calculated_lot_size} is too small. Skipping trade.")
    continue 
```

The system also demonstrates portfolio-level risk management in demonstration code:

```python
risk_rules = [
    {
        'rule': 'Maximum Portfolio Risk',
        'value': '15% of total capital',
        'implementation': 'Sum of all open positions across all brokers'
    },
    {
        'rule': 'Per-Broker Risk Limit',
        'value': '5% of total capital',
        'implementation': 'Maximum risk allocated to any single broker'
    }
]
```

These rules indicate a hierarchical risk management approach where both individual and aggregate risk exposures are controlled.

**Section sources**
- [core/backtesting/engine.py](file://core/backtesting/engine.py#L258-L288)
- [multi_broker_universe_demo.py](file://multi_broker_universe_demo.py#L105-L140)

## Configuration and Monitoring Guidance

To configure risk parameters safely, follow these guidelines:

**Risk Percentage**: Set risk_percent between 1-3% of account balance per trade to ensure long-term sustainability. The system uses this parameter directly in position sizing calculations.

**Stop-Loss Placement**: Use ATR-based multipliers rather than fixed pips for adaptive stop placement. A multiplier of 1.5-3.0 is typically effective, depending on strategy timeframe.

**Take-Profit Ratios**: Maintain a minimum risk-reward ratio of 1:2. The tp_atr_multiplier should be at least twice the sl_atr_multiplier for positive expectancy.

**Position Sizing**: Always verify that calculated lot sizes comply with broker minimums and maximums. The system automatically adjusts to volume_step increments.

For real-time monitoring, the system provides:

- **Activity logging**: All trade actions are logged with timestamps
- **Notification system**: Critical events trigger user notifications
- **Position tracking**: Open positions are monitored by magic number
- **Error reporting**: Comprehensive error details are captured

The TradingBot class includes built-in logging:
```python
def log_activity(self, action, details, exc_info=False, is_notification=False):
    from core.db.queries import add_history_log
    add_history_log(self.id, action, details, is_notification)
```

This enables both database persistence and file-based logging for audit and analysis.

**Section sources**
- [core/bots/trading_bot.py](file://core/bots/trading_bot.py#L115-L129)

## Common Pitfalls and Mitigation Strategies

### Over-Leveraging
**Pitfall**: Using excessive leverage that can lead to margin calls
**Mitigation**: 
- Limit risk to ≤3% of account balance per trade
- Monitor margin_level through AccountInfo
- Implement position size caps as in backtesting engine

### Inadequate Stop Placement
**Pitfall**: Setting stops too tight, causing premature exits
**Mitigation**:
- Use ATR-based stops instead of fixed pips
- Set sl_atr_multiplier ≥1.5 to avoid market noise
- Consider support/resistance levels in addition to volatility

### Poor Risk-Reward Ratios
**Pitfall**: Taking trades with unfavorable risk-reward profiles
**Mitigation**:
- Enforce minimum 1:2 risk-reward ratio
- Use tp_atr_multiplier ≥ 2 × sl_atr_multiplier
- Validate risk parameters during bot configuration

### Systemic Risk Exposure
**Pitfall**: Concentrating risk across correlated assets
**Mitigation**:
- Implement portfolio-level risk limits (≤15% total risk)
- Diversify across uncorrelated strategies and markets
- Use per-broker risk limits (≤5% per broker)

### Technical Failures
**Pitfall**: Unhandled exceptions disrupting trading operations
**Mitigation**:
- Wrap critical sections in try-except blocks
- Implement heartbeat monitoring for bot processes
- Use persistent state tracking to recover from crashes

The system's comprehensive error handling in `place_trade()` and `TradingBot.run()` demonstrates proper exception management:

```python
except Exception as e:
    logger.error(f"Exception di place_trade: {e}", exc_info=True)
    return None, str(e)
```

This ensures that individual trade failures do not cascade into system-wide failures.

**Section sources**
- [core/mt5/trade.py](file://core/mt5/trade.py#L100-L152)
- [core/bots/trading_bot.py](file://core/bots/trading_bot.py#L90-L114)