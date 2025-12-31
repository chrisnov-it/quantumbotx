# core/brokers/mt5_broker.py
"""
MetaTrader 5 Broker Implementation
Connects QuantumBotX to MT5 terminals via the universal BaseBroker interface.
"""

import logging
import pandas as pd
import MetaTrader5 as mt5
from typing import Dict, List, Optional, Union
from datetime import datetime, timedelta

from .base_broker import BaseBroker, OrderType, OrderStatus, Timeframe, Position, Order, AccountInfo
from core.utils.mt5 import get_rates_mt5, TIMEFRAME_MAP as MT5_TIMEFRAME_MAP

logger = logging.getLogger(__name__)

class MT5Broker(BaseBroker):
    """
    MT5 Implementation of the BaseBroker.
    Wraps MetaTrader5 library calls into a unified API.
    """
    
    def __init__(self, broker_name: str = "MetaTrader 5"):
        super().__init__(broker_name)
        self.timeframe_map = {
            Timeframe.M1: mt5.TIMEFRAME_M1,
            Timeframe.M5: mt5.TIMEFRAME_M5,
            Timeframe.M15: mt5.TIMEFRAME_M15,
            Timeframe.M30: mt5.TIMEFRAME_M30,
            Timeframe.H1: mt5.TIMEFRAME_H1,
            Timeframe.H4: mt5.TIMEFRAME_H4,
            Timeframe.D1: mt5.TIMEFRAME_D1
        }
        
    def connect(self, credentials: Dict) -> bool:
        """Connect to MT5 terminal"""
        try:
            login = credentials.get('login')
            password = credentials.get('password')
            server = credentials.get('server', 'MetaQuotes-Demo')
            
            if not mt5.initialize(login=int(login), password=password, server=server):
                logger.error(f"MT5 initialization failed: {mt5.last_error()}")
                self.is_connected = False
                return False
                
            self.is_connected = True
            self.supported_symbols = [s.name for s in mt5.symbols_get()]
            logger.info("MT5 connected successfully.")
            return True
        except Exception as e:
            logger.error(f"Error connecting to MT5: {e}")
            return False
            
    def disconnect(self) -> bool:
        """Disconnect from MT5"""
        mt5.shutdown()
        self.is_connected = False
        return True
        
    def get_symbols(self) -> List[str]:
        """Get list of available trading symbols"""
        if not self.is_connected:
            return []
        symbols = mt5.symbols_get()
        return [s.name for s in symbols] if symbols else []
        
    def get_market_data(self, symbol: str, timeframe: Timeframe, 
                       count: int = 500) -> pd.DataFrame:
        """Get OHLCV market data from MT5"""
        mt5_tf = self.timeframe_map.get(timeframe, mt5.TIMEFRAME_H1)
        return get_rates_mt5(symbol, mt5_tf, count)
        
    def get_current_price(self, symbol: str) -> Dict[str, float]:
        """Get current bid/ask prices"""
        tick = mt5.symbol_info_tick(symbol)
        if tick:
            return {"bid": tick.bid, "ask": tick.ask}
        return {"bid": 0.0, "ask": 0.0}
        
    def place_order(self, symbol: str, order_type: OrderType, side: str,
                   size: float, price: Optional[float] = None,
                   stop_loss: Optional[float] = None,
                   take_profit: Optional[float] = None) -> Optional[Order]:
        """Place a trading order in MT5"""
        if not self.is_connected:
            return None
            
        # Map OrderType to MT5 constant
        mt5_type = None
        if order_type == OrderType.MARKET_BUY:
            mt5_type = mt5.ORDER_TYPE_BUY
        elif order_type == OrderType.MARKET_SELL:
            mt5_type = mt5.ORDER_TYPE_SELL
        # ... support other types as needed
        
        if mt5_type is None:
            logger.error(f"Unsupported order type for MT5: {order_type}")
            return None
            
        curr_price = price or (self.get_current_price(symbol)['ask'] if mt5_type == mt5.ORDER_TYPE_BUY else self.get_current_price(symbol)['bid'])
        
        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": size,
            "type": mt5_type,
            "price": curr_price,
            "sl": stop_loss or 0.0,
            "tp": take_profit or 0.0,
            "magic": 2024001, # Default magic number
            "comment": "QuantumBotX Trade",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_FOK,
        }
        
        result = mt5.order_send(request)
        if result and result.retcode == mt5.TRADE_RETCODE_DONE:
            order = Order(str(result.order), symbol, order_type, side, size, curr_price)
            order.status = OrderStatus.FILLED
            return order
        else:
            logger.error(f"MT5 Order failed: {result.comment if result else 'Unknown error'}")
            return None
            
    def cancel_order(self, order_id: str) -> bool:
        """Cancel an existing order (MT5 usually handles this via close or delete pending)"""
        # Simplistic implementation for now
        return False
        
    def get_positions(self) -> List[Position]:
        """Get all open positions from MT5"""
        mt5_positions = mt5.positions_get()
        positions = []
        if mt5_positions:
            for p in mt5_positions:
                side = 'long' if p.type == mt5.POSITION_TYPE_BUY else 'short'
                positions.append(Position(
                    symbol=p.symbol,
                    side=side,
                    size=p.volume,
                    entry_price=p.price_open,
                    current_price=p.price_current,
                    unrealized_pnl=p.profit
                ))
        return positions
        
    def get_orders(self) -> List[Order]:
        """Get all pending orders from MT5"""
        mt5_orders = mt5.orders_get()
        orders = []
        if mt5_orders:
            for o in mt5_orders:
                # Map MT5 order types back to our OrderType
                # This is a simplification
                order_type = OrderType.LIMIT_BUY if o.type == mt5.ORDER_TYPE_BUY_LIMIT else OrderType.LIMIT_SELL
                orders.append(Order(
                    order_id=str(o.ticket),
                    symbol=o.symbol,
                    order_type=order_type,
                    side='buy' if 'BUY' in order_type.name else 'sell',
                    size=o.volume_initial,
                    price=o.price_open
                ))
        return orders
        
    def get_account_info(self) -> AccountInfo:
        """Get account information from MT5"""
        inf = mt5.account_info()
        if inf:
            return AccountInfo(
                balance=inf.balance,
                equity=inf.equity,
                margin=inf.margin,
                free_margin=inf.margin_free,
                margin_level=inf.margin_level,
                currency=inf.currency
            )
        return AccountInfo(0, 0, 0, 0, 0)
        
    def get_trade_history(self, days: int = 30) -> List[Dict]:
        """Get trade history from MT5"""
        from_date = datetime.now() - timedelta(days=days)
        history = mt5.history_deals_get(from_date, datetime.now())
        deals = []
        if history:
            for d in history:
                deals.append({
                    "ticket": d.ticket,
                    "symbol": d.symbol,
                    "type": d.type,
                    "volume": d.volume,
                    "price": d.price,
                    "profit": d.profit,
                    "time": datetime.fromtimestamp(d.time)
                })
        return deals
