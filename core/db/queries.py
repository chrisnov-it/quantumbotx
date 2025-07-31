# core/db/queries.py - VERSI PERBAIKAN LENGKAP

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

def add_history_log(bot_id, action, details):
    """Menambahkan log aktivitas/riwayat untuk bot tertentu."""
    try:
        with get_db_connection() as conn:
            conn.execute(
                'INSERT INTO trade_history (bot_id, action, details) VALUES (?, ?, ?)',
                (bot_id, action, details)
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