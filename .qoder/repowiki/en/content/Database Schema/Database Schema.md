# Database Schema

<cite>
**Referenced Files in This Document**   
- [init_db.py](file://init_db.py) - *Updated with AI mentor system tables in commit a24fa86*
- [core/db/models.py](file://core/db/models.py) - *Added AI mentor database functions in commit a24fa86*
- [core/routes/ai_mentor.py](file://core/routes/ai_mentor.py) - *AI mentor web interface implementation*
- [core/ai/trading_mentor_ai.py](file://core/ai/trading_mentor_ai.py) - *AI mentor logic and analysis implementation*
</cite>

## Update Summary
**Changes Made**   
- Added comprehensive documentation for the new AI mentor system database tables
- Updated entity relationship model to include new entities and relationships
- Added new sections for trading_sessions, ai_mentor_reports, and daily_trading_data tables
- Updated database initialization process to reflect new table creation
- Enhanced data access patterns section with AI mentor system interactions
- Added security considerations for the new AI mentor functionality

## Table of Contents
1. [Introduction](#introduction)
2. [Database Initialization Process](#database-initialization-process)
3. [Entity Relationship Model](#entity-relationship-model)
4. [Table Definitions](#table-definitions)
   - [users](#users)
   - [bots](#bots)
   - [trade_history](#trade_history)
   - [backtest_results](#backtest_results)
   - [trading_sessions](#trading_sessions)
   - [ai_mentor_reports](#ai_mentor_reports)
   - [daily_trading_data](#daily_trading_data)
5. [Data Access Patterns](#data-access-patterns)
6. [Query Optimization and Performance](#query-optimization-and-performance)
7. [Data Lifecycle and Retention](#data-lifecycle-and-retention)
8. [Security Considerations](#security-considerations)

## Introduction
This document provides comprehensive documentation for the quantumbotx database schema, which supports an automated trading system. The database stores information about trading bots, their activities, backtesting results, user profiles, and now includes a revolutionary AI mentor system for Indonesian traders. Built on SQLite, the schema is designed for simplicity, reliability, and efficient data retrieval for both real-time trading operations and historical analysis. This documentation details all entities, their relationships, field definitions, constraints, and access patterns to ensure proper understanding and maintenance of the system.

## Database Initialization Process

The database schema is initialized through the `init_db.py` script, which creates all necessary tables and inserts default user data. The process is idempotent, using `CREATE TABLE IF NOT EXISTS` statements to prevent errors when the script is run multiple times. With the recent addition of the AI mentor system, three new tables have been added: `trading_sessions`, `ai_mentor_reports`, and `daily_trading_data`.

``mermaid
flowchart TD
Start([Start]) --> CheckForce["Check for --force flag"]
CheckForce --> DeleteDB{"--force flag present?"}
DeleteDB --> |Yes| RemoveFile["Remove existing bots.db file"]
DeleteDB --> |No| ConnectDB["Create connection to bots.db"]
RemoveFile --> ConnectDB
ConnectDB --> CreateTable["Create tables: users, bots, trade_history, backtest_results"]
CreateTable --> CreateAISessions["Create AI mentor tables: trading_sessions, ai_mentor_reports, daily_trading_data"]
CreateAISessions --> InsertUser["Insert default admin user"]
InsertUser --> CloseConn["Close database connection"]
CloseConn --> End([Initialization Complete])
style Start fill:#4CAF50,stroke:#388E3C
style End fill:#4CAF50,stroke:#388E3C
```

**Diagram sources**
- [init_db.py](file://init_db.py#L0-L198)

**Section sources**
- [init_db.py](file://init_db.py#L0-L198)

## Entity Relationship Model

The quantumbotx database consists of seven primary entities with well-defined relationships. The `users` table stores application user information. The `bots` table contains configurations for automated trading bots, each associated with a user. The `trade_history` table logs all actions and events related to each bot, forming a chronological record of bot activity. The `backtest_results` table stores the outcomes of strategy backtesting simulations, allowing for performance analysis without risking real capital.

The new AI mentor system introduces three additional tables. The `trading_sessions` table represents daily trading sessions for users, capturing emotional and market context. The `daily_trading_data` table records individual trades within each session for AI analysis. The `ai_mentor_reports` table stores comprehensive AI-generated reports that analyze trading patterns, emotional impact, and risk management, providing personalized recommendations and motivational messages.

``mermaid
erDiagram
users {
INTEGER id PK
TEXT name NOT NULL
TEXT email NOT NULL UK
TEXT password_hash NOT NULL
DATETIME join_date
}
bots {
INTEGER id PK
TEXT name NOT NULL
TEXT market NOT NULL
TEXT status NOT NULL
REAL lot_size NOT NULL
INTEGER sl_pips NOT NULL
INTEGER tp_pips NOT NULL
TEXT timeframe NOT NULL
INTEGER check_interval_seconds NOT NULL
TEXT strategy NOT NULL
TEXT strategy_params
}
trade_history {
INTEGER id PK
INTEGER bot_id FK NOT NULL
DATETIME timestamp
TEXT action NOT NULL
TEXT details
INTEGER is_notification NOT NULL
INTEGER is_read NOT NULL
}
backtest_results {
INTEGER id PK
DATETIME timestamp
TEXT strategy_name NOT NULL
TEXT data_filename NOT NULL
REAL total_profit_usd NOT NULL
INTEGER total_trades NOT NULL
REAL win_rate_percent NOT NULL
REAL max_drawdown_percent NOT NULL
INTEGER wins NOT NULL
INTEGER losses NOT NULL
TEXT equity_curve
TEXT trade_log
TEXT parameters
}
trading_sessions {
INTEGER id PK
DATE session_date NOT NULL
INTEGER user_id FK
INTEGER total_trades NOT NULL
REAL total_profit_loss NOT NULL
TEXT emotions NOT NULL
TEXT market_conditions NOT NULL
TEXT personal_notes
INTEGER risk_score
DATETIME created_at
}
ai_mentor_reports {
INTEGER id PK
INTEGER session_id FK NOT NULL
TEXT trading_patterns_analysis
TEXT emotional_analysis
INTEGER risk_management_score
TEXT recommendations
TEXT motivation_message
TEXT language
DATETIME created_at
}
daily_trading_data {
INTEGER id PK
INTEGER session_id FK NOT NULL
INTEGER bot_id FK NOT NULL
TEXT symbol NOT NULL
DATETIME entry_time
DATETIME exit_time
REAL profit_loss NOT NULL
REAL lot_size NOT NULL
BOOLEAN stop_loss_used
BOOLEAN take_profit_used
REAL risk_percent
TEXT strategy_used
DATETIME created_at
}
users ||--o{ bots : "owns"
bots ||--o{ trade_history : "generates"
users ||--o{ trading_sessions : "has"
trading_sessions ||--o{ ai_mentor_reports : "receives"
trading_sessions ||--o{ daily_trading_data : "contains"
bots ||--o{ daily_trading_data : "generates"
```

**Diagram sources**
- [init_db.py](file://init_db.py#L40-L198)
- [core/db/models.py](file://core/db/models.py#L0-L261)

## Table Definitions

### users
The `users` table stores application user profiles, including authentication credentials and registration information.

**Field Definitions:**
- `id`: Primary key, auto-incrementing integer identifier
- `name`: User's full name, required field
- `email`: User's email address, required and unique
- `password_hash`: Secure hash of user's password using Werkzeug's generate_password_hash
- `join_date`: Timestamp of account creation, defaults to current time

**Constraints:**
- Primary Key: `id`
- Unique Constraint: `email`
- NOT NULL constraints on `name`, `email`, and `password_hash`

**Sample Data Record:**
```json
{
  "id": 1,
  "name": "Admin User",
  "email": "admin@quantumbotx.com",
  "join_date": "2025-01-15 10:30:00"
}
```

**Section sources**
- [init_db.py](file://init_db.py#L40-L47)
- [core/routes/api_profile.py](file://core/routes/api_profile.py#L0-L38)

### bots
The `bots` table stores configuration data for automated trading bots, defining their behavior and trading parameters.

**Field Definitions:**
- `id`: Primary key, auto-incrementing integer identifier
- `name`: Bot name, required field
- `market`: Trading market (e.g., "EURUSD", "XAUUSD"), required
- `status`: Current status ("Aktif" or "Dijeda"), defaults to "Dijeda"
- `lot_size`: Trade lot size in units, defaults to 0.01
- `sl_pips`: Stop loss distance in pips, defaults to 100
- `tp_pips`: Take profit distance in pips, defaults to 200
- `timeframe`: Chart timeframe (e.g., "H1", "M15"), defaults to "H1"
- `check_interval_seconds`: Frequency of market analysis in seconds, defaults to 60
- `strategy`: Name of the trading strategy implementation
- `strategy_params`: JSON string containing strategy-specific parameters

**Constraints:**
- Primary Key: `id`
- NOT NULL constraints on all fields except `strategy_params`
- Default values for `status`, `lot_size`, `sl_pips`, `tp_pips`, `timeframe`, and `check_interval_seconds`

**Sample Data Record:**
```json
{
  "id": 1,
  "name": "EURUSD Scalper",
  "market": "EURUSD",
  "status": "Aktif",
  "lot_size": 0.1,
  "sl_pips": 15,
  "tp_pips": 30,
  "timeframe": "M15",
  "check_interval_seconds": 30,
  "strategy": "ma_crossover",
  "strategy_params": "{\"fast_period\": 9, \"slow_period\": 21}"
}
```

**Section sources**
- [init_db.py](file://init_db.py#L49-L58)
- [core/db/queries.py](file://core/db/queries.py#L0-L68)

### trade_history
The `trade_history` table logs all activities and events related to trading bots, serving as an audit trail and notification system.

**Field Definitions:**
- `id`: Primary key, auto-incrementing integer identifier
- `bot_id`: Foreign key referencing the bots table, required
- `timestamp`: Date and time of the event, defaults to current time
- `action`: Type of action (e.g., "POSISI DIBUKA", "POSISI DITUTUP")
- `details`: Additional information about the event
- `is_notification`: Flag indicating if the entry should trigger a user notification (0 or 1)
- `is_read`: Flag indicating if the notification has been read by the user (0 or 1)

**Constraints:**
- Primary Key: `id`
- Foreign Key: `bot_id` references `bots(id)` with CASCADE DELETE
- NOT NULL constraints on `bot_id`, `action`, `is_notification`, and `is_read`
- Default values for `timestamp`, `is_notification`, and `is_read`

**Sample Data Record:**
```json
{
  "id": 101,
  "bot_id": 1,
  "timestamp": "2025-01-15 14:25:30",
  "action": "POSISI DIBUKA",
  "details": "Buy position opened at 1.0850, volume: 0.1",
  "is_notification": 1,
  "is_read": 0
}
```

**Section sources**
- [init_db.py](file://init_db.py#L68-L78)
- [core/db/queries.py](file://core/db/queries.py#L70-L102)
- [core/db/models.py](file://core/db/models.py#L0-L19)

### backtest_results
The `backtest_results` table stores the outcomes of strategy backtesting simulations, enabling performance evaluation and optimization.

**Field Definitions:**
- `id`: Primary key, auto-incrementing integer identifier
- `timestamp`: Date and time of the backtest execution, defaults to current time
- `strategy_name`: Name of the tested strategy
- `data_filename`: Name of the historical data file used
- `total_profit_usd`: Total profit in USD from the simulation
- `total_trades`: Number of trades executed during backtest
- `win_rate_percent`: Percentage of winning trades
- `max_drawdown_percent`: Maximum drawdown percentage during simulation
- `wins`: Number of winning trades
- `losses`: Number of losing trades
- `equity_curve`: JSON array of equity values over time
- `trade_log`: JSON array of individual trade records
- `parameters`: JSON object of strategy parameters used

**Constraints:**
- Primary Key: `id`
- NOT NULL constraints on `strategy_name`, `data_filename`, `total_profit_usd`, `total_trades`, `win_rate_percent`, `max_drawdown_percent`, `wins`, and `losses`

**Sample Data Record:**
```json
{
  "id": 50,
  "timestamp": "2025-01-15 11:45:20",
  "strategy_name": "Pulse Sync",
  "data_filename": "EURUSD_H1_2024.csv",
  "total_profit_usd": 2450.75,
  "total_trades": 89,
  "win_rate_percent": 62.4,
  "max_drawdown_percent": 18.7,
  "wins": 56,
  "losses": 33,
  "equity_curve": "[10000, 10150, 10080, ...]",
  "trade_log": "[{\"entry_price\": 1.0850, \"exit_price\": 1.0880, \"profit\": 30}, ...]",
  "parameters": "{\"trend_period\": 100, \"macd_fast\": 12, \"macd_slow\": 26}"
}
```

**Section sources**
- [init_db.py](file://init_db.py#L80-L114)
- [core/routes/api_backtest.py](file://core/routes/api_backtest.py#L25-L57)
- [core/routes/api_backtest.py](file://core/routes/api_backtest.py#L85-L130)

### trading_sessions
The `trading_sessions` table represents daily trading sessions for users, capturing the emotional and market context of trading activities. This table is central to the AI mentor system, enabling personalized analysis and feedback.

**Field Definitions:**
- `id`: Primary key, auto-incrementing integer identifier
- `session_date`: Date of the trading session, required and unique per user
- `user_id`: Foreign key referencing the users table, defaults to 1 (single user system)
- `total_trades`: Number of trades executed during the session, defaults to 0
- `total_profit_loss`: Cumulative profit or loss for the session, defaults to 0.0
- `emotions`: Trader's emotional state during the session (e.g., "tenang", "serakah", "takut", "frustasi"), defaults to "netral"
- `market_conditions`: Description of market conditions (e.g., "normal", "trending", "sideways"), defaults to "normal"
- `personal_notes`: Trader's personal notes about the session
- `risk_score`: Numerical score (1-10) representing risk management quality, defaults to 5
- `created_at`: Timestamp when the session was created, defaults to current time

**Constraints:**
- Primary Key: `id`
- Foreign Key: `user_id` references `users(id)` with CASCADE DELETE
- NOT NULL constraints on `session_date`, `total_trades`, `total_profit_loss`, `emotions`, and `market_conditions`
- Default values for `user_id`, `total_trades`, `total_profit_loss`, `emotions`, `market_conditions`, `risk_score`, and `created_at`
- Unique constraint on the combination of `session_date` and `user_id` to prevent duplicate daily sessions

**Sample Data Record:**
```json
{
  "id": 1,
  "session_date": "2025-01-15",
  "user_id": 1,
  "total_trades": 5,
  "total_profit_loss": 77.70,
  "emotions": "tenang",
  "market_conditions": "trending",
  "personal_notes": "Fokus pada EURUSD dan XAUUSD. Pakai stop loss ketat dan lot size kecil. Alhamdulillah profit!",
  "risk_score": 8,
  "created_at": "2025-01-15 09:00:00"
}
```

**Section sources**
- [init_db.py](file://init_db.py#L116-L135)
- [core/db/models.py](file://core/db/models.py#L33-L64)
- [core/routes/ai_mentor.py](file://core/routes/ai_mentor.py#L0-L315)

### ai_mentor_reports
The `ai_mentor_reports` table stores comprehensive AI-generated reports that analyze trading patterns, emotional impact, and risk management. These reports provide personalized recommendations and motivational messages in Bahasa Indonesia, creating a supportive mentoring experience.

**Field Definitions:**
- `id`: Primary key, auto-incrementing integer identifier
- `session_id`: Foreign key referencing the trading_sessions table, required
- `trading_patterns_analysis`: JSON string containing analysis of trading patterns and behaviors
- `emotional_analysis`: JSON string containing analysis of emotional impact on trading performance
- `risk_management_score`: Integer score representing the quality of risk management during the session
- `recommendations`: JSON string containing personalized trading recommendations and tips
- `motivation_message`: Text field containing motivational messages to encourage the trader
- `language`: Language of the report, defaults to "bahasa_indonesia"
- `created_at`: Timestamp when the report was generated, defaults to current time

**Constraints:**
- Primary Key: `id`
- Foreign Key: `session_id` references `trading_sessions(id)` with CASCADE DELETE
- NOT NULL constraints on `session_id`
- Default values for `language` and `created_at`

**Sample Data Record:**
```json
{
  "id": 1,
  "session_id": 1,
  "trading_patterns_analysis": "{\"pola_utama\": \"Trading Disiplin\", \"analisis\": \"Bagus! Anda berhasil profit $77.70 hari ini. Saya melihat Anda mengikuti aturan dengan baik.\", \"kekuatan\": \"Konsisten dengan strategi yang dipilih\", \"area_perbaikan\": \"Pertahankan kedisiplinan ini\"}",
  "emotional_analysis": "{\"feedback\": \"Luar biasa! Emosi yang tenang menghasilkan keputusan trading yang objektif.\", \"tip\": \"Pertahankan ketenangan ini. Ini adalah kunci trader profesional.\"}",
  "risk_management_score": 8,
  "recommendations": "[\"- Profit bagus! Jangan serakah, ambil sebagian profit untuk disyukuri.\", \"- Pertahankan strategi yang sama, jangan ganti-ganti.\", \"- Dokumentasikan apa yang membuat Anda sukses hari ini.\"]",
  "motivation_message": "Luar biasa! Anda sudah menunjukkan potensi trader yang hebat! 🚀\\n\\n🎯 **Ingat Journey Anda:** Dari awalnya ikut mentor yang hilang kontak, sekarang Anda sudah bisa trading mandiri dengan sistem sendiri!",
  "language": "bahasa_indonesia",
  "created_at": "2025-01-15 18:30:00"
}
```

**Section sources**
- [init_db.py](file://init_db.py#L136-L154)
- [core/db/models.py](file://core/db/models.py#L176-L207)
- [core/ai/trading_mentor_ai.py](file://core/ai/trading_mentor_ai.py#L0-L350)

### daily_trading_data
The `daily_trading_data` table records individual trades within each trading session for AI analysis. This granular data enables the AI mentor system to provide detailed feedback on trading behavior, risk management, and performance patterns.

**Field Definitions:**
- `id`: Primary key, auto-incrementing integer identifier
- `session_id`: Foreign key referencing the trading_sessions table, required
- `bot_id`: Foreign key referencing the bots table, required
- `symbol`: Trading symbol (e.g., "EURUSD", "XAUUSD"), required
- `entry_time`: Timestamp of trade entry
- `exit_time`: Timestamp of trade exit
- `profit_loss`: Profit or loss amount from the trade, required
- `lot_size`: Trade lot size, required
- `stop_loss_used`: Boolean flag indicating if stop loss was triggered (0 or 1), defaults to 0
- `take_profit_used`: Boolean flag indicating if take profit was triggered (0 or 1), defaults to 0
- `risk_percent`: Percentage of account risked on the trade
- `strategy_used`: Name of the trading strategy used for this trade
- `created_at`: Timestamp when the record was created, defaults to current time

**Constraints:**
- Primary Key: `id`
- Foreign Key: `session_id` references `trading_sessions(id)` with CASCADE DELETE
- Foreign Key: `bot_id` references `bots(id)` with CASCADE DELETE
- NOT NULL constraints on `session_id`, `bot_id`, `symbol`, `profit_loss`, and `lot_size`
- Default values for `stop_loss_used`, `take_profit_used`, and `created_at`

**Sample Data Record:**
```json
{
  "id": 1,
  "session_id": 1,
  "bot_id": 1,
  "symbol": "EURUSD",
  "entry_time": "2025-01-15 10:30:00",
  "exit_time": "2025-01-15 12:45:00",
  "profit_loss": 45.50,
  "lot_size": 0.01,
  "stop_loss_used": 1,
  "take_profit_used": 0,
  "risk_percent": 1.0,
  "strategy_used": "ma_crossover",
  "created_at": "2025-01-15 12:45:00"
}
```

**Section sources**
- [init_db.py](file://init_db.py#L155-L175)
- [core/db/models.py](file://core/db/models.py#L65-L92)
- [core/routes/ai_mentor.py](file://core/routes/ai_mentor.py#L0-L315)

## Data Access Patterns

The application follows a service-layer pattern for database access, with dedicated query functions in `core/db/models.py` that encapsulate all database operations. This ensures consistent error handling and prevents SQL injection through parameterized queries. The AI mentor system introduces new data access patterns focused on daily session management and AI-driven analysis.

``mermaid
sequenceDiagram
participant Frontend
participant API as API Route
participant Models as models.py
participant DB as Database
Frontend->>API : GET /ai-mentor/today-report
API->>Models : get_trading_session_data(today)
Models->>DB : SELECT * FROM trading_sessions WHERE session_date = ?
DB-->>Models : Return session data
Models->>DB : SELECT * FROM daily_trading_data WHERE session_id = ?
DB-->>Models : Return trade records
Models-->>API : Return session with trades
API->>Models : generate_daily_report(session)
Models->>Models : Analyze trading patterns and emotions
Models->>Models : Evaluate risk management
Models->>Models : Generate recommendations
Models->>Models : Create motivational message
Models-->>API : Return AI report
API->>Models : save_ai_mentor_report(session_id, analysis)
Models->>DB : INSERT INTO ai_mentor_reports VALUES (...)
DB-->>Models : Confirm insertion
Models-->>API : Return success
API-->>Frontend : Return AI mentor report
```

**Diagram sources**
- [core/db/models.py](file://core/db/models.py#L0-L261)
- [core/routes/ai_mentor.py](file://core/routes/ai_mentor.py#L0-L315)
- [core/ai/trading_mentor_ai.py](file://core/ai/trading_mentor_ai.py#L0-L350)

**Section sources**
- [core/db/models.py](file://core/db/models.py#L0-L261)
- [core/routes/ai_mentor.py](file://core/routes/ai_mentor.py#L0-L315)

## Query Optimization and Performance

The database schema includes several performance considerations for handling large datasets, particularly in the `trade_history`, `backtest_results`, and `daily_trading_data` tables which can grow significantly over time.

**Indexing Strategy:**
While the current schema does not explicitly define indexes in the DDL statements, optimal performance would require the following indexes:
- Index on `trade_history(bot_id, timestamp)` for efficient retrieval of bot-specific history
- Index on `backtest_results(timestamp)` for chronological sorting of results
- Index on `bots(status)` to quickly identify active bots
- Index on `trading_sessions(session_date, user_id)` for efficient daily session lookup
- Index on `daily_trading_data(session_id)` for retrieving all trades in a session
- Index on `ai_mentor_reports(session_id)` for retrieving reports by session

**Query Optimization Techniques:**
- All queries use parameterized statements to prevent SQL injection and enable query plan caching
- The `get_history_by_bot_id` function includes an ORDER BY clause to return results in reverse chronological order
- The `get_all_backtest_history` function retrieves all records with a DESC sort on timestamp
- JSON fields (`equity_curve`, `trade_log`, `parameters`, `trading_patterns_analysis`, `emotional_analysis`, `recommendations`) are parsed in the application layer to avoid complex SQL operations on serialized data
- The AI mentor system uses batch operations to update session summaries when new trades are logged, reducing the need for expensive aggregation queries

For large datasets, pagination should be implemented to prevent memory issues when retrieving extensive history records. The current implementation loads all records into memory, which may become problematic as the database grows.

**Section sources**
- [core/db/queries.py](file://core/db/queries.py#L70-L102)
- [core/db/queries.py](file://core/db/queries.py#L165-L173)
- [core/db/models.py](file://core/db/models.py#L93-L153)

## Data Lifecycle and Retention

The database implements a simple data lifecycle management strategy through its schema design and application logic.

**Data Retention Policies:**
- **User Data**: Retained indefinitely unless explicitly deleted
- **Bot Configurations**: Retained until the bot is deleted by the user
- **Trade History**: Retained as long as the associated bot exists (enforced by CASCADE DELETE)
- **Backtest Results**: Retained indefinitely, with no automatic cleanup mechanism
- **Trading Sessions**: Retained indefinitely, with one session per day per user
- **AI Mentor Reports**: Retained indefinitely, with one report per session
- **Daily Trading Data**: Retained as long as the associated session exists (enforced by CASCADE DELETE)

**Data Lifecycle Events:**
- When a bot is deleted, all associated trade history records are automatically removed due to the foreign key constraint with ON DELETE CASCADE
- When a trading session is deleted, all associated daily trading data and AI mentor reports are automatically removed due to the foreign key constraints with ON DELETE CASCADE
- Notification records in `trade_history` are marked as read via the `mark_notifications_as_read` function but are not automatically purged
- No automated archiving or data purging processes are implemented in the current system

For production use, additional data retention policies should be considered, such as:
- Implementing time-based archiving for old trade history records
- Adding a soft-delete mechanism for bots and sessions instead of immediate deletion
- Creating a maintenance script to periodically clean up obsolete backtest results
- Implementing data anonymization for old trading sessions after a certain period

**Section sources**
- [init_db.py](file://init_db.py#L68-L78)
- [core/db/queries.py](file://core/db/queries.py#L43-L68)
- [core/db/queries.py](file://core/db/queries.py#L130-L163)
- [init_db.py](file://init_db.py#L116-L175)

## Security Considerations

The database implementation includes several security measures to protect sensitive data and ensure system integrity.

**Authentication and Access Control:**
- User passwords are stored as secure hashes using Werkzeug's `generate_password_hash` function
- The system appears to have a single-user design with a default admin account (ID=1)
- API endpoints for profile updates (`/api/profile`) only allow modification of the default user (ID=1)
- The AI mentor system assumes a single-user context with user_id defaulting to 1

**Data Protection:**
- The database file (`bots.db`) is stored in the application root directory, which should have appropriate file system permissions
- All database queries use parameterized statements to prevent SQL injection attacks
- Sensitive operations like user updates and bot management require authenticated access through the web interface
- The AI mentor system stores emotional and personal data that should be protected with appropriate security measures

**Security Recommendations:**
- Implement multi-user support with proper authentication and authorization
- Encrypt the database file at rest for additional protection
- Add input validation for all user-provided data before database insertion
- Implement role-based access control for different user types
- Regularly audit database access and modification logs
- Consider using environment variables for database configuration instead of hardcoded values
- Implement data minimization principles for the AI mentor system, only collecting necessary emotional and personal data
- Add encryption for sensitive fields in the AI mentor tables, particularly personal notes and emotional analysis

The current implementation prioritizes simplicity over comprehensive security, which is appropriate for a personal trading bot system but would require enhancement for multi-user or enterprise deployment.

**Section sources**
- [init_db.py](file://init_db.py#L0-L47)
- [core/routes/api_profile.py](file://core/routes/api_profile.py#L0-L38)
- [core/db/connection.py](file://core/db/connection.py#L0-L14)
- [core/db/models.py](file://core/db/models.py#L0-L261)