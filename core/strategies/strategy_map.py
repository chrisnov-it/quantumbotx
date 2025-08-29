# core/strategies/strategy_map.py

from .ma_crossover import MACrossoverStrategy
from .quantumbotx_hybrid import QuantumBotXHybridStrategy
from .quantumbotx_crypto import QuantumBotXCryptoStrategy
from .rsi_crossover import RSICrossoverStrategy
from .bollinger_reversion import BollingerBandsStrategy
from .bollinger_squeeze import BollingerSqueezeStrategy
from .mercy_edge import MercyEdgeStrategy
from .quantum_velocity import QuantumVelocityStrategy
from .pulse_sync import PulseSyncStrategy
from .turtle_breakout import TurtleBreakoutStrategy
from .ichimoku_cloud import IchimokuCloudStrategy
from .dynamic_breakout import DynamicBreakoutStrategy
from .index_momentum import IndexMomentumStrategy
from .index_breakout_pro import IndexBreakoutProStrategy
from .beginner_defaults import BEGINNER_DEFAULTS
from .strategy_selector import StrategySelector

STRATEGY_MAP = {
    'MA_CROSSOVER': MACrossoverStrategy,
    'QUANTUMBOTX_HYBRID': QuantumBotXHybridStrategy,
    'QUANTUMBOTX_CRYPTO': QuantumBotXCryptoStrategy,
    'RSI_CROSSOVER': RSICrossoverStrategy,
    'BOLLINGER_REVERSION': BollingerBandsStrategy,
    'BOLLINGER_SQUEEZE': BollingerSqueezeStrategy,
    'MERCY_EDGE': MercyEdgeStrategy,
    'quantum_velocity': QuantumVelocityStrategy,
    'PULSE_SYNC': PulseSyncStrategy,
    'TURTLE_BREAKOUT': TurtleBreakoutStrategy,
    'ICHIMOKU_CLOUD': IchimokuCloudStrategy,
    'DYNAMIC_BREAKOUT': DynamicBreakoutStrategy,
    'INDEX_MOMENTUM': IndexMomentumStrategy,
    'INDEX_BREAKOUT_PRO': IndexBreakoutProStrategy,
}

# Beginner-friendly strategy metadata
STRATEGY_METADATA = {
    # ✅ BEGINNER FRIENDLY
    'MA_CROSSOVER': {
        'difficulty': 'BEGINNER',
        'complexity_score': 2,
        'recommended_for_beginners': True,
        'description': 'Simple trend following - perfect first strategy',
        'market_types': ['FOREX', 'GOLD', 'CRYPTO'],
        'learning_priority': 1
    },
    'RSI_CROSSOVER': {
        'difficulty': 'BEGINNER',
        'complexity_score': 3,
        'recommended_for_beginners': True,
        'description': 'Momentum analysis - great second strategy',
        'market_types': ['FOREX', 'GOLD'],
        'learning_priority': 2
    },
    'TURTLE_BREAKOUT': {
        'difficulty': 'BEGINNER',
        'complexity_score': 2,
        'recommended_for_beginners': True,
        'description': 'Breakout trading - excellent for trending markets',
        'market_types': ['GOLD', 'FOREX'],
        'learning_priority': 3
    },
    
    # 📚 INTERMEDIATE
    'BOLLINGER_REVERSION': {
        'difficulty': 'INTERMEDIATE',
        'complexity_score': 3,
        'recommended_for_beginners': False,
        'description': 'Mean reversion - good for ranging markets',
        'market_types': ['FOREX'],
        'learning_priority': 4
    },
    'PULSE_SYNC': {
        'difficulty': 'INTERMEDIATE',
        'complexity_score': 7,
        'recommended_for_beginners': False,
        'description': 'Multi-indicator confirmation - solid intermediate strategy',
        'market_types': ['FOREX', 'GOLD'],
        'learning_priority': 5
    },
    'ICHIMOKU_CLOUD': {
        'difficulty': 'INTERMEDIATE',
        'complexity_score': 4,
        'recommended_for_beginners': False,
        'description': 'Japanese technical analysis - comprehensive system',
        'market_types': ['FOREX', 'GOLD'],
        'learning_priority': 6
    },
    'BOLLINGER_SQUEEZE': {
        'difficulty': 'INTERMEDIATE',
        'complexity_score': 5,
        'recommended_for_beginners': False,
        'description': 'Volatility compression trading',
        'market_types': ['GOLD', 'CRYPTO'],
        'learning_priority': 7
    },
    
    # 🎓 ADVANCED
    'QUANTUM_VELOCITY': {
        'difficulty': 'ADVANCED',
        'complexity_score': 5,
        'recommended_for_beginners': False,
        'description': 'Advanced volatility breakout system',
        'market_types': ['GOLD', 'CRYPTO'],
        'learning_priority': 8
    },
    'MERCY_EDGE': {
        'difficulty': 'ADVANCED',
        'complexity_score': 6,
        'recommended_for_beginners': False,
        'description': 'AI-enhanced multi-timeframe analysis',
        'market_types': ['FOREX', 'GOLD'],
        'learning_priority': 9
    },
    'DYNAMIC_BREAKOUT': {
        'difficulty': 'ADVANCED',
        'complexity_score': 6,
        'recommended_for_beginners': False,
        'description': 'Dynamic breakout detection',
        'market_types': ['GOLD', 'CRYPTO'],
        'learning_priority': 10
    },
    
    # 🚀 EXPERT
    'QUANTUMBOTX_HYBRID': {
        'difficulty': 'EXPERT',
        'complexity_score': 8,
        'recommended_for_beginners': False,
        'description': 'Multi-asset adaptive strategy',
        'market_types': ['FOREX', 'GOLD', 'CRYPTO'],
        'learning_priority': 11
    },
    'QUANTUMBOTX_CRYPTO': {
        'difficulty': 'EXPERT',
        'complexity_score': 12,
        'recommended_for_beginners': False,
        'description': 'Crypto-specialized advanced system',
        'market_types': ['CRYPTO'],
        'learning_priority': 12
    },
    
    # 📈 INDEX SPECIALISTS
    'INDEX_MOMENTUM': {
        'difficulty': 'INTERMEDIATE',
        'complexity_score': 4,
        'recommended_for_beginners': False,
        'description': 'Stock index momentum with gap detection',
        'market_types': ['INDICES'],
        'learning_priority': 8
    },
    'INDEX_BREAKOUT_PRO': {
        'difficulty': 'ADVANCED',
        'complexity_score': 7,
        'recommended_for_beginners': False,
        'description': 'Professional index breakout with institutional analysis',
        'market_types': ['INDICES'],
        'learning_priority': 10
    }
}

def get_beginner_strategies():
    """Get strategies recommended for beginners"""
    return [name for name, info in STRATEGY_METADATA.items() 
            if info['recommended_for_beginners']]

def get_strategies_by_difficulty(difficulty):
    """Get strategies by difficulty level"""
    return [name for name, info in STRATEGY_METADATA.items() 
            if info['difficulty'] == difficulty.upper()]

def get_strategies_for_market(market_type):
    """Get strategies suitable for specific market type"""
    market_upper = market_type.upper()
    
    # Handle index symbols by converting to INDICES market type
    if market_upper in ['US30', 'US100', 'US500', 'DE30', 'UK100', 'JP225']:
        market_upper = 'INDICES'
    
    return [name for name, info in STRATEGY_METADATA.items() 
            if market_upper in info['market_types']]

def get_strategy_info(strategy_name):
    """Get complete strategy information"""
    metadata = STRATEGY_METADATA.get(strategy_name, {})
    beginner_info = BEGINNER_DEFAULTS.get(strategy_name, {})
    
    return {
        'strategy_class': STRATEGY_MAP.get(strategy_name),
        'metadata': metadata,
        'beginner_info': beginner_info
    }
