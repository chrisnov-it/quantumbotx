# System Overview

<cite>
**Referenced Files in This Document**   
- [README.md](file://README.md)
- [run.py](file://run.py)
- [core/__init__.py](file://core/__init__.py)
- [core/bots/controller.py](file://core/bots/controller.py)
- [core/bots/trading_bot.py](file://core/bots/trading_bot.py)
- [core/strategies/strategy_map.py](file://core/strategies/strategy_map.py)
- [core/strategies/base_strategy.py](file://core/strategies/base_strategy.py)
- [core/mt5/trade.py](file://core/mt5/trade.py)
- [core/utils/mt5.py](file://core/utils/mt5.py)
- [core/db/connection.py](file://core/db/connection.py)
- [core/db/models.py](file://core/db/models.py)
- [core/db/queries.py](file://core/db/queries.py)
- [core/routes/api_bots.py](file://core/routes/api_bots.py)
- [core/routes/api_backtest.py](file://core/routes/api_backtest.py)
- [core/ai/trading_mentor_ai.py](file://core/ai/trading_mentor_ai.py) - *Added in commit a24fa86*
- [core/routes/ai_mentor.py](file://core/routes/ai_mentor.py) - *Added in commit a24fa86*
</cite>

## Update Summary
**Changes Made**   
- Added comprehensive documentation for the new Indonesian AI Trading Mentor System
- Updated Introduction and Architecture Overview sections to reflect the new AI mentor feature
- Added new section on AI Mentor System with detailed component analysis
- Enhanced dependency analysis to include AI-related components
- Added new workflow example for AI mentor interaction
- Updated referenced files list to include new AI mentor files

## Table of Contents
1. [Introduction](#introduction)
2. [Project Structure](#project-structure)
3. [Core Components](#core-components)
4. [Architecture Overview](#architecture-overview)
5. [Detailed Component Analysis](#detailed-component-analysis)
6. [Workflow Examples](#workflow-examples)
7. [Dependency Analysis](#dependency-analysis)
8. [Performance and Scalability](#performance-and-scalability)
9. [Conclusion](#conclusion)

## Introduction

QuantumBotX is an AI-powered modular trading bot platform integrated with MetaTrader 5 (MT5), designed for automated trading, backtesting, and portfolio monitoring. The system enables users to create, manage, and deploy algorithmic trading strategies across various financial instruments including forex, stocks, and commodities. It features a responsive web interface built with Flask and modern frontend technologies, allowing traders to configure bots, analyze performance, and monitor live trading activities in real time.

The platform supports multiple technical strategies such as Moving Average Crossover, Bollinger Bands Reversion, and a proprietary QuantumBotX Hybrid strategy that adapts to market conditions using ADX indicators. A revolutionary new feature, the Indonesian AI Trading Mentor System, provides personalized guidance and emotional support to traders, analyzing their trading sessions and offering culturally relevant recommendations in Bahasa Indonesia. All trading activities are logged persistently in a local SQLite database, ensuring traceability and auditability. The system is designed to operate in both demo and live trading environments, with safeguards to prevent unintended execution.

This document provides a comprehensive overview of the QuantumBotX system, detailing its architecture, core components, data flows, and operational workflows. It is structured to serve both technical developers and non-technical users by balancing conceptual clarity with in-depth implementation details.

## Project Structure

The QuantumBotX project follows a modular, feature-based organization that separates concerns across core functional domains. The root directory contains configuration files, entry points, and static assets, while the `core` directory houses all business logic and services.

``mermaid
graph TB
subgraph "Root"
runpy[run.py]
README[README.md]
requirements[requirements.txt]
initdb[init_db.py]
env[.env.example]
end
subgraph "Core Modules"
core[core/]
core --> ai[ai/]
core --> backtesting[backtesting/]
core --> bots[bots/]
core --> db[db/]
core --> interfaces[interfaces/]
core --> mt5[mt5/]
core --> routes[routes/]
core --> services[services/]
core --> strategies[strategies/]
core --> utils[utils/]
end
subgraph "Frontend Assets"
static[static/]
templates[templates/]
end
runpy --> core
core --> static
core --> templates
```

**Diagram sources**
- [run.py](file://run.py)
- [core/__init__.py](file://core/__init__.py)

**Section sources**
- [README.md](file://README.md)
- [run.py](file://run.py)

## Core Components

QuantumBotX is composed of several interconnected modules that work together to enable automated trading functionality. The primary components include:

- **Web Interface**: A Flask-based frontend with HTML/CSS/JavaScript templates and Chart.js visualizations.
- **Backend Logic**: Python modules handling trading logic, strategy execution, and MT5 integration.
- **Database Layer**: SQLite storage for bot configurations, trade history, and user profiles.
- **Strategy Engine**: A pluggable system supporting multiple algorithmic trading strategies.
- **Backtesting Module**: A dedicated engine for evaluating strategy performance on historical data.
- **AI Mentor System**: A revolutionary feature providing personalized trading guidance and emotional support in Bahasa Indonesia.

The system uses a Model-View-Controller (MVC)-like pattern where Flask routes handle HTTP requests (controller), templates render the UI (view), and core modules implement business logic (model). Threading is used to run trading bots concurrently without blocking the main application.

**Section sources**
- [core/__init__.py](file://core/__init__.py)
- [core/bots/controller.py](file://core/bots/controller.py)
- [core/strategies/strategy_map.py](file://core/strategies/strategy_map.py)

## Architecture Overview

QuantumBotX follows a layered architecture with clear separation between the presentation, application logic, and external integration layers. The system is initialized via `run.py`, which sets up the Flask application, establishes a connection to MetaTrader 5, and registers shutdown handlers.

``mermaid
graph TD
A[Client Browser] --> B[Flask Web Server]
B --> C[API Routes]
C --> D[Bot Controller]
D --> E[Trading Bot Thread]
E --> F[Strategy Logic]
E --> G[MT5 Integration]
G --> H[MetaTrader 5 Platform]
D --> I[Database]
F --> I
G --> I
C --> J[Backtesting Engine]
J --> I
J --> K[Historical Data]
C --> L[AI Mentor System]
L --> M[Indonesian Trading Mentor AI]
L --> I
M --> N[Trading Session Analysis]
style A fill:#f9f,stroke:#333
style H fill:#f96,stroke:#333
style I fill:#bbf,stroke:#333
```

**Diagram sources**
- [run.py](file://run.py)
- [core/__init__.py](file://core/__init__.py)
- [core/bots/trading_bot.py](file://core/bots/trading_bot.py)
- [core/mt5/trade.py](file://core/mt5/trade.py)
- [core/ai/trading_mentor_ai.py](file://core/ai/trading_mentor_ai.py)
- [core/routes/ai_mentor.py](file://core/routes/ai_mentor.py)

## Detailed Component Analysis

### Bot Management System

The bot management system is responsible for lifecycle control of trading bots, including creation, starting, stopping, and deletion. The `TradingBot` class extends Python's `threading.Thread`, allowing each bot to run independently with its own strategy and market parameters.

``mermaid
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
+dict last_analysis
+run()
+stop()
+log_activity(action, details)
+_handle_trade_signal(signal, position)
}
class BaseStrategy {
<<abstract>>
+analyze(df) abstract
+get_definable_params() classmethod
}
TradingBot --> BaseStrategy : "uses"
TradingBot --> "MT5 API" : "interacts with"
TradingBot --> "Database" : "logs to"
```

**Diagram sources**
- [core/bots/trading_bot.py](file://core/bots/trading_bot.py)
- [core/strategies/base_strategy.py](file://core/strategies/base_strategy.py)

**Section sources**
- [core/bots/trading_bot.py](file://core/bots/trading_bot.py)
- [core/bots/controller.py](file://core/bots/controller.py)

### Strategy Execution Flow

Each trading bot executes its strategy in a loop, fetching price data from MT5, analyzing it using the selected strategy, and executing trades based on the generated signals. The execution flow is as follows:

``mermaid
flowchart TD
Start([Start Bot]) --> VerifySymbol["Verify Symbol in MT5"]
VerifySymbol --> LoadData["Fetch Historical Data"]
LoadData --> Analyze["Execute Strategy.analyze()"]
Analyze --> GetSignal["Get Signal: BUY/SELL/HOLD"]
GetSignal --> CheckPosition["Check Open Position"]
CheckPosition --> SignalDecision{Signal == BUY?}
SignalDecision --> |Yes| HandleBuy["Close SELL if exists<br/>Open BUY Order"]
SignalDecision --> |No| SignalDecision2{Signal == SELL?}
SignalDecision2 --> |Yes| HandleSell["Close BUY if exists<br/>Open SELL Order"]
SignalDecision2 --> |No| Wait["Wait check_interval seconds"]
HandleBuy --> Wait
HandleSell --> Wait
Wait --> Loop["Loop to Analyze"]
```

**Diagram sources**
- [core/bots/trading_bot.py](file://core/bots/trading_bot.py)
- [core/mt5/trade.py](file://core/mt5/trade.py)

**Section sources**
- [core/bots/trading_bot.py](file://core/bots/trading_bot.py)

### API and Route Structure

The system exposes a RESTful API through Flask blueprints, with each route file handling a specific domain such as bots, backtesting, or portfolio data. The main application factory in `core/__init__.py` registers these blueprints during initialization.

``mermaid
graph TB
A[/] --> B[index.html]
C[/trading_bots] --> D[trading_bots.html]
E[/bots/:id] --> F[bot_detail.html]
G[/backtesting] --> H[backtesting.html]
I[/api/bots] --> J[api_bots.py]
K[/api/backtest] --> L[api_backtest.py]
M[/api/dashboard] --> N[api_dashboard.py]
O[/ai-mentor] --> P[ai_mentor.py]
P --> Q[dashboard.html]
P --> R[daily_report.html]
P --> S[quick_feedback.html]
style A fill:#adf,stroke:#333
style I fill:#fda,stroke:#333
style K fill:#fda,stroke:#333
style M fill:#fda,stroke:#333
style O fill:#fda,stroke:#333
```

**Diagram sources**
- [core/__init__.py](file://core/__init__.py)
- [core/routes/api_bots.py](file://core/routes/api_bots.py)
- [core/routes/api_backtest.py](file://core/routes/api_backtest.py)
- [core/routes/ai_mentor.py](file://core/routes/ai_mentor.py)

**Section sources**
- [core/__init__.py](file://core/__init__.py)

### AI Mentor System

The Indonesian AI Trading Mentor System is a revolutionary feature that provides personalized guidance to traders, analyzing their trading sessions and offering culturally relevant recommendations in Bahasa Indonesia. The system consists of two main components: the `IndonesianTradingMentorAI` class that performs the analysis, and the Flask routes that expose this functionality through the web interface.

``mermaid
classDiagram
class IndonesianTradingMentorAI {
+str personality
+str language
+str cultural_context
+analyze_trading_session(session)
+generate_daily_report(session)
+_detect_trading_patterns(session)
+_analyze_emotional_impact(session)
+_evaluate_risk_management(session)
+_generate_recommendations(session)
+_create_motivation_message(session)
}
class TradingSession {
+date date
+list trades
+str emotions
+str market_conditions
+float profit_loss
+str notes
}
class ai_mentor_bp {
+dashboard()
+today_report()
+update_emotions()
+history()
+view_session()
+quick_feedback()
+generate_instant_feedback()
+api_dashboard_summary()
+settings()
}
IndonesianTradingMentorAI --> TradingSession : "analyzes"
ai_mentor_bp --> IndonesianTradingMentorAI : "uses"
ai_mentor_bp --> TradingSession : "manages"
```

**Diagram sources**
- [core/ai/trading_mentor_ai.py](file://core/ai/trading_mentor_ai.py)
- [core/routes/ai_mentor.py](file://core/routes/ai_mentor.py)

**Section sources**
- [core/ai/trading_mentor_ai.py](file://core/ai/trading_mentor_ai.py)
- [core/routes/ai_mentor.py](file://core/routes/ai_mentor.py)

## Workflow Examples

### Bot Creation and Activation

The process of creating and activating a trading bot involves several coordinated steps across the frontend, backend, and MT5 platform:

``mermaid
sequenceDiagram
participant Frontend
participant API as api_bots.py
participant Controller as bot controller
participant Bot as TradingBot
participant MT5 as MetaTrader 5
Frontend->>API : POST /api/bots (new bot config)
API->>Controller : add_new_bot_to_controller(id)
Controller->>Controller : queries.get_bot_by_id(id)
Controller->>Controller : mulai_bot(id)
Controller->>Bot : new TradingBot(...).start()
Bot->>MT5 : find_mt5_symbol(market)
Bot->>MT5 : get_rates_mt5(symbol, timeframe)
Bot->>Bot : strategy.analyze(df)
Bot->>MT5 : place_trade() on signal
Bot->>Controller : update last_analysis
Bot->>Database : log_activity()
```

**Diagram sources**
- [core/bots/controller.py](file://core/bots/controller.py)
- [core/bots/trading_bot.py](file://core/bots/trading_bot.py)
- [core/mt5/trade.py](file://core/mt5/trade.py)

**Section sources**
- [core/bots/controller.py](file://core/bots/controller.py)

### Backtesting Process

The backtesting workflow allows users to evaluate strategy performance on historical data before deploying live:

``mermaid
sequenceDiagram
participant Frontend
participant API as api_backtest.py
participant Engine as backtesting engine
participant Strategy
participant MT5
Frontend->>API : GET /api/backtest?params
API->>Engine : run_backtest(strategy, params)
Engine->>MT5 : get_rates_mt5(symbol, timeframe, period)
Engine->>Strategy : strategy.analyze(df) for each bar
Strategy->>Engine : return signal
Engine->>Engine : simulate trade execution
Engine->>Engine : record PnL, metrics
Engine->>API : return results
API->>Frontend : JSON with performance data
```

**Diagram sources**
- [core/routes/api_backtest.py](file://core/routes/api_backtest.py)
- [core/backtesting/engine.py](file://core/backtesting/engine.py)

**Section sources**
- [core/routes/api_backtest.py](file://core/routes/api_backtest.py)

### AI Mentor Interaction

The AI mentor interaction workflow enables traders to receive personalized guidance based on their trading performance and emotional state:

``mermaid
sequenceDiagram
participant Trader
participant Frontend
participant API as ai_mentor.py
participant Mentor as IndonesianTradingMentorAI
participant Database
Trader->>Frontend : Visit AI Mentor dashboard
Frontend->>API : GET /ai-mentor/
API->>Database : get_trading_session_data(today)
API->>Database : get_recent_mentor_reports(7)
API->>Frontend : Render dashboard with data
Trader->>Frontend : Click "Today's Report"
Frontend->>API : GET /ai-mentor/today-report
API->>Database : get_trading_session_data(today)
API->>Mentor : analyze_trading_session(session)
Mentor->>Mentor : generate_daily_report(session)
API->>Database : save_ai_mentor_report(session_id, analysis)
API->>Frontend : Render daily_report.html
Trader->>Frontend : Update emotions and notes
Frontend->>API : POST /ai-mentor/update-emotions
API->>Database : update_session_emotions_and_notes()
API->>Frontend : Return success response
```

**Diagram sources**
- [core/routes/ai_mentor.py](file://core/routes/ai_mentor.py)
- [core/ai/trading_mentor_ai.py](file://core/ai/trading_mentor_ai.py)
- [core/db/models.py](file://core/db/models.py)

**Section sources**
- [core/routes/ai_mentor.py](file://core/routes/ai_mentor.py)
- [core/ai/trading_mentor_ai.py](file://core/ai/trading_mentor_ai.py)

## Dependency Analysis

QuantumBotX has a well-defined dependency structure with minimal circular references. The core modules depend on utility and database components, while maintaining loose coupling through configuration and interfaces.

``mermaid
graph TD
runpy --> core
core --> flask
core --> mt5
core --> pandas
core --> sqlite3
core --> dotenv
core --> logging
core --> threading
core --> utils
core --> db
core --> strategies
core --> mt5module
core --> bots
core --> ai
core --> routes
bots --> strategies
bots --> mt5module
bots --> db
bots --> utils
mt5module --> utils
mt5module --> db
strategies --> base_strategy
db --> connection
db --> models
db --> queries
ai --> db
routes --> ai
routes --> db
routes --> flask
style runpy fill:#f96,stroke:#333
style flask fill:#69f,stroke:#333
style mt5 fill:#f96,stroke:#333
```

**Diagram sources**
- [requirements.txt](file://requirements.txt)
- [core/__init__.py](file://core/__init__.py)
- [core/bots/controller.py](file://core/bots/controller.py)
- [core/ai/trading_mentor_ai.py](file://core/ai/trading_mentor_ai.py)
- [core/routes/ai_mentor.py](file://core/routes/ai_mentor.py)

**Section sources**
- [requirements.txt](file://requirements.txt)

## Performance and Scalability

The system's performance is primarily constrained by the MetaTrader 5 API's rate limits and the single-threaded nature of Python. However, the use of threading allows multiple bots to operate concurrently without blocking each other.

Key architectural decisions impacting scalability include:

- **Thread-per-bot model**: Each bot runs in its own thread, enabling parallel execution but limited by Python's GIL.
- **Centralized MT5 connection**: A single MT5 connection is shared across all bots, reducing resource usage.
- **SQLite database**: Lightweight and file-based, suitable for single-user applications but not for high-concurrency scenarios.
- **In-memory bot registry**: Active bots are tracked in a dictionary (`active_bots`), enabling fast lookups and management.
- **AI Mentor System**: The new AI mentor feature adds computational overhead for session analysis but is designed to run on-demand rather than continuously.

For improved scalability, future versions could implement process-based concurrency, connection pooling, or migration to a client-server architecture with a dedicated backend service. The AI mentor system could be enhanced with machine learning models for more sophisticated analysis.

**Section sources**
- [core/bots/controller.py](file://core/bots/controller.py)
- [core/bots/trading_bot.py](file://core/bots/trading_bot.py)
- [core/utils/mt5.py](file://core/utils/mt5.py)
- [core/ai/trading_mentor_ai.py](file://core/ai/trading_mentor_ai.py)

## Conclusion

QuantumBotX is a well-structured, modular trading bot platform that effectively integrates Python-based algorithmic logic with the MetaTrader 5 ecosystem. Its architecture demonstrates clear separation of concerns, with distinct components for web interface, strategy execution, and external integration. The use of Flask, threading, and SQLite makes it accessible for individual traders while providing sufficient functionality for automated trading.

The system's strengths include its pluggable strategy architecture, comprehensive logging, user-friendly web interface, and the revolutionary new Indonesian AI Trading Mentor System that provides personalized guidance in Bahasa Indonesia. Areas for improvement include enhanced error handling, support for distributed deployment, and real-time notifications. Overall, QuantumBotX provides a solid foundation for algorithmic trading that balances complexity with usability.