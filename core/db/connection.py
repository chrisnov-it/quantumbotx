# core/db/connection.py
import sqlite3
import os
import sys

# Tentukan nama file database di satu tempat.
DATABASE_FILENAME = 'bots.db'

def get_db_connection():
    """Membuat dan mengembalikan koneksi ke database SQLite."""
    # Get the directory where the executable is located
    if getattr(sys, 'frozen', False):
        # Running as PyInstaller bundle
        base_dir = os.path.dirname(sys.executable)
        db_path = os.path.join(base_dir, DATABASE_FILENAME)
    else:
        # Running as script
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        db_path = os.path.join(BASE_DIR, '..', '..', DATABASE_FILENAME)

    conn = sqlite3.connect(db_path)
    # Mengatur agar hasil query bisa diakses seperti dictionary
    conn.row_factory = sqlite3.Row
    return conn
