# core/strategies/index_optimizations.py

"""
Stock Index Strategy Optimizations
Provides optimized parameters for trading stock indices like US30, US100, US500, DE30
"""

# Index-specific strategy parameters optimized for stock market characteristics
INDEX_STRATEGY_PARAMS = {
    'MA_CROSSOVER': {
        'US30': {
            'fast_period': 12,
            'slow_period': 26,
            'risk_percent': 0.5,
            'description': 'Dow Jones - Industrial focus, moderate volatility'
        },
        'US100': {
            'fast_period': 10,
            'slow_period': 22,
            'risk_percent': 0.7,
            'description': 'Nasdaq - Tech heavy, higher volatility'
        },
        'US500': {
            'fast_period': 12,
            'slow_period': 26,
            'risk_percent': 0.5,
            'description': 'S&P 500 - Broad market, balanced approach'
        },
        'DE30': {
            'fast_period': 14,
            'slow_period': 30,
            'risk_percent': 0.4,
            'description': 'DAX - European market, conservative approach'
        }
    },
    
    'TURTLE_BREAKOUT': {
        'US30': {
            'entry_period': 15,
            'exit_period': 8,
            'risk_percent': 0.6,
            'description': 'Dow breakouts - established trends'
        },
        'US100': {
            'entry_period': 12,
            'exit_period': 6,
            'risk_percent': 0.8,
            'description': 'Nasdaq breakouts - fast moving'
        },
        'US500': {
            'entry_period': 15,
            'exit_period': 8,
            'risk_percent': 0.6,
            'description': 'S&P breakouts - broad market momentum'
        },
        'DE30': {
            'entry_period': 18,
            'exit_period': 10,
            'risk_percent': 0.5,
            'description': 'DAX breakouts - European session'
        }
    },
    
    'QUANTUMBOTX_HYBRID': {
        'US30': {
            'adx_period': 12,
            'adx_threshold': 22,
            'ma_fast_period': 12,
            'ma_slow_period': 26,
            'bb_length': 18,
            'risk_percent': 0.5,
            'description': 'Adaptive Dow trading'
        },
        'US100': {
            'adx_period': 10,
            'adx_threshold': 24,
            'ma_fast_period': 10,
            'ma_slow_period': 22,
            'bb_length': 16,
            'risk_percent': 0.7,
            'description': 'Adaptive Nasdaq - higher sensitivity'
        },
        'US500': {
            'adx_period': 12,
            'adx_threshold': 22,
            'ma_fast_period': 12,
            'ma_slow_period': 26,
            'bb_length': 18,
            'risk_percent': 0.5,
            'description': 'Adaptive S&P 500'
        },
        'DE30': {
            'adx_period': 14,
            'adx_threshold': 20,
            'ma_fast_period': 14,
            'ma_slow_period': 30,
            'bb_length': 20,
            'risk_percent': 0.4,
            'description': 'Adaptive DAX - European session'
        }
    },
    
    'BOLLINGER_SQUEEZE': {
        'US30': {
            'bb_length': 16,
            'bb_std': 2.0,
            'squeeze_factor': 0.75,
            'squeeze_window': 8,
            'risk_percent': 0.6,
            'description': 'Dow volatility compression'
        },
        'US100': {
            'bb_length': 14,
            'bb_std': 2.2,
            'squeeze_factor': 0.8,
            'squeeze_window': 6,
            'risk_percent': 0.8,
            'description': 'Nasdaq squeeze - tech volatility'
        },
        'US500': {
            'bb_length': 16,
            'bb_std': 2.0,
            'squeeze_factor': 0.75,
            'squeeze_window': 8,
            'risk_percent': 0.6,
            'description': 'S&P squeeze trading'
        },
        'DE30': {
            'bb_length': 18,
            'bb_std': 1.8,
            'squeeze_factor': 0.7,
            'squeeze_window': 10,
            'risk_percent': 0.5,
            'description': 'DAX squeeze - European hours'
        }
    }
}

# Trading hour restrictions for different indices
INDEX_TRADING_HOURS = {
    'US30': {
        'market_open': '14:30',  # UTC
        'market_close': '21:00',  # UTC
        'pre_market': '08:00',   # UTC
        'post_market': '00:00',  # UTC next day
        'timezone': 'Eastern'
    },
    'US100': {
        'market_open': '14:30',
        'market_close': '21:00',
        'pre_market': '08:00',
        'post_market': '00:00',
        'timezone': 'Eastern'
    },
    'US500': {
        'market_open': '14:30',
        'market_close': '21:00',
        'pre_market': '08:00',
        'post_market': '00:00',
        'timezone': 'Eastern'
    },
    'DE30': {
        'market_open': '07:00',  # UTC
        'market_close': '15:30',  # UTC
        'pre_market': '06:00',
        'post_market': '16:00',
        'timezone': 'CET'
    }
}

# Risk management adjustments for indices
INDEX_RISK_ADJUSTMENTS = {
    'gap_protection': {
        'enabled': True,
        'max_overnight_exposure': 50,  # % of normal position
        'description': 'Reduce position size before market close'
    },
    'news_filter': {
        'enabled': True,
        'avoid_news_minutes': 30,  # Minutes before/after major news
        'description': 'Avoid trading during major economic announcements'
    },
    'volatility_filter': {
        'max_atr_multiplier': 3.0,  # Skip trades if ATR too high
        'description': 'Skip trades during extreme volatility'
    }
}

def get_index_params(strategy_name, symbol):
    """
    Get optimized parameters for a specific strategy and index
    
    Args:
        strategy_name (str): Strategy identifier (e.g., 'MA_CROSSOVER')
        symbol (str): Index symbol (e.g., 'US30')
    
    Returns:
        dict: Optimized parameters for the strategy-symbol combination
    """
    return INDEX_STRATEGY_PARAMS.get(strategy_name, {}).get(symbol, {})

def get_trading_hours(symbol):
    """Get trading hours for a specific index"""
    return INDEX_TRADING_HOURS.get(symbol, {})

def get_risk_adjustments():
    """Get index-specific risk management rules"""
    return INDEX_RISK_ADJUSTMENTS

def is_index_symbol(symbol):
    """Check if symbol is a stock index"""
    return symbol.upper() in ['US30', 'US100', 'US500', 'DE30', 'UK100', 'JP225', 'AUS200']

def get_recommended_strategies_for_index(symbol):
    """Get recommended strategies for a specific index, sorted by suitability"""
    recommendations = {
        'US30': [
            ('MA_CROSSOVER', 'Excellent for Dow trends'),
            ('TURTLE_BREAKOUT', 'Great for established moves'),
            ('QUANTUMBOTX_HYBRID', 'Adaptive to all conditions')
        ],
        'US100': [
            ('TURTLE_BREAKOUT', 'Perfect for tech volatility'),
            ('BOLLINGER_SQUEEZE', 'Excellent for Nasdaq gaps'),
            ('MA_CROSSOVER', 'Good for trending phases')
        ],
        'US500': [
            ('QUANTUMBOTX_HYBRID', 'Best for broad market'),
            ('MA_CROSSOVER', 'Excellent trend following'),
            ('TURTLE_BREAKOUT', 'Good momentum capture')
        ],
        'DE30': [
            ('MA_CROSSOVER', 'Conservative European approach'),
            ('QUANTUMBOTX_HYBRID', 'Adaptive to DAX patterns'),
            ('BOLLINGER_SQUEEZE', 'European session volatility')
        ]
    }
    
    return recommendations.get(symbol.upper(), [])

# Progressive learning path for index trading
INDEX_LEARNING_PATH = [
    {
        'week': 1,
        'strategy': 'MA_CROSSOVER',
        'symbol': 'US30',
        'description': 'Start with simple trend following on liquid Dow',
        'risk': 0.3,
        'focus': 'Learn index behavior vs forex'
    },
    {
        'week': 2,
        'strategy': 'MA_CROSSOVER',
        'symbol': 'US500',
        'description': 'Expand to broader S&P 500 market',
        'risk': 0.4,
        'focus': 'Compare different index characteristics'
    },
    {
        'week': 3,
        'strategy': 'TURTLE_BREAKOUT',
        'symbol': 'US100',
        'description': 'Learn breakout trading on volatile Nasdaq',
        'risk': 0.5,
        'focus': 'Understand tech sector dynamics'
    },
    {
        'week': 4,
        'strategy': 'QUANTUMBOTX_HYBRID',
        'symbol': 'US500',
        'description': 'Deploy adaptive strategy on proven market',
        'risk': 0.5,
        'focus': 'Multi-condition adaptation'
    },
    {
        'week': 5,
        'strategy': 'BOLLINGER_SQUEEZE',
        'symbol': 'DE30',
        'description': 'European market with volatility trading',
        'risk': 0.4,
        'focus': 'Different timezone and volatility patterns'
    }
]

def get_learning_path():
    """Get the progressive learning path for index trading"""
    return INDEX_LEARNING_PATH