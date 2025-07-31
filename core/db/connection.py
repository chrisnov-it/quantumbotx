# core/db/connection.py
import sqlite3
import os

# Tentukan nama file database di satu tempat.
DATABASE_FILENAME = 'bots.db'
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_PATH = os.path.join(BASE_DIR, '..', '..', DATABASE_FILENAME)

def get_db_connection():
    """Membuat dan mengembalikan koneksi ke database SQLite."""
    conn = sqlite3.connect(DATABASE_PATH)
    # Mengatur agar hasil query bisa diakses seperti dictionary
    conn.row_factory = sqlite3.Row
    return conn