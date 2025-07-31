import MetaTrader5 as mt5
import locale

locale.setlocale(locale.LC_NUMERIC, 'C')

def parse_decimal(val):
    try:
        return float(str(val).replace(',', '.'))
    except Exception:
        return 0.0

def initialize_mt5(account, password, server):
    if not mt5.initialize():
        print("Gagal inisialisasi MT5:", mt5.last_error())
        return False
    if not mt5.login(account, password=password, server=server):
        print("Gagal login ke MT5:", mt5.last_error())
        mt5.shutdown()
        return False
    print(f"Berhasil login ke akun MT5: {account} di server {server}")
    return True

def place_trade(symbol, trade_type, lot, sl_pips, tp_pips, magic_number):
    info = mt5.symbol_info(symbol)
    if info is None:
        print(f"Gagal ambil info simbol {symbol}")
        return None

    filling = info.filling_modes[0]
    price = mt5.symbol_info_tick(symbol).ask if trade_type == mt5.ORDER_TYPE_BUY else mt5.symbol_info_tick(symbol).bid
    point = info.point

    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": lot,
        "type": trade_type,
        "price": price,
        "sl": price - sl_pips * point if trade_type == mt5.ORDER_TYPE_BUY else price + sl_pips * point,
        "tp": price + tp_pips * point if trade_type == mt5.ORDER_TYPE_BUY else price - tp_pips * point,
        "magic": magic_number,
        "comment": "Bot by QuantumBotX",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": filling,
    }
    result = mt5.order_send(request)
    if result.retcode != mt5.TRADE_RETCODE_DONE:
        print(f"Order gagal: {result.comment}")
        return None
    print(f"Order dikirim! Ticket: {result.order}")
    return result

def close_trade(position):
    price = mt5.symbol_info_tick(position.symbol).bid if position.type == mt5.ORDER_TYPE_BUY else mt5.symbol_info_tick(position.symbol).ask
    close_request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": position.symbol,
        "volume": position.volume,
        "type": mt5.ORDER_TYPE_SELL if position.type == mt5.ORDER_TYPE_BUY else mt5.ORDER_TYPE_BUY,
        "position": position.ticket,
        "price": price,
        "magic": position.magic,
        "comment": "Auto-close by bot",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_RETURN,
    }
    result = mt5.order_send(close_request)
    return result.retcode == mt5.TRADE_RETCODE_DONE
