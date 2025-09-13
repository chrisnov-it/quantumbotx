# Portfolio API

<cite>
**Referenced Files in This Document**   
- [api_portfolio.py](file://core/routes/api_portfolio.py)
- [mt5.py](file://core/utils/mt5.py)
- [portfolio.js](file://static/js/portfolio.js)
- [portfolio.html](file://templates/portfolio.html)
- [api_history.py](file://core/routes/api_history.py)
- [api_dashboard.py](file://core/routes/api_dashboard.py)
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
This document provides comprehensive RESTful API documentation for the Portfolio API in the quantumbotx system. The Portfolio API enables real-time access to trading positions, asset allocation data, and performance metrics synchronized with MetaTrader 5 (MT5). It supports frontend visualization of open positions, profit/loss trends, and asset distribution. The API is designed for integration with dashboard components and trading analytics tools, providing critical data for portfolio monitoring and decision-making.

## Project Structure
The quantumbotx project follows a modular Flask-based architecture with clear separation of concerns. The Portfolio API resides within the `core/routes` directory as a Flask Blueprint, while data retrieval logic is encapsulated in utility modules. Frontend components are organized in static and template directories, enabling a clean separation between backend services and user interface.

```mermaid
graph TB
subgraph "Backend"
A[api_portfolio.py] --> B[mt5.py]
C[api_history.py] --> B
D[api_dashboard.py] --> B
end
subgraph "Frontend"
E[portfolio.html] --> F[portfolio.js]
F --> A
F --> C
F --> D
end
B --> G[MetaTrader 5]
style A fill:#4B5563,stroke:#374151
style B fill:#10B981,stroke:#047857
style E fill:#8B5CF6,stroke:#7C3AED
style F fill:#3B82F6,stroke:#2563EB
```

**Diagram sources**
- [api_portfolio.py](file://core/routes/api_portfolio.py)
- [mt5.py](file://core/utils/mt5.py)
- [portfolio.js](file://static/js/portfolio.js)
- [portfolio.html](file://templates/portfolio.html)

**Section sources**
- [api_portfolio.py](file://core/routes/api_portfolio.py)
- [mt5.py](file://core/utils/mt5.py)

## Core Components
The Portfolio API consists of two primary endpoints: `/open-positions` and `/allocation`. These endpoints retrieve real-time trading data from MT5 through utility functions and format it for frontend consumption. The system integrates with MT5's position and deal history APIs to provide comprehensive portfolio visibility. The frontend components use JavaScript to periodically fetch this data and update visualizations including tables, line charts, and doughnut charts.

**Section sources**
- [api_portfolio.py](file://core/routes/api_portfolio.py#L1-L57)
- [mt5.py](file://core/utils/mt5.py#L55-L65)
- [portfolio.js](file://static/js/portfolio.js#L0-L150)

## Architecture Overview
The Portfolio API operates as a middleware layer between the MT5 trading platform and the web frontend. It follows a request-response pattern where HTTP GET requests trigger data retrieval from MT5, processing, and JSON response generation. The architecture emphasizes real-time data synchronization with automatic error handling for connection failures.

```mermaid
sequenceDiagram
participant Frontend as "Frontend (portfolio.js)"
participant API as "Portfolio API"
participant MT5Util as "MT5 Utility"
participant MT5 as "MetaTrader 5"
Frontend->>API : GET /api/portfolio/open-positions
API->>MT5Util : get_open_positions_mt5()
MT5Util->>MT5 : mt5.positions_get()
MT5-->>MT5Util : Position Data
MT5Util-->>API : List of Positions
API-->>Frontend : JSON Response
Frontend->>API : GET /api/portfolio/allocation
API->>MT5Util : get_open_positions_mt5()
MT5Util->>MT5 : mt5.positions_get()
MT5-->>MT5Util : Position Data
MT5Util-->>API : List of Positions
API->>API : Process Allocation Logic
API-->>Frontend : JSON Response with Allocation Data
Note over Frontend,API : Data refreshes every 5 seconds
```

**Diagram sources**
- [api_portfolio.py](file://core/routes/api_portfolio.py)
- [mt5.py](file://core/utils/mt5.py)
- [portfolio.js](file://static/js/portfolio.js)

## Detailed Component Analysis

### Portfolio API Endpoints
The Portfolio API provides two endpoints for retrieving portfolio data. The `/open-positions` endpoint returns raw position data from MT5, while the `/allocation` endpoint processes this data to provide asset distribution metrics.

#### Open Positions Endpoint
```mermaid
flowchart TD
Start([GET /api/portfolio/open-positions]) --> CallMT5["Call get_open_positions_mt5()"]
CallMT5 --> CheckResult{"Positions Retrieved?"}
CheckResult --> |Yes| ReturnJSON["Return JSON positions"]
CheckResult --> |No| ReturnEmpty["Return []"]
CallMT5 --> Exception{"Exception?"}
Exception --> |Yes| LogError["Log error, return 500"]
Exception --> |No| Continue
style Start fill:#2563EB,stroke:#1D4ED8
style ReturnJSON fill:#10B981,stroke:#047857
style LogError fill:#EF4444,stroke:#DC2626
```

**Diagram sources**
- [api_portfolio.py](file://core/routes/api_portfolio.py#L10-L18)

#### Asset Allocation Endpoint
```mermaid
flowchart TD
StartAlloc([GET /api/portfolio/allocation]) --> FetchPositions["Fetch positions from MT5"]
FetchPositions --> InitSummary["Initialize allocation_summary"]
InitSummary --> LoopStart["For each position"]
LoopStart --> ExtractSymbol["Extract symbol and volume"]
ExtractSymbol --> Classify{"Classify by symbol pattern"}
Classify --> |Forex| AddForex["allocation_summary.Forex += volume"]
Classify --> |Gold| AddGold["allocation_summary.Emas += volume"]
Classify --> |Stocks| AddStocks["allocation_summary.Saham += volume"]
Classify --> |Crypto| AddCrypto["allocation_summary.Crypto += volume"]
Classify --> |Other| AddOther["allocation_summary.Lainnya += volume"]
AddForex --> LoopEnd
AddGold --> LoopEnd
AddStocks --> LoopEnd
AddCrypto --> LoopEnd
AddOther --> LoopEnd
LoopEnd --> FilterZero["Remove zero-value categories"]
FilterZero --> FormatResponse["Format as labels/values"]
FormatResponse --> ReturnResponse["Return JSON response"]
style StartAlloc fill:#2563EB,stroke:#1D4ED8
style ReturnResponse fill:#10B981,stroke:#047857
```

**Diagram sources**
- [api_portfolio.py](file://core/routes/api_portfolio.py#L20-L57)

### Data Retrieval from MT5
The `get_open_positions_mt5()` function in the MT5 utility module serves as the primary interface to the MetaTrader 5 platform. It handles the conversion of MT5's native position objects into JSON-serializable dictionaries.

```mermaid
classDiagram
class MT5Position {
+int ticket
+int symbol
+int type
+double volume
+double price_open
+double price_current
+double profit
+int time
+int magic
+string comment
}
class PositionDict {
+int ticket
+str symbol
+int type
+float volume
+float price_open
+float price_current
+float profit
+int time
+int magic
+str comment
}
MT5Position --> PositionDict : "Convert to dict via _asdict()"
class MT5Utility {
+get_open_positions_mt5() list[dict]
+get_trade_history_mt5(days) list[dict]
+get_account_info_mt5() dict
}
MT5Utility --> MT5Position : "Uses MT5 API"
PositionDict --> APIResponse : "Returned to API endpoints"
```

**Diagram sources**
- [mt5.py](file://core/utils/mt5.py#L55-L65)

## Dependency Analysis
The Portfolio API has a clear dependency chain that starts from the frontend and terminates at the MT5 platform. Understanding these dependencies is crucial for troubleshooting and system maintenance.

```mermaid
graph LR
A[portfolio.html] --> B[portfolio.js]
B --> C[api_portfolio.py]
C --> D[mt5.py]
D --> E[MetaTrader5]
B --> F[api_history.py]
B --> G[api_dashboard.py]
F --> D
G --> D
style A fill:#8B5CF6,stroke:#7C3AED
style B fill:#3B82F6,stroke:#2563EB
style C fill:#4B5563,stroke:#374151
style D fill:#10B981,stroke:#047857
style E fill:#F59E0B,stroke:#D97706
```

**Diagram sources**
- [portfolio.html](file://templates/portfolio.html)
- [portfolio.js](file://static/js/portfolio.js)
- [api_portfolio.py](file://core/routes/api_portfolio.py)
- [mt5.py](file://core/utils/mt5.py)
- [api_history.py](file://core/routes/api_history.py)
- [api_dashboard.py](file://core/routes/api_dashboard.py)

**Section sources**
- [api_portfolio.py](file://core/routes/api_portfolio.py)
- [mt5.py](file://core/utils/mt5.py)
- [portfolio.js](file://static/js/portfolio.js)

## Performance Considerations
The Portfolio API is designed for real-time data delivery with a 5-second refresh interval. This balance between data freshness and system load is critical for maintaining responsiveness without overwhelming the MT5 connection. The implementation includes error handling to prevent cascading failures during MT5 connectivity issues. Caching is not implemented at the API level, meaning each request triggers a fresh MT5 data pull, which ensures data accuracy but increases MT5 load under high request volumes.

## Troubleshooting Guide
This section addresses common issues encountered with the Portfolio API and provides resolution steps.

### Connection Timeouts to MT5
**Symptoms**: 
- API returns 500 error with message
- Frontend displays "Failed to load data" message
- Console shows "Error saat get_open_positions_mt5" in logs

**Causes**:
- MT5 terminal not running
- Incorrect account credentials
- Network connectivity issues
- MT5 server overload

**Solutions**:
1. Verify MT5 terminal is running and logged in
2. Check account credentials in configuration
3. Restart MT5 terminal and application
4. Verify network connectivity to MT5 server
5. Check MT5 logs for specific error codes

### Stale or Missing Positions
**Symptoms**:
- Portfolio shows outdated positions
- Closed positions still appear in UI
- Position count mismatch with MT5

**Causes**:
- Synchronization delay
- MT5 data refresh rate
- API polling interval limitations

**Solutions**:
1. Force refresh by restarting the application
2. Manually refresh MT5 market data
3. Verify MT5 connection status
4. Check if positions are truly closed in MT5

### Error Handling Implementation
The API implements comprehensive error handling to maintain stability during MT5 connectivity issues:

```python
try:
    positions = get_open_positions_mt5()
    return jsonify(positions)
except Exception as e:
    return jsonify({"error": str(e)}), 500
```

The frontend also includes error handling for failed API requests:

```javascript
catch (error) {
    console.error("Gagal mengambil data portfolio:", error);
    portfolioTableBody.innerHTML = `<tr><td colspan="6" class="p-4 text-center text-red-500">Gagal memuat data: ${error.message}</td></tr>`;
}
```

**Section sources**
- [mt5.py](file://core/utils/mt5.py#L55-L65)
- [api_portfolio.py](file://core/routes/api_portfolio.py#L10-L18)
- [portfolio.js](file://static/js/portfolio.js#L85-L92)

## Conclusion
The Portfolio API in quantumbotx provides essential functionality for monitoring real-time trading positions and asset allocation. By integrating with MetaTrader 5, it delivers accurate, up-to-date portfolio information to the web interface. The system's architecture prioritizes reliability and real-time performance, with comprehensive error handling for MT5 connectivity issues. Future enhancements could include caching mechanisms, WebSocket-based real-time updates, and more sophisticated performance analytics. The current implementation effectively serves the core requirements of position tracking and portfolio visualization.