# core/bots/controller.py

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
        logger.info(f"Memuat {len(all_bots_data)} bot dari database.")
        # Anda bisa menambahkan logika untuk memulai bot yang statusnya 'Aktif' di sini jika perlu
    except Exception as e:
        logger.error(f"Gagal memuat bot dari database saat startup: {e}", exc_info=True)

def mulai_bot(bot_id: int):
    """Memulai thread untuk bot yang dipilih."""
    if bot_id in active_bots and active_bots[bot_id].is_alive():
        return True, f"Bot {bot_id} sudah berjalan."

    bot_data = queries.get_bot_by_id(bot_id)
    if not bot_data:
        return False, f"Bot dengan ID {bot_id} tidak ditemukan."

    try:
        bot_thread = TradingBot(
            id=bot_data['id'], name=bot_data['name'], market=bot_data['market'],
            lot_size=bot_data['lot_size'], sl_pips=bot_data['sl_pips'],
            tp_pips=bot_data['tp_pips'], timeframe=bot_data['timeframe'],
            check_interval=bot_data['check_interval_seconds'], strategy=bot_data['strategy']
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

def stop_bot(bot_id: int):
    """Menghentikan thread bot yang sedang berjalan."""
    if bot_id in active_bots and active_bots[bot_id].is_alive():
        bot_thread = active_bots[bot_id]
        bot_thread.stop()
        bot_thread.join(timeout=10) # Tunggu thread berhenti
        del active_bots[bot_id]
        queries.update_bot_status(bot_id, 'Dijeda')
        logger.info(f"Bot {bot_id} berhasil dihentikan.")
        return True, f"Bot {bot_thread.name} berhasil dihentikan."
    
    # Jika bot tidak ada di memori tapi statusnya 'Aktif' di DB (state tidak konsisten)
    queries.update_bot_status(bot_id, 'Dijeda')
    return True, f"Bot {bot_id} dihentikan (state tidak konsisten telah diperbaiki)."

def perbarui_bot(bot_id: int, data: dict):
    """Memperbarui konfigurasi bot di database."""
    bot_instance = active_bots.get(bot_id)
    if bot_instance and bot_instance.is_alive():
        logger.info(f"Menghentikan bot {bot_id} sementara untuk pembaruan.")
        stop_bot(bot_id)

    # --- PERBAIKAN DI SINI ---
    # Ganti nama kunci 'check_interval_seconds' dari frontend
    # menjadi 'interval' yang sesuai dengan kolom database.
    if 'check_interval_seconds' in data:
        data['interval'] = data.pop('check_interval_seconds')
    # --- AKHIR PERBAIKAN ---

    try:
        success = queries.update_bot(bot_id=bot_id, **data)
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
    stop_bot(bot_id) # Pastikan thread berhenti sebelum dihapus
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