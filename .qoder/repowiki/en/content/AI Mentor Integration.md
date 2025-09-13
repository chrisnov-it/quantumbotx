# AI Mentor Integration

<cite>
**Referenced Files in This Document**   
- [trading_mentor_ai.py](file://core/ai/trading_mentor_ai.py#L0-L351)
- [ollama_client.py](file://core/ai/ollama_client.py#L0-L14)
- [ai_mentor.py](file://core/routes/ai_mentor.py#L0-L333)
- [models.py](file://core/db/models.py#L0-L262)
- [trading_bot.py](file://core/bots/trading_bot.py#L0-L206)
- [dashboard.html](file://templates/ai_mentor/dashboard.html#L0-L288)
- [daily_report.html](file://templates/ai_mentor/daily_report.html#L0-L150)
- [quick_feedback.html](file://templates/ai_mentor/quick_feedback.html#L0-L100)
</cite>

## Table of Contents
1. [Introduction](#introduction)
2. [Project Structure](#project-structure)
3. [Core Components](#core-components)
4. [Architecture Overview](#architecture-overview)
5. [Detailed Component Analysis](#detailed-component-analysis)
6. [Data Flow and Timing](#data-flow-and-timing)
7. [Dependency Analysis](#dependency-analysis)
8. [Performance Considerations](#performance-considerations)
9. [Troubleshooting Guide](#troubleshooting-guide)
10. [Conclusion](#conclusion)

## Introduction
The AI Mentor Integration system provides personalized trading guidance to users through an AI-powered digital mentor. Designed specifically for beginner traders in Indonesia, this system analyzes trading behavior, emotional state, and risk management practices to deliver culturally relevant feedback in Bahasa Indonesia. The integration connects trading bots, database systems, and web interfaces to create a comprehensive learning and analysis environment that helps users improve their trading skills over time.

## Project Structure
The AI mentor functionality is organized across multiple directories within the QuantumBotX project structure. The core AI logic resides in the `core/ai` directory, while API endpoints are defined in `core/routes`, database models in `core/db`, and bot integration in `core/bots`. Templates for the web interface are located in `templates/ai_mentor`. This modular structure separates concerns while maintaining clear integration points between components.

``mermaid
graph TD
subgraph "AI Core"
A[trading_mentor_ai.py]
B[ollama_client.py]
end
subgraph "API Layer"
C[ai_mentor.py]
end
subgraph "Data Layer"
D[models.py]
E[bots.db]
end
subgraph "Bot Integration"
F[trading_bot.py]
end
subgraph "Web Interface"
G[dashboard.html]
H[daily_report.html]
I[quick_feedback.html]
end
A --> C
C --> D
D --> E
F --> D
C --> G
C --> H
C --> I
```

**Diagram sources**
- [trading_mentor_ai.py](file://core/ai/trading_mentor_ai.py#L0-L351)
- [ai_mentor.py](file://core/routes/ai_mentor.py#L0-L333)
- [models.py](file://core/db/models.py#L0-L262)
- [trading_bot.py](file://core/bots/trading_bot.py#L0-L206)
- [dashboard.html](file://templates/ai_mentor/dashboard.html#L0-L288)

## Core Components
The AI Mentor system consists of several key components that work together to provide personalized trading feedback. The core functionality is implemented in the `IndonesianTradingMentorAI` class, which analyzes trading sessions and generates comprehensive reports. This class is supported by database functions that store and retrieve trading data, API routes that expose the functionality to the web interface, and integration with trading bots that log trading activities.

**Section sources**
- [trading_mentor_ai.py](file://core/ai/trading_mentor_ai.py#L0-L351)
- [models.py](file://core/db/models.py#L0-L262)
- [ai_mentor.py](file://core/routes/ai_mentor.py#L0-L333)

## Architecture Overview
The AI Mentor system follows a layered architecture with clear separation between components. At the core is the AI analysis engine, which processes trading data and generates personalized feedback. This engine is fed by data collected from trading bots and stored in a SQLite database. The results are exposed through Flask API routes and rendered in web templates for user consumption.

``mermaid
graph TD
A[Trading Bot] --> |Logs trades| B[Database]
B --> |Provides data| C[AI Mentor Engine]
C --> |Generates analysis| B
C --> |Provides reports| D[API Routes]
D --> |Serves data| E[Web Templates]
E --> |Displays| F[User Interface]
G[User] --> |Updates emotions| D
D --> |Stores| B
```

**Diagram sources**
- [trading_bot.py](file://core/bots/trading_bot.py#L0-L206)
- [models.py](file://core/db/models.py#L0-L262)
- [trading_mentor_ai.py](file://core/ai/trading_mentor_ai.py#L0-L351)
- [ai_mentor.py](file://core/routes/ai_mentor.py#L0-L333)

## Detailed Component Analysis

### AI Mentor Engine Analysis
The AI Mentor Engine is implemented in the `IndonesianTradingMentorAI` class, which provides personalized trading feedback in Bahasa Indonesia. The engine analyzes trading sessions across multiple dimensions including trading patterns, emotional impact, risk management, and provides specific recommendations and motivational messages.

#### Class Diagram
``mermaid
classDiagram
class IndonesianTradingMentorAI {
+personality : str
+language : str
+cultural_context : str
+analyze_trading_session(session) Dict[str, Any]
+_detect_trading_patterns(session) Dict[str, str]
+_analyze_emotional_impact(session) Dict[str, str]
+_evaluate_risk_management(session) Dict[str, str]
+_generate_recommendations(session) List[str]
+_create_motivation_message(session) str
+generate_daily_report(session) str
}
class TradingSession {
+date : date
+trades : List[Dict]
+emotions : str
+market_conditions : str
+profit_loss : float
+notes : str
}
class IndonesianTradingMentorAI --> TradingSession : "analyzes"
```

**Diagram sources**
- [trading_mentor_ai.py](file://core/ai/trading_mentor_ai.py#L0-L351)

**Section sources**
- [trading_mentor_ai.py](file://core/ai/trading_mentor_ai.py#L0-L351)

### Database Integration Analysis
The database integration layer handles the storage and retrieval of trading session data for AI analysis. It includes functions for creating trading sessions, logging trade data, and retrieving session information for analysis. The system uses SQLite as the database backend and maintains several related tables for storing comprehensive trading data.

#### Database Functions Flowchart
``mermaid
flowchart TD
Start([Start]) --> CreateSession["create_trading_session()"]
CreateSession --> GetOrCreate["get_or_create_today_session()"]
GetOrCreate --> LogTrade["log_trade_for_ai_analysis()"]
LogTrade --> UpdateSummary["Update session summary"]
UpdateSummary --> SaveData["Save to daily_trading_data table"]
SaveData --> Retrieve["get_trading_session_data()"]
Retrieve --> ReturnData["Return structured session data"]
ReturnData --> End([End])
```

**Diagram sources**
- [models.py](file://core/db/models.py#L0-L262)

**Section sources**
- [models.py](file://core/db/models.py#L0-L262)

### API Routes Analysis
The API routes provide the interface between the backend AI mentor system and the frontend web interface. These routes handle requests for dashboard data, daily reports, historical data, and user input for emotions and notes. The routes are implemented as a Flask blueprint and integrate with both the AI engine and database functions.

#### API Request Flow
``mermaid
sequenceDiagram
participant User as "User Browser"
participant Route as "ai_mentor.py"
participant DB as "Database"
participant AI as "TradingMentorAI"
User->>Route : GET /ai-mentor/
Route->>DB : get_trading_session_data(today)
DB-->>Route : Session data
Route->>DB : get_recent_mentor_reports(7)
DB-->>Route : Recent reports
Route->>User : Render dashboard.html
User->>Route : GET /ai-mentor/today-report
Route->>DB : get_trading_session_data(today)
DB-->>Route : Session data
Route->>AI : generate_daily_report(session)
AI-->>Route : AI report
Route->>DB : save_ai_mentor_report()
DB-->>Route : Success
Route->>User : Render daily_report.html
```

**Diagram sources**
- [ai_mentor.py](file://core/routes/ai_mentor.py#L0-L333)

**Section sources**
- [ai_mentor.py](file://core/routes/ai_mentor.py#L0-L333)

### Trading Bot Integration Analysis
The trading bot integration is responsible for logging trading activities to the database for subsequent AI analysis. When a trade is closed, the bot captures relevant data including profit/loss, lot size, risk percentage, and strategy used, then logs this information through the database interface.

#### Trade Logging Sequence
``mermaid
sequenceDiagram
participant Bot as "TradingBot"
participant DB as "Database"
Bot->>Bot : _handle_trade_signal()
alt Close Position
Bot->>Bot : Calculate profit_loss
Bot->>Bot : Determine stop_loss_used, take_profit_used
Bot->>DB : log_trade_for_ai_analysis()
DB-->>Bot : Success
end
Bot->>Bot : Continue trading loop
```

**Diagram sources**
- [trading_bot.py](file://core/bots/trading_bot.py#L0-L206)
- [models.py](file://core/db/models.py#L0-L262)

**Section sources**
- [trading_bot.py](file://core/bots/trading_bot.py#L0-L206)

### Web Interface Analysis
The web interface presents AI mentor analysis to users through several HTML templates. The dashboard provides an overview of recent trading activity and AI insights, while the daily report shows a comprehensive analysis of a specific trading session. A quick feedback modal allows users to update their emotional state and trading notes.

#### Template Structure
``mermaid
graph TD
A[dashboard.html] --> B[Base Template]
A --> C[Quick Stats Cards]
A --> D[Today's Trading Section]
A --> E[AI Insights Section]
A --> F[Floating Chat Button]
G[daily_report.html] --> B
G --> H[Comprehensive AI Report]
G --> I[Formatted Analysis Sections]
G --> J[Emotion and Notes Display]
K[quick_feedback.html] --> B
K --> L[Emotion Selection]
K --> M[Notes Input]
K --> N[Submit Button]
```

**Diagram sources**
- [dashboard.html](file://templates/ai_mentor/dashboard.html#L0-L288)
- [daily_report.html](file://templates/ai_mentor/daily_report.html#L0-L150)
- [quick_feedback.html](file://templates/ai_mentor/quick_feedback.html#L0-L100)

**Section sources**
- [dashboard.html](file://templates/ai_mentor/dashboard.html#L0-L288)
- [daily_report.html](file://templates/ai_mentor/daily_report.html#L0-L150)
- [quick_feedback.html](file://templates/ai_mentor/quick_feedback.html#L0-L100)

## Data Flow and Timing

### Data Collection Process
The AI mentor system collects data through a well-defined process that begins with trading bot activities and ends with comprehensive AI analysis. The data flow follows a specific sequence and timing pattern to ensure accurate and timely feedback for users.

#### Data Flow Diagram
``mermaid
flowchart LR
A[Trading Bot Executes Trade] --> B[Bot Closes Position]
B --> C[Bot Logs Trade Data to Database]
C --> D[Data Stored in daily_trading_data Table]
D --> E[User Requests Daily Report]
E --> F[API Retrieves Session Data from Database]
F --> G[AI Mentor Analyzes Trading Session]
G --> H[AI Generates Comprehensive Report]
H --> I[Report Saved to ai_mentor_reports Table]
I --> J[Report Displayed to User in Web Interface]
```

**Diagram sources**
- [trading_bot.py](file://core/bots/trading_bot.py#L0-L206)
- [models.py](file://core/db/models.py#L0-L262)
- [trading_mentor_ai.py](file://core/ai/trading_mentor_ai.py#L0-L351)
- [ai_mentor.py](file://core/routes/ai_mentor.py#L0-L333)

**Section sources**
- [trading_bot.py](file://core/bots/trading_bot.py#L0-L206)
- [models.py](file://core/db/models.py#L0-L262)

### Timing of Data Collection
The timing of data collection and analysis follows a specific pattern based on user actions and system events:

1. **Real-time logging**: Trade data is logged immediately when a position is closed by the trading bot.
2. **On-demand analysis**: AI analysis is performed when a user requests the daily report, not automatically at the end of the day.
3. **Session creation**: A trading session is created when the first trade of the day is logged or when the user first accesses the AI mentor dashboard.

This approach ensures that data is captured as it happens while allowing users to control when the AI analysis is generated, giving them the opportunity to update their emotional state and add personal notes before the analysis is performed.

## Dependency Analysis
The AI mentor system has a well-defined dependency structure that ensures modularity while maintaining necessary integration points. The core AI engine has no external dependencies beyond standard Python libraries, while the API routes depend on both the AI engine and database functions. The trading bot depends on the database functions for logging, and all web templates depend on the API routes for data.

``mermaid
graph LR
A[trading_bot.py] --> B[models.py]
C[ai_mentor.py] --> B
C --> D[trading_mentor_ai.py]
B --> E[bots.db]
C --> F[dashboard.html]
C --> G[daily_report.html]
C --> H[quick_feedback.html]
```

**Diagram sources**
- [trading_bot.py](file://core/bots/trading_bot.py#L0-L206)
- [ai_mentor.py](file://core/routes/ai_mentor.py#L0-L333)
- [models.py](file://core/db/models.py#L0-L262)
- [trading_mentor_ai.py](file://core/ai/trading_mentor_ai.py#L0-L351)

**Section sources**
- [trading_bot.py](file://core/bots/trading_bot.py#L0-L206)
- [ai_mentor.py](file://core/routes/ai_mentor.py#L0-L333)
- [models.py](file://core/db/models.py#L0-L262)

## Performance Considerations
The AI mentor system is designed with performance in mind, particularly considering that it operates in a trading environment where timely feedback is valuable. The system uses several strategies to ensure good performance:

1. **Lazy analysis**: AI analysis is performed on-demand rather than automatically at the end of each day, reducing unnecessary computation.
2. **Efficient database queries**: The database functions are designed to retrieve only the necessary data for each operation.
3. **Caching**: Recent reports are retrieved in batches to minimize database queries.
4. **Simple AI model**: The AI mentor uses rule-based analysis rather than complex machine learning models, ensuring fast response times.

The system is optimized for the typical usage pattern where users check their AI mentor dashboard once or twice per day, generating a comprehensive report when needed.

## Troubleshooting Guide
When issues occur with the AI mentor integration, they typically fall into one of several categories. This guide provides steps to diagnose and resolve common problems.

**Section sources**
- [trading_bot.py](file://core/bots/trading_bot.py#L0-L206)
- [models.py](file://core/db/models.py#L0-L262)
- [ai_mentor.py](file://core/routes/ai_mentor.py#L0-L333)
- [trading_mentor_ai.py](file://core/ai/trading_mentor_ai.py#L0-L351)

### Common Issues and Solutions

1. **No data in AI mentor dashboard**
   - Verify that trading bots are active and executing trades
   - Check that the `bots.db` database file exists and is writable
   - Ensure that the `daily_trading_data` and `trading_sessions` tables have been created

2. **AI report not generating**
   - Confirm that there is trading data for the requested date
   - Check server logs for errors in the `ai_mentor.py` routes
   - Verify that the `IndonesianTradingMentorAI` class is properly instantiated

3. **Emotions and notes not saving**
   - Check that the `update_session_emotions_and_notes` function is being called correctly
   - Verify database permissions and table structure
   - Ensure the session date matches the current date

4. **Performance issues with report generation**
   - Monitor database size and consider archiving old data
   - Check for inefficient queries in the database functions
   - Verify that the AI analysis is only performed when explicitly requested

## Conclusion
The AI Mentor Integration system provides a comprehensive solution for delivering personalized trading feedback to users. By collecting data from trading bots, analyzing it through a culturally-aware AI engine, and presenting insights through an intuitive web interface, the system helps users improve their trading skills over time. The modular architecture ensures maintainability and scalability, while the on-demand analysis approach balances timely feedback with computational efficiency. This integration represents a significant value-add for the QuantumBotX platform, transforming it from a simple trading bot system into a comprehensive learning and development environment for traders.