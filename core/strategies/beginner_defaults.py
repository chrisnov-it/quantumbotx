# core/strategies/beginner_defaults.py
"""
🎓 Beginner-Friendly Strategy Defaults
Simplified parameters for new traders with educational explanations
"""

# Beginner-optimized defaults for each strategy
BEGINNER_DEFAULTS = {
    # ✅ RECOMMENDED FOR BEGINNERS (Simple & Effective)
    'MA_CROSSOVER': {
        'difficulty': 'BEGINNER',
        'recommended': True,
        'description': 'Simple trend following - When fast line crosses slow line',
        'params': {
            'fast_period': 10,  # Faster signals for beginners
            'slow_period': 30   # Shorter period for quicker feedback
        },
        'explanation': {
            'fast_period': 'Fast moving average (10 = responds quickly to price changes)',
            'slow_period': 'Slow moving average (30 = shows main trend direction)'
        }
    },
    
    'RSI_CROSSOVER': {
        'difficulty': 'BEGINNER',
        'recommended': True,
        'description': 'Momentum trading - Buy when momentum increases',
        'params': {
            'rsi_period': 14,        # Standard RSI
            'rsi_ma_period': 7,      # Faster MA for more signals
            'trend_filter_period': 30 # Shorter trend filter
        },
        'explanation': {
            'rsi_period': 'RSI calculation period (14 = standard)',
            'rsi_ma_period': 'Smooth RSI signals (7 = responsive)',
            'trend_filter_period': 'Main trend direction (30 = recent trend)'
        }
    },
    
    'TURTLE_BREAKOUT': {
        'difficulty': 'BEGINNER',
        'recommended': True,
        'description': 'Breakout trading - Buy when price breaks above recent highs',
        'params': {
            'entry_period': 15,  # Shorter for more signals
            'exit_period': 8     # Quicker exits
        },
        'explanation': {
            'entry_period': 'Breakout period (15 = look at last 15 bars)',
            'exit_period': 'Exit period (8 = quick profit taking)'
        }
    },
    
    # 📚 INTERMEDIATE (Good for learning)
    'BOLLINGER_REVERSION': {
        'difficulty': 'INTERMEDIATE',
        'recommended': False,
        'description': 'Mean reversion - Buy when price bounces from support',
        'params': {
            'bb_length': 20,
            'bb_std': 2.0,
            'trend_filter_period': 50  # Shorter for beginners
        },
        'explanation': {
            'bb_length': 'Bollinger Band period (20 = standard)',
            'bb_std': 'Band width (2.0 = captures 95% of price moves)',
            'trend_filter_period': 'Trend direction (50 = medium-term trend)'
        }
    },
    
    'PULSE_SYNC': {
        'difficulty': 'INTERMEDIATE',
        'recommended': False,
        'description': 'Multi-indicator confirmation - Multiple signals must agree',
        'params': {
            'trend_period': 50,      # Shorter trend
            'macd_fast': 12,
            'macd_slow': 26,
            'macd_signal': 9,
            'stoch_k': 14,
            'stoch_d': 3,
            'stoch_smooth': 3
        },
        'explanation': {
            'trend_period': 'Main trend (50 = intermediate trend)',
            'macd_fast': 'MACD fast line (12 = responsive)',
            'macd_slow': 'MACD slow line (26 = stable)',
            'macd_signal': 'MACD signal line (9 = trigger)',
            'stoch_k': 'Stochastic main line (14 = standard)',
            'stoch_d': 'Stochastic signal line (3 = smooth)',
            'stoch_smooth': 'Stochastic smoothing (3 = clean signals)'
        }
    },
    
    # 🎓 ADVANCED (For experienced traders)
    'QUANTUM_VELOCITY': {
        'difficulty': 'ADVANCED',
        'recommended': False,
        'description': 'Volatility breakout - Complex squeeze and breakout detection',
        'params': {
            'ema_period': 100,       # Shorter EMA for beginners
            'bb_length': 20,
            'bb_std': 2.0,
            'squeeze_window': 8,     # Shorter window
            'squeeze_factor': 0.8    # Less sensitive
        },
        'explanation': {
            'ema_period': 'Trend filter (100 = long-term direction)',
            'bb_length': 'Bollinger period (20 = standard)',
            'bb_std': 'Band sensitivity (2.0 = normal)',
            'squeeze_window': 'Squeeze detection (8 = recent compression)',
            'squeeze_factor': 'Squeeze threshold (0.8 = less sensitive)'
        }
    },
    
    'MERCY_EDGE': {
        'difficulty': 'ADVANCED',
        'recommended': False,
        'description': 'AI-enhanced multi-timeframe - Professional grade strategy',
        'params': {
            'macd_fast': 12,
            'macd_slow': 26,
            'macd_signal': 9,
            'stoch_k': 14,
            'stoch_d': 3,
            'stoch_smooth': 3
        },
        'explanation': {
            'macd_fast': 'MACD fast EMA (12 = quick response)',
            'macd_slow': 'MACD slow EMA (26 = trend stability)',
            'macd_signal': 'MACD signal line (9 = entry trigger)',
            'stoch_k': 'Stochastic K% (14 = momentum period)',
            'stoch_d': 'Stochastic D% (3 = signal smoothing)',
            'stoch_smooth': 'K% smoothing (3 = noise reduction)'
        }
    },
    
    'QUANTUMBOTX_CRYPTO': {
        'difficulty': 'EXPERT',
        'recommended': False,
        'description': 'Crypto specialist - Multiple indicators for volatile markets',
        'params': {
            'adx_period': 10,
            'adx_threshold': 20,
            'ma_fast_period': 12,
            'ma_slow_period': 26,
            'bb_length': 20,
            'bb_std': 2.2,
            'trend_filter_period': 50,  # Shorter for crypto
            'rsi_period': 14,
            'rsi_overbought': 70,       # Less extreme
            'rsi_oversold': 30,         # Less extreme
            'volatility_filter': 1.5,   # Less sensitive
            'weekend_mode': True
        },
        'explanation': {
            'adx_period': 'Trend strength period (10 = crypto responsive)',
            'adx_threshold': 'Minimum trend strength (20 = moderate)',
            'ma_fast_period': 'Fast moving average (12 = quick signals)',
            'ma_slow_period': 'Slow moving average (26 = trend filter)',
            'bb_length': 'Bollinger period (20 = standard)',
            'bb_std': 'Band width (2.2 = crypto volatility)',
            'trend_filter_period': 'Main trend (50 = crypto optimized)',
            'rsi_period': 'RSI calculation (14 = standard)',
            'rsi_overbought': 'Sell threshold (70 = moderate)',
            'rsi_oversold': 'Buy threshold (30 = moderate)',
            'volatility_filter': 'Volatility sensitivity (1.5 = balanced)',
            'weekend_mode': 'Weekend adjustments (True = safer)'
        }
    }
}

# Strategy recommendations based on experience level
STRATEGY_RECOMMENDATIONS = {
    'ABSOLUTE_BEGINNER': [
        'MA_CROSSOVER',      # Start here - simple and effective
        'TURTLE_BREAKOUT'    # Learn breakout concepts
    ],
    
    'BEGINNER': [
        'MA_CROSSOVER',
        'RSI_CROSSOVER',
        'TURTLE_BREAKOUT'
    ],
    
    'INTERMEDIATE': [
        'MA_CROSSOVER',
        'RSI_CROSSOVER', 
        'BOLLINGER_REVERSION',
        'PULSE_SYNC'
    ],
    
    'ADVANCED': [
        'QUANTUM_VELOCITY',
        'MERCY_EDGE',
        'ICHIMOKU_CLOUD'
    ],
    
    'EXPERT': [
        'QUANTUMBOTX_CRYPTO',
        'QUANTUMBOTX_HYBRID',
        'DYNAMIC_BREAKOUT'
    ]
}

# Educational tips for each difficulty level
LEARNING_TIPS = {
    'BEGINNER': [
        "🎯 Start with MA_CROSSOVER - it's the foundation of technical analysis",
        "📚 Learn one strategy well before moving to complex ones",
        "💡 Use small lot sizes (0.01) while learning",
        "📊 Always backtest before live trading",
        "🛡️ Set stop losses - never risk more than 2% per trade",
        "⚡ NEW: ATR-based risk management automatically protects you!",
        "🥇 Special protection for Gold (XAUUSD) prevents account blowouts",
        "📈 System calculates lot sizes based on volatility - genius!"
    ],
    
    'INTERMEDIATE': [
        "🔄 Try different strategies on demo account first",
        "📈 Learn to identify market conditions (trending vs ranging)",
        "⚖️ Understand risk-to-reward ratios (aim for 1:2 minimum)",
        "📋 Keep a trading journal to track performance",
        "🎨 Combine strategies for different market conditions",
        "🧮 Master ATR multipliers for different market conditions",
        "📊 Learn to read ATR values to gauge market volatility"
    ],
    
    'ADVANCED': [
        "🧠 Focus on risk management over profit maximization", 
        "📊 Use multiple timeframe analysis",
        "🔍 Optimize parameters based on market conditions",
        "💼 Consider portfolio-level risk management",
        "🚀 Explore algorithmic trading concepts",
        "⚡ Create custom ATR-based position sizing rules",
        "🎯 Develop market-specific risk management systems"
    ]
}

# ATR-Based Risk Management Education
ATR_EDUCATION = {
    'concept_explanation': {
        'simple': 'ATR = How much price typically moves each day',
        'detailed': [
            '📊 ATR measures average daily price movement',
            '🔍 High ATR = Volatile market (big swings)',
            '🔍 Low ATR = Calm market (small movements)',
            '🎯 Used to set smart stop losses and take profits',
            '🛡️ Automatically adjusts position size to market conditions'
        ]
    },
    'examples': {
        'EURUSD': {
            'typical_atr': '50 pips (0.0050)',
            'risk_example': '1% risk = $100 max loss on $10,000 account',
            'sl_distance': '2x ATR = 100 pips stop loss',
            'tp_distance': '4x ATR = 200 pips take profit',
            'explanation': 'Stable forex pair - normal parameters work well'
        },
        'XAUUSD': {
            'typical_atr': '$15 (very high!)',
            'risk_example': '1% risk CAPPED for safety',
            'sl_distance': '1x ATR = $15 stop loss (reduced for safety)',
            'tp_distance': '2x ATR = $30 take profit (conservative)',
            'explanation': '🥇 System automatically protects you from gold volatility!'
        }
    },
    'protection_features': [
        '🛡️ Automatic risk capping for volatile instruments',
        '🥇 Special gold protection prevents account blowouts',
        '📉 Dynamic position sizing based on market volatility',
        '🚨 Emergency brake system skips dangerous trades',
        '📊 Real-time risk calculation and logging'
    ]
}

def get_beginner_defaults(strategy_name: str) -> dict:
    """Get beginner-friendly defaults for a strategy"""
    return BEGINNER_DEFAULTS.get(strategy_name, {})

def get_strategy_recommendations(level: str) -> list:
    """Get recommended strategies for experience level"""
    return STRATEGY_RECOMMENDATIONS.get(level.upper(), [])

def get_learning_tips(level: str) -> list:
    """Get learning tips for experience level"""
    return LEARNING_TIPS.get(level.upper(), [])

def is_beginner_friendly(strategy_name: str) -> bool:
    """Check if strategy is beginner-friendly"""
    strategy_info = BEGINNER_DEFAULTS.get(strategy_name, {})
    return strategy_info.get('difficulty') == 'BEGINNER'

def get_strategy_explanation(strategy_name: str, param_name: str) -> str:
    """Get explanation for a specific parameter"""
    strategy_info = BEGINNER_DEFAULTS.get(strategy_name, {})
    explanations = strategy_info.get('explanation', {})
    return explanations.get(param_name, f"Parameter: {param_name}")

def get_atr_education_info() -> dict:
    """Get ATR education information for beginners"""
    return ATR_EDUCATION

def explain_atr_for_beginners(symbol: str = 'EURUSD') -> dict:
    """Get beginner-friendly ATR explanation with examples"""
    examples = ATR_EDUCATION['examples']
    return {
        'concept': ATR_EDUCATION['concept_explanation'],
        'example': examples.get(symbol, examples['EURUSD']),
        'protection_features': ATR_EDUCATION['protection_features']
    }