# UI Templates

<cite>
**Referenced Files in This Document**   
- [base.html](file://templates/base.html)
- [index.html](file://templates/index.html)
- [trading_bots.html](file://templates/trading_bots.html)
- [backtesting.html](file://templates/backtesting.html)
- [portfolio.html](file://templates/portfolio.html)
- [profile.html](file://templates/profile.html)
- [notifications.html](file://templates/notifications.html)
- [404.html](file://templates/404.html)
- [500.html](file://templates/500.html)
- [bot_detail.html](file://templates/bot_detail.html)
- [forex.html](file://templates/forex.html)
- [history.html](file://templates/history.html)
- [settings.html](file://templates/settings.html)
- [stocks.html](file://templates/stocks.html)
- [backtest_history.html](file://templates/backtest_history.html)
- [ai_mentor/dashboard.html](file://templates/ai_mentor/dashboard.html) - *Added in recent commit*
- [ai_mentor/daily_report.html](file://templates/ai_mentor/daily_report.html) - *Added in recent commit*
- [ai_mentor/quick_feedback.html](file://templates/ai_mentor/quick_feedback.html) - *Added in recent commit*
- [core/routes/ai_mentor.py](file://core/routes/ai_mentor.py) - *Added in recent commit*
- [core/ai/trading_mentor_ai.py](file://core/ai/trading_mentor_ai.py) - *Added in recent commit*
</cite>

## Update Summary
**Changes Made**   
- Added comprehensive documentation for the new AI Mentor system templates
- Added new section for AI Mentor System covering dashboard, daily report, and quick feedback views
- Updated Table of Contents to include new AI Mentor section
- Added references to new AI mentor templates and backend implementation files
- Enhanced source tracking with specific file references for new AI mentor components
- Updated introduction to reflect expanded template coverage

## Table of Contents
1. [Introduction](#introduction)
2. [Base Template Structure](#base-template-structure)
3. [Dashboard (Index)](#dashboard-index)
4. [Trading Bots Management](#trading-bots-management)
5. [Backtesting Interface](#backtesting-interface)
6. [Portfolio Tracking](#portfolio-tracking)
7. [User Profile](#user-profile)
8. [Notifications](#notifications)
9. [Error Pages](#error-pages)
10. [Bot Detail View](#bot-detail-view)
11. [Market Data Pages](#market-data-pages)
12. [Settings Page](#settings-page)
13. [Backtest History](#backtest-history)
14. [AI Mentor System](#ai-mentor-system)

## Introduction
This document provides comprehensive documentation for all HTML templates used in the QuantumBotX frontend application. The templates are built using Jinja2 templating engine and follow a consistent design pattern centered around a shared base layout. Each template serves a specific purpose in the trading platform, from dashboard overview to bot management, backtesting, portfolio tracking, and user settings. The documentation covers template inheritance, block definitions, form structures, data display components, and dynamic content handling. This update includes new documentation for the AI Mentor system, a revolutionary feature that provides personalized trading guidance in Bahasa Indonesia for Indonesian traders.

## Base Template Structure
The `base.html` template serves as the foundational layout for all pages in the application, providing a consistent user interface with a sidebar navigation, header, and content area. It implements template inheritance through Jinja2 blocks, allowing child templates to inject page-specific content and assets.

``mermaid
graph TD
A[base.html] --> B[index.html]
A --> C[trading_bots.html]
A --> D[backtesting.html]
A --> E[portfolio.html]
A --> F[profile.html]
A --> G[notifications.html]
A --> H[bot_detail.html]
A --> I[forex.html]
A --> J[history.html]
A --> K[settings.html]
A --> L[stocks.html]
A --> M[backtest_history.html]
A --> N[404.html]
A --> O[500.html]
A --> P[ai_mentor/dashboard.html]
A --> Q[ai_mentor/daily_report.html]
A --> R[ai_mentor/quick_feedback.html]
S[CSS & JS Libraries] --> A
T[Tailwind CSS] --> A
U[Chart.js] --> A
V[Font Awesome] --> A
W[Toastify] --> A
```

**Diagram sources**
- [base.html](file://templates/base.html#L1-L80)

**Section sources**
- [base.html](file://templates/base.html#L1-L80)

### Template Blocks
The base template defines several blocks that child templates can override:

- **title**: Page title displayed in the browser tab
- **head_extra**: Additional CSS or meta tags specific to the page
- **content**: Main content area of the page
- **scripts**: JavaScript files and inline scripts specific to the page

### Layout Components
The template implements a responsive layout with:
- A fixed sidebar with navigation links
- A main content area with header and dynamic content
- Responsive design using Tailwind CSS
- Font Awesome icons for visual elements
- Toastify for user notifications

### Navigation System
The sidebar navigation uses an `active_page` variable to highlight the current page. Navigation items include:
- Dashboard
- Trading Bots
- Portfolio
- Backtester
- History
- Settings
- Stocks
- Forex
- AI Mentor

The header includes a search bar and notification bell with a dot indicator for unread notifications.

## Dashboard (Index)
The `index.html` template represents the landing page and dashboard of the QuantumBotX platform, providing an overview of the user's trading activities and performance metrics.

``mermaid
flowchart TD
A[Dashboard] --> B[Stat Cards]
A --> C[Price Chart]
A --> D[RSI Chart]
A --> E[Active Bots List]
B --> B1[Total Equity]
B --> B2[Today's Profit]
B --> B3[Active Bots]
B --> B4[Total Bots]
C --> C1[EUR/USD Price Chart]
D --> D1[EUR/USD RSI Chart]
E --> E1[Bot List Container]
E --> E2[View All Bots Link]
```

**Diagram sources**
- [index.html](file://templates/index.html#L1-L63)
- [base.html](file://templates/base.html#L1-L80)

**Section sources**
- [index.html](file://templates/index.html#L1-L63)

### Content Structure
The dashboard is organized into several sections:
- **Header**: Displays the page title and welcome message
- **Stat Cards**: Four cards showing key performance indicators with loading spinners
- **Charts**: Two Chart.js canvases for price and RSI visualization
- **Active Bots**: List of currently running bots with a link to view all bots

### Data Visualization
The dashboard includes two interactive charts:
- **Price Chart**: Displays EUR/USD price data using Chart.js
- **RSI Chart**: Shows RSI indicator values for EUR/USD on H1 timeframe

Both charts are initialized through the linked `dashboard.js` script, which fetches data from the backend API.

### Dynamic Content
All stat cards display loading spinners initially, indicating that the values are populated asynchronously via JavaScript. The active bots list also shows a loading message before being populated with data.

## Trading Bots Management
The `trading_bots.html` template provides an interface for managing trading bots, including creating new bots, viewing existing bots, and controlling their operation.

``mermaid
flowchart TD
A[Trading Bots] --> B[Header with Actions]
A --> C[Bots Table]
A --> D[Create Bot Modal]
B --> B1[Page Title]
B --> B2[Start All Button]
B --> B3[Stop All Button]
B --> B4[Create Bot Button]
C --> C1[Name/Market Column]
C --> C2[Parameters Column]
C --> C3[Configuration Column]
C --> C4[Status Column]
C --> C5[Actions Column]
D --> D1[Bot Name Input]
D --> D2[Market Input]
D --> D3[Risk Settings]
D --> D4[Timeframe Selection]
D --> D5[Strategy Selection]
D --> D6[Strategy Parameters]
```

**Diagram sources**
- [trading_bots.html](file://templates/trading_bots.html#L1-L131)
- [base.html](file://templates/base.html#L1-L80)

**Section sources**
- [trading_bots.html](file://templates/trading_bots.html#L1-L131)

### Header and Actions
The page header includes:
- Title and description
- Three action buttons:
  - **Start All**: Activates all paused bots
  - **Stop All**: Stops all running bots
  - **Create Bot**: Opens the bot creation modal

### Bots Table
The main content displays a table of all configured bots with columns for:
- **Name / Market**: Bot name and trading market
- **Parameter**: Key trading parameters
- **Configuration**: Timeframe and check interval
- **Status**: Current operational status
- **Actions**: Control buttons for individual bots

The table body is populated dynamically via JavaScript, with an initial loading message.

### Create Bot Modal
A modal dialog allows users to create or edit bots with a comprehensive form:
- **Bot Information**: Name and market inputs
- **Risk Management**: Risk percentage and stop-loss/take-profit ATR multipliers
- **Scheduling**: Timeframe selection and check interval
- **Strategy Selection**: Dropdown to choose from available strategies
- **Strategy Parameters**: Dynamic container for strategy-specific parameters loaded via JavaScript

The modal includes a loading overlay and is designed to be scrollable on smaller screens.

## Backtesting Interface
The `backtesting.html` template provides a user interface for running strategy backtests on historical market data.

``mermaid
flowchart TD
A[Backtesting] --> B[Configuration Column]
A --> C[Results Column]
B --> B1[Strategy Selection]
B --> B2[Data File Upload]
B --> B3[Risk Management Inputs]
B --> B4[Strategy Parameters]
B --> B5[Run Backtest Button]
C --> C1[Results Summary]
C --> C2[Equity Chart]
C --> C3[Results Log]
D[Loading Spinner] --> C
```

**Diagram sources**
- [backtesting.html](file://templates/backtesting.html#L1-L68)
- [base.html](file://templates/base.html#L1-L80)

**Section sources**
- [backtesting.html](file://templates/backtesting.html#L1-L68)

### Two-Column Layout
The interface uses a responsive two-column layout:
- **Left Column (1/3 width)**: Configuration form
- **Right Column (2/3 width)**: Results display

On smaller screens, the layout becomes a single column.

### Configuration Form
The form includes:
- **Strategy Selection**: Dropdown to choose the trading strategy
- **Data Upload**: File input for uploading historical CSV data
- **Risk Management**: SL and TP ATR multipliers
- **Strategy Parameters**: Dynamic container populated based on selected strategy
- **Run Button**: Submits the form to execute the backtest

### Results Display
After running a backtest, the results are displayed in:
- **Summary Metrics**: Grid of performance statistics
- **Equity Curve**: Chart showing the backtest performance over time
- **Results Log**: Detailed log of trades and events

The results container is initially hidden and revealed after a successful backtest. A loading spinner is displayed during execution.

## Portfolio Tracking
The `portfolio.html` template displays real-time information about the user's open trading positions from their MetaTrader 5 account.

``mermaid
flowchart TD
A[Portfolio] --> B[Header with Summary]
A --> C[Charts Grid]
A --> D[Positions Table]
C --> C1[Profit/Loss Chart]
C --> C2[Asset Allocation Chart]
D --> D1[Symbol Column]
D --> D2[Type Column]
D --> D3[Volume Column]
D --> D4[Open Price Column]
D --> D5[Profit/Loss Column]
D --> D6[Magic Number Column]
```

**Diagram sources**
- [portfolio.html](file://templates/portfolio.html#L1-L55)
- [base.html](file://templates/base.html#L1-L80)

**Section sources**
- [portfolio.html](file://templates/portfolio.html#L1-L55)

### Header and Summary
The header includes:
- Page title and description
- Portfolio summary section (populated dynamically)

### Charts
Two charts provide visual insights:
- **Profit/Loss Chart**: Real-time graph of open position performance
- **Asset Allocation Chart**: Pie chart showing distribution across different assets

Both charts use Chart.js with the date-fns adapter for proper time formatting.

### Positions Table
A table displays all open positions with columns for:
- **Symbol**: Trading instrument
- **Type**: Buy or sell position
- **Volume**: Trade size
- **Open Price**: Entry price
- **Profit/Loss**: Current unrealized profit/loss
- **Magic Number**: Identifier for bot association

The table body is populated dynamically with a loading message initially.

## User Profile
The `profile.html` template allows users to view and edit their account information and security settings.

``mermaid
flowchart TD
A[Profile] --> B[User Card]
A --> C[Account Details Form]
B --> B1[Profile Image]
B --> B2[Name Display]
B --> B3[Role]
B --> B4[Join Date]
C --> C1[Full Name Input]
C --> C2[Email Input]
C --> C3[Password Change]
C --> C4[Save Button]
```

**Diagram sources**
- [profile.html](file://templates/profile.html#L1-L49)
- [base.html](file://templates/base.html#L1-L80)

**Section sources**
- [profile.html](file://templates/profile.html#L1-L49)

### Two-Column Layout
The page uses a responsive grid:
- **Left Column (1/3 width)**: User information card with profile image
- **Right Column (2/3 width)**: Editable form

### User Information Card
Displays:
- Profile icon (default user icon)
- Full name
- Role/position
- Join date

### Account Form
Contains fields for:
- **Full Name**: Editable text input
- **Email**: Read-only display
- **Password**: Optional password change field (leave blank to keep current)

The form includes a save button to submit changes.

## Notifications
The `notifications.html` template provides a simple interface for viewing user notifications.

``mermaid
flowchart TD
A[Notifications] --> B[Header]
A --> C[Notifications Container]
C --> C1[Loading Message]
```

**Diagram sources**
- [notifications.html](file://templates/notifications.html#L1-L17)
- [base.html](file://templates/base.html#L1-L80)

**Section sources**
- [notifications.html](file://templates/notifications.html#L1-L17)

### Minimal Design
The page consists of:
- **Header**: Title "Notifications"
- **Container**: Div that will be populated with notification items via JavaScript

Initially, the container displays a loading message. The actual notifications are fetched and rendered by the `notifications.js` script.

## Error Pages
The application includes custom error pages for common HTTP errors, providing a consistent user experience even when errors occur.

### 404 Page Not Found
The `404.html` template displays when a requested page cannot be found.

``mermaid
flowchart TD
A[404 Page] --> B[Error Code Display]
A --> C[Error Message]
A --> D[Return to Dashboard Link]
B --> B1[Large 404 Text]
C --> C1[Page Not Found Message]
D --> D1[Home Button with Icon]
```

**Diagram sources**
- [404.html](file://templates/404.html#L1-L24)
- [base.html](file://templates/base.html#L1-L80)

**Section sources**
- [404.html](file://templates/404.html#L1-L24)

The page features:
- Large "404" text in blue
- "Page Not Found" message
- Description explaining the error
- Button to return to the dashboard

### 500 Internal Server Error
The `500.html` template displays when a server error occurs.

``mermaid
flowchart TD
A[500 Page] --> B[Error Code Display]
A --> C[Error Message]
A --> D[Return to Dashboard Link]
B --> B1[Large 500 Text]
C --> C1[Internal Error Message]
D --> D1[Home Button with Icon]
```

**Diagram sources**
- [500.html](file://templates/500.html#L1-L27)
- [base.html](file://templates/base.html#L1-L80)

**Section sources**
- [500.html](file://templates/500.html#L1-L27)

The page features:
- Large "500" text in red
- "Internal Server Error" message
- Description indicating the server encountered a problem
- Button to return to the dashboard

Both error pages use a centered layout with Tailwind CSS and include a home button with an icon.

## Bot Detail View
The `bot_detail.html` template provides a detailed view of an individual trading bot, showing its configuration, activity log, and real-time analysis.

``mermaid
flowchart TD
A[Bot Detail] --> B[Header]
A --> C[Activity Log Column]
A --> D[Info & Analysis Column]
B --> B1[Bot Name]
B --> B2[Market]
B --> B3[Status Badge]
C --> C1[Activity Log]
D --> D1[Parameters]
D --> D2[Real-Time Analysis]
D --> D3[Signal Display]
```

**Diagram sources**
- [bot_detail.html](file://templates/bot_detail.html#L1-L48)
- [base.html](file://templates/base.html#L1-L80)

**Section sources**
- [bot_detail.html](file://templates/bot_detail.html#L1-L48)

### Header
Displays:
- Bot name (loaded dynamically)
- Market information
- Status badge showing current state

### Two-Column Layout
- **Left Column (2/3 width)**: Activity log with scrollable container
- **Right Column (1/3 width)**: Two information cards

### Information Cards
- **Parameters**: Displays the bot's configuration settings
- **Real-Time Analysis**: Shows current market analysis and trading signals
- **Signal Display**: Prominent area showing the current trading signal

The content is populated dynamically via JavaScript.

## Market Data Pages
The application includes dedicated pages for viewing market data for different asset classes.

### Forex Page
The `forex.html` template displays real-time data for forex currency pairs.

``mermaid
flowchart TD
A[Forex Page] --> B[Header]
A --> C[Forex Table]
A --> D[Modal]
C --> C1[Pair Column]
C --> C2[Bid Price Column]
C --> C3[Ask Price Column]
C --> C4[Spread Column]
C --> C5[Actions Column]
```

**Diagram sources**
- [forex.html](file://templates/forex.html#L1-L51)
- [base.html](file://templates/base.html#L1-L80)

**Section sources**
- [forex.html](file://templates/forex.html#L1-L51)

Features:
- Table of forex pairs with bid/ask prices and spread
- Clickable actions that open a modal with additional information
- Hidden modal that can be displayed via JavaScript

### Stocks Page
The `stocks.html` template displays real-time data for stocks.

``mermaid
flowchart TD
A[Stocks Page] --> B[Header]
A --> C[Stocks Table]
A --> D[Modal]
C --> C1[Stock Column]
C --> C2[Price Column]
C --> C3[24h Change Column]
C --> C4[Time Column]
C --> C5[Actions Column]
```

**Diagram sources**
- [stocks.html](file://templates/stocks.html#L1-L51)
- [base.html](file://templates/base.html#L1-L80)

**Section sources**
- [stocks.html](file://templates/stocks.html#L1-L51)

Features:
- Table of stocks with current price and 24-hour change
- Time of last update
- Clickable actions that open a modal with additional information
- Hidden modal that can be displayed via JavaScript

Both market pages follow the same pattern of a table with dynamic data and a reusable modal component.

## Settings Page
The `settings.html` template provides access to application settings and user preferences.

``mermaid
flowchart TD
A[Settings Page] --> B[Profile Section]
A --> C[API Keys Section]
B --> B1[Full Name Input]
B --> B2[Email Display]
B --> B3[Save Button]
C --> C1[API Keys Content]
```

**Diagram sources**
- [settings.html](file://templates/settings.html#L1-L34)
- [base.html](file://templates/base.html#L1-L80)

**Section sources**
- [settings.html](file://templates/settings.html#L1-L34)

### Layout
Uses a two-column grid:
- **Left Column (2/3 width)**: Settings sections
- **Right Column (1/3 width)**: Reserved for future use

### Sections
- **Profile**: Allows editing of user profile information
- **API Keys**: Placeholder section for exchange API key management

The profile section includes fields for name and email, with a save button to apply changes.

## Backtest History
The `backtest_history.html` template provides an interface for viewing past backtest results.

``mermaid
flowchart TD
A[Backtest History] --> B[History List Column]
A --> C[Detail View Column]
B --> B1[Backtest List]
C --> C2[Summary Metrics]
C --> C3[Equity Chart]
C --> C4[Parameters]
C --> C5[Log]
C --> C6[Placeholder]
```

**Diagram sources**
- [backtest_history.html](file://templates/backtest_history.html#L1-L44)
- [base.html](file://templates/base.html#L1-L80)

**Section sources**
- [backtest_history.html](file://templates/backtest_history.html#L1-L44)

### Two-Column Layout
- **Left Column (1/3 width)**: List of past backtests
- **Right Column (2/3 width)**: Detailed view of selected backtest

### Functionality
- Initially displays a loading message in the list
- When a backtest is selected, the detail view shows:
  - Summary metrics
  - Equity curve chart
  - Strategy parameters
  - Execution log
- A placeholder message is displayed when no backtest is selected

The interface allows users to review and compare past backtest results without rerunning simulations.

## AI Mentor System
The AI Mentor system is a revolutionary new feature that provides personalized trading guidance for Indonesian traders. The system consists of three main templates that work together to provide daily analysis, emotional feedback, and trading recommendations in Bahasa Indonesia.

**Diagram sources**
- [ai_mentor/dashboard.html](file://templates/ai_mentor/dashboard.html#L1-L288)
- [ai_mentor/daily_report.html](file://templates/ai_mentor/daily_report.html#L1-L317)
- [ai_mentor/quick_feedback.html](file://templates/ai_mentor/quick_feedback.html#L1-L167)
- [core/routes/ai_mentor.py](file://core/routes/ai_mentor.py#L1-L333)
- [core/ai/trading_mentor_ai.py](file://core/ai/trading_mentor_ai.py#L1-L351)

**Section sources**
- [ai_mentor/dashboard.html](file://templates/ai_mentor/dashboard.html#L1-L288)
- [ai_mentor/daily_report.html](file://templates/ai_mentor/daily_report.html#L1-L317)
- [ai_mentor/quick_feedback.html](file://templates/ai_mentor/quick_feedback.html#L1-L167)
- [core/routes/ai_mentor.py](file://core/routes/ai_mentor.py#L1-L333)
- [core/ai/trading_mentor_ai.py](file://core/ai/trading_mentor_ai.py#L1-L351)

### AI Mentor Dashboard
The `ai_mentor/dashboard.html` template serves as the main interface for the AI Mentor system, providing an overview of the user's trading performance and emotional state.

``mermaid
flowchart TD
A[AI Mentor Dashboard] --> B[Header Section]
A --> C[Quick Stats]
A --> D[Today's Trading]
A --> E[AI Insights]
B --> B1[Title and Description]
B --> B2[Language and Features]
C --> C1[Total Sessions]
C --> C2[Win Rate]
C --> C3[Today's P&L]
C --> C4[AI Status]
D --> D1[Total Trades]
D --> D2[P&L]
D --> D3[Emotions]
D --> D4[Personal Notes]
D --> D5[Action Buttons]
E --> E1[Recent Reports]
E --> E2[AI Analysis]
E --> E3[Daily Tips]
```

**Diagram sources**
- [ai_mentor/dashboard.html](file://templates/ai_mentor/dashboard.html#L1-L288)

**Section sources**
- [ai_mentor/dashboard.html](file://templates/ai_mentor/dashboard.html#L1-L288)
- [core/routes/ai_mentor.py](file://core/routes/ai_mentor.py#L21-L60)

The dashboard includes:
- **Header Section**: Displays the AI Mentor title with Indonesian flag and features
- **Quick Stats**: Four cards showing total sessions, win rate, today's P&L, and AI status
- **Today's Trading**: Section showing today's trading details including emotions and personal notes
- **AI Insights**: Recent reports and AI-generated daily tips

The dashboard is accessible via the `/ai-mentor` route and is integrated with the main application through the `ai_mentor_bp` blueprint.

### Daily Report
The `ai_mentor/daily_report.html` template provides a detailed analysis of the user's trading session, including pattern detection, emotional impact analysis, and risk management evaluation.

``mermaid
flowchart TD
A[Daily Report] --> B[Header Section]
A --> C[Trading Summary]
A --> D[AI Analysis]
A --> E[Risk Management]
B --> B1[Report Title]
B --> B2[Date and Performance]
C --> C1[Total Trades]
C --> C2[P&L]
C --> C3[Emotions]
C --> C4[Market Conditions]
D --> D1[Trading Patterns]
D --> D2[Emotional Analysis]
E --> E1[Risk Score]
E --> E2[Feedback]
E --> E3[Improvement Suggestions]
```

**Diagram sources**
- [ai_mentor/daily_report.html](file://templates/ai_mentor/daily_report.html#L1-L317)

**Section sources**
- [ai_mentor/daily_report.html](file://templates/ai_mentor/daily_report.html#L1-L317)
- [core/routes/ai_mentor.py](file://core/routes/ai_mentor.py#L65-L104)
- [core/ai/trading_mentor_ai.py](file://core/ai/trading_mentor_ai.py#L1-L351)

Key features:
- **Trading Summary**: Overview of the day's trading performance
- **AI Analysis**: Detailed analysis of trading patterns and emotional impact
- **Risk Management**: Evaluation of risk management practices with color-coded scores
- **Recommendations**: Personalized tips and motivational messages

The report is generated by the `IndonesianTradingMentorAI` class, which analyzes the user's trading session and provides feedback in Bahasa Indonesia.

### Quick Feedback
The `ai_mentor/quick_feedback.html` template provides a modal form for users to quickly update their emotional state and trading notes.

``mermaid
flowchart TD
A[Quick Feedback Form] --> B[Emotion Selection]
A --> C[P&L Input]
A --> D[Personal Notes]
A --> E[Action Buttons]
B --> B1[Tenang]
B --> B2[Serakah]
B --> B3[Takut]
B --> B4[Frustasi]
C --> C1[Numeric Input]
D --> D1[Text Area]
E --> E1[Instant Feedback]
E --> E2[Save Data]
```

**Diagram sources**
- [ai_mentor/quick_feedback.html](file://templates/ai_mentor/quick_feedback.html#L1-L167)

**Section sources**
- [ai_mentor/quick_feedback.html](file://templates/ai_mentor/quick_feedback.html#L1-L167)
- [core/routes/ai_mentor.py](file://core/routes/ai_mentor.py#L154-L167)
- [core/routes/ai_mentor.py](file://core/routes/ai_mentor.py#L106-L134)

Components:
- **Emotion Selection**: Buttons for selecting current emotional state (tenang, serakah, takut, frustasi)
- **P&L Input**: Field for entering current profit/loss
- **Personal Notes**: Text area for adding trading notes
- **Action Buttons**: Instant feedback and save data buttons

The form is integrated with JavaScript functions that provide instant AI feedback and submit data to the `/ai-mentor/update-emotions` endpoint.

### System Integration
The AI Mentor system is fully integrated with the main QuantumBotX application through several key components:

- **Blueprint Registration**: The `ai_mentor_bp` blueprint is registered in `core/__init__.py` and handles all AI mentor routes
- **Database Integration**: Trading session data is stored and retrieved through the `core/db/models.py` functions
- **Frontend Integration**: The AI mentor summary is displayed on the main dashboard through the `/ai-mentor/api/dashboard-summary` API endpoint
- **JavaScript Integration**: The `index.html` template includes JavaScript functions that update the AI mentor status and load summary data

The system is designed to provide a seamless experience for Indonesian traders, combining technical analysis with emotional intelligence to improve trading performance.