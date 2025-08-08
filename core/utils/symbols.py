# core\utils\symbols.py

import MetaTrader5 as mt5
import logging

logger = logging.getLogger(__name__)

# --- KONFIGURASI PENTING ---
# Cukup gunakan kata kunci umum yang ada di dalam path saham.
# Logika baru akan mencari kata-kata ini di mana saja dalam path.
# Contoh path: "Nasdaq\\Stock\\ZDAI" -> akan cocok dengan 'stock'.
STOCK_KEYWORDS = ['stock', 'share', 'equity', 'saham']

# Prefix untuk Forex, berdasarkan output Anda: "path": "Forex\\AUDCAD"
FOREX_PREFIX = 'forex\\'

def get_all_symbols_from_mt5():
    """Fungsi helper untuk mengambil semua simbol dari MT5 dengan aman."""
    try:
        # Koneksi sudah diinisialisasi saat aplikasi pertama kali berjalan.
        # Kita tidak perlu melakukan initialize() di sini lagi.
        symbols = mt5.symbols_get()
        if symbols:
            return symbols
        logger.warning("mt5.symbols_get() tidak mengembalikan simbol apapun.")
        return []
    except Exception as e:
        logger.error(f"Error saat mengambil simbol dari MT5: {e}", exc_info=True)
        return []

def get_stock_symbols(limit=20):
    """
    Mengambil simbol saham, mengurutkannya berdasarkan volume harian tertinggi,
    dan mengembalikan sejumlah 'limit' teratas.
    """
    all_symbols = get_all_symbols_from_mt5()
    stock_details = []

    if not all_symbols:
        return []

    for s in all_symbols:
        if any(keyword in s.path.lower() for keyword in STOCK_KEYWORDS):
            # Ambil info detail untuk mendapatkan volume
            info = mt5.symbol_info(s.name)
            if info:
                stock_details.append({
                    "name": s.name,
                    "description": s.description,
                    # Gunakan volumehigh sebagai proksi untuk aktivitas/popularitas harian
                    "daily_volume": info.volumehigh
                })

    if not stock_details:
        logger.warning(f"Tidak ada simbol saham yang ditemukan dengan kata kunci: {STOCK_KEYWORDS}. Periksa path simbol Anda dan konfigurasi di core/utils/symbols.py")
        return []

    # Urutkan daftar saham berdasarkan volume harian, dari tertinggi ke terendah
    sorted_stocks = sorted(stock_details, key=lambda x: x.get('daily_volume', 0), reverse=True)

    # Kembalikan hanya sejumlah 'limit' teratas
    return sorted_stocks[:limit]

def get_forex_symbols():
    """Mengambil simbol forex berdasarkan filter path."""
    all_symbols = get_all_symbols_from_mt5()
    forex_list = []

    if not all_symbols:
        return []

    for s in all_symbols:
        if s.path.lower().startswith(FOREX_PREFIX):
            tick = mt5.symbol_info_tick(s.name)
            if tick:
                forex_list.append({
                    "name": s.name,
                    "description": s.description,
                    "ask": tick.ask,
                    "bid": tick.bid,
                    "spread": s.spread,
                    "digits": s.digits,
                })

    return forex_list
