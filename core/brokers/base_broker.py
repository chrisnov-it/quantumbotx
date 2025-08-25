# core/brokers/base_broker.py
"""
Universal Broker Interface for Multi-Platform Trading
Supports MT5, Binance, and other brokers through unified API
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Union
from enum import Enum
import pandas as pd
from datetime import datetime

class OrderType(Enum):
    MARKET_BUY = "market_buy"
    MARKET_SELL = "market_sell"
    LIMIT_BUY = "limit_buy"
    LIMIT_SELL = "limit_sell"
    STOP_LOSS = "stop_loss"
    TAKE_PROFIT = "take_profit"

class OrderStatus(Enum):
    PENDING = "pending"
    FILLED = "filled"
    CANCELLED = "cancelled"
    REJECTED = "rejected"

class Timeframe(Enum):
    M1 = "1m"
    M5 = "5m"
    M15 = "15m"
    M30 = "30m"
    H1 = "1h"
    H4 = "4h"
    D1 = "1d"

class Position:
    def __init__(self, symbol: str, side: str, size: float, entry_price: float, 
                 current_price: float, unrealized_pnl: float, realized_pnl: float = 0):
        self.symbol = symbol
        self.side = side  # 'long' or 'short'
        self.size = size
        self.entry_price = entry_price
        self.current_price = current_price
        self.unrealized_pnl = unrealized_pnl
        self.realized_pnl = realized_pnl
        self.timestamp = datetime.now()

class Order:
    def __init__(self, order_id: str, symbol: str, order_type: OrderType, 
                 side: str, size: float, price: Optional[float] = None):
        self.order_id = order_id
        self.symbol = symbol
        self.order_type = order_type
        self.side = side
        self.size = size
        self.price = price
        self.status = OrderStatus.PENDING
        self.filled_size = 0.0
        self.avg_fill_price = 0.0
        self.timestamp = datetime.now()

class AccountInfo:
    def __init__(self, balance: float, equity: float, margin: float, 
                 free_margin: float, margin_level: float, currency: str = "USD"):
        self.balance = balance
        self.equity = equity
        self.margin = margin
        self.free_margin = free_margin
        self.margin_level = margin_level
        self.currency = currency
        self.timestamp = datetime.now()

class BaseBroker(ABC):
    """
    Abstract base class for all broker implementations.
    Provides unified interface for MT5, Binance, and other brokers.
    """
    
    def __init__(self, broker_name: str):
        self.broker_name = broker_name
        self.is_connected = False
        self.supported_symbols = []
        
    @abstractmethod
    def connect(self, credentials: Dict) -> bool:
        """Connect to broker with credentials"""
        pass
    
    @abstractmethod
    def disconnect(self) -> bool:
        """Disconnect from broker"""
        pass
    
    @abstractmethod
    def get_symbols(self) -> List[str]:
        """Get list of available trading symbols"""
        pass
    
    @abstractmethod
    def get_market_data(self, symbol: str, timeframe: Timeframe, 
                       count: int = 500) -> pd.DataFrame:
        """
        Get OHLCV market data
        Returns: DataFrame with columns [time, open, high, low, close, volume]
        """
        pass
    
    @abstractmethod
    def get_current_price(self, symbol: str) -> Dict[str, float]:
        """
        Get current bid/ask prices
        Returns: {"bid": price, "ask": price}
        """
        pass
    
    @abstractmethod
    def place_order(self, symbol: str, order_type: OrderType, side: str,
                   size: float, price: Optional[float] = None,
                   stop_loss: Optional[float] = None,
                   take_profit: Optional[float] = None) -> Order:
        """Place a trading order"""
        pass
    
    @abstractmethod
    def cancel_order(self, order_id: str) -> bool:
        """Cancel an existing order"""
        pass
    
    @abstractmethod
    def get_positions(self) -> List[Position]:
        """Get all open positions"""
        pass
    
    @abstractmethod
    def get_orders(self) -> List[Order]:
        """Get all pending orders"""
        pass
    
    @abstractmethod
    def get_account_info(self) -> AccountInfo:
        """Get account information"""
        pass
    
    @abstractmethod
    def get_trade_history(self, days: int = 30) -> List[Dict]:
        """Get trade history"""
        pass
    
    # Utility methods (implemented in base class)
    def normalize_symbol(self, symbol: str) -> str:
        """Normalize symbol format for the broker"""
        return symbol.upper().replace("/", "").replace("-", "")
    
    def calculate_position_size(self, account_balance: float, risk_percent: float,
                              entry_price: float, stop_loss: float) -> float:
        """Calculate position size based on risk management"""
        risk_amount = account_balance * (risk_percent / 100)
        price_difference = abs(entry_price - stop_loss)
        
        if price_difference == 0:
            return 0
            
        position_size = risk_amount / price_difference
        return position_size
    
    def validate_symbol(self, symbol: str) -> bool:
        """Check if symbol is supported by broker"""
        return symbol in self.supported_symbols
    
    def is_market_open(self) -> bool:
        """Check if market is currently open (override for specific markets)"""
        return True  # Crypto markets are always open