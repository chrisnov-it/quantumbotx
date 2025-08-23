# core/mt5/trade.py

import logging
import math
import MetaTrader5 as mt5
import pandas_ta as ta
from core.utils.mt5 import get_rates_mt5, TIMEFRAME_MAP

logger = logging.getLogger(__name__)

def calculate_lot_size(account_currency, symbol, risk_percent, sl_price, entry_price):
    """Menghitung ukuran lot yang sesuai berdasarkan risiko."""
    try:
        # 1. Dapatkan informasi akun dan simbol
        account_info = mt5.account_info()
        if account_info is None:
            logger.error("Gagal mendapatkan informasi akun.")
            return None

        symbol_info = mt5.symbol_info(symbol)
        if symbol_info is None:
            logger.error(f"Gagal mendapatkan info untuk simbol {symbol}.")
            return None

        # 2. Tentukan parameter penting
        balance = account_info.balance
        amount_to_risk = balance * (risk_percent / 100.0)
        sl_pips_distance = abs(entry_price - sl_price)
        
        # 3. Kalkulasi nilai per lot
        # MT5 menyediakan cara untuk mengkalkulasi profit/loss untuk trade hipotetis
        # Kita gunakan ini untuk menentukan nilai per lot
        lot_value_check = mt5.order_calc_profit(
            mt5.ORDER_TYPE_BUY, symbol, 1.0, entry_price, sl_price
        )
        if lot_value_check is None or lot_value_check == 0:
            logger.error(f"Gagal mengkalkulasi profit/loss untuk {symbol}")
            return None

        # Nilai absolut dari loss untuk 1 lot standar
        loss_for_one_lot = abs(lot_value_check)

        if loss_for_one_lot == 0:
            logger.error("Loss per lot adalah nol, tidak bisa menghitung lot size.")
            return None

        # 4. Hitung lot size
        lot_size = amount_to_risk / loss_for_one_lot

        # 5. Sesuaikan dengan batasan broker
        volume_step = symbol_info.volume_step
        min_volume = symbol_info.volume_min
        max_volume = symbol_info.volume_max

        # Bulatkan ke volume step terdekat
        lot_size = math.floor(lot_size / volume_step) * volume_step
        lot_size = round(lot_size, len(str(volume_step).split('.')[1]) if '.' in str(volume_step) else 0)

        if lot_size < min_volume:
            logger.warning(f"Lot size terhitung ({lot_size}) di bawah minimum ({min_volume}). Menggunakan lot minimum.")
            return min_volume
        
        if lot_size > max_volume:
            logger.warning(f"Lot size terhitung ({lot_size}) di atas maksimum ({max_volume}). Menggunakan lot maksimum.")
            return max_volume

        return lot_size

    except Exception as e:
        logger.error(f"Error saat kalkulasi lot size: {e}", exc_info=True)
        return None

def place_trade(symbol, order_type, risk_percent, sl_atr_multiplier, tp_atr_multiplier, magic_id, timeframe_str):
    """
    Menempatkan trade dengan kalkulasi lot size & SL/TP dinamis.
    """
    try:
        # --- 1. Dapatkan data & hitung ATR ---
        symbol_info = mt5.symbol_info(symbol)
        if symbol_info is None: return None, "Symbol not found"
        digits = symbol_info.digits

        timeframe_const = TIMEFRAME_MAP.get(timeframe_str, mt5.TIMEFRAME_H1)
        df = get_rates_mt5(symbol, timeframe_const, 30)
        if df is None or df.empty or len(df) < 15: return None, "Insufficient data for ATR"

        atr = ta.atr(df['high'], df['low'], df['close'], length=14).iloc[-1]
        if atr is None or atr == 0: return None, "Invalid ATR value"

        # --- 2. Tentukan harga & level SL/TP ---
        price = mt5.symbol_info_tick(symbol).ask if order_type == mt5.ORDER_TYPE_BUY else mt5.symbol_info_tick(symbol).bid
        sl_distance = atr * sl_atr_multiplier
        tp_distance = atr * tp_atr_multiplier

        sl_level = round(price - sl_distance if order_type == mt5.ORDER_TYPE_BUY else price + sl_distance, digits)
        tp_level = round(price + tp_distance if order_type == mt5.ORDER_TYPE_BUY else price - tp_distance, digits)

        # --- 3. Hitung Lot Size Dinamis ---
        lot_size = calculate_lot_size(mt5.account_info().currency, symbol, risk_percent, sl_level, price)
        if lot_size is None:
            return None, "Failed to calculate lot size."

        # --- 4. Kirim Order ---
        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": lot_size,
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
            return None, result.comment
        
        logger.info(f"Order BERHASIL: Lot={lot_size}, SL={sl_level}, TP={tp_level}")
        return result, "Order placed successfully"

    except Exception as e:
        logger.error(f"Exception di place_trade: {e}", exc_info=True)
        return None, str(e)

def close_trade(position):
    """Menutup posisi yang ada."""
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