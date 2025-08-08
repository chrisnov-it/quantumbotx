# core/bots/controller.py

import json
import logging
from core.db import queries
from .trading_bot import TradingBot

logger = logging.getLogger(__name__)

# Dictionary untuk menyimpan instance thread bot yang aktif
# Key: bot_id (int), Value: TradingBot instance
active_bots = {}

def ambil_semua_bot():
    """
    Mengambil semua bot dari database saat aplikasi pertama kali dimulai.
    Tidak memulai thread, hanya memuat konfigurasi.
    """
    try:
        all_bots_data = queries.get_all_bots()
        if not all_bots_data:
            logger.info("Database tidak memiliki bot untuk dimuat.")
            return
            
        logger.info(f"Memuat {len(all_bots_data)} bot dari database. Memeriksa bot yang perlu diaktifkan ulang...")
        for bot_data in all_bots_data:
            if bot_data.get('status') == 'Aktif':
                logger.info(f"Bot ID {bot_data['id']} ({bot_data['name']}) memiliki status 'Aktif'. Mencoba memulai ulang...")
                mulai_bot(bot_data['id'])
    except Exception as e:
        logger.error(f"Gagal memuat bot dari database saat startup: {e}", exc_info=True)

def mulai_bot(bot_id: int):
    """Memulai thread untuk bot yang dipilih."""
    if bot_id in active_bots and active_bots[bot_id].is_alive():
        return True, f"Bot {bot_id} sudah berjalan."

    bot_data = queries.get_bot_by_id(bot_id)
    if not bot_data:
        return False, f"Bot dengan ID {bot_id} tidak ditemukan."

    # Ubah string JSON dari DB menjadi dictionary Python
    params_dict = json.loads(bot_data.get('strategy_params', '{}'))

    try:
        bot_thread = TradingBot(
            id=bot_data['id'], name=bot_data['name'], market=bot_data['market'],
            lot_size=bot_data['lot_size'], sl_pips=bot_data['sl_pips'],
            tp_pips=bot_data['tp_pips'], timeframe=bot_data['timeframe'],
            check_interval=bot_data['check_interval_seconds'], strategy=bot_data['strategy'],
            strategy_params=params_dict
        )
        bot_thread.start()
        active_bots[bot_id] = bot_thread
        queries.update_bot_status(bot_id, 'Aktif')
        logger.info(f"Bot {bot_id} ({bot_data['name']}) berhasil dimulai.")
        return True, f"Bot {bot_data['name']} berhasil dimulai."
    except Exception as e:
        logger.error(f"Gagal memulai bot {bot_id}: {e}", exc_info=True)
        queries.update_bot_status(bot_id, 'Error')
        return False, f"Gagal memulai bot: {e}"

def hentikan_bot(bot_id: int):
    """Menghentikan thread bot yang sedang berjalan."""
    # PERBAIKAN: Gunakan .pop() untuk mengambil dan menghapus bot secara atomik.
    # Ini mencegah race condition di mana dua proses mencoba menghentikan bot yang sama.
    bot_thread = active_bots.pop(bot_id, None)

    if bot_thread and bot_thread.is_alive():
        bot_thread.stop()
        bot_thread.join(timeout=10) # Tunggu thread berhenti
        queries.update_bot_status(bot_id, 'Dijeda')
        logger.info(f"Bot {bot_id} berhasil dihentikan.")
        return True, f"Bot {bot_thread.name} berhasil dihentikan."
    
    # Jika bot tidak ada di memori (mungkin sudah dihentikan oleh proses lain)
    # atau jika status di DB tidak konsisten, pastikan status di DB benar.
    queries.update_bot_status(bot_id, 'Dijeda') # Pastikan status di DB adalah 'Dijeda'
    return True, f"Bot {bot_id} sudah dihentikan atau tidak sedang berjalan."

def mulai_semua_bot():
    """Memulai semua bot yang statusnya 'Dijeda'."""
    all_bots = queries.get_all_bots()
    bots_to_start = [bot for bot in all_bots if bot['status'] == 'Dijeda']
    
    if not bots_to_start:
        return False, "Tidak ada bot yang bisa dimulai (semua sudah aktif atau error)."

    started_count = 0
    for bot in bots_to_start:
        success, _ = mulai_bot(bot['id'])
        if success:
            started_count += 1
    
    return True, f"Berhasil memulai {started_count} dari {len(bots_to_start)} bot."

def hentikan_semua_bot():
    """Menghentikan semua bot yang sedang berjalan."""
    running_bot_ids = list(active_bots.keys())
    if not running_bot_ids:
        return False, "Tidak ada bot yang sedang berjalan."

    for bot_id in running_bot_ids:
        hentikan_bot(bot_id)
    return True, f"Sinyal berhenti telah dikirim ke {len(running_bot_ids)} bot."

# Alias untuk dipanggil oleh atexit di run.py, memastikan nama sesuai.
shutdown_all_bots = hentikan_semua_bot

def perbarui_bot(bot_id: int, data: dict):
    """Memperbarui konfigurasi bot di database."""
    bot_instance = active_bots.get(bot_id)
    if bot_instance and bot_instance.is_alive():
        logger.info(f"Menghentikan bot {bot_id} sementara untuk pembaruan.")
        hentikan_bot(bot_id)

    # --- PERBAIKAN DI SINI ---
    # Ganti nama kunci 'check_interval_seconds' dari frontend
    # menjadi 'interval' yang sesuai dengan kolom database.
    if 'check_interval_seconds' in data:
        data['interval'] = data.pop('check_interval_seconds')

    # Ambil parameter kustom, ubah jadi string JSON, dan simpan
    custom_params = data.pop('params', {})
    data['strategy_params'] = json.dumps(custom_params)

    # --- PERBAIKAN BARU: Filter data untuk mencegah TypeError ---
    # Hanya teruskan argumen yang diharapkan oleh fungsi queries.update_bot
    expected_args = [
        'name', 'market', 'lot_size', 'sl_pips', 'tp_pips',
        'timeframe', 'interval', 'strategy', 'strategy_params'
    ]
    
    update_data = {key: data[key] for key in expected_args if key in data}

    try:
        # Gunakan dictionary yang sudah difilter
        success = queries.update_bot(bot_id=bot_id, **update_data)
        if success:
            logger.info(f"Konfigurasi bot {bot_id} berhasil diperbarui di database.")
            return True, "Bot berhasil diperbarui."
        else:
            return False, "Gagal memperbarui bot di database."
    except Exception as e:
        logger.error(f"Error saat memperbarui bot {bot_id} di DB: {e}", exc_info=True)
        return False, str(e)

def hapus_bot(bot_id: int):
    """Menghentikan dan menghapus bot."""
    hentikan_bot(bot_id) # Pastikan thread berhenti sebelum dihapus
    return queries.delete_bot(bot_id)

def add_new_bot_to_controller(bot_id: int):
    """Menambahkan bot baru dan langsung memulainya jika statusnya 'Aktif'."""
    bot_data = queries.get_bot_by_id(bot_id)
    if bot_data and bot_data.get('status') == 'Aktif':
        mulai_bot(bot_id)

def get_bot_instance_by_id(bot_id: int):
    """Mengembalikan instance thread bot yang aktif."""
    return active_bots.get(bot_id)

def get_bot_analysis_data(bot_id: int):
    """Mengambil data analisis terakhir dari instance bot."""
    bot = active_bots.get(bot_id)
    if bot and hasattr(bot, 'last_analysis'):
        return bot.last_analysis
    return None