# core/db/connection.py - VERSI FINAL

import sqlite3
import os

# Menentukan path absolut ke file database
# Ini memastikan DB ditemukan dari mana pun skrip dijalankan
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, '..', '..', 'bots.db')

def get_db_connection():
    """
    Membuat dan mengembalikan koneksi ke database SQLite.
    Fungsi ini adalah satu-satunya sumber koneksi database untuk seluruh aplikasi.
    """
    try:
        # check_same_thread=False diperlukan untuk aplikasi multi-threaded seperti Flask
        conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        # 'row_factory' membuat hasil query bisa diakses seperti dictionary
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.Error as e:
        print(f"FATAL: Gagal koneksi ke database di {DB_PATH}: {e}")
        return None
