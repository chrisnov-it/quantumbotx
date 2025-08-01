# core/strategies/strategy_map.py

# Import the STRATEGY CLASSES, not the old analyze functions.
from .ma_crossover import MACrossoverStrategy
from .quantumbotx_hybrid import QuantumBotXHybridStrategy
from .rsi_breakout import RSIBreakoutStrategy
from .bollinger_bands import BollingerBandsStrategy
from .bollinger_squeeze import BollingerSqueezeStrategy
from .mercy_edge import MercyEdgeStrategy
from .quantum_velocity import QuantumVelocityStrategy
from .pulse_sync import PulseSyncStrategy

STRATEGY_MAP = {
    # The map is now a simple key-to-class mapping.
    'MA_CROSSOVER': MACrossoverStrategy,
    'QUANTUMBOTX_HYBRID': QuantumBotXHybridStrategy,
    'RSI_BREAKOUT': RSIBreakoutStrategy,
    'BOLLINGER_BANDS': BollingerBandsStrategy,
    'BOLLINGER_SQUEEZE': BollingerSqueezeStrategy,
    'MERCY_EDGE': MercyEdgeStrategy,
    'quantum_velocity': QuantumVelocityStrategy, # <-- Tambahkan strategi baru
    'PULSE_SYNC': PulseSyncStrategy,
}

# NOTE: You will need to refactor your other strategy files
