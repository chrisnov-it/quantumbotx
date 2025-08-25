# core/brokers/interactive_brokers.py
"""
Interactive Brokers Integration for QuantumBotX
Professional-grade multi-asset trading platform
"""

import pandas as pd
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging
import threading

from .base_broker import (
    BaseBroker, OrderType, OrderStatus, Timeframe, 
    Position, Order, AccountInfo
)

logger = logging.getLogger(__name__)

class InteractiveBrokersBroker(BaseBroker):
    """
    Interactive Brokers (IBKR) implementation using TWS API.
    Supports stocks, forex, futures, options, and more.
    """
    
    def __init__(self, paper_trading: bool = True):
        super().__init__("Interactive Brokers")
        self.paper_trading = paper_trading
        self.ib_app = None
        self.client_id = 1  # Unique client ID
        self.port = 7497 if paper_trading else 7496  # Paper vs Live port
        self.host = "127.0.0.1"
        self.is_connected_flag = False
        
        # Data storage
        self.positions_data = {}
        self.orders_data = {}
        self.account_data = {}
        self.market_data_cache = {}
        
        # Timeframe mapping (IB uses specific duration/bar size combinations)
        self.timeframe_map = {
            Timeframe.M1: ("1 D", "1 min"),     # 1 day of 1-minute bars
            Timeframe.M5: ("5 D", "5 mins"),    # 5 days of 5-minute bars
            Timeframe.M15: ("10 D", "15 mins"),  # 10 days of 15-minute bars
            Timeframe.M30: ("1 M", "30 mins"),   # 1 month of 30-minute bars
            Timeframe.H1: ("1 M", "1 hour"),     # 1 month of 1-hour bars
            Timeframe.H4: ("3 M", "4 hours"),    # 3 months of 4-hour bars
            Timeframe.D1: ("1 Y", "1 day"),      # 1 year of daily bars
        }
    
    def connect(self, credentials: Dict) -> bool:
        """
        Connect to Interactive Brokers TWS/Gateway
        credentials: {"host": "127.0.0.1", "port": 7497, "client_id": 1}
        """
        try:
            # Import here to avoid dependency issues if not installed
            from ibapi.client import EClient
            from ibapi.wrapper import EWrapper
            from ibapi.contract import Contract
            
            # Override connection parameters if provided
            self.host = credentials.get("host", self.host)
            self.port = credentials.get("port", self.port)
            self.client_id = credentials.get("client_id", self.client_id)
            
            # Create IB App class that combines EClient and EWrapper
            class IBApp(EWrapper, EClient):
                def __init__(self, broker_instance):
                    EClient.__init__(self, self)
                    self.broker = broker_instance
                    self.next_order_id = None
                
                def nextValidId(self, orderId: int):
                    """Callback when connection is established"""
                    self.next_order_id = orderId
                    self.broker.is_connected_flag = True
                    logger.info(f"IB connection established. Next order ID: {orderId}")
                
                def accountSummary(self, reqId: int, account: str, tag: str, value: str, currency: str):
                    """Account summary callback"""
                    if account not in self.broker.account_data:
                        self.broker.account_data[account] = {}
                    self.broker.account_data[account][tag] = {
                        'value': value,
                        'currency': currency
                    }
                
                def position(self, account: str, contract, position: float, avgCost: float):
                    """Position callback"""
                    symbol = contract.symbol
                    self.broker.positions_data[symbol] = {
                        'account': account,
                        'symbol': symbol,
                        'position': position,
                        'avg_cost': avgCost,
                        'contract': contract
                    }
                
                def openOrder(self, orderId, contract, order, orderState):
                    """Open order callback"""
                    self.broker.orders_data[orderId] = {
                        'order_id': orderId,
                        'contract': contract,
                        'order': order,
                        'state': orderState
                    }
                
                def historicalData(self, reqId, bar):
                    """Historical data callback"""
                    if reqId not in self.broker.market_data_cache:
                        self.broker.market_data_cache[reqId] = []
                    
                    self.broker.market_data_cache[reqId].append({
                        'date': bar.date,
                        'open': bar.open,
                        'high': bar.high,
                        'low': bar.low,
                        'close': bar.close,
                        'volume': bar.volume
                    })
                
                def error(self, reqId, errorCode, errorString, advancedOrderRejectJson=""):
                    """Error callback"""
                    logger.error(f"IB Error {errorCode}: {errorString}")
            
            # Create and connect IB app
            self.ib_app = IBApp(self)
            self.ib_app.connect(self.host, self.port, self.client_id)
            
            # Start message processing in separate thread
            def run_loop():
                self.ib_app.run()
            
            api_thread = threading.Thread(target=run_loop, daemon=True)
            api_thread.start()
            
            # Wait for connection
            timeout = 10  # 10 seconds timeout
            for _ in range(timeout * 10):  # Check every 0.1 seconds
                if self.is_connected_flag:
                    break
                time.sleep(0.1)
            
            if self.is_connected_flag:
                self.is_connected = True
                
                # Request account summary
                self.ib_app.reqAccountSummary(1, "All", "$LEDGER")
                time.sleep(2)  # Wait for data
                
                # Load supported symbols (simplified list)
                self.supported_symbols = [
                    # Forex
                    'EUR.USD', 'GBP.USD', 'USD.JPY', 'USD.CHF', 'AUD.USD', 'USD.CAD',
                    # Stocks
                    'AAPL', 'GOOGL', 'MSFT', 'TSLA', 'AMZN', 'META',
                    # Futures
                    'ES', 'NQ', 'YM', 'RTY',  # Stock index futures
                    'GC', 'SI', 'CL',         # Commodity futures
                ]
                
                logger.info(f"Connected to Interactive Brokers {'Paper' if self.paper_trading else 'Live'}")
                return True
            else:
                logger.error("Failed to establish IB connection within timeout")
                return False
                
        except ImportError:
            logger.error("ibapi package not installed. Install with: pip install ibapi")
            return False
        except Exception as e:
            logger.error(f"Failed to connect to Interactive Brokers: {e}")
            self.is_connected = False
            return False
    
    def disconnect(self) -> bool:
        """Disconnect from Interactive Brokers"""
        if self.ib_app:
            self.ib_app.disconnect()
        self.is_connected = False
        self.is_connected_flag = False
        logger.info("Disconnected from Interactive Brokers")
        return True
    
    def get_symbols(self) -> List[str]:
        """Get list of available trading symbols"""
        return self.supported_symbols
    
    def _create_contract(self, symbol: str) -> 'Contract':
        """Create IB Contract object for symbol"""
        from ibapi.contract import Contract
        
        contract = Contract()
        
        # Determine contract type based on symbol format
        if '.' in symbol:  # Forex (EUR.USD format)
            base, quote = symbol.split('.')
            contract.symbol = base
            contract.secType = "CASH"
            contract.currency = quote
            contract.exchange = "IDEALPRO"
        elif symbol in ['ES', 'NQ', 'YM', 'RTY', 'GC', 'SI', 'CL']:  # Futures
            contract.symbol = symbol
            contract.secType = "FUT"
            contract.exchange = "CME"  # Simplified
            contract.lastTradeDateOrContractMonth = "202412"  # Would need dynamic
        else:  # Stocks
            contract.symbol = symbol
            contract.secType = "STK"
            contract.currency = "USD"
            contract.exchange = "SMART"
        
        return contract
    
    def get_market_data(self, symbol: str, timeframe: Timeframe, count: int = 500) -> pd.DataFrame:
        """Get OHLCV market data from Interactive Brokers"""
        if not self.is_connected:
            raise Exception("Not connected to Interactive Brokers")
        
        try:
            contract = self._create_contract(symbol)
            duration, bar_size = self.timeframe_map[timeframe]
            
            # Request historical data
            req_id = int(time.time())  # Unique request ID
            self.market_data_cache[req_id] = []
            
            self.ib_app.reqHistoricalData(
                req_id, contract, "", duration, bar_size, "TRADES", 1, 1, False, []
            )
            
            # Wait for data
            timeout = 10
            for _ in range(timeout * 10):
                if req_id in self.market_data_cache and len(self.market_data_cache[req_id]) > 0:
                    break
                time.sleep(0.1)
            
            # Convert to DataFrame
            data = self.market_data_cache.get(req_id, [])
            if not data:
                return pd.DataFrame()
            
            df_data = []
            for bar in data:
                # Parse IB date format
                try:
                    if len(bar['date']) == 8:  # Daily format: 20231201
                        date_obj = datetime.strptime(bar['date'], '%Y%m%d')
                    else:  # Intraday format: 20231201 10:30:00
                        date_obj = datetime.strptime(bar['date'], '%Y%m%d %H:%M:%S')
                except:
                    date_obj = datetime.now()
                
                df_data.append({
                    'time': date_obj,
                    'open': bar['open'],
                    'high': bar['high'],
                    'low': bar['low'],
                    'close': bar['close'],
                    'volume': bar['volume']
                })
            
            # Clean up cache
            del self.market_data_cache[req_id]
            
            return pd.DataFrame(df_data)
            
        except Exception as e:
            logger.error(f"Failed to get IB market data for {symbol}: {e}")
            return pd.DataFrame()
    
    def get_current_price(self, symbol: str) -> Dict[str, float]:
        """Get current bid/ask prices"""
        if not self.is_connected:
            raise Exception("Not connected to Interactive Brokers")
        
        try:
            # IB requires market data subscription for real-time prices
            # For demo purposes, return last close price as both bid/ask
            # In real implementation, would use reqMktData
            df = self.get_market_data(symbol, Timeframe.M1, 1)
            if not df.empty:
                last_price = df.iloc[-1]['close']
                return {"bid": last_price - 0.0001, "ask": last_price + 0.0001}
            else:
                return {"bid": 0.0, "ask": 0.0}
        except Exception as e:
            logger.error(f"Failed to get IB current price for {symbol}: {e}")
            return {"bid": 0.0, "ask": 0.0}
    
    def place_order(self, symbol: str, order_type: OrderType, side: str,
                   size: float, price: Optional[float] = None,
                   stop_loss: Optional[float] = None,
                   take_profit: Optional[float] = None) -> Order:
        """Place a trading order on Interactive Brokers"""
        if not self.is_connected:
            raise Exception("Not connected to Interactive Brokers")
        
        try:
            from ibapi.order import Order as IBOrder
            
            contract = self._create_contract(symbol)
            
            # Create IB order
            ib_order = IBOrder()
            ib_order.action = "BUY" if side.lower() == "buy" else "SELL"
            ib_order.totalQuantity = size
            
            # Set order type
            if order_type in [OrderType.MARKET_BUY, OrderType.MARKET_SELL]:
                ib_order.orderType = "MKT"
            elif order_type in [OrderType.LIMIT_BUY, OrderType.LIMIT_SELL]:
                ib_order.orderType = "LMT"
                ib_order.lmtPrice = price
            
            # Get next order ID
            if not self.ib_app.next_order_id:
                logger.error("No valid order ID available")
                raise Exception("No valid order ID")
            
            order_id = self.ib_app.next_order_id
            self.ib_app.next_order_id += 1
            
            # Place order
            self.ib_app.placeOrder(order_id, contract, ib_order)
            
            # Create Order object
            order = Order(
                order_id=str(order_id),
                symbol=symbol,
                order_type=order_type,
                side=side.lower(),
                size=size,
                price=price
            )
            
            order.status = OrderStatus.PENDING
            logger.info(f"IB order placed: {order_id} for {symbol}")
            return order
            
        except Exception as e:
            logger.error(f"Failed to place IB order: {e}")
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
            self.ib_app.cancelOrder(int(order_id))
            return True
        except Exception as e:
            logger.error(f"Failed to cancel IB order {order_id}: {e}")
            return False
    
    def get_positions(self) -> List[Position]:
        """Get all open positions"""
        if not self.is_connected:
            return []
        
        try:
            # Request positions
            self.ib_app.reqPositions()
            time.sleep(2)  # Wait for data
            
            positions = []
            for symbol, pos_data in self.positions_data.items():
                if pos_data['position'] != 0:  # Only non-zero positions
                    position = Position(
                        symbol=symbol,
                        side='long' if pos_data['position'] > 0 else 'short',
                        size=abs(pos_data['position']),
                        entry_price=pos_data['avg_cost'],
                        current_price=pos_data['avg_cost'],  # Would need market price
                        unrealized_pnl=0.0  # Would need calculation
                    )
                    positions.append(position)
            
            return positions
            
        except Exception as e:
            logger.error(f"Failed to get IB positions: {e}")
            return []
    
    def get_orders(self) -> List[Order]:
        """Get all pending orders"""
        if not self.is_connected:
            return []
        
        try:
            # Request open orders
            self.ib_app.reqOpenOrders()
            time.sleep(2)  # Wait for data
            
            orders = []
            for order_id, order_data in self.orders_data.items():
                order = Order(
                    order_id=str(order_id),
                    symbol=order_data['contract'].symbol,
                    order_type=OrderType.LIMIT_BUY,  # Simplified
                    side=order_data['order'].action.lower(),
                    size=order_data['order'].totalQuantity,
                    price=getattr(order_data['order'], 'lmtPrice', None)
                )
                order.status = OrderStatus.PENDING
                orders.append(order)
            
            return orders
            
        except Exception as e:
            logger.error(f"Failed to get IB orders: {e}")
            return []
    
    def get_account_info(self) -> AccountInfo:
        """Get account information"""
        if not self.is_connected:
            return AccountInfo(0, 0, 0, 0, 0, "USD")
        
        try:
            # Use cached account data
            account_data = list(self.account_data.values())[0] if self.account_data else {}
            
            net_liquidation = float(account_data.get('NetLiquidation', {}).get('value', 0))
            total_cash = float(account_data.get('TotalCashValue', {}).get('value', 0))
            buying_power = float(account_data.get('BuyingPower', {}).get('value', 0))
            
            return AccountInfo(
                balance=total_cash,
                equity=net_liquidation,
                margin=0.0,  # Would need calculation
                free_margin=buying_power,
                margin_level=100.0,  # Would need calculation
                currency="USD"
            )
            
        except Exception as e:
            logger.error(f"Failed to get IB account info: {e}")
            return AccountInfo(0, 0, 0, 0, 0, "USD")
    
    def get_trade_history(self, days: int = 30) -> List[Dict]:
        """Get trade history"""
        if not self.is_connected:
            return []
        
        try:
            # IB trade history would require execution reports
            # For now, return empty list
            logger.warning("IB trade history not implemented - requires execution report handling")
            return []
            
        except Exception as e:
            logger.error(f"Failed to get IB trade history: {e}")
            return []
    
    def normalize_symbol(self, symbol: str) -> str:
        """Normalize symbol format for Interactive Brokers"""
        # Convert common formats to IB format
        symbol = symbol.upper()
        
        # Forex: EURUSD -> EUR.USD
        forex_pairs = ['EURUSD', 'GBPUSD', 'USDJPY', 'USDCHF', 'AUDUSD', 'USDCAD']
        for pair in forex_pairs:
            if symbol == pair:
                return f"{pair[:3]}.{pair[3:]}"
        
        return symbol
    
    def is_market_open(self) -> bool:
        """Check if markets are open (simplified)"""
        now = datetime.now()
        # US market hours: weekdays, roughly 9:30 AM - 4:00 PM ET
        return now.weekday() < 5  # Simplified

# Convenience function
def create_ib_broker(paper_trading: bool = True) -> InteractiveBrokersBroker:
    """Create an Interactive Brokers broker instance"""
    return InteractiveBrokersBroker(paper_trading=paper_trading)