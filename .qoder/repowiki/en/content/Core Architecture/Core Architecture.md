# Core Architecture

<cite>
**Referenced Files in This Document**   
- [core/__init__.py](file://core/__init__.py#L1-L196) - *Updated in recent commit*
- [run.py](file://run.py#L1-L51) - *Updated in recent commit*
- [core/routes/api_bots.py](file://core/routes/api_bots.py#L1-L167) - *Updated in recent commit*
- [core/bots/controller.py](file://core/bots/controller.py#L1-L176) - *Updated in recent commit*
- [core/bots/trading_bot.py](file://core/bots/trading_bot.py#L1-L169) - *Updated in recent commit*
- [core/strategies/base_strategy.py](file://core/strategies/base_strategy.py#L1-L28) - *Updated in recent commit*
- [core/strategies/strategy_map.py](file://core/strategies/strategy_map.py#L1-L27) - *Updated in recent commit*
- [core/mt5/trade.py](file://core/mt5/trade.py#L1-L152) - *Updated in recent commit*
- [core/db/queries.py](file://core/db/queries.py#L1-L174) - *Updated in recent commit*
- [core/utils/mt5.py](file://core/utils/mt5.py#L1-L144) - *Updated in recent commit*
- [core/brokers/broker_factory.py](file://core/brokers/broker_factory.py) - *Added in commit b1b92d363a4b3a0d16a8d55f47e41313ed93865f*
- [core/brokers/base_broker.py](file://core/brokers/base_broker.py) - *Added in commit b1b92d363a4b3a0d16a8d55f47e41313ed93865f*
- [core/brokers/binance_broker.py](file://core/brokers/binance_broker.py) - *Added in commit b1b92d363a4b3a0d16a8d55f47e41313ed93865f*
- [core/brokers/ctrader_broker.py](file://core/brokers/ctrader_broker.py) - *Added in commit b1b92d363a4b3a0d16a8d55f47e41313ed93865f*
- [core/brokers/interactive_brokers.py](file://core/brokers/interactive_brokers.py) - *Added in commit b1b92d363a4b3a0d16a8d55f47e41313ed93865f*
- [core/brokers/tradingview_broker.py](file://core/brokers/tradingview_broker.py) - *Added in commit b1b92d363a4b3a0d16a8d55f47e41313ed93865f*
- [core/brokers/indonesian_brokers.py](file://core/brokers/indonesian_brokers.py) - *Added in commit b1b92d363a4b3a0d16a8d55f47e41313ed93865f*
- [broker_symbol_migrator.py](file://broker_symbol_migrator.py) - *Added in commit b1b92d363a4b3a0d16a8d55f47e41313ed93865f*
- [core/ai/trading_mentor_ai.py](file://core/ai/trading_mentor_ai.py#L1-L351) - *Added in commit a24fa8637bb6dc7c2f6d6fae6a633611836bf329*
- [core/routes/ai_mentor.py](file://core/routes/ai_mentor.py#L1-L333) - *Added in commit a24fa8637bb6dc7c2f6d6fae6a633611836bf329*
- [core/db/models.py](file://core/db/models.py#L1-L262) - *Modified in commit a24fa8637bb6dc7c2f6d6fae6a633611836bf329*
- [templates/ai_mentor/dashboard.html](file://templates/ai_mentor/dashboard.html#L1-L288) - *Added in commit a24fa8637bb6dc7c2f6d6fae6a633611836bf329*
</cite>

## Update Summary
**Changes Made**   
- Added comprehensive documentation for the new Indonesian AI Trading Mentor System
- Updated system context and integration points to include AI mentor functionality
- Added new architectural patterns section for the AI Mentor pattern
- Updated component interaction diagrams to reflect AI mentor data flow
- Added AI mentor database schema documentation
- Updated project structure to include new AI modules
- Enhanced error handling and scalability section with AI mentor considerations

## Table of Contents
1. [Introduction](#introduction)
2. [Project Structure](#project-structure)
3. [Application Factory and Initialization](#application-factory-and-initialization)
4. [Component Interaction and Data Flow](#component-interaction-and-data-flow)
5. [Architectural Patterns](#architectural-patterns)
6. [System Context and Integration Points](#system-context-and-integration-points)
7. [Error Handling and Scalability](#error-handling-and-scalability)

## Introduction
The QuantumBotX application is a modular Flask-based trading automation system designed to manage algorithmic trading bots across multiple trading platforms. This document provides a comprehensive architectural overview of the core application structure, detailing the modular design, component interactions, data flow, and key architectural patterns. The system enables users to create, manage, and monitor trading bots that execute strategies based on technical indicators and market data from various brokers including MetaTrader 5, Binance, cTrader, Interactive Brokers, and TradingView. The architecture emphasizes separation of concerns, extensibility, and robust error handling to ensure reliable operation in a financial trading environment. The recent addition of a multi-broker architecture significantly expands the system's capabilities, allowing for diversified trading across different asset classes and markets. Additionally, the revolutionary Indonesian AI Trading Mentor System has been introduced, providing personalized guidance and emotional support to Indonesian traders in their native language, enhancing the educational and psychological aspects of trading.

## Project Structure
The project follows a layered, modular structure with clear separation of concerns. Core functionality is organized into distinct directories, each responsible for a specific aspect of the application. The structure promotes maintainability and scalability by isolating components such as business logic, database operations, API routes, and external integrations.

``mermaid
graph TB
subgraph "Core Modules"
A[core]
A --> B[bots]
A --> C[strategies]
A --> D[db]
A --> E[mt5]
A --> F[routes]
A --> G[utils]
A --> H[brokers]
A --> I[ai]
end
subgraph "AI Mentor Components"
I --> J[trading_mentor_ai.py]
I --> K[ollama_client.py]
end
subgraph "Broker Implementations"
H --> L[base_broker.py]
H --> M[broker_factory.py]
H --> N[binance_broker.py]
H --> O[ctrader_broker.py]
H --> P[interactive_brokers.py]
H --> Q[tradingview_broker.py]
H --> R[indonesian_brokers.py]
end
subgraph "Frontend Assets"
S[static]
S --> T[css]
S --> U[js]
end
subgraph "Templates"
V[templates]
end
subgraph "Root Files"
W[run.py]
X[requirements.txt]
Y[README.md]
Z[broker_symbol_migrator.py]
end
W --> A
V --> A
S --> A
Z --> A
```

**Diagram sources**
- [core/__init__.py](file://core/__init__.py#L1-L196)
- [run.py](file://run.py#L1-L51)
- [core/brokers/broker_factory.py](file://core/brokers/broker_factory.py)
- [core/ai/trading_mentor_ai.py](file://core/ai/trading_mentor_ai.py)
- [broker_symbol_migrator.py](file://broker_symbol_migrator.py)

**Section sources**
- [core/__init__.py](file://core/__init__.py#L1-L196)
- [run.py](file://run.py#L1-L51)
- [core/brokers/broker_factory.py](file://core/brokers/broker_factory.py)
- [core/ai/trading_mentor_ai.py](file://core/ai/trading_mentor_ai.py)
- [broker_symbol_migrator.py](file://broker_symbol_migrator.py)

## Application Factory and Initialization
The Flask application is created using the application factory pattern implemented in `core/__init__.py`. This pattern allows for flexible configuration and testing by encapsulating the app creation logic within the `create_app()` function. The factory configures the Flask instance with appropriate settings, registers blueprints for API routes, and sets up logging.

The `run.py` file serves as the entry point, calling the factory function to create the app instance. It also handles centralized initialization of broker connections through the BrokerFactory and registers a shutdown function to ensure proper cleanup of resources when the application terminates. The application factory now includes registration of the AI mentor blueprint, making the Indonesian AI Trading Mentor System fully integrated into the application's routing system.

``mermaid
sequenceDiagram
participant Run as run.py
participant Factory as create_app()
participant App as Flask App
participant BrokerFactory as BrokerFactory
participant Shutdown as shutdown_app()
Run->>Factory : create_app()
Factory->>App : Initialize Flask instance
Factory->>App : Configure logging
Factory->>App : Register blueprints
Factory->>App : Register AI mentor blueprint
Factory-->>Run : Return app instance
Run->>BrokerFactory : load_brokers_from_env()
Run->>BrokerFactory : create_broker("mt5")
Run->>BrokerFactory : create_broker("binance")
Run->>Run : Register shutdown_app with atexit
Run->>App : app.run()
deactivate Run
Shutdown->>App : shutdown_all_bots()
Shutdown->>BrokerFactory : disconnect_all()
```

**Diagram sources**
- [core/__init__.py](file://core/__init__.py#L1-L196)
- [run.py](file://run.py#L1-L51)
- [core/brokers/broker_factory.py](file://core/brokers/broker_factory.py#L174-L217)

**Section sources**
- [core/__init__.py](file://core/__init__.py#L1-L196)
- [run.py](file://run.py#L1-L51)
- [core/brokers/broker_factory.py](file://core/brokers/broker_factory.py)

## Component Interaction and Data Flow
The system follows a clear request-response flow where API routes delegate to business logic components, which in turn interact with various broker platforms and database layers. When an HTTP request is received, it is routed to the appropriate blueprint handler, which orchestrates the necessary operations across the application layers.

For example, when a user requests to start a trading bot, the API route calls the controller, which retrieves bot configuration from the database, instantiates a `TradingBot` thread, and manages its lifecycle. The bot then periodically fetches market data from the configured broker, applies a trading strategy, and executes trades through the broker integration layer. Additionally, trading data is logged for analysis by the Indonesian AI Trading Mentor System, which provides personalized feedback and guidance to users.

``mermaid
sequenceDiagram
participant Client as "Frontend Client"
participant API as "API Route"
participant Controller as "Bot Controller"
participant DB as "Database"
participant Strategy as "Trading Strategy"
participant Broker as "Broker (MT5/Binance/etc.)"
participant AIMentor as "AI Trading Mentor"
Client->>API : POST /api/bots/{id}/start
API->>Controller : start_bot(bot_id)
Controller->>DB : get_bot_by_id(bot_id)
DB-->>Controller : Bot configuration
Controller->>Controller : Create TradingBot instance
Controller->>Controller : Start bot thread
Controller-->>API : Success response
API-->>Client : 200 OK
loop Bot Execution Cycle
TradingBot->>Broker : get_market_data(symbol, timeframe)
Broker-->>TradingBot : Price data (DataFrame)
TradingBot->>Strategy : analyze(df)
Strategy-->>TradingBot : Signal (BUY/SELL/HOLD)
alt Signal is BUY/SELL
TradingBot->>Broker : place_order()
Broker-->>TradingBot : Trade result
TradingBot->>DB : add_history_log()
TradingBot->>DB : log_trade_for_ai_analysis()
end
TradingBot->>TradingBot : sleep(check_interval)
end
Client->>API : GET /ai-mentor/dashboard
API->>DB : get_trading_session_data(today)
API->>DB : get_recent_mentor_reports(7)
API->>AIMentor : generate_daily_report(session)
AIMentor-->>API : AI analysis report
API-->>Client : Render dashboard with AI insights
```

**Diagram sources**
- [core/routes/api_bots.py](file://core/routes/api_bots.py#L1-L167)
- [core/bots/controller.py](file://core/bots/controller.py#L1-L176)
- [core/bots/trading_bot.py](file://core/bots/trading_bot.py#L1-L169)
- [core/brokers/base_broker.py](file://core/brokers/base_broker.py#L100-L150)
- [core/db/queries.py](file://core/db/queries.py#L1-L174)
- [core/routes/ai_mentor.py](file://core/routes/ai_mentor.py#L1-L333)
- [core/ai/trading_mentor_ai.py](file://core/ai/trading_mentor_ai.py#L1-L351)

**Section sources**
- [core/routes/api_bots.py](file://core/routes/api_bots.py#L1-L167)
- [core/bots/controller.py](file://core/bots/controller.py#L1-L176)
- [core/bots/trading_bot.py](file://core/bots/trading_bot.py#L1-L169)
- [core/brokers/base_broker.py](file://core/brokers/base_broker.py)
- [core/routes/ai_mentor.py](file://core/routes/ai_mentor.py)
- [core/ai/trading_mentor_ai.py](file://core/ai/trading_mentor_ai.py)

## Architectural Patterns
The QuantumBotX application implements several key architectural patterns to achieve modularity, extensibility, and maintainability.

### Strategy Pattern
The Strategy pattern is used to implement various trading algorithms. All strategies inherit from the `BaseStrategy` abstract base class, which defines the interface for the `analyze()` method. Concrete strategy classes such as `MACrossoverStrategy`, `RSICrossoverStrategy`, and `BollingerSqueezeStrategy` provide specific implementations. The `STRATEGY_MAP` dictionary in `strategy_map.py` serves as a registry that maps strategy identifiers to their corresponding classes, enabling dynamic strategy selection.

``mermaid
classDiagram
class BaseStrategy {
<<abstract>>
+bot_instance
+params
+analyze(df)*
+get_definable_params()
}
class MACrossoverStrategy {
+analyze(df)
+get_definable_params()
}
class RSICrossoverStrategy {
+analyze(df)
+get_definable_params()
}
class BollingerSqueezeStrategy {
+analyze(df)
+get_definable_params()
}
BaseStrategy <|-- MACrossoverStrategy
BaseStrategy <|-- RSICrossoverStrategy
BaseStrategy <|-- BollingerSqueezeStrategy
```

**Diagram sources**
- [core/strategies/base_strategy.py](file://core/strategies/base_strategy.py#L1-L28)
- [core/strategies/strategy_map.py](file://core/strategies/strategy_map.py#L1-L27)

### Broker Factory Pattern
The application implements a Factory pattern for broker management through the `BrokerFactory` class. This pattern provides a unified interface for creating and managing connections to multiple broker platforms. The factory maintains a registry of broker configurations and instances, allowing for centralized management of broker connections.

``mermaid
classDiagram
class BrokerFactory {
-static _brokers : Dict[str, BaseBroker]
-static _configs : Dict[str, Dict]
+register_broker_config(broker_id, broker_type, config)
+create_broker(broker_id)
+get_broker(broker_id)
+disconnect_all()
+get_all_brokers()
}
class BaseBroker {
<<abstract>>
+broker_name : str
+is_connected : bool
+connect(credentials)
+disconnect()
+get_symbols()
+get_market_data(symbol, timeframe, count)
+place_order(symbol, order_type, side, size, price)
}
class BinanceBroker {
+connect(credentials)
+get_market_data(symbol, timeframe, count)
+place_order(symbol, order_type, side, size, price)
}
class CTraderBroker {
+connect(credentials)
+get_market_data(symbol, timeframe, count)
+place_order(symbol, order_type, side, size, price)
}
class InteractiveBrokersBroker {
+connect(credentials)
+get_market_data(symbol, timeframe, count)
+place_order(symbol, order_type, side, size, price)
}
class TradingViewBroker {
+connect(credentials)
+get_market_data(symbol, timeframe, count)
+place_order(symbol, order_type, side, size, price)
}
BrokerFactory --> "1" BaseBroker : creates/manages
BaseBroker <|-- BinanceBroker
BaseBroker <|-- CTraderBroker
BaseBroker <|-- InteractiveBrokersBroker
BaseBroker <|-- TradingViewBroker
```

**Diagram sources**
- [core/brokers/broker_factory.py](file://core/brokers/broker_factory.py#L35-L141)
- [core/brokers/base_broker.py](file://core/brokers/base_broker.py#L72-L171)

### Singleton Pattern for Bot Management
The application uses a dictionary-based Singleton pattern for managing active bot instances. The `active_bots` dictionary in `controller.py` serves as a central registry that maps bot IDs to their corresponding `TradingBot` thread instances. This pattern ensures that only one instance of each bot exists at any time and provides a global point of access for starting, stopping, and monitoring bots.

``mermaid
classDiagram
class BotController {
-active_bots : dict[int, TradingBot]
+mulai_bot(bot_id)
+hentikan_bot(bot_id)
+get_bot_instance_by_id(bot_id)
}
class TradingBot {
-id : int
-status : str
-_stop_event : Event
+run()
+stop()
+is_stopped()
}
BotController --> "1" TradingBot : manages
BotController --> "1" "active_bots" : uses
```

**Section sources**
- [core/bots/controller.py](file://core/bots/controller.py#L1-L176)
- [core/bots/trading_bot.py](file://core/bots/trading_bot.py#L1-L169)

### AI Mentor Pattern
The application implements a specialized pattern for the Indonesian AI Trading Mentor System, which provides personalized guidance to traders. The `IndonesianTradingMentorAI` class analyzes trading sessions, evaluates risk management, and generates motivational messages in Bahasa Indonesia. This pattern combines emotional intelligence with trading analytics to support trader psychology.

``mermaid
classDiagram
class IndonesianTradingMentorAI {
-personality : str
-language : str
-cultural_context : str
+analyze_trading_session(session)
+generate_daily_report(session)
+_detect_trading_patterns(session)
+_analyze_emotional_impact(session)
+_evaluate_risk_management(session)
+_generate_recommendations(session)
+_create_motivation_message(session)
}
class TradingSession {
-date : date
-trades : List[Dict]
-emotions : str
-market_conditions : str
-profit_loss : float
-notes : str
}
class OllamaClient {
+ask_ollama(prompt, model)
}
IndonesianTradingMentorAI --> "1" TradingSession : analyzes
IndonesianTradingMentorAI --> "1" OllamaClient : uses for advanced AI
```

**Diagram sources**
- [core/ai/trading_mentor_ai.py](file://core/ai/trading_mentor_ai.py#L1-L351)
- [core/ai/ollama_client.py](file://core/ai/ollama_client.py#L1-L14)
- [core/db/models.py](file://core/db/models.py#L1-L262)

### MVC-like Separation
The application follows an MVC-like architectural pattern with clear separation between components:
- **Model**: Database operations in `core/db/queries.py` and entity definitions
- **View**: Frontend templates in `templates/` and static assets in `static/`
- **Controller**: Business logic in `core/bots/controller.py` and API routes in `core/routes/`

This separation allows for independent development and testing of each component while maintaining clear interfaces between layers.

## System Context and Integration Points
The QuantumBotX system integrates with several external components and services to provide its functionality. The primary integration is with multiple trading platforms including MetaTrader 5, Binance, cTrader, Interactive Brokers, and TradingView, which provide market data, trade execution, and account information. The application also uses a SQLite database to persist bot configurations and trading history. Additionally, the system integrates with the Ollama AI framework for enhanced AI capabilities in the trading mentor system.

The system context diagram below illustrates the main components and their interactions:

``mermaid
graph LR
subgraph "External Systems"
MT5[MetaTrader 5 Platform]
Binance[Binance Exchange]
cTrader[cTrader Platform]
IB[Interactive Brokers]
TradingView[TradingView Platform]
Ollama[Ollama AI Framework]
Browser[Web Browser]
end
subgraph "QuantumBotX Application"
Frontend[Frontend UI]
Backend[Flask Backend]
DB[(SQLite Database)]
BrokerFactory[Broker Factory]
AIMentor[AI Trading Mentor]
end
Browser --> Frontend
Frontend --> Backend
Backend --> BrokerFactory
Backend --> AIMentor
BrokerFactory --> MT5
BrokerFactory --> Binance
BrokerFactory --> cTrader
BrokerFactory --> IB
BrokerFactory --> TradingView
AIMentor --> Ollama
Backend --> DB
DB --> Backend
MT5 --> Backend
Binance --> Backend
cTrader --> Backend
IB --> Backend
TradingView --> Backend
Ollama --> AIMentor
```

**Diagram sources**
- [core/brokers/broker_factory.py](file://core/brokers/broker_factory.py)
- [core/brokers/base_broker.py](file://core/brokers/base_broker.py)
- [core/db/queries.py](file://core/db/queries.py#L1-L174)
- [core/utils/mt5.py](file://core/utils/mt5.py#L1-L144)
- [core/ai/ollama_client.py](file://core/ai/ollama_client.py)
- [core/ai/trading_mentor_ai.py](file://core/ai/trading_mentor_ai.py)

**Section sources**
- [core/brokers/broker_factory.py](file://core/brokers/broker_factory.py)
- [core/brokers/base_broker.py](file://core/brokers/base_broker.py)
- [core/db/queries.py](file://core/db/queries.py#L1-L174)
- [core/utils/mt5.py](file://core/utils/mt5.py#L1-L144)
- [core/ai/ollama_client.py](file://core/ai/ollama_client.py)
- [core/ai/trading_mentor_ai.py](file://core/ai/trading_mentor_ai.py)

## Error Handling and Scalability
The application implements comprehensive error handling strategies to ensure reliability in a financial trading context. Each critical operation is wrapped in try-except blocks with appropriate logging. The system distinguishes between recoverable errors (such as temporary connection issues) and fatal errors (such as invalid configurations), allowing for appropriate recovery strategies.

For scalability, the application uses threading to manage multiple trading bots concurrently. Each bot runs in its own thread, allowing for independent execution cycles based on their configured intervals. The `active_bots` dictionary provides a thread-safe mechanism for managing bot lifecycles, with atomic operations for starting and stopping bots.

The multi-broker architecture introduces additional considerations for error handling and scalability:
- **Broker-specific error handling**: Each broker implementation handles platform-specific errors and connection issues
- **Connection resilience**: The BrokerFactory automatically attempts reconnection for disconnected brokers
- **Symbol migration**: The broker_symbol_migrator.py tool automatically detects broker changes and migrates symbol configurations
- **Resource management**: The BrokerFactory manages connection limits and prevents resource exhaustion

The AI mentor system adds new dimensions to error handling and scalability:
- **AI-specific error handling**: The system gracefully handles AI service failures and provides fallback messages
- **Cultural context awareness**: The Indonesian AI Trading Mentor System incorporates cultural context in its guidance
- **Emotional intelligence integration**: The system analyzes trader emotions and provides appropriate motivational messages
- **Personalized feedback**: The system generates personalized recommendations based on individual trading patterns

The architecture supports extensibility through several mechanisms:
- New trading strategies can be added by creating classes that inherit from `BaseStrategy` and registering them in `STRATEGY_MAP`
- Additional broker integrations can be added by creating classes that inherit from `BaseBroker` and registering them in `BrokerFactory`
- Additional API endpoints can be implemented by creating new route files and registering blueprints in the application factory
- The database schema can be extended to support new features while maintaining backward compatibility
- The broker integration layer can be enhanced with additional functionality without affecting the core business logic
- The AI mentor system can be extended with new analysis modules and cultural contexts

These design choices ensure that the QuantumBotX application can evolve to meet changing requirements while maintaining stability and performance.

**Section sources**
- [core/bots/controller.py](file://core/bots/controller.py#L1-L176)
- [core/bots/trading_bot.py](file://core/bots/trading_bot.py#L1-L169)
- [core/utils/logger.py](file://core/utils/logger.py)
- [core/db/queries.py](file://core/db/queries.py#L1-L174)
- [core/brokers/broker_factory.py](file://core/brokers/broker_factory.py)
- [broker_symbol_migrator.py](file://broker_symbol_migrator.py)
- [core/ai/trading_mentor_ai.py](file://core/ai/trading_mentor_ai.py)
- [core/routes/ai_mentor.py](file://core/routes/ai_mentor.py)
- [core/db/models.py](file://core/db/models.py#L1-L262)