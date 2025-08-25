# core/brokers/broker_factory.py
"""
Broker Factory for QuantumBotX
Manages multiple brokers and provides unified interface
"""

import logging
from typing import Dict, Optional, List
from enum import Enum

from .base_broker import BaseBroker
from .binance_broker import BinanceBroker
from .ctrader_broker import CTraderBroker
from .interactive_brokers import InteractiveBrokersBroker
from .tradingview_broker import TradingViewBroker
from .indonesian_brokers import (
    IndopremierBroker, XMIndonesiaBroker, 
    OctaFXIndonesiaBroker, HSBCIndonesiaBroker
)

logger = logging.getLogger(__name__)

class BrokerType(Enum):
    MT5 = "mt5"
    BINANCE = "binance"
    BINANCE_FUTURES = "binance_futures"
    CTRADER = "ctrader"
    INTERACTIVE_BROKERS = "interactive_brokers"
    TRADINGVIEW = "tradingview"
    # Indonesian brokers
    INDOPREMIER = "indopremier"
    XM_INDONESIA = "xm_indonesia"
    OCTAFX_INDONESIA = "octafx_indonesia"
    HSBC_INDONESIA = "hsbc_indonesia"

class BrokerFactory:
    """
    Factory class to create and manage different broker instances
    """
    
    _brokers: Dict[str, BaseBroker] = {}
    _configs: Dict[str, Dict] = {}
    
    @classmethod
    def register_broker_config(cls, broker_id: str, broker_type: BrokerType, config: Dict):
        """Register broker configuration"""
        cls._configs[broker_id] = {
            'type': broker_type,
            'config': config
        }
    
    @classmethod
    def create_broker(cls, broker_id: str) -> Optional[BaseBroker]:
        """Create broker instance from registered configuration"""
        
        if broker_id in cls._brokers:
            return cls._brokers[broker_id]
        
        if broker_id not in cls._configs:
            logger.error(f"No configuration found for broker: {broker_id}")
            return None
        
        broker_config = cls._configs[broker_id]
        broker_type = broker_config['type']
        config = broker_config['config']
        
        try:
            if broker_type == BrokerType.BINANCE:
                broker = BinanceBroker(testnet=config.get('testnet', True))
            elif broker_type == BrokerType.BINANCE_FUTURES:
                # Future implementation
                broker = BinanceBroker(testnet=config.get('testnet', True))
            elif broker_type == BrokerType.CTRADER:
                broker = CTraderBroker(demo=config.get('demo', True))
            elif broker_type == BrokerType.INTERACTIVE_BROKERS:
                broker = InteractiveBrokersBroker(paper_trading=config.get('paper_trading', True))
            elif broker_type == BrokerType.TRADINGVIEW:
                broker = TradingViewBroker(paper_trading=config.get('paper_trading', True))
            elif broker_type == BrokerType.INDOPREMIER:
                broker = IndopremierBroker(demo=config.get('demo', True))
            elif broker_type == BrokerType.XM_INDONESIA:
                broker = XMIndonesiaBroker(demo=config.get('demo', True))
            elif broker_type == BrokerType.OCTAFX_INDONESIA:
                broker = OctaFXIndonesiaBroker(demo=config.get('demo', True))
            elif broker_type == BrokerType.HSBC_INDONESIA:
                broker = HSBCIndonesiaBroker(demo=config.get('demo', True))
            elif broker_type == BrokerType.MT5:
                # Import MT5 broker when implemented
                from .mt5_broker import MT5Broker
                broker = MT5Broker()
            else:
                logger.error(f"Unsupported broker type: {broker_type}")
                return None
            
            # Connect broker
            if broker.connect(config.get('credentials', {})):
                cls._brokers[broker_id] = broker
                logger.info(f"Successfully created and connected broker: {broker_id}")
                return broker
            else:
                logger.error(f"Failed to connect broker: {broker_id}")
                return None
                
        except Exception as e:
            logger.error(f"Error creating broker {broker_id}: {e}")
            return None
    
    @classmethod
    def get_broker(cls, broker_id: str) -> Optional[BaseBroker]:
        """Get existing broker instance"""
        return cls._brokers.get(broker_id)
    
    @classmethod
    def disconnect_all(cls):
        """Disconnect all brokers"""
        for broker_id, broker in cls._brokers.items():
            try:
                broker.disconnect()
                logger.info(f"Disconnected broker: {broker_id}")
            except Exception as e:
                logger.error(f"Error disconnecting broker {broker_id}: {e}")
        
        cls._brokers.clear()
    
    @classmethod
    def get_all_brokers(cls) -> Dict[str, BaseBroker]:
        """Get all connected brokers"""
        return cls._brokers.copy()
    
    @classmethod
    def get_supported_symbols(cls, broker_id: str) -> List[str]:
        """Get supported symbols for a broker"""
        broker = cls.get_broker(broker_id)
        if broker:
            return broker.get_symbols()
        return []
    
    @classmethod
    def is_broker_connected(cls, broker_id: str) -> bool:
        """Check if broker is connected"""
        broker = cls.get_broker(broker_id)
        return broker.is_connected if broker else False

# Configuration helper functions
def setup_demo_brokers():
    """Setup demo brokers for testing"""
    
    # Binance Testnet configuration
    BrokerFactory.register_broker_config(
        broker_id="binance_testnet",
        broker_type=BrokerType.BINANCE,
        config={
            'testnet': True,
            'credentials': {
                'api_key': '',  # Add your testnet API key
                'secret_key': ''  # Add your testnet secret key
            }
        }
    )
    
    # MT5 Demo configuration
    BrokerFactory.register_broker_config(
        broker_id="mt5_demo",
        broker_type=BrokerType.MT5,
        config={
            'credentials': {
                'login': '',  # Add your MT5 demo login
                'password': '',  # Add your MT5 demo password
                'server': 'MetaQuotes-Demo'
            }
        }
    )

def load_brokers_from_env():
    """Load broker configurations from environment variables"""
    import os
    
    # Binance configuration
    binance_api_key = os.getenv('BINANCE_API_KEY')
    binance_secret = os.getenv('BINANCE_SECRET_KEY')
    binance_testnet = os.getenv('BINANCE_TESTNET', 'true').lower() == 'true'
    
    if binance_api_key and binance_secret:
        BrokerFactory.register_broker_config(
            broker_id="binance",
            broker_type=BrokerType.BINANCE,
            config={
                'testnet': binance_testnet,
                'credentials': {
                    'api_key': binance_api_key,
                    'secret_key': binance_secret
                }
            }
        )
    
    # MT5 configuration
    mt5_login = os.getenv('MT5_LOGIN')
    mt5_password = os.getenv('MT5_PASSWORD')
    mt5_server = os.getenv('MT5_SERVER', 'MetaQuotes-Demo')
    
    if mt5_login and mt5_password:
        BrokerFactory.register_broker_config(
            broker_id="mt5",
            broker_type=BrokerType.MT5,
            config={
                'credentials': {
                    'login': mt5_login,
                    'password': mt5_password,
                    'server': mt5_server
                }
            }
        )

# Example usage
if __name__ == "__main__":
    # Load configurations
    load_brokers_from_env()
    
    # Create brokers
    binance_broker = BrokerFactory.create_broker("binance")
    mt5_broker = BrokerFactory.create_broker("mt5")
    
    if binance_broker:
        print(f"Binance connected: {binance_broker.is_connected}")
        symbols = binance_broker.get_symbols()[:10]  # First 10 symbols
        print(f"Binance symbols: {symbols}")
    
    if mt5_broker:
        print(f"MT5 connected: {mt5_broker.is_connected}")
        account_info = mt5_broker.get_account_info()
        print(f"MT5 balance: {account_info.balance}")
    
    # Cleanup
    BrokerFactory.disconnect_all()