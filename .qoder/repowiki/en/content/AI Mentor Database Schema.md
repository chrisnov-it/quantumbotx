# AI Mentor Database Schema

<cite>
**Referenced Files in This Document**   
- [models.py](file://core/db/models.py#L33-L260)
- [init_db.py](file://init_db.py#L125-L175)
- [ai_mentor.py](file://core/routes/ai_mentor.py#L25-L332)
</cite>

## Table of Contents
1. [Introduction](#introduction)
2. [Database Schema Overview](#database-schema-overview)
3. [Trading Sessions Table](#trading-sessions-table)
4. [AI Mentor Reports Table](#ai-mentor-reports-table)
5. [Daily Trading Data Table](#daily-trading-data-table)
6. [Data Relationships and Flow](#data-relationships-and-flow)
7. [Example Queries](#example-queries)
8. [API Integration](#api-integration)

## Introduction
The AI Mentor database schema is designed to capture and analyze trading performance with an emphasis on emotional and behavioral patterns. This documentation details the three core tables—`trading_sessions`, `ai_mentor_reports`, and `daily_trading_data`—that enable the AI mentor system to provide personalized feedback, generate daily reports, and track long-term trading behavior. The schema supports both quantitative trading metrics and qualitative emotional context, allowing for holistic performance analysis.

## Database Schema Overview
The AI Mentor system uses three interconnected tables to store trading session data, AI-generated reports, and detailed trade records. These tables are built on SQLite and are initialized via the `init_db.py` script. The schema is designed to support daily trading analysis, emotional tracking, and AI-driven recommendations.

``mermaid
erDiagram
trading_sessions {
int id PK
date session_date
int user_id FK
int total_trades
float total_profit_loss
string emotions
string market_conditions
string personal_notes
int risk_score
datetime created_at
}
ai_mentor_reports {
int id PK
int session_id FK
text trading_patterns_analysis
text emotional_analysis
int risk_management_score
text recommendations
text motivation_message
string language
datetime created_at
}
daily_trading_data {
int id PK
int session_id FK
int bot_id FK
string symbol
datetime entry_time
datetime exit_time
float profit_loss
float lot_size
boolean stop_loss_used
boolean take_profit_used
float risk_percent
string strategy_used
datetime created_at
}
trading_sessions ||--o{ daily_trading_data : "contains"
trading_sessions ||--o{ ai_mentor_reports : "generates"
```

**Diagram sources**
- [init_db.py](file://init_db.py#L125-L175)

**Section sources**
- [init_db.py](file://init_db.py#L125-L175)

## Trading Sessions Table
The `trading_sessions` table represents a daily trading session and serves as the primary entity for organizing trading data. Each session is uniquely identified by date and user, and contains aggregated performance metrics and emotional context.

### Field Descriptions
- **id**: Primary key, auto-incremented integer
- **session_date**: Date of the trading session (DATE, NOT NULL)
- **user_id**: Foreign key referencing the user (INTEGER, DEFAULT 1)
- **total_trades**: Count of trades executed during the session (INTEGER, DEFAULT 0)
- **total_profit_loss**: Net profit/loss for the session (REAL, DEFAULT 0.0)
- **emotions**: Trader's emotional state during the session (TEXT, DEFAULT 'netral')
- **market_conditions**: Description of market environment (TEXT, DEFAULT 'normal')
- **personal_notes**: Free-form notes from the trader (TEXT)
- **risk_score**: Self-assessed or calculated risk behavior score (INTEGER, DEFAULT 5)
- **created_at**: Timestamp when session was created (DATETIME, DEFAULT CURRENT_TIMESTAMP)

### Key Functions
- **create_trading_session()**: Creates a new session for a given date
- **get_or_create_today_session()**: Retrieves or creates the current day's session
- **update_session_emotions_and_notes()**: Updates emotional state and personal notes

``mermaid
flowchart TD
Start([Start]) --> CheckSession["Check if session exists for today"]
CheckSession --> |Exists| ReturnSession["Return existing session ID"]
CheckSession --> |Not Exists| CreateSession["Create new trading session"]
CreateSession --> InsertDB["INSERT INTO trading_sessions"]
InsertDB --> ReturnNewID["Return new session ID"]
ReturnSession --> End
ReturnNewID --> End
```

**Diagram sources**
- [models.py](file://core/db/models.py#L33-L64)

**Section sources**
- [models.py](file://core/db/models.py#L33-L64)
- [init_db.py](file://init_db.py#L125-L135)

## AI Mentor Reports Table
The `ai_mentor_reports` table stores AI-generated analysis and feedback for each trading session. These reports are generated based on trading patterns, emotional state, and performance metrics.

### Field Descriptions
- **id**: Primary key, auto-incremented integer
- **session_id**: Foreign key referencing trading_sessions.id (INTEGER, NOT NULL)
- **trading_patterns_analysis**: JSON string of trading pattern analysis (TEXT)
- **emotional_analysis**: JSON string of emotion vs. performance correlation (TEXT)
- **risk_management_score**: Numerical score for risk behavior (INTEGER)
- **recommendations**: JSON array of actionable recommendations (TEXT)
- **motivation_message**: Encouraging message from AI mentor (TEXT)
- **language**: Language of the report (TEXT, DEFAULT 'bahasa_indonesia')
- **created_at**: Timestamp when report was generated (DATETIME, DEFAULT CURRENT_TIMESTAMP)

### Key Functions
- **save_ai_mentor_report()**: Persists AI analysis to the database
- **get_recent_mentor_reports()**: Retrieves recent reports for dashboard display

``mermaid
sequenceDiagram
participant Frontend
participant AI_Mentor
participant DB as "Database"
Frontend->>AI_Mentor : Request daily report
AI_Mentor->>DB : get_trading_session_data(today)
DB-->>AI_Mentor : Session data with trades
AI_Mentor->>AI_Mentor : analyze_trading_session()
AI_Mentor->>DB : save_ai_mentor_report(session_id, analysis)
DB-->>AI_Mentor : Success status
AI_Mentor-->>Frontend : Render daily_report.html
```

**Diagram sources**
- [models.py](file://core/db/models.py#L176-L204)
- [ai_mentor.py](file://core/routes/ai_mentor.py#L75-L95)

**Section sources**
- [models.py](file://core/db/models.py#L176-L204)
- [ai_mentor.py](file://core/routes/ai_mentor.py#L75-L95)

## Daily Trading Data Table
The `daily_trading_data` table contains granular details of individual trades executed during a session. This data is used by the AI mentor to analyze trading patterns, strategy effectiveness, and risk management.

### Field Descriptions
- **id**: Primary key, auto-incremented integer
- **session_id**: Foreign key referencing trading_sessions.id (INTEGER, NOT NULL)
- **bot_id**: Foreign key referencing bots.id (INTEGER, NOT NULL)
- **symbol**: Trading instrument (e.g., EUR/USD, BTC/USD) (TEXT, NOT NULL)
- **entry_time**: Trade entry timestamp (DATETIME)
- **exit_time**: Trade exit timestamp (DATETIME)
- **profit_loss**: Profit or loss in account currency (REAL, NOT NULL)
- **lot_size**: Trade size in lots (REAL, NOT NULL)
- **stop_loss_used**: Whether stop loss was triggered (BOOLEAN, DEFAULT 0)
- **take_profit_used**: Whether take profit was triggered (BOOLEAN, DEFAULT 0)
- **risk_percent**: Percentage of account risked (REAL)
- **strategy_used**: Name of trading strategy (TEXT)
- **created_at**: Record creation timestamp (DATETIME, DEFAULT CURRENT_TIMESTAMP)

### Key Functions
- **log_trade_for_ai_analysis()**: Records trade data for AI analysis
- **get_trading_session_data()**: Retrieves session data including associated trades

``mermaid
classDiagram
class DailyTradingData {
+int id
+int session_id
+int bot_id
+string symbol
+datetime entry_time
+datetime exit_time
+float profit_loss
+float lot_size
+bool stop_loss_used
+bool take_profit_used
+float risk_percent
+string strategy_used
+datetime created_at
+log_trade_for_ai_analysis(bot_id, symbol, profit_loss, lot_size, ...)
+get_trading_session_data(session_date)
}
DailyTradingData --> trading_sessions : "belongs to"
DailyTradingData --> bots : "executed by"
```

**Diagram sources**
- [models.py](file://core/db/models.py#L66-L91)
- [init_db.py](file://init_db.py#L165-L175)

**Section sources**
- [models.py](file://core/db/models.py#L66-L91)
- [init_db.py](file://init_db.py#L165-L175)

## Data Relationships and Flow
The three tables form a hierarchical data structure where a trading session contains multiple trades and generates one AI report. The data flow begins with trade execution, continues with session aggregation, and culminates in AI analysis.

``mermaid
flowchart LR
A[Trading Bot Executes Trade] --> B[log_trade_for_ai_analysis]
B --> C[daily_trading_data]
C --> D[get_trading_session_data]
D --> E[AI Mentor Analysis]
E --> F[save_ai_mentor_report]
F --> G[ai_mentor_reports]
G --> H[Web Dashboard Display]
style A fill:#f9f,stroke:#333
style H fill:#bbf,stroke:#333
```

The system ensures data consistency through foreign key constraints and transactional updates. When a trade is logged, it automatically updates the session's total trades and profit/loss metrics.

**Diagram sources**
- [models.py](file://core/db/models.py#L66-L91)
- [ai_mentor.py](file://core/routes/ai_mentor.py#L75-L95)

**Section sources**
- [models.py](file://core/db/models.py#L66-L260)

## Example Queries
The following SQL queries demonstrate common operations on the AI Mentor database schema:

### Create a New Trading Session
```sql
INSERT INTO trading_sessions 
(session_date, emotions, market_conditions, personal_notes) 
VALUES ('2025-01-15', 'tenang', 'volatile', 'Fokus pada risk management');
```

### Log a Trade for AI Analysis
```sql
INSERT INTO daily_trading_data 
(session_id, bot_id, symbol, profit_loss, lot_size, 
stop_loss_used, take_profit_used, risk_percent, strategy_used) 
VALUES (1, 101, 'BTC/USD', 250.50, 0.1, 0, 1, 1.5, 'quantumbotx_crypto');
```

### Generate AI Mentor Report
```sql
INSERT INTO ai_mentor_reports 
(session_id, trading_patterns_analysis, emotional_analysis,
risk_management_score, recommendations, motivation_message) 
VALUES (
  1,
  '{"trend_following": 0.7, "counter_trend": 0.3}',
  '{"fear": 0.2, "greed": 0.6}',
  7,
  '["Tingkatkan disiplin", "Kurangi ukuran posisi"]',
  'Kamu hampir mencapai target bulanan! Teruskan!'
);
```

### Retrieve Today's Session with Trades
```sql
SELECT ts.*, dtd.symbol, dtd.profit_loss, dtd.lot_size
FROM trading_sessions ts
LEFT JOIN daily_trading_data dtd ON ts.id = dtd.session_id
WHERE ts.session_date = date('now')
ORDER BY dtd.created_at;
```

### Get Recent Performance Summary
```sql
SELECT ts.session_date, ts.total_profit_loss, ts.emotions, 
       mr.motivation_message, mr.created_at
FROM trading_sessions ts
LEFT JOIN ai_mentor_reports mr ON ts.id = mr.session_id
ORDER BY ts.session_date DESC
LIMIT 7;
```

**Section sources**
- [models.py](file://core/db/models.py#L33-L260)

## API Integration
The AI Mentor database schema is integrated with the web application through Flask routes in `ai_mentor.py`. These endpoints enable the frontend to retrieve session data, update emotional context, and generate AI reports.

### Key API Endpoints
- **GET /ai-mentor/**: Dashboard displaying recent reports and statistics
- **GET /ai-mentor/today-report**: Detailed AI analysis for current session
- **POST /ai-mentor/update-emotions**: Update emotional state and personal notes
- **GET /ai-mentor/history**: Historical AI mentor reports
- **GET /ai-mentor/session/{date}**: View report for specific date
- **POST /ai-mentor/api/generate-instant-feedback**: Real-time AI feedback

### Data Flow Example
``mermaid
sequenceDiagram
participant User
participant Frontend
participant Backend
participant Database
User->>Frontend : Visit AI Mentor Dashboard
Frontend->>Backend : GET /api/dashboard-summary
Backend->>Database : get_recent_mentor_reports(7)
Database-->>Backend : Return recent reports
Backend->>Backend : Calculate win rate, statistics
Backend-->>Frontend : JSON summary
Frontend->>User : Display dashboard with metrics
User->>Frontend : Update emotions to "serakah"
Frontend->>Backend : POST /update-emotions {emotions : "serakah"}
Backend->>Database : update_session_emotions_and_notes()
Database-->>Backend : Success status
Backend-->>Frontend : Confirmation
Frontend->>User : Show success message
```

The integration ensures that all user interactions with the AI mentor system are persisted in the database and available for future analysis. The system handles missing data gracefully by creating sessions on-demand and providing default values for optional fields.

**Diagram sources**
- [ai_mentor.py](file://core/routes/ai_mentor.py#L25-L332)

**Section sources**
- [ai_mentor.py](file://core/routes/ai_mentor.py#L25-L332)