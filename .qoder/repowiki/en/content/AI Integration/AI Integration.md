# AI Integration

<cite>
**Referenced Files in This Document**   
- [ollama_client.py](file://core/ai/ollama_client.py) - *Updated in recent commit*
- [quantum_velocity.py](file://core/strategies/quantum_velocity.py) - *No changes*
- [mercy_edge.py](file://core/strategies/mercy_edge.py) - *No changes*
- [ollama.py](file://core/utils/ollama.py) - *No changes*
- [ai.py](file://core/utils/ai.py) - *No changes*
- [base_strategy.py](file://core/strategies/base_strategy.py) - *No changes*
- [trading_mentor_ai.py](file://core/ai/trading_mentor_ai.py) - *Added in commit a24fa8637bb6dc7c2f6d6fae6a633611836bf329*
- [ai_mentor.py](file://core/routes/ai_mentor.py) - *Added in commit a24fa8637bb6dc7c2f6d6fae6a633611836bf329*
- [dashboard.html](file://templates/ai_mentor/dashboard.html) - *Added in commit a24fa8637bb6dc7c2f6d6fae6a633611836bf329*
- [daily_report.html](file://templates/ai_mentor/daily_report.html) - *Added in commit a24fa8637bb6dc7c2f6d6fae6a633611836bf329*
- [quick_feedback.html](file://templates/ai_mentor/quick_feedback.html) - *Added in commit a24fa8637bb6dc7c2f6d6fae6a633611836bf329*
- [models.py](file://core/db/models.py) - *Updated in commit a24fa8637bb6dc7c2f6d6fae6a633611836bf329*
</cite>

## Update Summary
- Added comprehensive documentation for the new Indonesian AI Trading Mentor System
- Updated AI Integration Overview to include the new mentor system
- Added new section on AI Mentor System Architecture and Functionality
- Added new section on User Interaction and Feedback Mechanisms
- Added new section on Data Storage and Retrieval for AI Mentor
- Updated Table of Contents to reflect new sections
- Added sources for all new files and updated sections

## Table of Contents
1. [AI Integration Overview](#ai-integration-overview)
2. [Ollama Client Architecture](#ollama-client-architecture)
3. [AI-Enhanced Trading Strategies](#ai-enhanced-trading-strategies)
4. [Communication Patterns with AI Models](#communication-patterns-with-ai-models)
5. [Configuration Options for AI Models](#configuration-options-for-ai-models)
6. [Performance Considerations](#performance-considerations)
7. [Error Handling and Response Validation](#error-handling-and-response-validation)
8. [Implementation Guidance for New AI Strategies](#implementation-guidance-for-new-ai-strategies)
9. [Indonesian AI Trading Mentor System](#indonesian-ai-trading-mentor-system)
10. [User Interaction and Feedback Mechanisms](#user-interaction-and-feedback-mechanisms)
11. [Data Storage and Retrieval for AI Mentor](#data-storage-and-retrieval-for-ai-mentor)

## AI Integration Overview

QuantumBotX integrates artificial intelligence through local Large Language Models (LLMs) via the Ollama framework, enabling advanced decision-making in algorithmic trading strategies. The system leverages AI to enhance signal validation, provide explanatory insights, and support hybrid decision logic in select trading strategies such as *Mercy Edge (AI)*. AI components are modular and isolated within dedicated modules under `core/ai` and `core/utils`, ensuring clean separation from core trading logic.

The integration follows a synchronous request-response model, where market data is formatted into prompts, sent to a locally running Ollama server, and parsed into actionable trading decisions. This design prioritizes interpretability and control, avoiding full AI-driven execution in favor of AI-augmented strategies.

A significant enhancement to the AI integration is the introduction of the **Indonesian AI Trading Mentor System**, a revolutionary feature that provides personalized guidance to Indonesian traders in Bahasa Indonesia. This system analyzes trading sessions, emotional states, and risk management practices to deliver culturally relevant feedback and recommendations.

**Section sources**
- [ollama_client.py](file://core/ai/ollama_client.py#L1-L13)
- [ai.py](file://core/utils/ai.py#L1-L58)
- [trading_mentor_ai.py](file://core/ai/trading_mentor_ai.py#L1-L350) - *Added in commit a24fa8637bb6dc7c2f6d6fae6a633611836bf329*

## Ollama Client Architecture

The Ollama client implementation in QuantumBotX provides a lightweight interface for interacting with locally hosted LLMs. Two distinct implementations exist: one using the official `ollama` Python package and another using direct HTTP requests to the Ollama API.

### Primary Ollama Client
Located in `core/ai/ollama_client.py`, this module defines a simple function-based interface:

```python
def ask_ollama(prompt, model="qwen2.5-coder:1.5b"):
    try:
        response = ollama.chat(
            model=model,
            messages=[{"role": "user", "content": prompt}]
        )
        return response['message']['content']
    except Exception as e:
        return f"Error: {e}"
```

This implementation uses the `ollama.chat()` method to send a user message and retrieve the model's response. It supports model selection via the `model` parameter and handles exceptions gracefully by returning error messages as strings.

### Fallback HTTP Client
An alternative implementation in `core/utils/ollama.py` uses direct HTTP calls:

```python
def ask_ollama(prompt, model="qwen2.5-coder:1.5b"):
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={"model": model, "prompt": prompt, "stream": False}
        )
        if response.status_code == 200:
            return response.json().get("response", "").strip()
        else:
            return f"Error: {response.status_code} - {response.text}"
    except Exception as e:
        return f"Exception during AI call: {e}"
```

This version communicates directly with the Ollama REST API at `http://localhost:11434`, offering resilience in environments where the Python package may not be available.

``mermaid
flowchart TD
A["Trading Strategy"] --> B["Format Market Data as Prompt"]
B --> C["Call ask_ollama()"]
C --> D{"Ollama Client Type"}
D --> E["ollama.chat() via Python Package"]
D --> F["HTTP POST to /api/generate"]
E --> G["Ollama Server (localhost:11434)"]
F --> G
G --> H["LLM Response"]
H --> I["Parse Decision & Explanation"]
I --> J["Trading Signal"]
```

**Diagram sources**
- [ollama_client.py](file://core/ai/ollama_client.py#L1-L13)
- [ollama.py](file://core/utils/ollama.py#L1-L14)

**Section sources**
- [ollama_client.py](file://core/ai/ollama_client.py#L1-L13)
- [ollama.py](file://core/utils/ollama.py#L1-L14)

## AI-Enhanced Trading Strategies

QuantumBotX features AI-augmented strategies that combine traditional technical indicators with AI-based validation. The primary example is the *Mercy Edge (AI)* strategy, while *Quantum Velocity* currently operates without AI integration.

### Mercy Edge (AI) Strategy

Located in `core/strategies/mercy_edge.py`, this strategy combines MACD, Stochastic, and AI validation for high-precision signals.

```python
class MercyEdgeStrategy(BaseStrategy):
    name = 'Mercy Edge (AI)'
    description = 'Strategi hybrid yang menggabungkan MACD, Stochastic, dan validasi AI untuk sinyal presisi tinggi.'
```

Although the current implementation does not directly call AI within the `analyze()` method, the strategy is explicitly designed for AI integration, as indicated by its name and description. The logical extension would involve calling `get_ai_analysis()` after generating initial signals to validate or refine them.

### Quantum Velocity Strategy

In contrast, the `QuantumVelocityStrategy` in `core/strategies/quantum_velocity.py` relies solely on technical indicators—specifically EMA 200 for trend filtering and Bollinger Band Squeeze for volatility breakout detection—without any AI component.

```python
class QuantumVelocityStrategy(BaseStrategy):
    name = 'Quantum Velocity'
    description = 'Menggabungkan filter tren jangka panjang (EMA 200) dengan pemicu volatilitas (Bollinger Squeeze Breakout).'
```

This strategy exemplifies the non-AI approach in QuantumBotX, using deterministic rules based on price and indicator conditions.

``mermaid
classDiagram
class BaseStrategy {
<<abstract>>
+bot : BotInstance
+params : dict
+__init__(bot_instance, params)
+analyze(df)*
+get_definable_params() classmethod
}
class MercyEdgeStrategy {
+name : str
+description : str
+analyze(df)
+analyze_df(df)
}
class QuantumVelocityStrategy {
+name : str
+description : str
+analyze(df)
+analyze_df(df)
}
BaseStrategy <|-- MercyEdgeStrategy
BaseStrategy <|-- QuantumVelocityStrategy
note right of MercyEdgeStrategy
Designed for AI integration
Combines MACD, Stochastic,
and potential AI validation
end note
note right of QuantumVelocityStrategy
Pure technical strategy
No AI components
Uses EMA + Bollinger Squeeze
end note
```

**Diagram sources**
- [mercy_edge.py](file://core/strategies/mercy_edge.py#L5-L122)
- [quantum_velocity.py](file://core/strategies/quantum_velocity.py#L6-L94)
- [base_strategy.py](file://core/strategies/base_strategy.py#L4-L28)

**Section sources**
- [mercy_edge.py](file://core/strategies/mercy_edge.py#L5-L122)
- [quantum_velocity.py](file://core/strategies/quantum_velocity.py#L6-L94)

## Communication Patterns with AI Models

AI communication in QuantumBotX follows a structured prompt-response-parsing workflow, primarily orchestrated through the `get_ai_analysis()` function in `core/utils/ai.py`.

### Prompt Engineering

The system constructs prompts using market data and bot context. While the exact prompt content is not fully visible in the current code, the structure is evident:

```python
prompt = f"Analyze the following market data for {bot.market} and decide whether to BUY, SELL, or HOLD..."
```

This indicates that prompts are dynamically generated with:
- Target market symbol
- Current market data (implied by parameter)
- Clear instruction for decision output

### Response Parsing

The AI response is parsed using simple string matching to extract trading decisions:

```python
decision = "HOLD"
explanation = response['message']['content']

if "BUY" in explanation.upper():
    decision = "BUY"
elif "SELL" in explanation.upper():
    decision = "SELL"
```

This approach converts unstructured LLM output into structured trading signals, with the full explanation preserved for logging and user transparency.

``mermaid
sequenceDiagram
participant Strategy as Trading Strategy
participant AIUtils as ai.py
participant OllamaClient as ollama_client.py
participant OllamaServer as Ollama Server
Strategy->>AIUtils : get_ai_analysis(bot_id, market_data)
AIUtils->>AIUtils : Retrieve bot instance
AIUtils->>AIUtils : Construct prompt
AIUtils->>OllamaClient : ask_ollama(prompt, model)
OllamaClient->>OllamaServer : HTTP POST /api/chat
OllamaServer-->>OllamaClient : {message : {content : "BUY..."}}
OllamaClient-->>AIUtils : Return response text
AIUtils->>AIUtils : Parse for BUY/SELL
AIUtils-->>Strategy : {ai_decision, ai_explanation}
```

**Diagram sources**
- [ai.py](file://core/utils/ai.py#L1-L58)
- [ollama_client.py](file://core/ai/ollama_client.py#L1-L13)

**Section sources**
- [ai.py](file://core/utils/ai.py#L1-L58)

## Configuration Options for AI Models

QuantumBotX provides configurable parameters for AI model interaction, though they are currently hardcoded in function definitions rather than exposed through user settings.

### Model Selection

The default model is specified in both client implementations:
- `qwen2.5-coder:1.5b` in `ollama_client.py` and `ollama.py`
- `llama3` in `ai.py` for `get_ai_analysis()`

This inconsistency suggests potential configuration drift or multiple use cases.

### Temperature and Response Settings

Currently, there are no explicit parameters for:
- **Temperature**: Controls randomness (not exposed)
- **Max tokens**: Response length limit (not set)
- **Timeout**: Request timeout (not implemented)

These settings are managed implicitly by the Ollama server defaults. Future enhancements could expose these via strategy parameters or a global AI configuration.

### Suggested Configuration Structure

To improve flexibility, configuration could be structured as:

```python
# Example configuration dictionary
ai_config = {
    "model": "llama3",
    "temperature": 0.7,
    "timeout": 30,
    "max_retries": 3,
    "system_prompt": "You are a professional trading analyst..."
}
```

**Section sources**
- [ollama_client.py](file://core/ai/ollama_client.py#L4-L4)
- [ollama.py](file://core/utils/ollama.py#L2-L2)
- [ai.py](file://core/utils/ai.py#L30-L30)

## Performance Considerations

Integrating synchronous AI calls into trading loops introduces significant performance implications that must be carefully managed.

### Latency Impact

Each `ask_ollama()` call introduces network and processing latency:
- Typical response times: 500ms to 5000ms depending on model size
- Blocks the trading loop during request
- Unsuitable for high-frequency trading (HFT)

### Synchronous vs Asynchronous Design

The current implementation uses **synchronous** calls, which:
- ✅ Simple to implement and debug
- ✅ Ensures ordered execution
- ❌ Blocks trading execution
- ❌ Increases risk of missed opportunities

For production use, an asynchronous pattern with caching would be preferable:

```python
# Pseudocode for improved design
async def get_ai_signal_async():
    if cache.has_fresh_signal():
        return cache.get()
    task = asyncio.create_task(call_ollama())
    return await task
```

### Optimization Recommendations

1. **Implement Caching**: Store AI decisions for a short duration (e.g., 5-15 minutes)
2. **Use Background Workers**: Offload AI calls to separate threads/processes
3. **Add Timeouts**: Prevent indefinite blocking with `requests` timeout parameters
4. **Fallback Logic**: Use last valid signal if AI is unresponsive
5. **Rate Limiting**: Prevent overwhelming the Ollama server

**Section sources**
- [ollama_client.py](file://core/ai/ollama_client.py#L1-L13)
- [ollama.py](file://core/utils/ollama.py#L1-L14)

## Error Handling and Response Validation

Robust error handling is critical for maintaining system stability when integrating external AI services.

### Current Error Handling

The system implements basic exception handling in all AI-related functions:

```python
try:
    response = ollama.chat(...)
    return response['message']['content']
except Exception as e:
    return f"Error: {e}"
```

This prevents crashes but returns error strings that must be handled by calling code.

### AI Service Unavailability

When the Ollama server is unreachable:
- HTTP client returns connection errors
- Python package may raise various exceptions
- Both return string-formatted errors

### Response Validation

The current validation is minimal:
- Checks for `response.status_code == 200` in HTTP client
- Parses JSON response
- Uses string matching for decision extraction

### Recommended Enhancements

1. **Structured Error Objects**:
```python
return {"error": "connection_failed", "message": str(e)}
```

2. **Response Schema Validation**:
```python
if not isinstance(response, dict) or 'message' not in response:
    raise ValueError("Invalid response format")
```

3. **Retry Mechanism**:
```python
for attempt in range(3):
    try:
        return call_ollama()
    except ConnectionError:
        time.sleep(1)
```

4. **Circuit Breaker Pattern**: Temporarily disable AI calls after repeated failures

**Section sources**
- [ollama_client.py](file://core/ai/ollama_client.py#L5-L12)
- [ollama.py](file://core/utils/ollama.py#L3-L13)
- [ai.py](file://core/utils/ai.py#L45-L58)

## Implementation Guidance for New AI Strategies

To create new AI-enhanced trading strategies in QuantumBotX, follow this structured approach.

### Step 1: Inherit from BaseStrategy

```python
from .base_strategy import BaseStrategy

class MyAIStrategy(BaseStrategy):
    name = 'My AI Strategy'
    description = 'Description of your strategy'
```

### Step 2: Define Configurable Parameters

```python
@classmethod
def get_definable_params(cls):
    return [
        {"name": "ai_model", "label": "AI Model", "type": "text", "default": "llama3"},
        {"name": "risk_level", "label": "Risk Level", "type": "number", "default": 0.7},
    ]
```

### Step 3: Integrate AI Analysis

```python
def analyze(self, df):
    # 1. Generate initial signal with technical indicators
    tech_signal = self._calculate_technical_signal(df)
    
    # 2. Get AI validation
    from core.utils.ai import get_ai_analysis
    ai_result = get_ai_analysis(self.bot.id, df.tail(50))
    
    # 3. Combine signals
    final_signal = self._combine_signals(tech_signal, ai_result)
    
    return final_signal
```

### Step 4: Implement Safety Measures

To prevent over-reliance on AI:

1. **Confidence Thresholding**:
```python
if ai_result.get("confidence", 0) < 0.6:
    return {"signal": "HOLD", ...}
```

2. **Circuit Breaker**:
```python
if ai_result["ai_decision"] == "ERROR":
    # Fall back to conservative strategy
    return self._safe_mode_analysis(df)
```

3. **Divergence Handling**:
```python
if tech_signal != ai_decision:
    # Require additional confirmation
    return {"signal": "HOLD", "explanation": "AI and technical signals diverge"}
```

### Best Practices

- **Always have a fallback**: Never allow AI to be the sole decision source
- **Log all AI interactions**: For audit and improvement
- **Validate inputs**: Sanitize market data before sending to AI
- **Monitor performance**: Track AI accuracy over time
- **Use explainability**: Always return the AI's reasoning

**Section sources**
- [ai.py](file://core/utils/ai.py#L1-L58)
- [base_strategy.py](file://core/strategies/base_strategy.py#L4-L28)
- [mercy_edge.py](file://core/strategies/mercy_edge.py#L5-L122)

## Indonesian AI Trading Mentor System

The Indonesian AI Trading Mentor System is a revolutionary feature that provides personalized guidance to Indonesian traders in Bahasa Indonesia. This system acts as a digital mentor, offering culturally relevant feedback, emotional support, and practical trading advice.

### Core Architecture

The system is implemented in `core/ai/trading_mentor_ai.py` and consists of the following key components:

- **IndonesianTradingMentorAI**: The main class that orchestrates the analysis and generates personalized feedback
- **TradingSession**: A dataclass that defines the structure of trading session data for analysis
- **Analysis Methods**: Specialized methods for different aspects of trading performance

```python
class IndonesianTradingMentorAI:
    """AI Mentor Trading in Bahasa Indonesia"""
    
    def __init__(self):
        self.personality = "supportive_indonesian_mentor"
        self.language = "bahasa_indonesia"
        self.cultural_context = "indonesian_trading_psychology"
        
    def analyze_trading_session(self, session: TradingSession) -> Dict[str, Any]:
        """Analyze trading session like an experienced mentor"""
        
        analysis = {
            'pola_trading': self._detect_trading_patterns(session),
            'emosi_vs_performa': self._analyze_emotional_impact(session),
            'manajemen_risiko': self._evaluate_risk_management(session),
            'rekomendasi': self._generate_recommendations(session),
            'motivasi': self._create_motivation_message(session)
        }
        
        return analysis
```

### Key Analysis Components

The AI mentor performs comprehensive analysis across multiple dimensions:

1. **Trading Pattern Detection**: Identifies the main trading pattern based on profitability and discipline
2. **Emotional Impact Analysis**: Evaluates how emotions affect trading performance
3. **Risk Management Evaluation**: Assesses risk management practices with a culturally relevant scoring system
4. **Personalized Recommendations**: Generates specific tips based on trading performance
5. **Motivational Messaging**: Provides supportive messages tailored to the trader's emotional state

```python
def _evaluate_risk_management(self, session: TradingSession) -> Dict[str, str]:
    """Evaluate risk management in the Indonesian context"""
    
    risk_score = self._calculate_risk_score(session.trades)
    
    if risk_score >= 8:
        return {
            'nilai': f'{risk_score}/10 - EXCELLENT!',
            'feedback': 'Manajemen risiko Anda sudah sangat bagus! Seperti trader profesional.',
            'detail': 'Anda konsisten dengan stop loss, lot size wajar, dan tidak over-trading.',
            'apresiasi': 'Dengan disiplin seperti ini, Anda pasti akan sukses jangka panjang! 🎯'
        }
    elif risk_score >= 6:
        return {
            'nilai': f'{risk_score}/10 - GOOD',
            'feedback': 'Manajemen risiko cukup baik, tapi masih ada yang bisa diperbaiki.',
            'detail': 'Kadang lot size agak besar, atau stop loss terlalu jauh.',
            'saran': 'Ingat prinsip: "Jangan pernah risiko lebih dari 2% modal per trade."'
        }
    else:
        return {
            'nilai': f'{risk_score}/10 - PERLU PERBAIKAN',
            'feedback': 'Manajemen risiko perlu diperbaiki agar modal tetap aman.',
            'detail': 'Lot size terlalu besar atau tidak pakai stop loss konsisten.',
            'peringatan': '⚠️ Ingat: "Modal adalah nyawa trader. Jaga baik-baik!"'
        }
```

### Cultural Context and Personalization

The system is specifically designed for Indonesian traders with several culturally relevant features:

- **Bahasa Indonesia Interface**: All communication is in Indonesian, making it accessible to local traders
- **Cultural References**: Uses Indonesian-specific examples and references (e.g., Jakarta market hours, BI rate)
- **Personal Journey Context**: Incorporates the trader's personal journey and achievements
- **Motivational Quotes**: Uses culturally appropriate motivational messages and proverbs

```python
def _add_personal_context(self, session: TradingSession) -> str:
    """Add personal context based on user journey"""
    
    context_messages = [
        "🎯 **Ingat Journey Anda:** Dari awalnya ikut mentor yang hilang kontak, "
        "sekarang Anda sudah bisa trading mandiri dengan sistem sendiri!",
        
        "💡 **Pencapaian Anda:** Demo account $4,649.94 profit bukan main-main! "
        "Ini bukti Anda sudah paham konsep trading.",
        
        "🇮🇩 **Visi Besar:** Anda sedang membangun sistem yang akan membantu "
        "trader pemula Indonesia. Setiap pengalaman hari ini adalah pelajaran untuk mereka!",
        
        "🚀 **Level Up:** Dengan konsistensi seperti ini, soon Anda bisa "
        "upgrade ke live account dan mulai earning real money!"
    ]
    
    import random
    return random.choice(context_messages)
```

### Daily Report Generation

The system generates comprehensive daily reports in Indonesian that summarize the trading session and provide actionable insights:

```python
def generate_daily_report(self, session: TradingSession) -> str:
    """Generate complete daily report in Bahasa Indonesia"""
    
    analysis = self.analyze_trading_session(session)
    
    report = f"""
🤖 **LAPORAN MENTOR AI TRADING - {session.date.strftime('%d %B %Y')}**

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 **RINGKASAN HARI INI:**
• Profit/Loss: ${session.profit_loss:.2f}
• Jumlah Trade: {len(session.trades)}
• Kondisi Emosi: {session.emotions.title()}
• Kondisi Market: {session.market_conditions}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔍 **ANALISIS POLA TRADING:**
{analysis['pola_trading']['analisis']}

**Kekuatan Anda:** {analysis['pola_trading']['kekuatan']}
**Yang Perlu Diperbaiki:** {analysis['pola_trading']['area_perbaikan']}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🧠 **ANALISIS EMOSI vs PERFORMA:**
{analysis['emosi_vs_performa']['feedback']}

💡 **Tip Emosi:** {analysis['emosi_vs_performa']['tip']}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🛡️ **EVALUASI MANAJEMEN RISIKO:**
**Skor:** {analysis['manajemen_risiko']['nilai']}
{analysis['manajemen_risiko']['feedback']}

{analysis['manajemen_risiko'].get('detail', '')}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{chr(10).join(analysis['rekomendasi'])}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💪 **PESAN MOTIVASI:**
{analysis['motivasi']}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📝 **CATATAN PRIBADI ANDA:**
"{session.notes if session.notes else 'Tidak ada catatan hari ini'}"

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎯 **RENCANA BESOK:**
• Fokus pada perbaikan yang disarankan
• Pertahankan yang sudah bagus
• Trading dengan emosi yang tenang
• Ingat: "Konsistensi mengalahkan perfeksi!"

Semangat trading! Mentor AI Anda akan selalu mendampingi! 🚀🇮🇩

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        """
        
    return report.strip()
```

``mermaid
classDiagram
class IndonesianTradingMentorAI {
+personality : str
+language : str
+cultural_context : str
+analyze_trading_session(session)
+_detect_trading_patterns(session)
+_analyze_emotional_impact(session)
+_evaluate_risk_management(session)
+_generate_recommendations(session)
+_create_motivation_message(session)
+generate_daily_report(session)
}
class TradingSession {
+date : date
+trades : List[Dict]
+emotions : str
+market_conditions : str
+profit_loss : float
+notes : str
}
class TradingSessionData {
+session_id : int
+total_trades : int
+total_profit_loss : float
+emotions : str
+market_conditions : str
+personal_notes : str
+risk_score : int
+trades : List[Dict]
}
class AIAnalysisResult {
+pola_trading : Dict
+emosi_vs_performa : Dict
+manajemen_risiko : Dict
+rekomendasi : List[str]
+motivasi : str
}
IndonesianTradingMentorAI --> TradingSession : analyzes
IndonesianTradingMentorAI --> AIAnalysisResult : produces
IndonesianTradingMentorAI --> TradingSessionData : consumes
```

**Diagram sources**
- [trading_mentor_ai.py](file://core/ai/trading_mentor_ai.py#L21-L304) - *Added in commit a24fa8637bb6dc7c2f6d6fae6a633611836bf329*
- [models.py](file://core/db/models.py#L94-L176) - *Updated in commit a24fa8637bb6dc7c2f6d6fae6a633611836bf329*

**Section sources**
- [trading_mentor_ai.py](file://core/ai/trading_mentor_ai.py#L1-L350) - *Added in commit a24fa8637bb6dc7c2f6d6fae6a633611836bf329*

## User Interaction and Feedback Mechanisms

The Indonesian AI Trading Mentor System provides multiple channels for user interaction and feedback, creating a comprehensive support ecosystem for traders.

### Web Interface Components

The system includes several HTML templates that provide a user-friendly interface for interacting with the AI mentor:

#### Dashboard Interface
The main dashboard (`dashboard.html`) provides an overview of trading performance and AI insights:

```html
<div class="mentor-card">
    <h1 class="text-3xl font-bold mb-2">🧠 AI Mentor Trading Indonesia</h1>
    <p class="text-blue-100 text-lg">Mentor digital Anda untuk sukses trading jangka panjang</p>
    <div class="mt-4 flex items-center space-x-4">
        <span class="text-blue-200">🇮🇩 Bahasa Indonesia</span>
        <span class="text-blue-200">• 📊 Analisis Real-time</span>
        <span class="text-blue-200">• 🎯 Personal</span>
    </div>
</div>
```

#### Daily Report Interface
The daily report (`daily_report.html`) presents detailed AI analysis in a structured format:

```html
<div class="ai-report-card">
    <div class="flex justify-between items-start">
        <div>
            <h1 class="text-3xl font-bold mb-2">📊 Laporan AI Mentor</h1>
            <p class="text-blue-100 text-lg">Analisis personal untuk {{ session_data.session_date if session_data else 'Hari Ini' }}</p>
        </div>
        <div class="text-right">
            {% if session_data %}
                <div class="text-3xl font-bold {{ 'text-green-300' if session_data.total_profit_loss > 0 else 'text-red-300' if session_data.total_profit_loss < 0 else 'text-gray-300' }}">
                    ${{ "%.2f"|format(session_data.total_profit_loss) }}
                </div>
                <div class="text-blue-200">{{ session_data.total_trades }} trades</div>
            {% else %}
                <div class="text-gray-300">No data</div>
            {% endif %}
        </div>
    </div>
</div>
```

#### Quick Feedback Interface
The quick feedback modal (`quick_feedback.html`) allows users to quickly provide emotional feedback and notes:

```html
<form id="quickFeedbackForm" onsubmit="submitQuickFeedback(event)">
    <div class="space-y-4">
        <!-- Emosi Saat Ini -->
        <div>
            <label class="block text-sm font-semibold text-gray-700 mb-2">🧠 Bagaimana perasaan Anda saat trading hari ini?</label>
            <div class="grid grid-cols-2 gap-2">
                <button type="button" onclick="selectEmotion('tenang')" class="emotion-btn p-3 border rounded-lg text-left hover:bg-blue-50 focus:ring-2 focus:ring-blue-500" data-emotion="tenang">
                    <div class="font-semibold text-green-600">😌 Tenang</div>
                    <div class="text-xs text-gray-500">Pikiran jernih, tidak terburu-buru</div>
                </button>
                <button type="button" onclick="selectEmotion('serakah')" class="emotion-btn p-3 border rounded-lg text-left hover:bg-yellow-50 focus:ring-2 focus:ring-yellow-500" data-emotion="serakah">
                    <div class="font-semibold text-yellow-600">🤑 Serakah</div>
                    <div class="text-xs text-gray-500">Ingin profit besar, agresif</div>
                </button>
                <button type="button" onclick="selectEmotion('takut')" class="emotion-btn p-3 border rounded-lg text-left hover:bg-purple-50 focus:ring-2 focus:ring-purple-500" data-emotion="takut">
                    <div class="font-semibold text-purple-600">😰 Takut</div>
                    <div class="text-xs text-gray-500">Khawatir loss, ragu-ragu</div>
                </button>
                <button type="button" onclick="selectEmotion('frustasi')" class="emotion-btn p-3 border rounded-lg text-left hover:bg-red-50 focus:ring-2 focus:ring-red-500" data-emotion="frustasi">
                    <div class="font-semibold text-red-600">😤 Frustasi</div>
                    <div class="text-xs text-gray-500">Kesal karena loss beruntun</div>
                </button>
            </div>
            <input type="hidden" id="selectedEmotion" name="emotions" value="netral" required>
        </div>
    </div>
</form>
```

### API Endpoints

The system exposes several API endpoints through `core/routes/ai_mentor.py` that enable web interface functionality:

```python
@ai_mentor_bp.route('/')
def dashboard():
    """Main AI Mentor dashboard"""
    try:
        recent_reports = get_recent_mentor_reports(7)
        today_session = get_trading_session_data(date.today())
        
        return render_template('ai_mentor/dashboard.html', 
                             recent_reports=recent_reports or [],
                             today_session=today_session,
                             win_rate=win_rate,
                             total_sessions=total_sessions)
    except Exception as e:
        logger.error(f"Error in AI mentor dashboard: {e}")
        return render_template('ai_mentor/dashboard.html', 
                             recent_reports=[], 
                             today_session=None,
                             win_rate=0, 
                             total_sessions=0)

@ai_mentor_bp.route('/today-report')
def today_report():
    """Generate AI report for today"""
    try:
        today = date.today()
        session_data = get_trading_session_data(today)
        
        mentor = IndonesianTradingMentorAI()
        trading_session = TradingSession(
            date=today,
            trades=session_data['trades'],
            emotions=session_data['emotions'],
            market_conditions=session_data['market_conditions'],
            profit_loss=session_data['total_profit_loss'],
            notes=session_data['personal_notes']
        )
        
        ai_report = mentor.generate_daily_report(trading_session)
        analysis = mentor.analyze_trading_session(trading_session)
        
        save_ai_mentor_report(session_data['session_id'], analysis)
        
        return render_template('ai_mentor/daily_report.html',
                             session_data=session_data,
                             ai_report=ai_report,
                             analysis=analysis)
                             
    except Exception as e:
        logger.error(f"Error generating today's AI report: {e}")
        flash("Gagal membuat laporan AI untuk hari ini", "error")
        return redirect(url_for('ai_mentor.dashboard'))

@ai_mentor_bp.route('/update-emotions', methods=['POST'])
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

@ai_mentor_bp.route('/api/generate-instant-feedback', methods=['POST'])
def generate_instant_feedback():
    """Generate instant AI feedback based on emotional input"""
    try:
        data = request.get_json()
        emotions = data.get('emotions', 'netral')
        notes = data.get('notes', '')
        current_pnl = data.get('current_pnl', 0)
        
        today_session = get_trading_session_data(date.today())
        
        mentor = IndonesianTradingMentorAI()
        
        temp_session = TradingSession(
            date=date.today(),
            trades=today_session.get('trades', []),
            emotions=emotions,
            market_conditions=today_session.get('market_conditions', 'normal'),
            profit_loss=current_pnl,
            notes=notes
        )
        
        analysis = mentor.analyze_trading_session(temp_session)
        
        return jsonify({
            'success': True,
            'feedback': {
                'emotional_analysis': analysis['emosi_vs_performa']['feedback'],
                'motivation': analysis['motivasi'],
                'quick_tips': analysis['rekomendasi'][:3]
            }
        })
        
    except Exception as e:
        logger.error(f"Error generating instant feedback: {e}")
        return jsonify({
            'success': False,
            'message': 'Failed to create AI feedback'
        }), 500
```

### Real-time Feedback System

The system includes a real-time feedback mechanism that provides immediate guidance to traders:

```javascript
function getInstantFeedback() {
    const formData = {
        emotions: selectedEmotionValue,
        notes: document.getElementById('personalNotes').value,
        current_pnl: parseFloat(document.getElementById('currentPnL').value) || 0
    };
    
    fetch('/ai-mentor/api/generate-instant-feedback', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(formData)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            const feedback = data.feedback;
            contentDiv.innerHTML = `
                <div class="space-y-3">
                    <div>
                        <strong class="text-blue-700">🧠 Emotional Analysis:</strong>
                        <p class="text-gray-700">${feedback.emotional_analysis}</p>
                    </div>
                    <div>
                        <strong class="text-green-700">💪 Motivation:</strong>
                        <p class="text-gray-700">${feedback.motivation}</p>
                    </div>
                    <div>
                        <strong class="text-purple-700">💡 Quick Tips:</strong>
                        <ul class="list-disc pl-5 text-gray-700">
                            ${feedback.quick_tips.map(tip => `<li>${tip}</li>`).join('')}
                        </ul>
                    </div>
                </div>
            `;
        } else {
            contentDiv.innerHTML = `<div class="text-red-600">❌ ${data.message}</div>`;
        }
    })
    .catch(error => {
        console.error('Error:', error);
        contentDiv.innerHTML = '<div class="text-red-600">❌ Failed to get feedback. Please try again.</div>';
    });
}
```

``mermaid
sequenceDiagram
participant User as Trader
participant UI as Web Interface
participant API as AI Mentor API
participant AI as IndonesianTradingMentorAI
User->>UI : Opens Quick Feedback Modal
UI->>User : Displays emotion selection buttons
User->>UI : Selects emotion and enters notes
UI->>API : POST /api/generate-instant-feedback
API->>AI : analyze_trading_session(temp_session)
AI->>API : Returns emotional analysis, motivation, and tips
API->>UI : Returns JSON with feedback
UI->>User : Displays instant AI feedback
User->>UI : Submits emotions and notes
UI->>API : POST /update-emotions
API->>DB : update_session_emotions_and_notes()
DB->>API : Success confirmation
API->>UI : Returns success message
UI->>User : Shows success alert and refreshes page
```

**Diagram sources**
- [ai_mentor.py](file://core/routes/ai_mentor.py#L189-L255) - *Added in commit a24fa8637bb6dc7c2f6d6fae6a633611836bf329*
- [quick_feedback.html](file://templates/ai_mentor/quick_feedback.html#L1-L166) - *Added in commit a24fa8637bb6dc7c2f6d6fae6a633611836bf329*

**Section sources**
- [ai_mentor.py](file://core/routes/ai_mentor.py#L1-L332) - *Added in commit a24fa8637bb6dc7c2f6d6fae6a633611836bf329*
- [dashboard.html](file://templates/ai_mentor/dashboard.html#L1-L287) - *Added in commit a24fa8637bb6dc7c2f6d6fae6a633611836bf329*
- [daily_report.html](file://templates/ai_mentor/daily_report.html#L1-L316) - *Added in commit a24fa8637bb6dc7c2f6d6fae6a633611836bf329*
- [quick_feedback.html](file://templates/ai_mentor/quick_feedback.html#L1-L166) - *Added in commit a24fa8637bb6dc7c2f6d6fae6a633611836bf329*

## Data Storage and Retrieval for AI Mentor

The Indonesian AI Trading Mentor System relies on a robust data storage and retrieval mechanism to maintain trading session data and AI analysis results.

### Database Schema

The system uses SQLite to store data in the `bots.db` database with the following key tables:

- **trading_sessions**: Stores information about each trading session
- **daily_trading_data**: Stores individual trade records for analysis
- **ai_mentor_reports**: Stores AI-generated analysis and recommendations

### Data Storage Functions

The system implements several functions in `core/db/models.py` to handle data persistence:

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

def log_trade_for_ai_analysis(bot_id: int, symbol: str, profit_loss: float, 
                              lot_size: float, stop_loss_used: bool = False,
                              take_profit_used: bool = False, risk_percent: float = 1.0,
                              strategy_used: str = '') -> None:
    """Log trade data for AI mentor analysis"""
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

def get_or_create_today_session() -> int:
    """Get today's session or create new if not exists"""
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

### Data Retrieval Functions

The system provides comprehensive functions for retrieving stored data:

```python
def get_trading_session_data(session_date: date) -> Optional[Dict[str, Any]]:
    """Retrieve trading session data for AI analysis"""
    try:
        with sqlite3.connect('bots.db') as conn:
            cursor = conn.cursor()
            
            # Check if table and columns exist
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='trading_sessions'")
            if not cursor.fetchone():
                print(f"[AI MENTOR DB ERROR] trading_sessions table not found")
                return None
            
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

def save_ai_mentor_report(session_id: int, analysis: Dict[str, Any]) -> bool:
    """Save AI mentor report to database"""
    try:
        with sqlite3.connect('bots.db') as conn:
            cursor = conn.cursor()
            cursor.execute(
                '''INSERT INTO ai_mentor_reports 
                   (session_id, trading_patterns_analysis, emotional_analysis,
                    risk_management_score, recommendations, motivation_message)
                   VALUES (?, ?, ?, ?, ?, ?)''',
                (session_id, 
                 json.dumps(analysis.get('pola_trading', {})),
                 json.dumps(analysis.get('emosi_vs_performa', {})),
                 analysis.get('manajemen_risiko', {}).get('nilai', '5/10'),
                 json.dumps(analysis.get('rekomendasi', [])),
                 analysis.get('motivasi', ''))
            )
            conn.commit()
            return True
    except Exception as e:
        print(f"[AI MENTOR DB ERROR] Failed to save AI report: {e}")
        return False

def get_recent_mentor_reports(limit: int = 7) -> List[Dict[str, Any]]:
    """Retrieve recent AI mentor reports"""
    try:
        with sqlite3.connect('bots.db') as conn:
            cursor = conn.cursor()
            
            # Adjust query based on available columns
            if 'total_profit_loss' in columns:
                profit_column = 'ts.total_profit_loss'
            else:
                profit_column = '0.0 as total_profit_loss'
                
            query = f'''
                SELECT ts.session_date, {profit_column}, ts.total_trades,
                       ts.emotions, COALESCE(mr.motivation_message, 'No AI analysis available') as motivation, mr.created_at
                FROM trading_sessions ts
                LEFT JOIN ai_mentor_reports mr ON ts.id = mr.session_id
                ORDER BY ts.session_date DESC
                LIMIT ?
            '''
            
            cursor.execute(query, (limit,))
            
            reports = []
            for row in cursor.fetchall():
                reports.append({
                    'session_date': row[0],
                    'profit_loss': row[1] if row[1] is not None else 0.0,
                    'total_trades': row[2] if row[2] is not None else 0,
                    'emotions': row[3] if row[3] else 'netral',
                    'motivation': row[4],
                    'created_at': row[5]
                })
            
            return reports
            
    except Exception as e:
        print(f"[AI MENTOR DB ERROR] Failed to retrieve recent reports: {e}")
        return []
```

### Data Flow Architecture

The data storage and retrieval system follows a well-defined architecture:

``mermaid
flowchart TD
A[Trading Bot Execution] --> B[Log Trade Data]
B --> C[Store in daily_trading_data]
C --> D[Update trading_sessions Summary]
E[User Interaction] --> F[Update Emotions & Notes]
F --> G[Update trading_sessions]
H[AI Mentor Analysis] --> I[Retrieve Session Data]
I --> J[Query trading_sessions & daily_trading_data]
J --> K[Generate AI Analysis]
K --> L[Store AI Report]
L --> M[Save to ai_mentor_reports]
N[Web Interface] --> O[Display Dashboard]
O --> P[Query Recent Reports]
P --> Q[Show AI Insights]
subgraph Database
direction TB
R[trading_sessions]
S[daily_trading_data]
T[ai_mentor_reports]
end
C --> R
D --> R
F --> R
I --> R
I --> S
L --> T
O --> T
```

**Diagram sources**
- [models.py](file://core/db/models.py#L26-L260) - *Updated in commit a24fa8637bb6dc7c2f6d6fae6a633611836bf329*

**Section sources**
- [models.py](file://core/db/models.py#L26-L260) - *Updated in commit a24fa8637bb6dc7c2f6d6fae6a633611836bf329*
- [trading_mentor_ai.py](file://core/ai/trading_mentor_ai.py#L1-L350) - *Added in commit a24fa8637bb6dc7c2f6d6fae6a633611836bf329*
- [ai_mentor.py](file://core/routes/ai_mentor.py#L1-L332) - *Added in commit a24fa8637bb6dc7c2f6d6fae6a633611836bf329*