# core/mt5/trade.py

import logging
import MetaTrader5 as mt5
import pandas as pd
import pandas_ta as ta
from core.utils.mt5 import get_rates_mt5, TIMEFRAME_MAP

logger = logging.getLogger(__name__)

def place_trade(symbol, order_type, volume, sl_atr_multiplier, tp_atr_multiplier, magic_id, timeframe_str):
    """
    Menempatkan trade dengan SL/TP dinamis berdasarkan ATR.
    """
    try:
        # --- 1. Dapatkan informasi & data yang diperlukan ---
        symbol_info = mt5.symbol_info(symbol)
        if symbol_info is None:
            logger.error(f"Gagal mendapatkan info untuk simbol {symbol}. Order dibatalkan.")
            return None, "Symbol not found"

        point = symbol_info.point
        digits = symbol_info.digits

        # Dapatkan data harga untuk menghitung ATR
        timeframe_const = TIMEFRAME_MAP.get(timeframe_str, mt5.TIMEFRAME_H1)
        # Kita butuh ~15 bar untuk ATR(14), ambil 30 untuk keamanan
        df = get_rates_mt5(symbol, timeframe_const, 30) 
        if df is None or df.empty or len(df) < 15:
            logger.error(f"Data tidak cukup untuk menghitung ATR untuk {symbol} TF {timeframe_str}. Order dibatalkan.")
            return None, "Insufficient data for ATR"

        # --- 2. Hitung ATR ---
        atr = ta.atr(df['high'], df['low'], df['close'], length=14).iloc[-1]
        if atr is None or atr == 0:
            logger.warning(f"Nilai ATR tidak valid (0 atau None) untuk {symbol}. Order dibatalkan.")
            return None, "Invalid ATR value"

        # --- 3. Tentukan harga entry & hitung SL/TP ---
        price = mt5.symbol_info_tick(symbol).ask if order_type == mt5.ORDER_TYPE_BUY else mt5.symbol_info_tick(symbol).bid
        
        sl_distance = atr * sl_atr_multiplier
        tp_distance = atr * tp_atr_multiplier

        if order_type == mt5.ORDER_TYPE_BUY:
            sl_level = price - sl_distance
            tp_level = price + tp_distance
        else: # ORDER_TYPE_SELL
            sl_level = price + sl_distance
            tp_level = price - tp_distance
            
        # Bulatkan ke jumlah digit yang benar
        sl_level = round(sl_level, digits)
        tp_level = round(tp_level, digits)

        # --- 4. Siapkan & kirim request order ---
        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": float(volume),
            "type": order_type,
            "price": price,
            "sl": sl_level,
            "tp": tp_level,
            "magic": magic_id,
            "comment": "QuantumBotX Trade",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_FOK,
        }

        result = mt5.order_send(request)

        if result.retcode != mt5.TRADE_RETCODE_DONE:
            logger.error(f"Order GAGAL, retcode={result.retcode}, comment: {result.comment}")
            logger.error(f"Request Gagal: {request}")
            return None, result.comment
        
        logger.info(f"Order BERHASIL ditempatkan: Deal #{result.deal}, Order #{result.order}")
        logger.info(f"ATR={atr:.{digits}f}, SL={sl_level:.{digits}f}, TP={tp_level:.{digits}f}")
        return result, "Order placed successfully"

    except Exception as e:
        logger.error(f"Exception saat menempatkan trade: {e}", exc_info=True)
        return None, str(e)

def close_trade(position):
    """
    Menutup posisi yang ada. (Tidak ada perubahan di sini)
    """
    try:
        close_order_type = mt5.ORDER_TYPE_SELL if position.type == mt5.ORDER_TYPE_BUY else mt5.ORDER_TYPE_BUY
        price = mt5.symbol_info_tick(position.symbol).bid if close_order_type == mt5.ORDER_TYPE_SELL else mt5.symbol_info_tick(position.symbol).ask

        request = {
            "action": mt5.TRADE_ACTION_DEAL, "position": position.ticket, "symbol": position.symbol,
            "volume": position.volume, "type": close_order_type, "price": price, "magic": position.magic,
            "comment": "QuantumBotX Close", "type_time": mt5.ORDER_TIME_GTC, "type_filling": mt5.ORDER_FILLING_FOK,
        }

        result = mt5.order_send(request)
        if result.retcode != mt5.TRADE_RETCODE_DONE:
            logger.error(f"Gagal menutup posisi #{position.ticket}, retcode={result.retcode}, comment: {result.comment}")
            return None, result.comment

        logger.info(f"Posisi #{position.ticket} berhasil ditutup.")
        return result, "Position closed successfully"

    except Exception as e:
        logger.error(f"Exception saat menutup posisi: {e}", exc_info=True)
        return None, str(e)
