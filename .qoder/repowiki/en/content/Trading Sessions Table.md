# Trading Sessions Table

<cite>
**Referenced Files in This Document**   
- [models.py](file://core/db/models.py#L30-L229)
- [init_db.py](file://init_db.py#L80-L114)
- [ai_mentor.py](file://core/routes/ai_mentor.py#L0-L199)
- [trading_mentor_ai.py](file://core/ai/trading_mentor_ai.py#L0-L350)
</cite>

## Table of Contents
1. [Introduction](#introduction)
2. [Table Schema](#table-schema)
3. [Core Functions](#core-functions)
4. [Data Flow and Usage](#data-flow-and-usage)
5. [Integration with AI Mentor System](#integration-with-ai-mentor-system)
6. [Example Usage Scenarios](#example-usage-scenarios)
7. [Relationships with Other Tables](#relationships-with-other-tables)

## Introduction
The **trading_sessions** table is a central component of the AI mentor system in the QuantumBotX platform. It stores daily trading session metadata including emotional state, market conditions, personal notes, and performance summaries. This data enables the AI mentor to provide personalized feedback and analysis to traders, focusing on both technical performance and psychological aspects of trading behavior.

The system is specifically designed for Indonesian traders, providing mentorship in Bahasa Indonesia while tracking key trading metrics. The table serves as the foundation for generating daily reports, analyzing trading patterns, and offering improvement recommendations.

**Section sources**
- [models.py](file://core/db/models.py#L30-L229)
- [init_db.py](file://init_db.py#L80-L114)

## Table Schema
The trading_sessions table contains comprehensive information about each trading day, capturing both quantitative metrics and qualitative assessments.

``mermaid
erDiagram
trading_sessions {
INTEGER id PK
DATE session_date
INTEGER user_id FK
INTEGER total_trades
REAL total_profit_loss
TEXT emotions
TEXT market_conditions
TEXT personal_notes
INTEGER risk_score
DATETIME created_at
}
trading_sessions ||--o{ daily_trading_data : "has"
trading_sessions ||--o{ ai_mentor_reports : "generates"
trading_sessions }o--|| users : "belongs to"
```

**Diagram sources**
- [init_db.py](file://init_db.py#L80-L114)

### Field Definitions
- **id**: Primary key, auto-incrementing identifier for the session
- **session_date**: Date of the trading session (DATE type, NOT NULL)
- **user_id**: Foreign key referencing the user who created the session, defaults to 1
- **total_trades**: Count of trades executed during the session, defaults to 0
- **total_profit_loss**: Cumulative profit/loss for all trades in the session, defaults to 0.0
- **emotions**: Trader's emotional state during the session (e.g., "tenang", "serakah", "takut", "frustasi"), defaults to "netral"
- **market_conditions**: Description of market conditions (e.g., "normal", "trending", "sideways"), defaults to "normal"
- **personal_notes**: Free-form text field for trader's personal reflections and observations
- **risk_score**: Numerical assessment of risk management quality, defaults to 5
- **created_at**: Timestamp when the session record was created, defaults to current datetime

The schema includes foreign key constraints that maintain referential integrity with the users table, ensuring each session is associated with a valid user.

**Section sources**
- [init_db.py](file://init_db.py#L80-L114)

## Core Functions
The system provides several key functions for managing trading session data, enabling creation, retrieval, and updating of session information.

### Session Creation and Retrieval
```python
def create_trading_session(session_date: date, emotions: str = 'netral', 
                          market_conditions: str = 'normal', notes: str = '') -> int:
    """Create a new trading session and return session_id"""
    try:
        with sqlite3.connect('bots.db') as conn:
            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO trading_sessions (session_date, emotions, market_conditions, personal_notes) VALUES (?, ?, ?, ?)',
                (session_date, emotions, market_conditions, notes)
            )
            session_id = cursor.lastrowid
            conn.commit()
            return session_id if session_id is not None else 0
    except Exception as e:
        print(f"[AI MENTOR DB ERROR] Failed to create trading session: {e}")
        return 0

def get_or_create_today_session() -> int:
    """Get today's session or create a new one if it doesn't exist"""
    today = date.today()
    try:
        with sqlite3.connect('bots.db') as conn:
            cursor = conn.cursor()
            cursor.execute(
                'SELECT id FROM trading_sessions WHERE session_date = ?',
                (today,)
            )
            result = cursor.fetchone()
            if result:
                return result[0]
            else:
                return create_trading_session(today)
    except Exception as e:
        print(f"[AI MENTOR DB ERROR] Failed to get today's session: {e}")
        return create_trading_session(today)
```

### Session Data Retrieval
```python
def get_trading_session_data(session_date: date) -> Optional[Dict[str, Any]]:
    """Retrieve trading session data for AI analysis"""
    try:
        with sqlite3.connect('bots.db') as conn:
            cursor = conn.cursor()
            
            # Check if table exists
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='trading_sessions'")
            if not cursor.fetchone():
                print(f"[AI MENTOR DB ERROR] trading_sessions table not found")
                return None
            
            # Check available columns
            cursor.execute("PRAGMA table_info(trading_sessions)")
            columns = [col[1] for col in cursor.fetchall()]
            
            # Build query based on available columns
            select_columns = ['id']
            if 'total_trades' in columns:
                select_columns.append('total_trades')
            else:
                select_columns.append('0 as total_trades')
                
            if 'total_profit_loss' in columns:
                select_columns.append('total_profit_loss')
            else:
                select_columns.append('0.0 as total_profit_loss')
                
            select_columns.extend(['emotions', 'market_conditions', 'personal_notes'])
            
            if 'risk_score' in columns:
                select_columns.append('risk_score')
            else:
                select_columns.append('5 as risk_score')
            
            query = f"SELECT {', '.join(select_columns)} FROM trading_sessions WHERE session_date = ?"
            
            # Get session info
            cursor.execute(query, (session_date,))
            session_result = cursor.fetchone()
            
            if not session_result:
                return None
                
            session_id = session_result[0]
            
            # Get trades for this session
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='daily_trading_data'")
            trades = []
            if cursor.fetchone():
                cursor.execute(
                    '''SELECT symbol, profit_loss, lot_size, stop_loss_used, 
                              take_profit_used, risk_percent, strategy_used
                       FROM daily_trading_data WHERE session_id = ?''',
                    (session_id,)
                )
                trades_data = cursor.fetchall()
                
                for trade in trades_data:
                    trades.append({
                        'symbol': trade[0],
                        'profit': trade[1],
                        'lot_size': trade[2],
                        'stop_loss_used': bool(trade[3]),
                        'take_profit_used': bool(trade[4]),
                        'risk_percent': trade[5] if trade[5] is not None else 1.0,
                        'strategy': trade[6] if trade[6] else 'Unknown'
                    })
            
            return {
                'session_id': session_id,
                'total_trades': session_result[1] if session_result[1] is not None else 0,
                'total_profit_loss': session_result[2] if session_result[2] is not None else 0.0,
                'emotions': session_result[3] if session_result[3] else 'netral',
                'market_conditions': session_result[4] if session_result[4] else 'normal',
                'personal_notes': session_result[5] if session_result[5] else '',
                'risk_score': session_result[6] if session_result[6] is not None else 5,
                'trades': trades
            }
    except Exception as e:
        print(f"[AI MENTOR DB ERROR] Failed to retrieve session data: {e}")
        return None
```

### Session Updates
```python
def update_session_emotions_and_notes(session_date: date, emotions: str, notes: str) -> bool:
    """Update emotions and notes for a trading session"""
    try:
        with sqlite3.connect('bots.db') as conn:
            cursor = conn.cursor()
            cursor.execute(
                '''UPDATE trading_sessions 
                   SET emotions = ?, personal_notes = ?
                   WHERE session_date = ?''',
                (emotions, notes, session_date)
            )
            conn.commit()
            return True
    except Exception as e:
        print(f"[AI MENTOR DB ERROR] Failed to update emotions and notes: {e}")
        return False
```

**Section sources**
- [models.py](file://core/db/models.py#L30-L229)

## Data Flow and Usage
The trading session data flows through the system in a structured manner, starting from creation and ending with AI-generated feedback.

``mermaid
flowchart TD
A[Start Trading Day] --> B{Session Exists?}
B --> |No| C[Create New Session]
B --> |Yes| D[Use Existing Session]
C --> E[Initialize Session Data]
D --> F[Continue Session]
E --> G[Log Trades via daily_trading_data]
F --> G
G --> H[Update Session Summary]
H --> I[Collect Emotions & Notes]
I --> J[Generate AI Report]
J --> K[Display Feedback to User]
subgraph "Database Operations"
C
D
G
H
I
end
subgraph "AI Processing"
J
K
end
```

**Diagram sources**
- [models.py](file://core/db/models.py#L30-L229)
- [trading_mentor_ai.py](file://core/ai/trading_mentor_ai.py#L0-L350)

The data flow begins when a user starts their trading day. The system checks if a session already exists for the current date using `get_or_create_today_session()`. If no session exists, a new one is created with default values. As trades are executed, they are logged in the daily_trading_data table, which automatically updates the parent session's total_trades and total_profit_loss fields.

Throughout the day, users can update their emotional state and add personal notes through the web interface. At the end of the trading day, the AI mentor system retrieves the complete session data using `get_trading_session_data()` and generates a comprehensive report with analysis and recommendations.

**Section sources**
- [models.py](file://core/db/models.py#L30-L229)
- [ai_mentor.py](file://core/routes/ai_mentor.py#L0-L199)

## Integration with AI Mentor System
The trading_sessions table is tightly integrated with the AI mentor system, serving as the primary data source for personalized trading feedback.

``mermaid
classDiagram
class IndonesianTradingMentorAI {
+personality : str
+language : str
+cultural_context : str
+analyze_trading_session(session : TradingSession) Dict[str, Any]
+_detect_trading_patterns(session : TradingSession) Dict[str, str]
+_analyze_emotional_impact(session : TradingSession) Dict[str, str]
+_evaluate_risk_management(session : TradingSession) Dict[str, str]
+_generate_recommendations(session : TradingSession) List[str]
+_create_motivation_message(session : TradingSession) str
+generate_daily_report(session : TradingSession) str
}
class TradingSession {
+date : date
+trades : List[Dict]
+emotions : str
+market_conditions : str
+profit_loss : float
+notes : str
}
class ai_mentor_bp {
+dashboard() RenderTemplate
+today_report() RenderTemplate
+update_emotions() JSONResponse
+history() RenderTemplate
+view_session(session_date : str) RenderTemplate
+quick_feedback() RenderTemplate
}
IndonesianTradingMentorAI --> TradingSession : "analyzes"
ai_mentor_bp --> IndonesianTradingMentorAI : "uses"
ai_mentor_bp --> models : "calls"
models --> trading_sessions : "manages"
```

**Diagram sources**
- [trading_mentor_ai.py](file://core/ai/trading_mentor_ai.py#L0-L350)
- [ai_mentor.py](file://core/routes/ai_mentor.py#L0-L199)

The `IndonesianTradingMentorAI` class processes trading session data through several specialized analysis methods:

- `_detect_trading_patterns()`: Identifies whether the trading behavior shows discipline or requires improvement
- `_analyze_emotional_impact()`: Evaluates how the trader's emotional state affected their decisions
- `_evaluate_risk_management()`: Assesses the quality of risk management practices
- `_generate_recommendations()`: Creates specific, actionable suggestions for improvement
- `_create_motivation_message()`: Provides culturally appropriate encouragement

The Flask blueprint `ai_mentor_bp` exposes web routes that allow users to interact with their trading sessions. The `/today-report` route generates a daily AI report by retrieving session data, processing it through the AI mentor, and saving the results to the database.

**Section sources**
- [trading_mentor_ai.py](file://core/ai/trading_mentor_ai.py#L0-L350)
- [ai_mentor.py](file://core/routes/ai_mentor.py#L0-L199)

## Example Usage Scenarios

### Creating a New Trading Session
When a user begins trading for the first time on a new day, the system automatically creates a session:

```python
# This happens automatically when the first trade is logged
session_id = get_or_create_today_session()
# If no session exists for today, create_trading_session() is called internally
# with default values: emotions='netral', market_conditions='normal', notes=''
```

### Logging Trades and Updating Session Metrics
As trades are executed, they are logged and the parent session is updated:

```python
def log_trade_for_ai_analysis(bot_id: int, symbol: str, profit_loss: float, 
                              lot_size: float, stop_loss_used: bool = False,
                              take_profit_used: bool = False, risk_percent: float = 1.0,
                              strategy_used: str = '') -> None:
    """Log trade data for AI analysis"""
    session_id = get_or_create_today_session()
    
    try:
        with sqlite3.connect('bots.db') as conn:
            cursor = conn.cursor()
            cursor.execute(
                '''INSERT INTO daily_trading_data 
                   (session_id, bot_id, symbol, profit_loss, lot_size, 
                    stop_loss_used, take_profit_used, risk_percent, strategy_used)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                (session_id, bot_id, symbol, profit_loss, lot_size,
                 stop_loss_used, take_profit_used, risk_percent, strategy_used)
            )
            
            # Update trading session summary
            cursor.execute(
                '''UPDATE trading_sessions 
                   SET total_trades = total_trades + 1,
                       total_profit_loss = total_profit_loss + ?
                   WHERE id = ?''',
                (profit_loss, session_id)
            )
            
            conn.commit()
    except Exception as e:
        print(f"[AI MENTOR DB ERROR] Failed to log trade for AI: {e}")
```

### Updating Emotional State and Personal Notes
Users can update their emotional state and add personal reflections through the web interface:

```python
# Called via AJAX from the frontend
@app.route('/update-emotions', methods=['POST'])
def update_emotions():
    """Update emotions and notes for today's session"""
    try:
        data = request.get_json()
        emotions = data.get('emotions', 'netral')
        notes = data.get('notes', '')
        
        success = update_session_emotions_and_notes(date.today(), emotions, notes)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Emotions and notes saved successfully!'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Failed to save data'
            }), 500
            
    except Exception as e:
        logger.error(f"Error updating emotions: {e}")
        return jsonify({
            'success': False,
            'message': 'System error occurred'
        }), 500
```

### Generating a Daily AI Report
At the end of the trading day, users can request a comprehensive AI-generated report:

```python
@app.route('/today-report')
def today_report():
    """Generate AI mentor report for today"""
    try:
        today = date.today()
        session_data = get_trading_session_data(today)
        
        if not session_data:
            flash("No trading data for today. Start trading to get AI analysis!", "info")
            return render_template('ai_mentor/no_data.html')
        
        # Generate AI analysis
        mentor = IndonesianTradingMentorAI()
        
        # Convert to TradingSession format
        trading_session = TradingSession(
            date=today,
            trades=session_data['trades'],
            emotions=session_data['emotions'],
            market_conditions=session_data['market_conditions'],
            profit_loss=session_data['total_profit_loss'],
            notes=session_data['personal_notes']
        )
        
        # Generate AI report
        ai_report = mentor.generate_daily_report(trading_session)
        analysis = mentor.analyze_trading_session(trading_session)
        
        # Save to database
        save_ai_mentor_report(session_data['session_id'], analysis)
        
        return render_template('ai_mentor/daily_report.html',
                             session_data=session_data,
                             ai_report=ai_report,
                             analysis=analysis)
                             
    except Exception as e:
        logger.error(f"Error generating today's AI report: {e}")
        flash("Failed to generate AI report for today", "error")
        return redirect(url_for('ai_mentor.dashboard'))
```

**Section sources**
- [models.py](file://core/db/models.py#L30-L229)
- [ai_mentor.py](file://core/routes/ai_mentor.py#L0-L199)
- [trading_mentor_ai.py](file://core/ai/trading_mentor_ai.py#L0-L350)

## Relationships with Other Tables
The trading_sessions table is part of a larger data model that tracks various aspects of the trading experience.

``mermaid
erDiagram
users ||--o{ trading_sessions : "has"
trading_sessions ||--o{ daily_trading_data : "contains"
trading_sessions ||--o{ ai_mentor_reports : "generates"
bots ||--o{ daily_trading_data : "executes"
users {
INTEGER id PK
TEXT name
TEXT email
TEXT password_hash
DATETIME join_date
}
trading_sessions {
INTEGER id PK
DATE session_date
INTEGER user_id FK
INTEGER total_trades
REAL total_profit_loss
TEXT emotions
TEXT market_conditions
TEXT personal_notes
INTEGER risk_score
DATETIME created_at
}
daily_trading_data {
INTEGER id PK
INTEGER session_id FK
INTEGER bot_id FK
TEXT symbol
DATETIME entry_time
DATETIME exit_time
REAL profit_loss
REAL lot_size
BOOLEAN stop_loss_used
BOOLEAN take_profit_used
REAL risk_percent
TEXT strategy_used
DATETIME created_at
}
ai_mentor_reports {
INTEGER id PK
INTEGER session_id FK
TEXT trading_patterns_analysis
TEXT emotional_analysis
INTEGER risk_management_score
TEXT recommendations
TEXT motivation_message
TEXT language
DATETIME created_at
}
bots {
INTEGER id PK
TEXT name
TEXT market
TEXT status
REAL lot_size
INTEGER sl_pips
INTEGER tp_pips
TEXT timeframe
INTEGER check_interval_seconds
TEXT strategy
TEXT strategy_params
}
```

**Diagram sources**
- [init_db.py](file://init_db.py#L80-L154)

The trading_sessions table has the following relationships:

- **One-to-Many with users**: Each user can have multiple trading sessions, but each session belongs to one user. This allows the system to provide personalized mentorship based on individual trading history.
- **One-to-Many with daily_trading_data**: Each trading session contains multiple individual trades. The daily_trading_data table stores detailed information about each trade, including symbol, profit/loss, lot size, and strategy used.
- **One-to-Many with ai_mentor_reports**: Each trading session generates one AI mentor report, which contains the AI's analysis, recommendations, and motivational message.
- **Many-to-One with bots**: Multiple bots can execute trades within a single trading session, allowing users to manage multiple automated trading strategies.

These relationships enable the AI mentor system to provide comprehensive feedback that considers the trader's emotional state, risk management practices, trading patterns, and overall performance across multiple strategies and instruments.

**Section sources**
- [init_db.py](file://init_db.py#L80-L154)
- [models.py](file://core/db/models.py#L30-L229)