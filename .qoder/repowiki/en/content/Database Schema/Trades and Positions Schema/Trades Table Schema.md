# Trades Table Schema

<cite>
**Referenced Files in This Document**   
- [init_db.py](file://init_db.py#L49-L78)
- [core/db/queries.py](file://core/db/queries.py#L70-L102)
- [core/bots/trading_bot.py](file://core/bots/trading_bot.py#L142-L168)
- [core/mt5/trade.py](file://core/mt5/trade.py#L0-L152)
- [core/utils/mt5.py](file://core/utils/mt5.py#L0-L144)
</cite>

## Table of Contents
1. [Trades Table Schema](#trades-table-schema)
2. [Field Definitions](#field-definitions)
3. [Foreign Key Relationship](#foreign-key-relationship)
4. [Indexing Strategy](#indexing-strategy)
5. [Data Storage and Usage](#data-storage-and-usage)
6. [Sample Record](#sample-record)
7. [Common Queries](#common-queries)
8. [Data Retention and Archiving](#data-retention-and-archiving)

## Field Definitions

The trade history in the QuantumBotX system is stored in the `trade_history` table, which captures key trading events and actions performed by automated trading bots. The table structure is defined during database initialization and includes the following fields:

- **id**: Primary key, auto-incrementing integer that uniquely identifies each trade history record.
- **bot_id**: Foreign key referencing the `id` field in the `bots` table. This establishes a relationship between a trade and the bot that executed it.
- **timestamp**: DATETIME field with a default value of `CURRENT_TIMESTAMP`, recording when the trade action occurred.
- **action**: TEXT field that stores the type of trade action (e.g., "OPEN BUY", "CLOSE SELL", "START", "STOP"). This field is critical for categorizing trade lifecycle events.
- **details**: TEXT field containing a human-readable description of the action, such as "Membuka posisi BELI berdasarkan sinyal." This provides context for the trade action.
- **is_notification**: INTEGER flag (0 or 1) indicating whether the record should trigger a user notification.
- **is_read**: INTEGER flag (0 or 1) used to track whether a notification has been viewed by the user.

These fields collectively capture the essential metadata of each trade, enabling performance tracking, audit logging, and user notifications.

**Section sources**
- [init_db.py](file://init_db.py#L49-L78)
- [core/db/queries.py](file://core/db/queries.py#L70-L102)

## Foreign Key Relationship

The `trade_history` table maintains a foreign key relationship with the `bots` table through the `bot_id` field. This relationship ensures referential integrity and enables efficient querying of trade history by bot. When a bot is deleted, all associated trade history records are automatically removed due to the `ON DELETE CASCADE` constraint defined in the schema.

This relationship allows the system to:
- Retrieve all trade history for a specific bot
- Aggregate performance metrics per bot
- Display bot-specific activity logs in the user interface
- Maintain data consistency across related entities

The foreign key constraint is implemented as follows:
```sql
FOREIGN KEY (bot_id) REFERENCES bots (id) ON DELETE CASCADE
```

**Section sources**
- [init_db.py](file://init_db.py#L49-L78)

## Indexing Strategy

To optimize query performance, particularly for retrieving trade history by bot and time, the system relies on implicit indexing through the primary key and foreign key constraints. Although explicit indexes are not defined in the current schema, the following fields are naturally indexed:

- **id**: Primary key index ensures fast lookups by record ID.
- **bot_id**: Foreign key index enables efficient filtering of trade history by bot.
- **timestamp**: While not explicitly indexed, timestamp-based queries benefit from the table's insertion order and can be optimized if performance demands increase.

For large-scale deployments, adding a composite index on `(bot_id, timestamp)` would significantly improve the performance of queries that retrieve chronological trade history for a specific bot.

**Section sources**
- [init_db.py](file://init_db.py#L49-L78)

## Data Storage and Usage

The `trade_history` table serves as the primary storage for trade lifecycle events in the QuantumBotX system. It is used to:
- Record trade execution events (open, close)
- Log bot status changes (start, stop)
- Store error and warning messages
- Generate user notifications
- Support backtesting validation
- Enable performance analytics

Trade events are recorded through the `log_activity` method in the `TradingBot` class, which calls the `add_history_log` function in the database queries module. This ensures consistent logging across all bot instances.

The table supports historical trade data storage for backtesting and performance analysis. By preserving a complete record of trade actions, the system can reconstruct trading performance, calculate key metrics, and validate strategy effectiveness.

**Section sources**
- [core/bots/trading_bot.py](file://core/bots/trading_bot.py#L142-L168)
- [core/db/queries.py](file://core/db/queries.py#L70-L102)

## Sample Record

A sample record of a completed long trade is as follows:

```json
{
  "id": 1001,
  "bot_id": 123,
  "timestamp": "2023-11-15 14:30:22",
  "action": "OPEN BUY",
  "details": "Membuka posisi BELI berdasarkan sinyal.",
  "is_notification": 1,
  "is_read": 0
}
```

Followed by a closing record:

```json
{
  "id": 1002,
  "bot_id": 123,
  "timestamp": "2023-11-15 16:45:18",
  "action": "CLOSE BUY",
  "details": "Menutup posisi BELI karena mencapai TP.",
  "is_notification": 1,
  "is_read": 0
}
```

Profit is calculated externally based on entry and exit prices, volume, and currency pair specifics. For example, a trade opening at 1.1000 and closing at 1.1050 with a volume of 0.1 lots on EUR/USD would yield a profit of approximately $50.

**Section sources**
- [core/bots/trading_bot.py](file://core/bots/trading_bot.py#L142-L168)

## Common Queries

The following queries are commonly used to aggregate performance metrics from the trade history data:

**Win Rate Calculation**
```sql
SELECT 
    bot_id,
    COUNT(CASE WHEN action = 'CLOSE BUY' OR action = 'CLOSE SELL' THEN 1 END) as total_trades,
    COUNT(CASE WHEN action IN ('CLOSE BUY', 'CLOSE SELL') AND details LIKE '%profit%' THEN 1 END) as winning_trades,
    (COUNT(CASE WHEN action IN ('CLOSE BUY', 'CLOSE SELL') AND details LIKE '%profit%' THEN 1 END) * 100.0 / 
     COUNT(CASE WHEN action = 'CLOSE BUY' OR action = 'CLOSE SELL' THEN 1 END)) as win_rate
FROM trade_history 
WHERE bot_id = ? 
GROUP BY bot_id;
```

**Average Holding Time**
```sql
SELECT 
    bot_id,
    AVG(julianday(close_time) - julianday(open_time)) as avg_holding_days
FROM (
    SELECT 
        th1.bot_id,
        th1.timestamp as open_time,
        MIN(th2.timestamp) as close_time
    FROM trade_history th1
    JOIN trade_history th2 ON th1.bot_id = th2.bot_id
    WHERE th1.action = 'OPEN BUY' 
      AND th2.action = 'CLOSE BUY' 
      AND th2.timestamp > th1.timestamp
    GROUP BY th1.id, th1.bot_id, th1.timestamp
) 
GROUP BY bot_id;
```

**Total PnL per Bot**
```sql
SELECT 
    bot_id,
    SUM(profit_amount) as total_pnl
FROM trade_history 
WHERE action IN ('CLOSE BUY', 'CLOSE SELL')
  AND details LIKE '%profit%'
GROUP BY bot_id;
```

These queries enable comprehensive performance analytics and are used to generate reports and dashboards for users.

**Section sources**
- [core/db/queries.py](file://core/db/queries.py#L70-L102)

## Data Retention and Archiving

For large-scale deployments, data retention and archiving considerations are critical to maintain system performance and manage storage costs. The current schema does not include automatic data retention policies, but the following strategies are recommended:

- **Time-based Archiving**: Move trade history records older than a specified period (e.g., 1 year) to an archive table or cold storage.
- **Partitioning**: Implement table partitioning by time (e.g., monthly partitions) to improve query performance and simplify data management.
- **Purging**: Regularly purge old records that are no longer needed for compliance or analysis.
- **Backup Strategy**: Implement regular backups of the trade history data to prevent data loss.

The `is_read` field can be leveraged to identify and archive older notifications that have been viewed by users, reducing the active dataset size.

**Section sources**
- [init_db.py](file://init_db.py#L49-L78)
- [core/db/queries.py](file://core/db/queries.py#L70-L102)