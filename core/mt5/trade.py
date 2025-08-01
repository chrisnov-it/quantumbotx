# core/mt5/trade.py

import logging
import MetaTrader5 as mt5

logger = logging.getLogger(__name__)

def place_trade(symbol, order_type, volume, sl_pips, tp_pips, magic_id):
    """
    Menempatkan trade dengan perhitungan SL/TP yang dinamis berdasarkan 'point' simbol.
    """
    try:
        # 1. Dapatkan informasi simbol untuk point dan digits
        symbol_info = mt5.symbol_info(symbol)
        if symbol_info is None:
            logger.error(f"Gagal mendapatkan info untuk simbol {symbol}. Order dibatalkan.")
            return None, "Symbol not found"

        point = symbol_info.point
        digits = symbol_info.digits

        # 2. Tentukan harga entry (ask untuk BUY, bid untuk SELL)
        if order_type == mt5.ORDER_TYPE_BUY:
            price = mt5.symbol_info_tick(symbol).ask
        elif order_type == mt5.ORDER_TYPE_SELL:
            price = mt5.symbol_info_tick(symbol).bid
        else:
            logger.error(f"Tipe order tidak valid: {order_type}")
            return None, "Invalid order type"

        # 3. Hitung SL dan TP berdasarkan pips dan point
        # Asumsi umum: 1 pip = 10 points. Ini membuat kode konsisten di semua pair.
        pip_value = 10 * point
        
        sl_level = 0.0
        tp_level = 0.0

        if order_type == mt5.ORDER_TYPE_BUY:
            sl_level = price - (sl_pips * pip_value)
            tp_level = price + (tp_pips * pip_value)
        elif order_type == mt5.ORDER_TYPE_SELL:
            sl_level = price + (sl_pips * pip_value)
            tp_level = price - (tp_pips * pip_value)
            
        # Bulatkan ke jumlah digit yang benar untuk menghindari error presisi
        sl_level = round(sl_level, digits)
        tp_level = round(tp_level, digits)

        # 4. Siapkan request order
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
            "type_filling": mt5.ORDER_FILLING_FOK, # FOK lebih umum didukung oleh broker ECN
        }

        # 5. Kirim order
        result = mt5.order_send(request)

        # 6. Cek hasil dan log
        if result.retcode != mt5.TRADE_RETCODE_DONE:
            logger.error(f"Order GAGAL, retcode={result.retcode}, comment: {result.comment}")
            logger.error(f"Request Gagal: {request}")
            return None, result.comment
        
        logger.info(f"Order BERHASIL ditempatkan: Deal #{result.deal}, Order #{result.order}")
        return result, "Order placed successfully"

    except Exception as e:
        logger.error(f"Exception saat menempatkan trade: {e}", exc_info=True)
        return None, str(e)

def close_trade(position):
    """
    Menutup posisi yang ada.
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