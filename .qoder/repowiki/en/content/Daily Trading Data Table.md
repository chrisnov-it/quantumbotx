# Daily Trading Data Table

<cite>
**Referenced Files in This Document**   
- [init_db.py](file://init_db.py#L150-L180)
- [core/db/models.py](file://core/db/models.py#L62-L92)
- [core/db/models.py](file://core/db/models.py#L94-L176)
- [core/routes/ai_mentor.py](file://core/routes/ai_mentor.py#L262-L289)
</cite>

## Table of Contents
1. [Introduction](#introduction)
2. [Table Purpose and Role](#table-purpose-and-role)
3. [Field Descriptions](#field-descriptions)
4. [Data Logging Process](#data-logging-process)
5. [Data Retrieval Process](#data-retrieval-process)
6. [Usage Example](#usage-example)
7. [Integration with AI Analysis](#integration-with-ai-analysis)

## Introduction
The `daily_trading_data` table is a core component of the QuantumBotX system, designed to capture granular trade execution details for daily performance tracking and artificial intelligence (AI)-driven behavioral and strategic analysis. This documentation provides a comprehensive overview of the table's structure, functionality, and integration within the broader trading ecosystem.

## Table Purpose and Role
The `daily_trading_data` table serves as a persistent record of individual trades executed by trading bots within the QuantumBotX platform. Its primary purpose is to provide structured, time-series data that supports post-trade analysis, performance evaluation, and AI mentorship features. Each trade is logged with contextual metadata such as symbol, lot size, risk parameters, and strategy used, enabling detailed retrospective analysis.

This table plays a critical role in feeding data to the AI Mentor system, which uses the aggregated trade history to generate personalized feedback, emotional pattern recognition, and strategic recommendations for traders. By linking trades to specific trading sessions via the `session_id`, the system maintains a coherent daily narrative of trading activity.

**Section sources**
- [init_db.py](file://init_db.py#L150-L180)
- [core/db/models.py](file://core/db/models.py#L62-L92)

## Field Descriptions
The following fields define the structure of the `daily_trading_data` table:

- **id**: Unique identifier for each trade record (Primary Key, Auto-increment)
- **session_id**: Foreign key linking the trade to a specific trading session in the `trading_sessions` table
- **bot_id**: Identifier of the trading bot that executed the trade
- **symbol**: Financial instrument traded (e.g., EURUSD, BTCUSD)
- **entry_time**: Timestamp of trade entry (DATETIME)
- **exit_time**: Timestamp of trade exit (DATETIME)
- **profit_loss**: Net profit or loss from the trade in USD or base currency
- **lot_size**: Trade volume in standard lots
- **stop_loss_used**: Boolean flag indicating whether the stop loss was triggered (0 = False, 1 = True)
- **take_profit_used**: Boolean flag indicating whether the take profit was triggered (0 = False, 1 = True)
- **risk_percent**: Percentage of account risk associated with the trade
- **strategy_used**: Name of the trading strategy employed (e.g., Bollinger Squeeze, MA Crossover)
- **created_at**: Timestamp of when the record was created (defaults to current time)

These fields collectively capture both quantitative performance metrics and qualitative decision-making context, enabling multidimensional analysis.

**Section sources**
- [init_db.py](file://init_db.py#L150-L180)

## Data Logging Process
Trade data is logged into the `daily_trading_data` table through the `log_trade_for_ai_analysis()` function defined in `models.py`. This function is called after a trade is closed, ensuring that complete trade outcomes are recorded.

The process begins by retrieving or creating a daily trading session using `get_or_create_today_session()`, which ensures all trades are grouped by calendar date. Once the session ID is obtained, the trade details are inserted into the table via a parameterized SQL INSERT statement.

Concurrently, the parent `trading_sessions` record is updated to reflect the new trade count and cumulative profit/loss, maintaining real-time session-level summaries.

``mermaid
sequenceDiagram
participant Bot as Trading Bot
participant Logger as log_trade_for_ai_analysis
participant DB as Database
Bot->>Logger : Execute trade completion
Logger->>Logger : Get or create today's session
Logger->>DB : INSERT INTO daily_trading_data (...)
DB-->>Logger : Success
Logger->>DB : UPDATE trading_sessions SET total_trades++, total_profit_loss += profit
DB-->>Logger : Success
Logger-->>Bot : Confirmation
```

**Diagram sources**
- [core/db/models.py](file://core/db/models.py#L62-L92)

**Section sources**
- [core/db/models.py](file://core/db/models.py#L62-L92)

## Data Retrieval Process
Data is retrieved from the `daily_trading_data` table using the `get_trading_session_data()` function, which fetches all trades associated with a specific session date. The function first validates the existence of the `daily_trading_data` table and then executes a SELECT query to retrieve trade records.

Each retrieved trade is formatted into a dictionary with standardized keys, including type conversion for boolean fields (`stop_loss_used`, `take_profit_used`) and default values for missing data (e.g., `risk_percent` defaults to 1.0 if null).

The result is a structured JSON-like object containing session metadata and an array of individual trade records, suitable for rendering in dashboards or processing by AI algorithms.

``mermaid
flowchart TD
Start([Retrieve Session Data]) --> CheckTable["Check if daily_trading_data table exists"]
CheckTable --> TableExists{"Table Exists?"}
TableExists --> |No| ReturnNoTrades["Return empty trades array"]
TableExists --> |Yes| QueryTrades["Query trades by session_id"]
QueryTrades --> FormatData["Format trade records"]
FormatData --> ApplyDefaults["Apply default values if null"]
ApplyDefaults --> ReturnData["Return structured session data"]
ReturnNoTrades --> ReturnData
ReturnData --> End([Function Exit])
```

**Diagram sources**
- [core/db/models.py](file://core/db/models.py#L94-L176)

**Section sources**
- [core/db/models.py](file://core/db/models.py#L94-L176)

## Usage Example
The following example demonstrates how a completed trade is logged and later retrieved:

```python
# Logging a completed trade
log_trade_for_ai_analysis(
    bot_id=101,
    symbol="EURUSD",
    profit_loss=45.70,
    lot_size=0.1,
    stop_loss_used=False,
    take_profit_used=True,
    risk_percent=1.5,
    strategy_used="Bollinger Squeeze"
)

# Retrieving today's trading data
from datetime import date
session_data = get_trading_session_data(date.today())

print(f"Total trades today: {session_data['total_trades']}")
print(f"Net P/L: ${session_data['total_profit_loss']:.2f}")

for trade in session_data['trades']:
    print(f"Symbol: {trade['symbol']}, "
          f"Profit: ${trade['profit']}, "
          f"Strategy: {trade['strategy']}, "
          f"TP Triggered: {trade['take_profit_used']}")
```

This would result in one record being inserted into `daily_trading_data` and the session summary being updated accordingly.

**Section sources**
- [core/db/models.py](file://core/db/models.py#L62-L92)
- [core/db/models.py](file://core/db/models.py#L94-L176)

## Integration with AI Analysis
The `daily_trading_data` table is foundational to the AI Mentor system, providing the raw data needed for behavioral and performance analysis. The AI processes trade patterns, risk behavior, and emotional context (from session metadata) to generate personalized feedback.

For example, if multiple trades show frequent stop loss usage without take profit execution, the AI may detect overtrading or poor entry timing and suggest strategy adjustments. Similarly, consistent profitability with low-risk percent may indicate underutilization of capital.

The integration is demonstrated in the AI mentor route, where daily summaries are generated based on the presence and outcome of trades:

```python
if summary['today_has_data']:
    if summary['today_profit_loss'] > 0:
        trading_analysis = "Positive performance today! 📈"
    elif summary['today_profit_loss'] < 0:
        trading_analysis = "Strategy evaluation needed 🔍"
```

This tight coupling between data logging and AI interpretation enables continuous learning and improvement for traders using the platform.

**Section sources**
- [core/routes/ai_mentor.py](file://core/routes/ai_mentor.py#L262-L289)
- [core/db/models.py](file://core/db/models.py#L62-L92)