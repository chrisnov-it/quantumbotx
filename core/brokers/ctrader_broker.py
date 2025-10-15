# core/brokers/ctrader_broker.py
"""
cTrader Broker Integration for QuantumBotX
Modern forex/CFD platform with excellent API
"""

import pandas as pd
import time
import requests
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging

from .base_broker import (
    BaseBroker, OrderType, OrderStatus, Timeframe, 
    Position, Order, AccountInfo
)

logger = logging.getLogger(__name__)

class CTraderBroker(BaseBroker):
    """
    cTrader (cTID) implementation of the universal broker interface.
    Uses cTrader REST API for modern forex trading.
    """
    
    def __init__(self, demo: bool = True):
        super().__init__("cTrader")
        self.demo = demo
        self.client_id = None
        self.client_secret = None
        self.access_token = None
        self.account_id = None
        self.base_url = "https://demo-api.ctraderapi.com" if demo else "https://api.ctraderapi.com"
        
        # Timeframe mapping
        self.timeframe_map = {
            Timeframe.M1: "M1",
            Timeframe.M5: "M5", 
            Timeframe.M15: "M15",
            Timeframe.M30: "M30",
            Timeframe.H1: "H1",
            Timeframe.H4: "H4",
            Timeframe.D1: "D1"
        }
    
    def connect(self, credentials: Dict) -> bool:
        """
        Connect to cTrader with OAuth credentials
        credentials: {"client_id": "...", "client_secret": "...", "account_id": "..."}
        """
        try:
            self.client_id = credentials.get("client_id")
            self.client_secret = credentials.get("client_secret")
            self.account_id = credentials.get("account_id")
            
            if not all([self.client_id, self.client_secret, self.account_id]):
                logger.error("cTrader client_id, client_secret, and account_id are required")
                return False
            
            # OAuth token request
            token_url = f"{self.base_url}/oauth/v2/token"
            token_data = {
                'grant_type': 'client_credentials',
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'scope': 'trading'
            }
            
            response = requests.post(token_url, data=token_data)
            
            if response.status_code == 200:
                token_info = response.json()
                self.access_token = token_info['access_token']
                self.is_connected = True
                
                # Get supported symbols
                self._load_symbols()
                
                logger.info(f"Connected to cTrader {'Demo' if self.demo else 'Live'}")
                return True
            else:
                logger.error(f"cTrader authentication failed: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to connect to cTrader: {e}")
            self.is_connected = False
            return False
    
    def disconnect(self) -> bool:
        """Disconnect from cTrader"""
        self.access_token = None
        self.is_connected = False
        logger.info("Disconnected from cTrader")
        return True
    
    def _make_request(self, endpoint: str, method: str = "GET", data: Dict = None) -> Dict:
        """Make authenticated request to cTrader API"""
        if not self.access_token:
            raise Exception("Not authenticated with cTrader")
        
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }
        
        url = f"{self.base_url}{endpoint}"
        
        if method == "GET":
            response = requests.get(url, headers=headers, params=data)
        elif method == "POST":
            response = requests.post(url, headers=headers, json=data)
        elif method == "PUT":
            response = requests.put(url, headers=headers, json=data)
        elif method == "DELETE":
            response = requests.delete(url, headers=headers)
        
        if response.status_code in [200, 201]:
            return response.json()
        else:
            raise Exception(f"cTrader API error: {response.status_code} - {response.text}")
    
    def _load_symbols(self):
        """Load available symbols from cTrader"""
        try:
            symbols_data = self._make_request("/v2/symbols")
            self.supported_symbols = [s['symbolName'] for s in symbols_data.get('symbols', [])]
        except Exception as e:
            logger.warning(f"Failed to load cTrader symbols: {e}")
            # Common forex symbols as fallback
            self.supported_symbols = [
                'EURUSD', 'GBPUSD', 'USDJPY', 'USDCHF', 'AUDUSD', 'USDCAD',
                'NZDUSD', 'EURGBP', 'EURJPY', 'GBPJPY', 'XAUUSD', 'XAGUSD'
            ]
    
    def get_symbols(self) -> List[str]:
        """Get list of available trading symbols"""
        return self.supported_symbols
    
    def get_market_data(self, symbol: str, timeframe: Timeframe, count: int = 500) -> pd.DataFrame:
        """Get OHLCV market data from cTrader"""
        if not self.is_connected:
            raise Exception("Not connected to cTrader")
        
        try:
            # Convert timeframe
            ct_timeframe = self.timeframe_map[timeframe]
            
            # Calculate from time (count bars back)
            now = datetime.utcnow()
            # Estimate time per bar
            minutes_per_bar = {
                'M1': 1, 'M5': 5, 'M15': 15, 'M30': 30,
                'H1': 60, 'H4': 240, 'D1': 1440
            }
            
            minutes_back = count * minutes_per_bar.get(ct_timeframe, 60)
            from_time = now - timedelta(minutes=minutes_back)
            
            # Request historical data
            params = {
                'symbolName': symbol,
                'periodName': ct_timeframe,
                'fromTimestamp': int(from_time.timestamp() * 1000),
                'toTimestamp': int(now.timestamp() * 1000),
                'count': count
            }
            
            data = self._make_request("/v2/bars", params=params)
            bars = data.get('bars', [])
            
            if not bars:
                return pd.DataFrame()
            
            # Convert to DataFrame
            df_data = []
            for bar in bars:
                df_data.append({
                    'time': datetime.fromtimestamp(bar['timestamp'] / 1000),
                    'open': bar['open'],
                    'high': bar['high'],
                    'low': bar['low'],
                    'close': bar['close'],
                    'volume': bar.get('volume', 0)
                })
            
            return pd.DataFrame(df_data)
            
        except Exception as e:
            logger.error(f"Failed to get market data for {symbol}: {e}")
            return pd.DataFrame()
    
    def get_current_price(self, symbol: str) -> Dict[str, float]:
        """Get current bid/ask prices"""
        if not self.is_connected:
            raise Exception("Not connected to cTrader")
        
        try:
            data = self._make_request(f"/v2/symbols/{symbol}/tick")
            return {
                "bid": data['bid'],
                "ask": data['ask']
            }
        except Exception as e:
            logger.error(f"Failed to get current price for {symbol}: {e}")
            return {"bid": 0.0, "ask": 0.0}
    
    def place_order(self, symbol: str, order_type: OrderType, side: str,
                   size: float, price: Optional[float] = None,
                   stop_loss: Optional[float] = None,
                   take_profit: Optional[float] = None) -> Order:
        """Place a trading order on cTrader"""
        if not self.is_connected:
            raise Exception("Not connected to cTrader")
        
        try:
            # Convert order parameters
            ct_side = "BUY" if side.lower() == "buy" else "SELL"
            
            # Convert volume to lots (cTrader uses volume in units)
            volume = int(size * 100000)  # Convert lots to units
            
            # Determine order type
            if order_type in [OrderType.MARKET_BUY, OrderType.MARKET_SELL]:
                ct_type = "MARKET"
            elif order_type in [OrderType.LIMIT_BUY, OrderType.LIMIT_SELL]:
                ct_type = "LIMIT"
            else:
                raise ValueError(f"Unsupported order type: {order_type}")
            
            # Prepare order data
            order_data = {
                'accountId': self.account_id,
                'symbolName': symbol,
                'orderType': ct_type,
                'tradeSide': ct_side,
                'volume': volume,
            }
            
            if ct_type == "LIMIT" and price:
                order_data['limitPrice'] = price
            
            if stop_loss:
                order_data['stopLoss'] = stop_loss
            if take_profit:
                order_data['takeProfit'] = take_profit
            
            # Place order
            result = self._make_request("/v2/orders", method="POST", data=order_data)
            
            # Create Order object
            order = Order(
                order_id=str(result.get('orderId', 'unknown')),
                symbol=symbol,
                order_type=order_type,
                side=side.lower(),
                size=size,
                price=price
            )
            
            order.status = OrderStatus.PENDING
            if result.get('executionType') == 'TRADE':
                order.status = OrderStatus.FILLED
            
            logger.info(f"cTrader order placed: {order.order_id} for {symbol}")
            return order
            
        except Exception as e:
            logger.error(f"Failed to place cTrader order: {e}")
            order = Order(
                order_id="failed",
                symbol=symbol,
                order_type=order_type,
                side=side.lower(),
                size=size,
                price=price
            )
            order.status = OrderStatus.REJECTED
            return order
    
    def cancel_order(self, order_id: str) -> bool:
        """Cancel an existing order"""
        if not self.is_connected:
            return False
        
        try:
            self._make_request(f"/v2/orders/{order_id}", method="DELETE")
            return True
        except Exception as e:
            logger.error(f"Failed to cancel cTrader order {order_id}: {e}")
            return False
    
    def get_positions(self) -> List[Position]:
        """Get all open positions"""
        if not self.is_connected:
            return []
        
        try:
            data = self._make_request(f"/v2/accounts/{self.account_id}/positions")
            positions = []
            
            for pos_data in data.get('positions', []):
                position = Position(
                    symbol=pos_data['symbolName'],
                    side='long' if pos_data['tradeSide'] == 'BUY' else 'short',
                    size=pos_data['volume'] / 100000,  # Convert units to lots
                    entry_price=pos_data['entryPrice'],
                    current_price=pos_data['currentPrice'],
                    unrealized_pnl=pos_data['unrealizedGrossProfit']
                )
                positions.append(position)
            
            return positions
            
        except Exception as e:
            logger.error(f"Failed to get cTrader positions: {e}")
            return []
    
    def get_orders(self) -> List[Order]:
        """Get all pending orders"""
        if not self.is_connected:
            return []
        
        try:
            data = self._make_request(f"/v2/accounts/{self.account_id}/orders")
            orders = []
            
            for order_data in data.get('orders', []):
                order = Order(
                    order_id=str(order_data['orderId']),
                    symbol=order_data['symbolName'],
                    order_type=OrderType.LIMIT_BUY,  # Simplified
                    side=order_data['tradeSide'].lower(),
                    size=order_data['volume'] / 100000,
                    price=order_data.get('limitPrice')
                )
                order.status = OrderStatus.PENDING
                orders.append(order)
            
            return orders
            
        except Exception as e:
            logger.error(f"Failed to get cTrader orders: {e}")
            return []
    
    def get_account_info(self) -> AccountInfo:
        """Get account information"""
        if not self.is_connected:
            return AccountInfo(0, 0, 0, 0, 0, "USD")
        
        try:
            data = self._make_request(f"/v2/accounts/{self.account_id}")
            
            balance = data.get('balance', 0)
            equity = data.get('equity', balance)
            margin = data.get('margin', 0)
            free_margin = data.get('freeMargin', balance)
            margin_level = data.get('marginLevel', 100)
            currency = data.get('currency', 'USD')
            
            return AccountInfo(
                balance=balance,
                equity=equity,
                margin=margin,
                free_margin=free_margin,
                margin_level=margin_level,
                currency=currency
            )
            
        except Exception as e:
            logger.error(f"Failed to get cTrader account info: {e}")
            return AccountInfo(0, 0, 0, 0, 0, "USD")
    
    def get_trade_history(self, days: int = 30) -> List[Dict]:
        """Get trade history"""
        if not self.is_connected:
            return []
        
        try:
            from_time = datetime.now() - timedelta(days=days)
            params = {
                'fromTimestamp': int(from_time.timestamp() * 1000),
                'toTimestamp': int(datetime.now().timestamp() * 1000)
            }
            
            data = self._make_request(f"/v2/accounts/{self.account_id}/deals", params=params)
            return data.get('deals', [])
            
        except Exception as e:
            logger.error(f"Failed to get cTrader trade history: {e}")
            return []
    
    def normalize_symbol(self, symbol: str) -> str:
        """Normalize symbol format for cTrader"""
        # cTrader typically uses format like 'EURUSD', 'GBPUSD'
        return symbol.upper().replace("/", "").replace("-", "")
    
    def is_market_open(self) -> bool:
        """Check if forex market is open"""
        now = datetime.utcnow()
        # Forex market is open from Sunday 22:00 UTC to Friday 22:00 UTC
        if now.weekday() == 5:  # Saturday
            return False
        if now.weekday() == 6 and now.hour < 22:  # Sunday before 22:00 UTC
            return False
        if now.weekday() == 4 and now.hour >= 22:  # Friday after 22:00 UTC
            return False
        return True

# Convenience function
def create_ctrader_broker(demo: bool = True) -> CTraderBroker:
    """Create a cTrader broker instance"""
    return CTraderBroker(demo=demo)