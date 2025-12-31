from core.interfaces.broker_interface import BrokerInterface
import logging
from datetime import datetime
import pandas as pd
from typing import Dict, Any, List, Optional

try:
    from core.utils.mt5 import (
        initialize_mt5, 
        get_rates_mt5,
        get_account_info_mt5,
        get_open_positions_mt5,
        find_mt5_symbol,
        TIMEFRAME_MAP,
        get_todays_profit_mt5
    )
    # Corrected import for trade functions
    from core.mt5.trade import place_trade as mt5_place_trade, close_trade as mt5_close_trade
    import MetaTrader5 as mt5
    MT5_AVAILABLE = True
except ImportError:
    MT5_AVAILABLE = False
    logger.error("MetaTrader5 module or dependencies not found. MT5Adapter will not work.")

logger = logging.getLogger(__name__)

class MT5Adapter(BrokerInterface):
    """
    Adapter for MetaTrader 5 using the official python library.
    Wraps the functions from core.utils.mt5 and core.mt5.trade.
    """

    def initialize(self, credentials: Dict[str, Any]) -> bool:
        """Login to MT5 if provided credentials, else assume already initialized."""
        if not credentials:
            return mt5.initialize() if MT5_AVAILABLE else False
        
        login = credentials.get('MT5_LOGIN') or credentials.get('login')
        password = credentials.get('MT5_PASSWORD') or credentials.get('password')
        server = credentials.get('MT5_SERVER') or credentials.get('server', 'MetaQuotes-Demo')
        
        if login and password:
            return initialize_mt5(int(login), password, server)
        return mt5.initialize() if MT5_AVAILABLE else False

    def get_account_info(self) -> Optional[Dict[str, Any]]:
        return get_account_info_mt5()

    def get_rates(self, symbol: str, timeframe: str, count: int = 100) -> pd.DataFrame:
        mt5_timeframe = TIMEFRAME_MAP.get(timeframe, mt5.TIMEFRAME_H1)
        valid_symbol = find_mt5_symbol(symbol)
        if not valid_symbol:
            logger.error(f"Symbol {symbol} not found in MT5")
            return pd.DataFrame()
        return get_rates_mt5(valid_symbol, mt5_timeframe, count)

    def get_open_positions(self) -> List[Dict[str, Any]]:
        mt5_positions = get_open_positions_mt5()
        standardized_positions = []
        for pos in mt5_positions:
            # Map MT5 type (0 for Buy, 1 for Sell) to string
            standardized_type = 'BUY' if pos.get('type') == mt5.POSITION_TYPE_BUY else 'SELL'
            pos['type'] = standardized_type
            standardized_positions.append(pos)
        return standardized_positions

    def place_order(self, symbol: str, order_type: str, volume: float, price: float = 0.0, sl: float = 0.0, tp: float = 0.0, comment: str = "") -> bool:
        valid_symbol = find_mt5_symbol(symbol)
        if not valid_symbol:
            return False

        mt5_order_type = mt5.ORDER_TYPE_BUY if order_type == 'BUY' else mt5.ORDER_TYPE_SELL
        
        # We use the existing place_trade logic but wrap the arguments
        # Wait, the existing place_trade uses ATR multipliers. 
        # For the universal adapter, we want raw SL/TP values.
        
        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": valid_symbol,
            "volume": volume,
            "type": mt5_order_type,
            "price": mt5.symbol_info_tick(valid_symbol).ask if order_type == 'BUY' else mt5.symbol_info_tick(valid_symbol).bid,
            "sl": sl,
            "tp": tp,
            "deviation": 20,
            "magic": 123456,
            "comment": comment,
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }
        
        result = mt5.order_send(request)
        if result is None or result.retcode != mt5.TRADE_RETCODE_DONE:
            logger.error(f"Order failed: {result.comment if result else 'No result'}")
            return False
            
        logger.info(f"Order placed: {result.order}")
        return True

    def close_position(self, ticket_id: Any, volume: float = 0.0) -> bool:
        """Close an existing position in MT5."""
        try:
            # Find the position by ticket
            positions = mt5.positions_get(ticket=int(ticket_id))
            if not positions:
                logger.warning(f"Position #{ticket_id} not found to close.")
                return False
            
            position = positions[0]
            # Use the existing close_trade utility
            result, msg = mt5_close_trade(position)
            return result is not None
        except Exception as e:
            logger.error(f"Error closing position {ticket_id}: {e}")
            return False

    def get_symbol_info(self, symbol: str) -> Optional[Dict[str, Any]]:
        valid_symbol = find_mt5_symbol(symbol)
        if not valid_symbol:
            return None
        info = mt5.symbol_info(valid_symbol)
        if info:
            return info._asdict()
        return None

    def get_todays_profit(self) -> float:
        return get_todays_profit_mt5()
