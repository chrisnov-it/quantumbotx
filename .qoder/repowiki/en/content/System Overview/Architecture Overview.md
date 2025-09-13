# Architecture Overview

<cite>
**Referenced Files in This Document**   
- [run.py](file://run.py)
- [core/__init__.py](file://core/__init__.py)
- [core/bots/controller.py](file://core/bots/controller.py)
- [core/bots/trading_bot.py](file://core/bots/trading_bot.py)
- [core/strategies/base_strategy.py](file://core/strategies/base_strategy.py)
- [core/strategies/strategy_map.py](file://core/strategies/strategy_map.py)
- [core/db/connection.py](file://core/db/connection.py)
- [core/db/models.py](file://core/db/models.py)
- [core/db/queries.py](file://core/db/queries.py)
- [core/mt5/trade.py](file://core/mt5/trade.py)
- [core/utils/mt5.py](file://core/utils/mt5.py)
- [core/routes/api_bots.py](file://core/routes/api_bots.py)
- [core/routes/api_dashboard.py](file://core/routes/api_dashboard.py)
</cite>

## Table of Contents
1. [Introduction](#introduction)
2. [Project Structure](#project-structure)
3. [Core Components](#core-components)
4. [Architecture Overview](#architecture-overview)
5. [Detailed Component Analysis](#detailed-component-analysis)
6. [Dependency Analysis](#dependency-analysis)
7. [Performance Considerations](#performance-considerations)
8. [Troubleshooting Guide](#troubleshooting-guide)
9. [Conclusion](#conclusion)

## Introduction
QuantumBotX is a modular, AI-powered trading platform built on Flask and integrated with the MetaTrader 5 (MT5) terminal. It enables users to create, manage, and backtest automated trading bots using a variety of technical strategies. The system follows a clean separation of concerns, dividing functionality into frontend (HTML/CSS/JS), backend logic (Python), and external MT5 integration. This document provides a comprehensive architectural overview, detailing the MVC-like structure, key components, data flows, and integration points. The design emphasizes extensibility through a plugin-style strategy system and robustness via persistent logging and error handling.

## Project Structure
The project is organized into a modular directory structure that separates concerns by functionality. The core application logic resides in the `core` directory, which contains submodules for bots, database operations, MT5 integration, routing, strategies, and utilities. Static assets (CSS, JS) and HTML templates are stored in dedicated directories, while configuration and entry points are located at the root.

```mermaid
graph TD
A[Project Root] --> B[core]
A --> C[static]
A --> D[templates]
A --> E[run.py]
A --> F[init_db.py]
A --> G[requirements.txt]
B --> H[bots]
B --> I[db]
B --> J[mt5]
B --> K[routes]
B --> L[strategies]
B --> M[utils]
H --> N[controller.py]
H --> O[trading_bot.py]
I --> P[connection.py]
I --> Q[models.py]
I --> R[queries.py]
J --> S[trade.py]
K --> T[api_bots.py]
K --> U[api_dashboard.py]
L --> V[base_strategy.py]
L --> W[strategy_map.py]
C --> X[css]
C --> Y[js]
D --> Z[HTML Templates]
```

**Diagram sources**
- [run.py](file://run.py#L1-L52)
- [core/__init__.py](file://core/__init__.py#L1-L138)

**Section sources**
- [run.py](file://run.py#L1-L52)
- [core/__init__.py](file://core/__init__.py#L1-L138)

## Core Components
The core components of QuantumBotX include the Flask application factory, a thread-based bot execution system, a strategy plugin architecture, and a RESTful API layer. The application is initialized via `run.py`, which sets up the Flask app, connects to MT5, and registers shutdown handlers. Bots are managed by the `controller.py` module, which maintains a dictionary of active bot threads. Each bot is an instance of the `TradingBot` class, which runs in its own thread and executes trades based on signals from a selected strategy. Strategies are implemented as classes that inherit from `BaseStrategy` and are registered in the `STRATEGY_MAP` for dynamic loading. Data persistence is handled by SQLite, with queries abstracted through the `queries.py` module.

**Section sources**
- [core/bots/controller.py](file://core/bots/controller.py#L1-L177)
- [core/bots/trading_bot.py](file://core/bots/trading_bot.py#L1-L170)
- [core/strategies/base_strategy.py](file://core/strategies/base_strategy.py#L1-L29)
- [core/strategies/strategy_map.py](file://core/strategies/strategy_map.py#L1-L28)

## Architecture Overview
QuantumBotX follows a modular, MVC-like architectural pattern with clear separation between the user interface, business logic, and data layers. The Flask application serves as the central hub, routing HTTP requests to appropriate API endpoints. These endpoints interact with core services that manage bot lifecycle, strategy execution, and data retrieval. The system integrates with the MetaTrader 5 terminal for real-time market data and trade execution. A SQLite database provides lightweight persistence for bot configurations, trade history, and notifications.

```mermaid
graph TB
subgraph "Frontend"
UI[User Interface]
JS[JavaScript]
CSS[CSS]
end
subgraph "Backend"
API[RESTful API]
Services[Core Services]
DB[(SQLite Database)]
end
subgraph "External"
MT5[MetaTrader 5 Terminal]
end
UI --> API
API --> Services
Services --> DB
Services --> MT5
MT5 --> Services
Services --> API
```

**Diagram sources**
- [run.py](file://run.py#L1-L52)
- [core/__init__.py](file://core/__init__.py#L1-L138)
- [core/routes/api_bots.py](file://core/routes/api_bots.py#L1-L168)
- [core/routes/api_dashboard.py](file://core/routes/api_dashboard.py#L1-L29)

## Detailed Component Analysis

### Bot Management System
The bot management system is responsible for creating, starting, stopping, and monitoring trading bots. It uses a thread-based model where each active bot runs in its own thread, allowing for concurrent execution without blocking the main application.

#### Class Diagram for Bot System
```mermaid
classDiagram
class TradingBot {
+int id
+str name
+str market
+float risk_percent
+int sl_pips
+int tp_pips
+str timeframe
+int check_interval
+str strategy_name
+dict strategy_params
+str status
+dict last_analysis
+run() void
+stop() void
+log_activity(action, details) void
+_handle_trade_signal(signal, position) void
}
class BaseStrategy {
+analyze(df) dict
+get_definable_params() list
}
class StrategyMap {
+STRATEGY_MAP : dict
}
class BotController {
+dict active_bots
+mulai_bot(bot_id) bool
+hentikan_bot(bot_id) bool
+shutdown_all_bots() void
+perbarui_bot(bot_id, data) bool
}
TradingBot --> BaseStrategy : "uses"
BotController --> TradingBot : "manages"
BotController --> StrategyMap : "references"
```

**Diagram sources**
- [core/bots/trading_bot.py](file://core/bots/trading_bot.py#L1-L170)
- [core/strategies/base_strategy.py](file://core/strategies/base_strategy.py#L1-L29)
- [core/strategies/strategy_map.py](file://core/strategies/strategy_map.py#L1-L28)
- [core/bots/controller.py](file://core/bots/controller.py#L1-L177)

### API Layer
The API layer exposes RESTful endpoints for managing bots, retrieving dashboard data, and interacting with trading strategies. It acts as the bridge between the frontend and the backend services.

#### Sequence Diagram for Bot Start Request
```mermaid
sequenceDiagram
participant Frontend
participant API as "api_bots.py"
participant Controller as "controller.py"
participant DB as "queries.py"
participant Bot as "TradingBot"
Frontend->>API : POST /api/bots/{id}/start
API->>Controller : mulai_bot(id)
Controller->>DB : get_bot_by_id(id)
DB-->>Controller : bot_data
Controller->>Bot : new TradingBot(bot_data)
Bot->>Bot : start()
Controller->>DB : update_bot_status(id, 'Aktif')
DB-->>Controller : success
Controller-->>API : success, message
API-->>Frontend : 200 OK, message
```

**Diagram sources**
- [core/routes/api_bots.py](file://core/routes/api_bots.py#L1-L168)
- [core/bots/controller.py](file://core/bots/controller.py#L1-L177)
- [core/db/queries.py](file://core/db/queries.py#L1-L175)

### Strategy Plugin System
The strategy plugin system allows for extensible trading logic by defining a common interface (`BaseStrategy`) that all strategies must implement. Strategies are dynamically loaded via the `STRATEGY_MAP`, enabling easy addition of new strategies without modifying core code.

#### Flowchart for Strategy Execution
```mermaid
flowchart TD
Start([Bot Loop Start]) --> GetData["Get Market Data via MT5"]
GetData --> HasData{"Data Retrieved?"}
HasData --> |No| LogError["Log Warning, Wait Interval"]
HasData --> |Yes| Analyze["Execute Strategy.analyze(df)"]
Analyze --> Signal{"Signal: BUY/SELL/HOLD?"}
Signal --> |BUY| HandleBuy["Handle BUY Signal"]
Signal --> |SELL| HandleSell["Handle SELL Signal"]
Signal --> |HOLD| Wait["Wait Check Interval"]
HandleBuy --> CloseSell["Close SELL if exists"]
HandleBuy --> OpenBuy["Open BUY Position"]
HandleSell --> CloseBuy["Close BUY if exists"]
HandleSell --> OpenSell["Open SELL Position"]
OpenBuy --> Wait
OpenSell --> Wait
CloseSell --> OpenBuy
CloseBuy --> OpenSell
Wait --> Sleep["Sleep(check_interval)"]
Sleep --> Start
```

**Diagram sources**
- [core/bots/trading_bot.py](file://core/bots/trading_bot.py#L1-L170)
- [core/strategies/base_strategy.py](file://core/strategies/base_strategy.py#L1-L29)

**Section sources**
- [core/bots/trading_bot.py](file://core/bots/trading_bot.py#L1-L170)
- [core/strategies/base_strategy.py](file://core/strategies/base_strategy.py#L1-L29)

## Dependency Analysis
The QuantumBotX application has a well-defined dependency graph with minimal circular dependencies. The core modules depend on standard libraries and the MetaTrader5 package, while internal modules maintain loose coupling through defined interfaces.

```mermaid
graph TD
run.py --> core/__init__.py
run.py --> core/bots/controller.py
run.py --> core/utils/mt5.py
core/__init__.py --> core/routes/api_bots.py
core/__init__.py --> core/routes/api_dashboard.py
core/bots/controller.py --> core/bots/trading_bot.py
core/bots/controller.py --> core/db/queries.py
core/bots/trading_bot.py --> core/strategies/strategy_map.py
core/bots/trading_bot.py --> core/mt5/trade.py
core/bots/trading_bot.py --> core/utils/mt5.py
core/mt5/trade.py --> core/utils/mt5.py
core/routes/api_bots.py --> core/bots/controller.py
core/routes/api_bots.py --> core/db/queries.py
core/routes/api_bots.py --> core/strategies/strategy_map.py
core/routes/api_dashboard.py --> core/utils/mt5.py
core/routes/api_dashboard.py --> core/db/queries.py
```

**Diagram sources**
- [run.py](file://run.py#L1-L52)
- [core/__init__.py](file://core/__init__.py#L1-L138)
- [core/bots/controller.py](file://core/bots/controller.py#L1-L177)
- [core/bots/trading_bot.py](file://core/bots/trading_bot.py#L1-L170)
- [core/mt5/trade.py](file://core/mt5/trade.py#L1-L153)
- [core/routes/api_bots.py](file://core/routes/api_bots.py#L1-L168)
- [core/routes/api_dashboard.py](file://core/routes/api_dashboard.py#L1-L29)

**Section sources**
- [run.py](file://run.py#L1-L52)
- [core/__init__.py](file://core/__init__.py#L1-L138)
- [core/bots/controller.py](file://core/bots/controller.py#L1-L177)

## Performance Considerations
The current architecture uses threading for bot execution, which is suitable for I/O-bound tasks like market data retrieval and trade execution. However, Python's Global Interpreter Lock (GIL) limits true parallelism, making this model less efficient for CPU-intensive strategies. The use of SQLite provides fast, lightweight persistence but may become a bottleneck with high-frequency trading or large datasets. The polling-based approach in `TradingBot.run()` introduces a small delay between analysis cycles, determined by the `check_interval` parameter. For improved scalability, a message queue system (e.g., Redis, RabbitMQ) could decouple bot execution from the main application, and a more robust database (e.g., PostgreSQL) could handle larger data volumes.

## Troubleshooting Guide
Common issues in QuantumBotX typically relate to MT5 connectivity, symbol resolution, or database operations. The system logs detailed information to both console and file (in production mode), which should be the first place to check for errors. If a bot fails to start, verify that the MT5 terminal is running and that the symbol exists in the Market Watch. Database issues can often be resolved by checking the `bots.db` file permissions and integrity. The `/api/health` endpoint can be used to verify that the Flask server is running. For strategy-specific problems, ensure that all required parameters are correctly configured and that the market data is available for the selected timeframe.

**Section sources**
- [run.py](file://run.py#L1-L52)
- [core/utils/logger.py](file://core/utils/logger.py)
- [core/db/queries.py](file://core/db/queries.py#L1-L175)
- [core/utils/mt5.py](file://core/utils/mt5.py#L1-L145)

## Conclusion
QuantumBotX presents a well-structured, modular architecture for automated trading with clear separation of concerns and extensible design. Its use of Flask, threading, and a plugin-based strategy system makes it accessible for development and customization. The integration with MetaTrader 5 provides reliable access to real trading environments, while the SQLite backend ensures simple deployment. Future improvements could include containerization for easier deployment, adoption of async/await for better concurrency, and implementation of a distributed backtesting framework for improved performance and scalability.