# core/db/queries.py

import logging
import sqlite3
from .connection import get_db_connection

logger = logging.getLogger(__name__)

def get_all_bots():
    """Mengambil semua data bot dari database."""
    try:
        with get_db_connection() as conn:
            bots = conn.execute('SELECT * FROM bots ORDER BY id DESC').fetchall()
            return [dict(row) for row in bots]
    except sqlite3.Error as e:
        logger.error(f"Database error saat mengambil semua bot: {e}")
        return []

def get_bot_by_id(bot_id):
    """Mengambil satu data bot berdasarkan ID-nya."""
    try:
        with get_db_connection() as conn:
            bot = conn.execute('SELECT * FROM bots WHERE id = ?', (bot_id,)).fetchone()
            return dict(bot) if bot else None
    except sqlite3.Error as e:
        logger.error(f"Database error saat mengambil bot {bot_id}: {e}")
        return None

def add_bot(name, market, lot_size, sl_pips, tp_pips, timeframe, interval, strategy, strategy_params='{}'):
    """Menambahkan bot baru ke database."""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO bots (name, market, lot_size, sl_pips, tp_pips, timeframe, check_interval_seconds, strategy, strategy_params, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'Dijeda')
            ''', (name, market, lot_size, sl_pips, tp_pips, timeframe, interval, strategy, strategy_params))
            conn.commit()
            return cursor.lastrowid
    except sqlite3.Error as e:
        logger.error(f"Gagal menambah bot ke DB: {e}", exc_info=True)
        return None

def update_bot(bot_id, name, market, lot_size, sl_pips, tp_pips, timeframe, interval, strategy, strategy_params='{}'):
    """Memperbarui data bot yang sudah ada di database."""
    try:
        with get_db_connection() as conn:
            conn.execute('''
                UPDATE bots SET 
                name = ?, market = ?, lot_size = ?, sl_pips = ?, tp_pips = ?, 
                timeframe = ?, check_interval_seconds = ?, strategy = ?, strategy_params = ?
                WHERE id = ?
            ''', (name, market, lot_size, sl_pips, tp_pips, timeframe, interval, strategy, strategy_params, bot_id))
            conn.commit()
            return True
    except sqlite3.Error as e:
        logger.error(f"Gagal memperbarui bot {bot_id} di DB: {e}", exc_info=True)
        return False

def delete_bot(bot_id):
    """Menghapus bot dari database berdasarkan ID."""
    try:
        with get_db_connection() as conn:
            conn.execute('DELETE FROM bots WHERE id = ?', (bot_id,))
            conn.commit()
            return True
    except sqlite3.Error as e:
        logger.error(f"Gagal menghapus bot {bot_id} dari DB: {e}", exc_info=True)
        return False

def update_bot_status(bot_id, status):
    """Memperbarui status bot (Aktif/Dijeda) di database."""
    try:
        with get_db_connection() as conn:
            conn.execute('UPDATE bots SET status = ? WHERE id = ?', (status, bot_id))
            conn.commit()
    except sqlite3.Error as e:
        logger.error(f"Gagal update status bot {bot_id}: {e}")

def add_history_log(bot_id, action, details, is_notification=False):
    """Menambahkan log aktivitas/riwayat untuk bot tertentu."""
    try:
        with get_db_connection() as conn:
            conn.execute(
                'INSERT INTO trade_history (bot_id, action, details, is_notification, is_read) VALUES (?, ?, ?, ?, ?)',
                (bot_id, action, details, is_notification, False) # is_read selalu False saat dibuat
            )
            conn.commit()
    except sqlite3.Error as e:
        logger.error(f"Gagal mencatat riwayat untuk bot {bot_id}: {e}")

def get_history_by_bot_id(bot_id):
    """Mengambil semua riwayat dari satu bot berdasarkan ID."""
    try:
        with get_db_connection() as conn:
            history = conn.execute(
                'SELECT * FROM trade_history WHERE bot_id = ? ORDER BY timestamp DESC',
                (bot_id,)
            ).fetchall()
            return [dict(row) for row in history]
    except sqlite3.Error as e:
        logger.error(f"Database error saat mengambil riwayat bot {bot_id}: {e}")
        return []

def get_notifications():
    """Mengambil semua log yang ditandai sebagai notifikasi."""
    try:
        with get_db_connection() as conn:
            notifications = conn.execute('''
                SELECT h.id, h.action, h.details, h.is_read, h.timestamp, b.name as bot_name
                FROM trade_history h
                LEFT JOIN bots b ON h.bot_id = b.id
                WHERE h.is_notification = 1
                ORDER BY h.timestamp DESC
            ''').fetchall()
            return [dict(row) for row in notifications]
    except sqlite3.Error as e:
        logger.error(f"Database error saat mengambil notifikasi: {e}")
        return []

def get_unread_notifications_count():
    """Menghitung jumlah notifikasi yang belum dibaca."""
    try:
        with get_db_connection() as conn:
            count = conn.execute('SELECT COUNT(id) as unread_count FROM trade_history WHERE is_notification = 1 AND is_read = 0').fetchone()
            return dict(count) if count else {'unread_count': 0}
    except sqlite3.Error as e:
        logger.error(f"Database error saat menghitung notifikasi: {e}")
        return {'unread_count': 0}

def get_unread_notifications():
    """Mengambil semua notifikasi yang belum dibaca untuk ditampilkan sebagai toast."""
    try:
        with get_db_connection() as conn:
            notifications = conn.execute('''
                SELECT h.id, h.details
                FROM trade_history h
                WHERE h.is_notification = 1 AND h.is_read = 0
                ORDER BY h.timestamp ASC
            ''').fetchall() # Ambil yang paling lama dulu untuk ditampilkan berurutan
            return [dict(row) for row in notifications]
    except sqlite3.Error as e:
        logger.error(f"Database error saat mengambil notifikasi belum dibaca: {e}")
        return []

def mark_notifications_as_read(notification_ids=None):
    """Menandai notifikasi sebagai sudah dibaca. Jika tidak ada ID, tandai semua.
       Jika diberikan list ID kosong, tidak lakukan apa-apa.
    """
    try:
        with get_db_connection() as conn:
            if notification_ids is not None: # Check if a list was explicitly provided (could be empty)
                if not notification_ids: # If the list is empty, do nothing
                    return True
                safe_ids = [int(id) for id in notification_ids]
                query = f"UPDATE trade_history SET is_read = 1 WHERE id IN ({(', '.join('?'*len(safe_ids)))})"
                conn.execute(query, safe_ids)
            else: # This is the case where it's called without arguments (mark all) or with None
                conn.execute('UPDATE trade_history SET is_read = 1 WHERE is_notification = 1 AND is_read = 0')
            conn.commit()
            return True
    except sqlite3.Error as e:
        logger.error(f"Database error saat menandai notifikasi: {e}")
        return False

def get_all_backtest_history():
    """Mengambil semua riwayat hasil backtest dari database."""
    try:
        with get_db_connection() as conn:
            history = conn.execute('SELECT * FROM backtest_results ORDER BY timestamp DESC').fetchall()
            return [dict(row) for row in history]
    except sqlite3.Error as e:
        logger.error(f"Database error saat mengambil riwayat backtest: {e}")
        return []
