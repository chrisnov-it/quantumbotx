import ccxt
import pandas as pd
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging
from core.interfaces.broker_interface import BrokerInterface

logger = logging.getLogger(__name__)

class CCXTAdapter(BrokerInterface):
    def __init__(self):
        self.exchange = None
        self.exchange_id = None
        # Map standard timeframes to CCXT format
        self.timeframe_map = {
            'M1': '1m', 'M5': '5m', 'M15': '15m', 'M30': '30m',
            'H1': '1h', 'H4': '4h', 'D1': '1d', 'W1': '1w', 'MN1': '1M'
        }

    def initialize(self, credentials: Dict[str, Any]) -> bool:
        try:
            self.exchange_id = credentials.get('EXCHANGE_ID', 'binance')
            exchange_class = getattr(ccxt, self.exchange_id)
            
            config = {
                'apiKey': credentials.get('API_KEY'),
                'secret': credentials.get('API_SECRET'),
                'enableRateLimit': True,
                'options': {'defaultType': 'future'} # Default to futures for bots
            }
            
            if credentials.get('PASSWORD'): 
                config['password'] = credentials.get('PASSWORD')
                
            # Enable testnet/demo if configured
            if credentials.get('TESTNET', False):
                config['options']['demo'] = True
                if self.exchange_id == 'binance':
                    # Manually point to Futures Testnet URL to be extra safe
                    config['urls'] = {
                        'api': {
                            'public': 'https://testnet.binancefuture.com/fapi/v1',
                            'private': 'https://testnet.binancefuture.com/fapi/v1',
                        }
                    }
                logger.info(f"Using {self.exchange_id} DEMO TRADING mode")
                
            self.exchange = exchange_class(config)
            
            # Test connection
            self.exchange.load_markets()
            logger.info(f"Connected to {self.exchange_id} successfully.")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize CCXT exchange {self.exchange_id}: {e}")
            return False

    def get_account_info(self) -> Optional[Dict[str, Any]]:
        try:
            balance = self.exchange.fetch_balance()
            # Normalize to standard format
            return {
                'balance': balance.get('total', {}).get('USDT', 0.0),
                'equity': balance.get('total', {}).get('USDT', 0.0), # Approx for spot
                'margin': 0.0, # Complex to calculate across exchanges
                'free_margin': balance.get('free', {}).get('USDT', 0.0)
            }
        except Exception as e:
            logger.error(f"Error fetching account info: {e}")
            return None

    def get_rates(self, symbol: str, timeframe: str, count: int = 100) -> pd.DataFrame:
        try:
            tf = self.timeframe_map.get(timeframe, '1h')
            ohlcv = self.exchange.fetch_ohlcv(symbol, tf, limit=count)
            
            df = pd.DataFrame(ohlcv, columns=['time', 'open', 'high', 'low', 'close', 'tick_volume'])
            df['time'] = pd.to_datetime(df['time'], unit='ms')
            return df
        except Exception as e:
            logger.error(f"Error fetching rates for {symbol}: {e}")
            return pd.DataFrame()

    def get_open_positions(self) -> List[Dict[str, Any]]:
        try:
            # This works best for Futures. Spot exchanges might not return "positions" in the same way.
            positions = self.exchange.fetch_positions()
            normalized_positions = []
            for pos in positions:
                if float(pos['contracts']) > 0: # Only active positions
                    normalized_positions.append({
                        'ticket': pos.get('id', f"{pos['symbol']}_{pos['side']}"),
                        'symbol': pos['symbol'],
                        'type': 0 if pos['side'] == 'long' else 1, # 0=BUY, 1=SELL (MT5 convention)
                        'volume': float(pos['contracts']),
                        'price': float(pos['entryPrice']),
                        'profit': float(pos.get('unrealizedPnl', 0.0)),
                        'sl': float(pos.get('stopLossPrice', 0.0) or 0.0),
                        'tp': float(pos.get('takeProfitPrice', 0.0) or 0.0),
                        'magic': 0 # CCXT doesn't support magic numbers natively usually
                    })
            return normalized_positions
        except Exception as e:
            # Fallback for Spot: check balance? No, simpler to just return empty for now or log warning
            # logger.warning(f"Could not fetch positions (might be Spot market): {e}")
            return []

    def place_order(self, symbol: str, order_type: str, volume: float, price: float = 0.0, sl: float = 0.0, tp: float = 0.0, comment: str = "") -> bool:
        try:
            side = 'buy' if order_type == 'BUY' or order_type == 0 else 'sell'
            type = 'limit' if price > 0 else 'market'
            
            params = {}
            # CCXT unified stopLoss/takeProfit is tricky, often exchange specific params
            # For simplicity in this POC, we might skip SL/TP attachment or use params
            if sl > 0:
                params['stopLoss'] = sl
            if tp > 0:
                params['takeProfit'] = tp
                
            if type == 'limit':
                self.exchange.create_order(symbol, type, side, volume, price, params)
            else:
                self.exchange.create_order(symbol, type, side, volume, None, params)
                
            logger.info(f"Order placed: {side} {symbol} {volume}")
            return True
        except Exception as e:
            logger.error(f"Error placing order: {e}")
            return False

    def close_position(self, position_id: str, volume: float = 0.0) -> bool:
        # Closing positions in CCXT usually means placing an opposite order
        # Or using close_position method if supported
        try:
            # Try to find position info to know symbol and amount
            # This is tricky without state. 
            # For now, we assume the bot logic handles "Close" by sending an opposite order signal
            # But the interface demands close_position.
            # We might need to implement this by fetching position first.
            logger.warning("close_position not fully implemented for CCXT yet. Use place_order with opposite side.")
            return False
        except Exception as e:
            logger.error(f"Error closing position: {e}")
            return False

    def get_symbol_info(self, symbol: str) -> Optional[Dict[str, Any]]:
        try:
            market = self.exchange.market(symbol)
            return {
                'name': market['symbol'],
                'digits': market['precision']['price'],
                'min_volume': market['limits']['amount']['min'],
                'max_volume': market['limits']['amount']['max'],
                'volume_step': market['precision']['amount'], # Approx
                'point': 1.0 / (10 ** market['precision']['price'])
            }
        except Exception as e:
            logger.error(f"Error getting symbol info for {symbol}: {e}")
            return None

    def get_todays_profit(self) -> float:
        # TODO: Implement profit calculation for CCXT
        return 0.0
