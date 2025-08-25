# core/brokers/binance_broker.py
"""
Binance Exchange Integration for QuantumBotX
Implements crypto trading through Binance API
"""

import pandas as pd
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging

from .base_broker import (
    BaseBroker, OrderType, OrderStatus, Timeframe, 
    Position, Order, AccountInfo
)

logger = logging.getLogger(__name__)

class BinanceBroker(BaseBroker):
    """
    Binance exchange implementation of the universal broker interface.
    Supports spot and futures trading.
    """
    
    def __init__(self, testnet: bool = True):
        super().__init__("Binance")
        self.testnet = testnet
        self.client = None
        self.base_url = "https://testnet.binance.vision" if testnet else "https://api.binance.com"
        
        # Timeframe mapping
        self.timeframe_map = {
            Timeframe.M1: "1m",
            Timeframe.M5: "5m", 
            Timeframe.M15: "15m",
            Timeframe.M30: "30m",
            Timeframe.H1: "1h",
            Timeframe.H4: "4h",
            Timeframe.D1: "1d"
        }
    
    def connect(self, credentials: Dict) -> bool:
        """
        Connect to Binance with API credentials
        credentials: {"api_key": "...", "secret_key": "..."}
        """
        try:
            # Import here to avoid dependency issues if not installed
            from binance.client import Client
            from binance.exceptions import BinanceAPIException
            
            api_key = credentials.get("api_key")
            secret_key = credentials.get("secret_key")
            
            if not api_key or not secret_key:
                logger.error("Binance API key and secret key are required")
                return False
            
            # Initialize Binance client
            self.client = Client(
                api_key=api_key,
                api_secret=secret_key,
                testnet=self.testnet
            )
            
            # Test connection
            account_info = self.client.get_account()
            self.is_connected = True
            
            # Get supported symbols
            exchange_info = self.client.get_exchange_info()
            self.supported_symbols = [s['symbol'] for s in exchange_info['symbols'] 
                                    if s['status'] == 'TRADING']
            
            logger.info(f"Connected to Binance {'Testnet' if self.testnet else 'Mainnet'}")
            logger.info(f"Account status: {account_info.get('accountType', 'Unknown')}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to Binance: {e}")
            self.is_connected = False
            return False
    
    def disconnect(self) -> bool:
        """Disconnect from Binance"""
        self.client = None
        self.is_connected = False
        logger.info("Disconnected from Binance")
        return True
    
    def get_symbols(self) -> List[str]:
        """Get list of available trading symbols"""
        if not self.is_connected:
            return []
        return self.supported_symbols
    
    def get_market_data(self, symbol: str, timeframe: Timeframe, count: int = 500) -> pd.DataFrame:
        """
        Get OHLCV market data from Binance
        """
        if not self.is_connected:
            raise Exception("Not connected to Binance")
        
        try:
            # Convert timeframe
            interval = self.timeframe_map[timeframe]
            
            # Get klines (candlestick data)
            klines = self.client.get_klines(
                symbol=symbol,
                interval=interval,
                limit=count
            )
            
            # Convert to DataFrame
            df = pd.DataFrame(klines, columns=[
                'timestamp', 'open', 'high', 'low', 'close', 'volume',
                'close_time', 'quote_asset_volume', 'number_of_trades',
                'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'
            ])
            
            # Clean and format data
            df['time'] = pd.to_datetime(df['timestamp'], unit='ms')
            df['open'] = pd.to_numeric(df['open'])
            df['high'] = pd.to_numeric(df['high'])
            df['low'] = pd.to_numeric(df['low'])
            df['close'] = pd.to_numeric(df['close'])
            df['volume'] = pd.to_numeric(df['volume'])
            
            # Return standardized format
            return df[['time', 'open', 'high', 'low', 'close', 'volume']].copy()
            
        except Exception as e:
            logger.error(f"Failed to get market data for {symbol}: {e}")
            return pd.DataFrame()
    
    def get_current_price(self, symbol: str) -> Dict[str, float]:
        """Get current bid/ask prices"""
        if not self.is_connected:
            raise Exception("Not connected to Binance")
        
        try:
            ticker = self.client.get_orderbook_ticker(symbol=symbol)
            return {
                "bid": float(ticker['bidPrice']),
                "ask": float(ticker['askPrice'])
            }
        except Exception as e:
            logger.error(f"Failed to get current price for {symbol}: {e}")
            return {"bid": 0.0, "ask": 0.0}
    
    def place_order(self, symbol: str, order_type: OrderType, side: str,
                   size: float, price: Optional[float] = None,
                   stop_loss: Optional[float] = None,
                   take_profit: Optional[float] = None) -> Order:
        """Place a trading order on Binance"""
        if not self.is_connected:
            raise Exception("Not connected to Binance")
        
        try:
            # Convert order parameters
            binance_side = side.upper()  # 'BUY' or 'SELL'
            
            # Determine order type
            if order_type == OrderType.MARKET_BUY or order_type == OrderType.MARKET_SELL:
                binance_type = "MARKET"
            elif order_type == OrderType.LIMIT_BUY or order_type == OrderType.LIMIT_SELL:
                binance_type = "LIMIT"
            else:
                raise ValueError(f"Unsupported order type: {order_type}")
            
            # Prepare order parameters
            order_params = {
                'symbol': symbol,
                'side': binance_side,
                'type': binance_type,
                'quantity': size,
            }
            
            if binance_type == "LIMIT":
                order_params['price'] = price
                order_params['timeInForce'] = 'GTC'  # Good Till Cancelled
            
            # Place order
            result = self.client.create_order(**order_params)
            
            # Create Order object
            order = Order(
                order_id=str(result['orderId']),
                symbol=symbol,
                order_type=order_type,
                side=side.lower(),
                size=size,
                price=price
            )
            
            # Update status based on result
            if result['status'] == 'FILLED':
                order.status = OrderStatus.FILLED
                order.filled_size = float(result.get('executedQty', 0))
                order.avg_fill_price = float(result.get('price', price or 0))
            elif result['status'] == 'NEW':
                order.status = OrderStatus.PENDING
            
            logger.info(f"Order placed: {order.order_id} for {symbol}")
            return order
            
        except Exception as e:
            logger.error(f"Failed to place order: {e}")
            # Return failed order
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
            # Note: Need symbol to cancel order in Binance
            # This is a limitation - may need to store order info
            logger.warning("Cancel order requires symbol - implement order tracking")
            return False
        except Exception as e:
            logger.error(f"Failed to cancel order {order_id}: {e}")
            return False
    
    def get_positions(self) -> List[Position]:
        """Get all open positions (for futures)"""
        if not self.is_connected:
            return []
        
        try:
            # For spot trading, positions are just balances
            account = self.client.get_account()
            positions = []
            
            for balance in account['balances']:
                free = float(balance['free'])
                locked = float(balance['locked'])
                total = free + locked
                
                if total > 0:
                    # Create position for non-zero balances
                    position = Position(
                        symbol=balance['asset'],
                        side='long',  # Spot is always long
                        size=total,
                        entry_price=0.0,  # Not available for spot
                        current_price=0.0,  # Would need to fetch
                        unrealized_pnl=0.0  # Not calculated for spot
                    )
                    positions.append(position)
            
            return positions
            
        except Exception as e:
            logger.error(f"Failed to get positions: {e}")
            return []
    
    def get_orders(self) -> List[Order]:
        """Get all pending orders"""
        if not self.is_connected:
            return []
        
        try:
            # Get open orders for all symbols (limitation: need symbol)
            # For now, return empty - would need to track symbols
            logger.warning("Get orders requires symbol tracking - implement order cache")
            return []
            
        except Exception as e:
            logger.error(f"Failed to get orders: {e}")
            return []
    
    def get_account_info(self) -> AccountInfo:
        """Get account information"""
        if not self.is_connected:
            return AccountInfo(0, 0, 0, 0, 0, "USDT")
        
        try:
            account = self.client.get_account()
            
            # Calculate total balance in USDT
            total_balance = 0.0
            
            for balance in account['balances']:
                free = float(balance['free'])
                locked = float(balance['locked'])
                total = free + locked
                
                if total > 0:
                    asset = balance['asset']
                    if asset == 'USDT':
                        total_balance += total
                    else:
                        # Convert to USDT (simplified - would need price conversion)
                        # For demo purposes, assume small balances
                        if asset in ['BTC', 'ETH']:
                            total_balance += total * 30000  # Rough estimate
                        else:
                            total_balance += total  # Assume stablecoin or ignore
            
            return AccountInfo(
                balance=total_balance,
                equity=total_balance,  # Same for spot
                margin=0.0,  # Not applicable for spot
                free_margin=total_balance,
                margin_level=100.0,  # Not applicable for spot
                currency="USDT"
            )
            
        except Exception as e:
            logger.error(f"Failed to get account info: {e}")
            return AccountInfo(0, 0, 0, 0, 0, "USDT")
    
    def get_trade_history(self, days: int = 30) -> List[Dict]:
        """Get trade history"""
        if not self.is_connected:
            return []
        
        try:
            # Get trades for major symbols (limitation: need symbol)
            logger.warning("Trade history requires symbol tracking - implement symbol cache")
            return []
            
        except Exception as e:
            logger.error(f"Failed to get trade history: {e}")
            return []
    
    def normalize_symbol(self, symbol: str) -> str:
        """Normalize symbol format for Binance"""
        # Binance uses format like 'BTCUSDT', 'ETHUSDT'
        symbol = symbol.upper().replace("/", "").replace("-", "")
        
        # Common conversions
        if symbol.endswith("USD") and not symbol.endswith("USDT"):
            symbol = symbol.replace("USD", "USDT")
        
        return symbol
    
    def is_market_open(self) -> bool:
        """Crypto markets are always open"""
        return True

# Convenience function to create Binance broker
def create_binance_broker(testnet: bool = True) -> BinanceBroker:
    """Create a Binance broker instance"""
    return BinanceBroker(testnet=testnet)