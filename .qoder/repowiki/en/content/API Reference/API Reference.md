# API Reference

<cite>
**Referenced Files in This Document**   
- [api_bots.py](file://core/routes/api_bots.py)
- [api_backtest.py](file://core/routes/api_backtest.py)
- [api_portfolio.py](file://core/routes/api_portfolio.py)
- [api_dashboard.py](file://core/routes/api_dashboard.py)
- [api_profile.py](file://core/routes/api_profile.py)
- [api_forex.py](file://core/routes/api_forex.py)
- [api_stocks.py](file://core/routes/api_stocks.py)
- [api_notifications.py](file://core/routes/api_notifications.py)
- [api_history.py](file://core/routes/api_history.py)
- [api_chart.py](file://core/routes/api_chart.py)
- [api_fundamentals.py](file://core/routes/api_fundamentals.py)
- [api_bots_fundamentals.py](file://core/routes/api_bots_fundamentals.py)
- [api_indicators.py](file://core/routes/api_indicators.py)
- [api_holiday.py](file://core/routes/api_holiday.py) - *Added in recent commit for holiday detection*
- [api_ramadan.py](file://core/routes/api_ramadan.py) - *Added in recent commit for Ramadan-specific features*
</cite>

## Update Summary
**Changes Made**   
- Added new section for Holiday API with endpoints for holiday detection and status
- Added new section for Ramadan API with endpoints for Ramadan-specific features and conditional visibility
- Updated Table of Contents to include new API sections
- Enhanced source tracking with new files introduced in recent commits

## Table of Contents
1. [Introduction](#introduction)
2. [Authentication](#authentication)
3. [API Versioning and Rate Limiting](#api-versioning-and-rate-limiting)
4. [Bots API](#bots-api)
5. [Backtesting API](#backtesting-api)
6. [Portfolio API](#portfolio-api)
7. [Dashboard API](#dashboard-api)
8. [Profile API](#profile-api)
9. [Forex API](#forex-api)
10. [Stocks API](#stocks-api)
11. [Notifications API](#notifications-api)
12. [History API](#history-api)
13. [Chart API](#chart-api)
14. [Fundamentals API](#fundamentals-api)
15. [Indicators API](#indicators-api)
16. [Holiday API](#holiday-api)
17. [Ramadan API](#ramadan-api)
18. [Error Response Format](#error-response-format)

## Introduction
The QuantumBotX application provides a comprehensive RESTful API for managing automated trading bots, backtesting strategies, portfolio monitoring, and market data analysis. This documentation details all available API endpoints grouped by functionality, including request/response formats, parameters, authentication requirements, and usage examples. The API is built using Flask and interacts with MetaTrader5 for market data and trade execution.

## Authentication
The API uses session-based authentication. Users must authenticate through the web interface, after which subsequent API requests are authenticated via session cookies. No API keys or tokens are required for endpoints.

**Authentication Mechanism**:
- User credentials are stored in a local SQLite database (`bots.db`)
- Passwords are hashed using `werkzeug.security.generate_password_hash`
- Session management is handled by Flask's built-in session system
- All API endpoints require an authenticated session

**Profile Endpoint**:
The `/api/profile` endpoint supports retrieving and updating user profile information, including name and password.

``mermaid
sequenceDiagram
participant Client
participant Server
participant Database
Client->>Server : GET /api/profile
Server->>Database : Query user data (id=1)
Database-->>Server : Return user data
Server-->>Client : 200 OK + user data
Client->>Server : PUT /api/profile
Server->>Server : Hash password if provided
Server->>Database : Update user record
Database-->>Server : Confirmation
Server-->>Client : 200 OK + success message
```

**Section sources**
- [api_profile.py](file://core/routes/api_profile.py#L1-L40)

## API Versioning and Rate Limiting
The QuantumBotX API does not implement explicit versioning in the URL paths. All endpoints are served from their base paths without version prefixes (e.g., `/api/` rather than `/api/v1/`).

**API Versioning Strategy**:
- No URL-based versioning
- Backward compatibility is maintained through careful endpoint design
- Changes to existing endpoints are minimized
- New functionality is added through new endpoints rather than modifying existing ones

**Rate Limiting**:
The codebase does not implement explicit rate limiting policies. There are no rate limit headers in responses, and no mechanisms to restrict the number of requests per time period. This means clients can make requests without being throttled by the server.

**Section sources**
- [api_bots.py](file://core/routes/api_bots.py)
- [api_backtest.py](file://core/routes/api_backtest.py)

## Bots API
The Bots API provides comprehensive management of trading bots, including creation, configuration, starting/stopping, and monitoring.

### Available Endpoints

#### **GET /api/strategies**
Retrieves a list of all available trading strategies.

**Parameters**: None

**Response Schema**:
```json
[
  {
    "id": "string",
    "name": "string",
    "description": "string"
  }
]
```

**Status Codes**:
- 200: Successful retrieval
- 500: Internal server error

**Example Response**:
```json
[
  {
    "id": "ma_crossover",
    "name": "MA Crossover",
    "description": "Simple moving average crossover strategy"
  },
  {
    "id": "rsi_crossover",
    "name": "RSI Crossover",
    "description": "Relative Strength Index crossover strategy"
  }
]
```

**Section sources**
- [api_bots.py](file://core/routes/api_bots.py#L7-L20)

#### **GET /api/strategies/{strategy_id}/params**
Retrieves configurable parameters for a specific strategy.

**Path Parameters**:
- `strategy_id`: The identifier of the strategy

**Response Schema**:
```json
[
  {
    "name": "string",
    "type": "string",
    "default": "any",
    "description": "string"
  }
]
```

**Status Codes**:
- 200: Strategy found and parameters returned
- 404: Strategy not found
- 500: Internal server error

**Example Response**:
```json
[
  {
    "name": "ma_short_period",
    "type": "integer",
    "default": 10,
    "description": "Short period for moving average"
  },
  {
    "name": "ma_long_period",
    "type": "integer",
    "default": 30,
    "description": "Long period for moving average"
  }
]
```

**Section sources**
- [api_bots.py](file://core/routes/api_bots.py#L22-L37)

#### **GET /api/bots**
Retrieves all configured trading bots.

**Query Parameters**: None

**Response Schema**:
```json
[
  {
    "id": "integer",
    "name": "string",
    "market": "string",
    "lot_size": "number",
    "sl_pips": "number",
    "tp_pips": "number",
    "timeframe": "string",
    "interval": "integer",
    "strategy": "string",
    "strategy_name": "string",
    "status": "string",
    "strategy_params": "object"
  }
]
```

**Status Codes**:
- 200: Successful retrieval

**Example Response**:
```json
[
  {
    "id": 1,
    "name": "EURUSD Scalper",
    "market": "EURUSD",
    "lot_size": 0.1,
    "sl_pips": 15,
    "tp_pips": 30,
    "timeframe": "M15",
    "interval": 60,
    "strategy": "ma_crossover",
    "strategy_name": "MA Crossover",
    "status": "Aktif"
  }
]
```

**Section sources**
- [api_bots.py](file://core/routes/api_bots.py#L39-L57)

#### **GET /api/bots/{bot_id}**
Retrieves detailed information about a specific bot.

**Path Parameters**:
- `bot_id`: The ID of the bot to retrieve

**Response Schema**:
Same as GET /api/bots but for a single bot object.

**Status Codes**:
- 200: Bot found and returned
- 404: Bot not found

**Example Response**:
```json
{
  "id": 1,
  "name": "EURUSD Scalper",
  "market": "EURUSD",
  "lot_size": 0.1,
  "sl_pips": 15,
  "tp_pips": 30,
  "timeframe": "M15",
  "interval": 60,
  "strategy": "ma_crossover",
  "strategy_name": "MA Crossover",
  "status": "Aktif",
  "strategy_params": {
    "ma_short_period": 10,
    "ma_long_period": 30
  }
}
```

**Section sources**
- [api_bots.py](file://core/routes/api_bots.py#L59-L72)

#### **POST /api/bots**
Creates a new trading bot.

**Request Body**:
```json
{
  "name": "string",
  "market": "string",
  "risk_percent": "number",
  "sl_atr_multiplier": "number",
  "tp_atr_multiplier": "number",
  "timeframe": "string",
  "check_interval_seconds": "integer",
  "strategy": "string",
  "params": "object"
}
```

**Response Schema**:
```json
{
  "message": "string",
  "bot_id": "integer"
}
```

**Status Codes**:
- 201: Bot created successfully
- 500: Failed to save bot

**Example Request**:
```json
{
  "name": "New Bot",
  "market": "EURUSD",
  "risk_percent": 1.5,
  "sl_atr_multiplier": 2.0,
  "tp_atr_multiplier": 3.0,
  "timeframe": "H1",
  "check_interval_seconds": 300,
  "strategy": "rsi_crossover",
  "params": {
    "rsi_period": 14,
    "overbought_level": 70,
    "oversold_level": 30
  }
}
```

**Sample curl command**:
```bash
curl -X POST http://localhost:5000/api/bots \
  -H "Content-Type: application/json" \
  -d '{
    "name": "New Bot",
    "market": "EURUSD",
    "risk_percent": 1.5,
    "sl_atr_multiplier": 2.0,
    "tp_atr_multiplier": 3.0,
    "timeframe": "H1",
    "check_interval_seconds": 300,
    "strategy": "rsi_crossover",
    "params": {
      "rsi_period": 14,
      "overbought_level": 70,
      "oversold_level": 30
    }
  }'
```

**Section sources**
- [api_bots.py](file://core/routes/api_bots.py#L74-L97)

#### **PUT /api/bots/{bot_id}**
Updates the configuration of an existing bot.

**Path Parameters**:
- `bot_id`: The ID of the bot to update

**Request Body**:
Same structure as POST /api/bots

**Response Schema**:
```json
{
  "message": "string"
}
```

**Status Codes**:
- 200: Bot updated successfully
- 500: Failed to update bot

**Validation Rules**:
- `name` is required
- `risk_percent`, `sl_atr_multiplier`, `tp_atr_multiplier` must be numbers
- `check_interval_seconds` must be an integer
- `timeframe` must be a valid timeframe (M1, M5, M15, M30, H1, H4, D1)

**Section sources**
- [api_bots.py](file://core/routes/api_bots.py#L99-L126)

#### **DELETE /api/bots/{bot_id}**
Deletes a trading bot.

**Path Parameters**:
- `bot_id`: The ID of the bot to delete

**Response Schema**:
```json
{
  "message": "string"
}
```

**Status Codes**:
- 200: Bot deleted successfully
- 500: Failed to delete bot

**Section sources**
- [api_bots.py](file://core/routes/api_bots.py#L128-L137)

#### **POST /api/bots/{bot_id}/start**
Starts a stopped bot.

**Path Parameters**:
- `bot_id`: The ID of the bot to start

**Response Schema**:
```json
{
  "message": "string"
}
```

**Status Codes**:
- 200: Bot started successfully
- 500: Failed to start bot

**Section sources**
- [api_bots.py](file://core/routes/api_bots.py#L139-L146)

#### **POST /api/bots/{bot_id}/stop**
Stops a running bot.

**Path Parameters**:
- `bot_id`: The ID of the bot to stop

**Response Schema**:
```json
{
  "message": "string"
}
```

**Status Codes**:
- 200: Bot stopped successfully
- 500: Failed to stop bot

**Section sources**
- [api_bots.py](file://core/routes/api_bots.py#L148-L155)

#### **POST /api/bots/start_all**
Starts all stopped bots.

**Response Schema**:
```json
{
  "message": "string"
}
```

**Status Codes**:
- 200: All bots started successfully
- 400: Failed to start all bots

**Section sources**
- [api_bots.py](file://core/routes/api_bots.py#L157-L164)

#### **POST /api/bots/stop_all**
Stops all running bots.

**Response Schema**:
```json
{
  "message": "string"
}
```

**Status Codes**:
- 200: All bots stopped successfully
- 400: Failed to stop all bots

**Section sources**
- [api_bots.py](file://core/routes/api_bots.py#L166-L173)

#### **GET /api/bots/{bot_id}/analysis**
Retrieves the latest analysis data for a bot.

**Path Parameters**:
- `bot_id`: The ID of the bot

**Response Schema**:
```json
{
  "signal": "string",
  "confidence": "number",
  "price": "number",
  "timestamp": "string"
}
```

**Status Codes**:
- 200: Analysis data returned
- 404: Bot not found

**Section sources**
- [api_bots.py](file://core/routes/api_bots.py#L175-L182)

#### **GET /api/bots/{bot_id}/history**
Retrieves the activity history for a bot.

**Path Parameters**:
- `bot_id`: The ID of the bot

**Response Schema**:
```json
[
  {
    "id": "integer",
    "bot_id": "integer",
    "message": "string",
    "timestamp": "string",
    "type": "string"
  }
]
```

**Status Codes**:
- 200: History returned successfully

**Section sources**
- [api_bots.py](file://core/routes/api_bots.py#L184-L191)

#### **GET /api/rsi_data**
Retrieves RSI data for charting.

**Query Parameters**:
- `symbol`: Trading symbol (default: EURUSD)
- `timeframe`: Chart timeframe (default: H1)

**Response Schema**:
```json
{
  "timestamps": ["string"],
  "rsi_values": ["number"]
}
```

**Status Codes**:
- 200: Data returned successfully
- 404: Unable to fetch data for symbol

**Section sources**
- [api_bots.py](file://core/routes/api_bots.py#L193-L217)

## Backtesting API
The Backtesting API enables users to test trading strategies against historical data.

### Available Endpoints

#### **POST /api/backtest/run**
Runs a backtest on historical data.

**Request Format**: multipart/form-data

**Form Parameters**:
- `file`: CSV file containing historical price data
- `strategy`: Strategy ID to test
- `params`: JSON string of strategy parameters

**CSV File Requirements**:
- Must contain a 'time' column (parsed as datetime)
- Must contain 'open', 'high', 'low', 'close', 'volume' columns

**Response Schema**:
```json
{
  "strategy_name": "string",
  "total_profit_usd": "number",
  "total_trades": "integer",
  "win_rate_percent": "number",
  "max_drawdown_percent": "number",
  "wins": "integer",
  "losses": "integer",
  "equity_curve": ["number"],
  "trades": [
    {
      "entry_time": "string",
      "exit_time": "string",
      "symbol": "string",
      "volume": "number",
      "entry_price": "number",
      "exit_price": "number",
      "profit_usd": "number",
      "profit_pips": "number"
    }
  ]
}
```

**Status Codes**:
- 200: Backtest completed successfully
- 400: Missing file or invalid parameters
- 500: Error during backtesting

**Sample curl command**:
```bash
curl -X POST http://localhost:5000/api/backtest/run \
  -F "file=@EURUSD_H1_data.csv" \
  -F "strategy=ma_crossover" \
  -F "params={\"ma_short_period\": 10, \"ma_long_period\": 30}"
```

**Section sources**
- [api_backtest.py](file://core/routes/api_backtest.py#L29-L85)

#### **GET /api/backtest/history**
Retrieves the history of completed backtests.

**Response Schema**:
```json
[
  {
    "id": "integer",
    "strategy_name": "string",
    "data_filename": "string",
    "total_profit_usd": "number",
    "total_trades": "integer",
    "win_rate_percent": "number",
    "max_drawdown_percent": "number",
    "wins": "integer",
    "losses": "integer",
    "equity_curve": ["number"],
    "trade_log": [
      {
        "entry_time": "string",
        "exit_time": "string",
        "symbol": "string",
        "volume": "number",
        "entry_price": "number",
        "exit_price": "number",
        "profit_usd": "number",
        "profit_pips": "number"
      }
    ],
    "parameters": "object",
    "created_at": "string"
  }
]
```

**Status Codes**:
- 200: History returned successfully
- 500: Error retrieving history

**Section sources**
- [api_backtest.py](file://core/routes/api_backtest.py#L87-L130)

## Portfolio API
The Portfolio API provides real-time information about open positions and asset allocation.

### Available Endpoints

#### **GET /api/portfolio/open-positions**
Retrieves all currently open trading positions.

**Response Schema**:
```json
[
  {
    "ticket": "integer",
    "symbol": "string",
    "volume": "number",
    "open_price": "number",
    "current_price": "number",
    "profit": "number",
    "type": "integer",
    "magic": "integer",
    "comment": "string"
  }
]
```

**Status Codes**:
- 200: Positions returned successfully
- 500: Error retrieving positions

**Section sources**
- [api_portfolio.py](file://core/routes/api_portfolio.py#L8-L18)

#### **GET /api/portfolio/allocation**
Retrieves asset allocation breakdown.

**Response Schema**:
```json
{
  "labels": ["string"],
  "values": ["number"]
}
```

**Asset Categories**:
- Forex: Currency pairs containing USD but not XAU or BTC
- Emas: Gold-related symbols containing XAU
- Saham: Stock symbols (AAPL, GOOGL, TSLA, ND100, SP500)
- Crypto: Cryptocurrency symbols (BTC, ETH)
- Lainnya: Other symbols not fitting the above categories

**Status Codes**:
- 200: Allocation returned successfully
- 500: Error calculating allocation

**Section sources**
- [api_portfolio.py](file://core/routes/api_portfolio.py#L20-L57)

## Dashboard API
The Dashboard API provides summary statistics for the application dashboard.

### Available Endpoints

#### **GET /api/dashboard/stats**
Retrieves key dashboard statistics.

**Response Schema**:
```json
{
  "equity": "number",
  "todays_profit": "number",
  "active_bots_count": "integer",
  "total_bots": "integer",
  "active_bots": [
    {
      "name": "string",
      "market": "string"
    }
  ]
}
```

**Status Codes**:
- 200: Statistics returned successfully
- 500: Error retrieving statistics

**Section sources**
- [api_dashboard.py](file://core/routes/api_dashboard.py#L8-L28)

## Profile API
The Profile API manages user profile information.

### Available Endpoints

#### **GET /api/profile**
Retrieves the current user's profile.

**Response Schema**:
```json
{
  "id": "integer",
  "name": "string",
  "email": "string",
  "join_date": "string"
}
```

**Status Codes**:
- 200: Profile returned successfully
- 404: User not found

**Section sources**
- [api_profile.py](file://core/routes/api_profile.py#L13-L23)

#### **PUT /api/profile**
Updates the user's profile.

**Request Body**:
```json
{
  "name": "string",
  "password": "string"
}
```

**Response Schema**:
```json
{
  "message": "string"
}
```

**Validation Rules**:
- `name` is required and cannot be empty
- `password` is optional; if provided, it will be hashed before storage

**Status Codes**:
- 200: Profile updated successfully
- 400: Name is empty

**Section sources**
- [api_profile.py](file://core/routes/api_profile.py#L25-L40)

## Forex API
The Forex API provides information about forex symbols and their profiles.

### Available Endpoints

#### **GET /api/forex-data**
Retrieves a list of forex symbols sorted by popularity.

**Response Schema**:
```json
[
  {
    "name": "string",
    "description": "string",
    "volume": "number"
  }
]
```

**Status Codes**:
- 200: Forex data returned successfully

**Section sources**
- [api_forex.py](file://core/routes/api_forex.py#L10-L17)

#### **GET /api/forex/{symbol}/profile**
Retrieves detailed profile information for a forex symbol.

**Path Parameters**:
- `symbol`: The forex symbol to retrieve

**Response Schema**:
```json
{
  "name": "string",
  "description": "string",
  "digits": "integer",
  "point": "number",
  "trade_contract_size": "number",
  "volume_min": "number",
  "volume_max": "number",
  "volume_step": "number"
}
```

**Status Codes**:
- 200: Symbol profile returned successfully
- 404: Could not fetch symbol profile

**Section sources**
- [api_forex.py](file://core/routes/api_forex.py#L19-L24)

## Stocks API
The Stocks API provides real-time stock market data and symbol information.

### Available Endpoints

#### **GET /api/stocks**
Retrieves current stock prices for popular stocks.

**Response Schema**:
```json
[
  {
    "symbol": "string",
    "last_price": "number",
    "change": "number",
    "time": "string"
  }
]
```

**Calculation Method**:
- Change is calculated as (current ask price - daily open price)
- Data is fetched from MetaTrader5 for the top 20 most popular stocks

**Status Codes**:
- 200: Stock data returned successfully

**Section sources**
- [api_stocks.py](file://core/routes/api_stocks.py#L17-L98)

#### **GET /api/stocks/{symbol}/profile**
Retrieves detailed profile information for a stock symbol.

**Path Parameters**:
- `symbol`: The stock symbol to retrieve

**Response Schema**: Same as forex symbol profile

**Status Codes**:
- 200: Symbol profile returned successfully
- 404: Could not fetch symbol profile

**Section sources**
- [api_stocks.py](file://core/routes/api_stocks.py#L8-L15)

#### **GET /api/stocks/{symbol}**
Retrieves detailed information for a specific stock.

**Path Parameters**:
- `symbol`: The stock symbol to retrieve

**Response Schema**:
```json
{
  "symbol": "string",
  "time": "string",
  "open": "number",
  "high": "number",
  "low": "number",
  "close": "number",
  "volume": "number"
}
```

**Status Codes**:
- 200: Stock detail returned successfully
- 404: Unable to fetch data for symbol

**Section sources**
- [api_stocks.py](file://core/routes/api_stocks.py#L100-L118)

#### **GET /api/symbols/all**
Retrieves all available symbols from MetaTrader5 with their paths.

**Response Schema**:
```json
[
  {
    "name": "string",
    "path": "string"
  }
]
```

**Status Codes**:
- 200: All symbols returned successfully
- 500: Error connecting to MetaTrader5

**Section sources**
- [api_stocks.py](file://core/routes/api_stocks.py#L120-L132)

## Notifications API
The Notifications API manages user notifications and their read status.

### Available Endpoints

#### **GET /api/notifications**
Retrieves all notifications and marks them as read.

**Response Schema**:
```json
[
  {
    "id": "integer",
    "title": "string",
    "message": "string",
    "type": "string",
    "timestamp": "string",
    "read": "boolean"
  }
]
```

**Behavior**: When this endpoint is called, all notifications are automatically marked as read.

**Status Codes**:
- 200: Notifications returned successfully
- 500: Error retrieving notifications

**Section sources**
- [api_notifications.py](file://core/routes/api_notifications.py#L7-L17)

#### **GET /api/notifications/unread-count**
Retrieves the count of unread notifications.

**Response Schema**: `integer`

**Status Codes**:
- 200: Count returned successfully
- 500: Error counting notifications

**Section sources**
- [api_notifications.py](file://core/routes/api_notifications.py#L19-L26)

#### **GET /api/notifications/unread**
Retrieves only unread notifications.

**Response Schema**: Same as GET /api/notifications

**Status Codes**:
- 200: Unread notifications returned successfully
- 500: Error retrieving notifications

**Section sources**
- [api_notifications.py](file://core/routes/api_notifications.py#L28-L37)

#### **POST /api/notifications/mark-as-read**
Marks specific notifications as read.

**Request Body**:
```json
{
  "ids": ["integer"]
}
```

**Response Schema**:
```json
{
  "message": "string"
}
```

**Validation Rules**:
- `ids` is required and must be an array of integers

**Status Codes**:
- 200: Notifications marked as read successfully
- 400: Invalid request body
- 500: Error marking notifications as read

**Section sources**
- [api_notifications.py](file://core/routes/api_notifications.py#L39-L52)

## History API
The History API provides access to trade history data.

### Available Endpoints

#### **GET /api/history**
Retrieves global trade history.

**Response Schema**:
```json
[
  {
    "ticket": "integer",
    "symbol": "string",
    "volume": "number",
    "price": "number",
    "profit": "number",
    "type": "integer",
    "time": "string"
  }
]
```

**Status Codes**:
- 200: History returned successfully

**Section sources**
- [api_history.py](file://core/routes/api_history.py#L13-L17)

#### **GET /api/bots/{bot_id}/history**
Retrieves trade history for a specific bot.

**Path Parameters**:
- `bot_id`: The ID of the bot

**Response Schema**:
```json
[
  {
    "ticket": "integer",
    "symbol": "string",
    "volume": "number",
    "price": "number",
    "profit": "number",
    "type": "integer",
    "time": "string"
  }
]
```

**Filtering**: History is filtered by the bot's magic number and the last 30 days.

**Status Codes**:
- 200: Bot history returned successfully
- 404: Bot not found
- 500: Error retrieving history

**Section sources**
- [api_history.py](file://core/routes/api_history.py#L19-L51)

## Chart API
The Chart API provides price data for charting purposes.

### Available Endpoints

#### **GET /api/chart/data**
Retrieves price data for charting.

**Query Parameters**:
- `symbol`: Trading symbol (default: EURUSD)

**Response Schema**:
```json
{
  "labels": ["string"],
  "data": ["number"]
}
```

**Data Source**: 100 most recent H1 bars from MetaTrader5

**Status Codes**:
- 200: Chart data returned successfully
- 500: Error retrieving chart data

**Section sources**
- [api_chart.py](file://core/routes/api_chart.py#L10-L21)

## Fundamentals API
The Fundamentals API provides fundamental data for trading instruments.

### Available Endpoints

#### **GET /api/bots/{bot_id}/fundamentals**
Retrieves fundamental data for a bot's market.

**Path Parameters**:
- `bot_id`: The ID of the bot

**Response Schema**: `object`

**Behavior**: Returns empty object for non-stock markets.

**Status Codes**:
- 200: Fundamentals returned successfully
- 404: Bot not found

**Section sources**
- [api_fundamentals.py](file://core/routes/api_fundamentals.py#L8-L19)

#### **GET /fundamental-data**
Retrieves fundamental data (placeholder implementation).

**Response Schema**:
```json
{
  "status": "string",
  "data": "string"
}
```

**Note**: This is a placeholder endpoint with sample data.

**Status Codes**:
- 200: Data returned successfully

**Section sources**
- [api_bots_fundamentals.py](file://core/routes/api_bots_fundamentals.py#L7-L10)

## Indicators API
The Indicators API provides technical indicator data.

### Available Endpoints

#### **GET /api/rsi_data**
Retrieves RSI indicator data.

**Query Parameters**:
- `symbol`: Trading symbol (default: EURUSD)
- `timeframe`: Chart timeframe (default: H1)

**Response Schema**:
```json
{
  "timestamps": ["string"],
  "rsi_values": ["number"]
}
```

**Calculation**: 14-period RSI using pandas-ta library

**Status Codes**:
- 200: RSI data returned successfully

**Section sources**
- [api_indicators.py](file://core/routes/api_indicators.py#L10-L35)

## Holiday API
The Holiday API provides automatic holiday detection and integration features for the dashboard.

### Available Endpoints

#### **GET /api/holiday/status**
Retrieves the current holiday status for dashboard integration.

**Response Schema**:
```json
{
  "success": "boolean",
  "is_holiday": "boolean",
  "holiday_name": "string",
  "greeting": "string",
  "ui_theme": "object",
  "trading_adjustments": "object",
  "ramadan_features": "object"
}
```

**Status Codes**:
- 200: Holiday status returned successfully
- 500: Error retrieving holiday status

**Section sources**
- [api_holiday.py](file://core/routes/api_holiday.py#L10-L98)

#### **GET /api/holiday/pause-status**
Checks if trading is currently paused due to holiday conditions.

**Response Schema**:
```json
{
  "success": "boolean",
  "is_paused": "boolean",
  "pause_reason": "string",
  "message": "string"
}
```

**Status Codes**:
- 200: Pause status returned successfully
- 500: Error checking pause status

**Section sources**
- [api_holiday.py](file://core/routes/api_holiday.py#L100-L140)

## Ramadan API
The Ramadan API provides Ramadan-specific trading features and conditional visibility controls.

### Available Endpoints

#### **GET /api/ramadan/status**
Retrieves the current Ramadan trading mode status.

**Response Schema**:
```json
{
  "success": "boolean",
  "is_ramadan": "boolean",
  "holiday_name": "string",
  "start_date": "string",
  "end_date": "string",
  "trading_adjustments": "object",
  "ui_theme": "object",
  "greeting": "string"
}
```

**Status Codes**:
- 200: Ramadan status returned successfully
- 500: Error retrieving Ramadan status

**Section sources**
- [api_ramadan.py](file://core/routes/api_ramadan.py#L10-L50)

#### **GET /api/ramadan/features**
Retrieves Ramadan-specific features data.

**Response Schema**:
```json
{
  "success": "boolean",
  "is_ramadan": "boolean",
  "features": "object"
}
```

**Status Codes**:
- 200: Ramadan features returned successfully
- 500: Error retrieving Ramadan features

**Section sources**
- [api_ramadan.py](file://core/routes/api_ramadan.py#L52-L75)

#### **GET /api/ramadan/pause-status**
Checks if trading is currently paused due to Ramadan prayer times.

**Response Schema**:
```json
{
  "success": "boolean",
  "is_paused": "boolean",
  "pause_reason": "string",
  "message": "string"
}
```

**Status Codes**:
- 200: Ramadan pause status returned successfully
- 500: Error checking Ramadan pause status

**Section sources**
- [api_ramadan.py](file://core/routes/api_ramadan.py#L77-L120)

#### **GET /api/ramadan/zakat-calculator**
Retrieves Zakat calculation information.

**Response Schema**:
```json
{
  "success": "boolean",
  "is_ramadan": "boolean",
  "zakat_info": "object"
}
```

**Status Codes**:
- 200: Zakat calculator data returned successfully
- 500: Error retrieving Zakat calculator data

**Section sources**
- [api_ramadan.py](file://core/routes/api_ramadan.py#L122-L140)

## Error Response Format
All API endpoints follow a standardized error response format when errors occur.

**Error Response Schema**:
```json
{
  "error": "string"
}
```

**Common Error Messages**:
- "Gagal memuat daftar strategi" - Failed to load strategy list
- "Strategi tidak ditemukan" - Strategy not found
- "Bot tidak ditemukan" - Bot not found
- "Tidak ada file data yang diunggah" - No data file uploaded
- "Nama file kosong" - Empty filename
- "Gagal mengambil notifikasi" - Failed to retrieve notifications
- "Tidak dapat mengambil data untuk {symbol}" - Cannot retrieve data for symbol

**HTTP Status Codes**:
- 400 Bad Request: Invalid request parameters or missing required data
- 404 Not Found: Resource not found
- 500 Internal Server Error: Server-side error during processing

**Section sources**
- [api_bots.py](file://core/routes/api_bots.py)
- [api_backtest.py](file://core/routes/api_backtest.py)
- [api_portfolio.py](file://core/routes/api_portfolio.py)
- [api_dashboard.py](file://core/routes/api_dashboard.py)
- [api_profile.py](file://core/routes/api_profile.py)
- [api_forex.py](file://core/routes/api_forex.py)
- [api_stocks.py](file://core/routes/api_stocks.py)
- [api_notifications.py](file://core/routes/api_notifications.py)
- [api_history.py](file://core/routes/api_history.py)
- [api_chart.py](file://core/routes/api_chart.py)
- [api_fundamentals.py](file://core/routes/api_fundamentals.py)
- [api_bots_fundamentals.py](file://core/routes/api_bots_fundamentals.py)
- [api_indicators.py](file://core/routes/api_indicators.py)
- [api_holiday.py](file://core/routes/api_holiday.py)
- [api_ramadan.py](file://core/routes/api_ramadan.py)