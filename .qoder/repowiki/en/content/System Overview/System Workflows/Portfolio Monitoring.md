# Portfolio Monitoring

<cite>
**Referenced Files in This Document**   
- [api_portfolio.py](file://core/routes/api_portfolio.py)
- [mt5.py](file://core/utils/mt5.py)
- [trade.py](file://core/mt5/trade.py)
- [models.py](file://core/db/models.py)
- [queries.py](file://core/db/queries.py)
- [api_notifications.py](file://core/routes/api_notifications.py)
- [portfolio.js](file://static/js/portfolio.js)
</cite>

## Table of Contents
1. [Introduction](#introduction)
2. [Core Data Flow Overview](#core-data-flow-overview)
3. [API and MT5 Integration](#api-and-mt5-integration)
4. [Frontend Polling Mechanism](#frontend-polling-mechanism)
5. [Asset Allocation Logic](#asset-allocation-logic)
6. [Database Persistence and Historical Tracking](#database-persistence-and-historical-tracking)
7. [Notification System Integration](#notification-system-integration)
8. [Error Handling and Resilience](#error-handling-and-resilience)
9. [Performance Considerations](#performance-considerations)
10. [Security Aspects](#security-aspects)
11. [Common Issues and Solutions](#common-issues-and-solutions)

## Introduction
The Portfolio Monitoring system in quantumbotx enables real-time tracking of open trading positions, profit and loss (P&L), equity trends, and asset allocation. It integrates with MetaTrader 5 (MT5) to fetch live account data, transforms it into a frontend-consumable format, and updates the user interface periodically. This document details the architecture, data flow, integration points, and operational characteristics of the portfolio monitoring workflow.

## Core Data Flow Overview
The portfolio monitoring workflow follows a client-server model where the frontend polls the backend API, which in turn retrieves live trading data from MT5. The data is processed, formatted, and returned to the frontend for visualization. Key components include:
- **Frontend (JavaScript)**: Polls `/api/portfolio/open-positions` and `/api/portfolio/allocation` endpoints every 5 seconds.
- **Backend API (Flask)**: Serves portfolio data via `api_portfolio.py`.
- **MT5 Integration Layer**: Uses `utils.mt5` module to interface with the MT5 terminal.
- **Database**: Logs trade actions and notifications via `models.py` and `queries.py`.

```mermaid
flowchart TD
A[Frontend] --> |Polls /api/portfolio/open-positions| B[api_portfolio.py]
B --> C[get_open_positions_mt5()]
C --> D[MT5 Terminal]
D --> C
C --> B
B --> A
E[Frontend] --> |Polls /api/portfolio/allocation| F[api_portfolio.py]
F --> C
C --> F
F --> E
```

**Diagram sources**
- [api_portfolio.py](file://core/routes/api_portfolio.py)
- [mt5.py](file://core/utils/mt5.py)
- [portfolio.js](file://static/js/portfolio.js)

**Section sources**
- [api_portfolio.py](file://core/routes/api_portfolio.py)
- [mt5.py](file://core/utils/mt5.py)
- [portfolio.js](file://static/js/portfolio.js)

## API and MT5 Integration
The `api_portfolio.py` file defines two main endpoints: `/open-positions` and `/allocation`. Both rely on `get_open_positions_mt5()` from `utils.mt5` to retrieve real-time position data from MT5.

### Key Functions
- **`get_open_positions_mt5()`**: Fetches all open positions from MT5 using `mt5.positions_get()` and converts them into a list of dictionaries.
- **`get_account_info_mt5()`**: Retrieves account-level data such as balance, equity, and margin (though not directly used in current portfolio endpoints).

```python
# core/routes/api_portfolio.py
@api_portfolio.route('/open-positions')
def api_open_positions():
    try:
        positions = get_open_positions_mt5()
        return jsonify(positions)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
```

This integration ensures that the frontend receives up-to-date position data on each poll.

**Section sources**
- [api_portfolio.py](file://core/routes/api_portfolio.py#L10-L18)
- [mt5.py](file://core/utils/mt5.py#L60-L70)

## Frontend Polling Mechanism
The `portfolio.js` script initializes the page by fetching portfolio data and setting up a 5-second polling interval to keep the UI synchronized with MT5.

### Polling Logic
- **Initial Load**: Calls `updatePortfolioData()` and `updateAssetAllocationChart()` once on page load.
- **Periodic Updates**: Uses `setInterval()` to refresh both endpoints every 5000ms.
- **Chart Updates**: Maintains a rolling 60-point P&L chart using Chart.js.

```javascript
// static/js/portfolio.js
setInterval(async () => {
    await updatePortfolioData();
    await updateAssetAllocationChart();
}, 5000);
```

The P&L chart displays real-time cumulative profit from open positions, while the asset allocation chart shows distribution across asset classes.

**Section sources**
- [portfolio.js](file://static/js/portfolio.js#L130-L150)

## Asset Allocation Logic
The `/allocation` endpoint categorizes open positions by symbol patterns to compute asset allocation for visualization.

### Classification Rules
- **Forex**: Symbols containing "USD" but not "XAU" or "BTC"
- **Emas (Gold)**: Symbols containing "XAU"
- **Saham (Stocks)**: Symbols matching AAPL, GOOGL, TSLA, ND100, SP500
- **Crypto**: Symbols containing "BTC" or "ETH"
- **Others**: All remaining symbols

```python
# core/routes/api_portfolio.py
if 'USD' in symbol and 'XAU' not in symbol and 'BTC' not in symbol:
    allocation_summary["Forex"] += volume
elif 'XAU' in symbol:
    allocation_summary["Emas"] += volume
```

The result is formatted as `{labels: [...], values: [...]}` for direct use in Chart.js doughnut charts.

**Section sources**
- [api_portfolio.py](file://core/routes/api_portfolio.py#L25-L50)

## Database Persistence and Historical Tracking
While real-time data comes from MT5, historical tracking and notifications are persisted in a local SQLite database (`bots.db`).

### Key Tables
- **`trade_history`**: Logs all trade actions (e.g., position opened/closed).
- **`notifications`**: Stores user-facing alerts, often derived from trade events.

The `log_trade_action()` function in `models.py` inserts records into `trade_history`, and if the action is a position event, it also creates a notification.

```python
# core/db/models.py
def log_trade_action(bot_id, action, details):
    cursor.execute('INSERT INTO trade_history ...')
    if action.startswith("POSISI") or ...:
        cursor.execute('INSERT INTO notifications ...')
```

This ensures that significant trading events are recorded and visible in the notifications panel.

**Section sources**
- [models.py](file://core/db/models.py#L3-L15)
- [queries.py](file://core/db/queries.py#L50-L60)

## Notification System Integration
The notification system is tightly coupled with portfolio and trading events. When a position is opened or closed, a notification is generated and stored in the database.

### API Endpoints
- **`/api/notifications`**: Returns all notifications, marking them as read.
- **`/api/notifications/unread-count`**: Provides unread count for UI badges.
- **`/api/notifications/unread`**: Returns unread notifications for toast messages.

```python
# core/routes/api_notifications.py
@api_notifications.route('/api/notifications/unread-count')
def get_unread_notifications_count_route():
    count = queries.get_unread_notifications_count()
    return jsonify(count)
```

These endpoints allow the frontend to display real-time alerts based on trading activity.

**Section sources**
- [api_notifications.py](file://core/routes/api_notifications.py#L10-L50)
- [queries.py](file://core/db/queries.py#L100-L130)

## Error Handling and Resilience
The system includes robust error handling at multiple levels to maintain stability during MT5 disconnections or API failures.

### Backend Error Handling
- **MT5 Disconnection**: If `mt5.positions_get()` returns `None`, `get_open_positions_mt5()` returns an empty list.
- **Exception Handling**: All API endpoints wrap logic in `try-except` blocks and return HTTP 500 with error messages.

```python
# core/utils/mt5.py
except Exception as e:
    logger.error(f"Error saat get_open_positions_mt5: {e}", exc_info=True)
    return []
```

### Frontend Resilience
- **Error Display**: If fetch fails, the table shows an error message.
- **Graceful Degradation**: Charts and tables retain last known data during outages.

**Section sources**
- [mt5.py](file://core/utils/mt5.py#L65-L70)
- [api_portfolio.py](file://core/routes/api_portfolio.py#L15-L18)
- [portfolio.js](file://static/js/portfolio.js#L100-L110)

## Performance Considerations
The current polling mechanism (5-second interval) balances responsiveness with system load.

### Optimization Opportunities
- **Reduce Polling Frequency**: For less volatile portfolios, increase interval to 10s.
- **Batch Requests**: Combine `/open-positions` and `/allocation` into a single endpoint.
- **WebSocket Fallback**: Implement real-time push from server if MT5 supports event-driven updates.

Currently, no P&L history is stored server-side; the frontend maintains the chart data in memory.

**Section sources**
- [portfolio.js](file://static/js/portfolio.js#L130-L150)

## Security Aspects
Exposing account-level data via APIs requires careful security consideration.

### Current Measures
- **No Authentication Shown**: The code does not include auth checks on `/api/portfolio/*` endpoints.
- **Data Minimization**: Only necessary position fields are exposed.
- **Error Sanitization**: Internal exceptions are logged but not exposed in detail.

### Recommendations
- **Implement Authentication**: Require JWT or session validation for portfolio endpoints.
- **Role-Based Access**: Restrict access based on user permissions.
- **Rate Limiting**: Prevent abuse of polling endpoints.

**Section sources**
- [api_portfolio.py](file://core/routes/api_portfolio.py)

## Common Issues and Solutions
### 1. **Stale Data**
- **Cause**: 5-second polling delay.
- **Solution**: Reduce interval or implement WebSocket-based updates.

### 2. **MT5 Rate Limiting**
- **Cause**: Excessive polling may trigger MT5 rate limits.
- **Solution**: Cache MT5 responses server-side for 1-2 seconds.

### 3. **Currency Conversion Inaccuracies**
- **Cause**: Profit values are in account currency; no multi-currency support.
- **Solution**: Integrate real-time FX rates for USD conversion display.

### 4. **Chart Performance**
- **Cause**: Large number of data points in P&L chart.
- **Solution**: Limit to last 60 points (already implemented).

### 5. **Connection Loss to MT5**
- **Cause**: MT5 terminal closed or network issue.
- **Solution**: Implement auto-reconnect logic in `initialize_mt5()` and retry mechanism.

```python
# core/utils/mt5.py
def initialize_mt5(account, password, server):
    if not mt5.initialize(...):
        logger.error("MT5 initialization failed")
        return False
```

**Section sources**
- [mt5.py](file://core/utils/mt5.py#L40-L50)
- [portfolio.js](file://static/js/portfolio.js#L100-L110)