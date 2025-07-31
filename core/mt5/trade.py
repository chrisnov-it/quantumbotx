# core/mt5/trade.py
import MetaTrader5 as mt5
import logging

logger = logging.getLogger(__name__)

def place_trade(symbol, order_type, volume, sl_pips, tp_pips, magic):
    """
    Menempatkan order trading ke MetaTrader 5 dengan logika yang lebih tangguh.
    """
    symbol_info = mt5.symbol_info(symbol)
    if symbol_info is None:
        logger.error(f"Gagal mendapatkan info untuk simbol {symbol}, order dibatalkan.")
        return None

    # --- PERBAIKAN UTAMA DI SINI ---
    # 1. Gunakan atribut yang benar: 'filling_mode' (singular)
    # 2. Pilih filling mode yang didukung. IOC lebih fleksibel daripada FOK.
    #    FOK (Fill Or Kill): Seluruh order harus terpenuhi, atau dibatalkan.
    #    IOC (Immediate Or Cancel): Bagian dari order bisa terpenuhi, sisanya dibatalkan.
    
    # Ambil filling mode yang diizinkan oleh simbol
    allowed_filling_mode = symbol_info.filling_mode

    # Pilih tipe filling. Prioritaskan IOC jika tersedia, jika tidak, FOK.
    filling_type = mt5.ORDER_FILLING_FOK # Default
    if allowed_filling_mode & mt5.ORDER_FILLING_IOC:
        filling_type = mt5.ORDER_FILLING_IOC
    elif allowed_filling_mode & mt5.ORDER_FILLING_FOK:
        filling_type = mt5.ORDER_FILLING_FOK
    else:
        logger.warning(f"Simbol {symbol} tidak mendukung FOK atau IOC. Menggunakan FOK sebagai fallback.")

    point = symbol_info.point
    price = mt5.symbol_info_tick(symbol).ask if order_type == mt5.ORDER_TYPE_BUY else mt5.symbol_info_tick(symbol).bid

    sl = 0.0
    tp = 0.0

    if order_type == mt5.ORDER_TYPE_BUY:
        sl = price - sl_pips * point if sl_pips > 0 else 0.0
        tp = price + tp_pips * point if tp_pips > 0 else 0.0
    elif order_type == mt5.ORDER_TYPE_SELL:
        sl = price + sl_pips * point if sl_pips > 0 else 0.0
        tp = price - tp_pips * point if tp_pips > 0 else 0.0

    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": float(volume),
        "type": order_type,
        "price": price,
        "sl": sl,
        "tp": tp,
        "magic": magic,
        "comment": "QuantumBotX Trade",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": filling_type,
    }

    logger.info(f"Mengirim order: {request}")
    result = mt5.order_send(request)

    if result is None:
        logger.error(f"order_send gagal, last_error()={mt5.last_error()}")
        return None

    if result.retcode != mt5.TRADE_RETCODE_DONE:
        logger.error(f"Order GAGAL, retcode={result.retcode}, comment: {result.comment}")
        logger.error(f"Request Gagal: {request}")
    else:
        logger.info(f"Order BERHASIL, ticket={result.order}, comment: {result.comment}")

    return result


def close_trade(position):
    """
    Menutup posisi trading yang ada.
    """
    if position is None:
        return

    symbol = position.symbol
    ticket = position.ticket
    volume = position.volume
    order_type = mt5.ORDER_TYPE_SELL if position.type == mt5.ORDER_TYPE_BUY else mt5.ORDER_TYPE_BUY
    price = mt5.symbol_info_tick(symbol).bid if position.type == mt5.ORDER_TYPE_BUY else mt5.symbol_info_tick(symbol).ask

    symbol_info = mt5.symbol_info(symbol)
    if symbol_info is None:
        logger.error(f"Gagal mendapatkan info untuk simbol {symbol} saat menutup posisi, order dibatalkan.")
        return None
        
    allowed_filling_mode = symbol_info.filling_mode
    filling_type = mt5.ORDER_FILLING_FOK
    if allowed_filling_mode & mt5.ORDER_FILLING_IOC:
        filling_type = mt5.ORDER_FILLING_IOC

    request = {
        "action": mt5.TRADE_ACTION_DEAL, "symbol": symbol, "volume": float(volume),
        "type": order_type, "position": ticket, "price": price, "magic": position.magic,
        "comment": "QuantumBotX Close", "type_time": mt5.ORDER_TIME_GTC, "type_filling": filling_type,
    }

    logger.info(f"Menutup posisi: {request}")
    result = mt5.order_send(request)

    if result and result.retcode == mt5.TRADE_RETCODE_DONE:
        logger.info(f"Posisi {ticket} berhasil ditutup.")
    else:
        logger.error(f"Gagal menutup posisi, retcode={result.retcode if result else 'N/A'}, comment: {result.comment if result else mt5.last_error()}")