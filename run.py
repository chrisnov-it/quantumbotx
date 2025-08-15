# run.py

import os
import atexit
import logging
import MetaTrader5 as mt5
from flask import jsonify
from core import create_app
from core.utils.mt5 import initialize_mt5
from core.bots.controller import shutdown_all_bots, ambil_semua_bot
from dotenv import load_dotenv

load_dotenv()

def shutdown_app():
    """Fungsi shutdown terpusat."""
    logging.info("Memulai proses shutdown aplikasi...")
    shutdown_all_bots()
    mt5.shutdown()
    logging.info("Koneksi MetaTrader 5 ditutup. Aplikasi berhenti.")

# Panggil pabrik untuk membuat aplikasi kita
app = create_app()

@app.route('/api/health')
def health_check():
    """Endpoint untuk memastikan server berjalan."""
    return jsonify({"status": "ok", "message": "Server is running"})

if __name__ == '__main__':
    # --- Inisialisasi MT5 Terpusat ---
    # Dilakukan di sini untuk memastikan hanya berjalan sekali.
    try:
        ACCOUNT = int(os.getenv('MT5_LOGIN'))
        PASSWORD = os.getenv('MT5_PASSWORD')
        SERVER = os.getenv('MT5_SERVER', 'MetaQuotes-Demo')
        if initialize_mt5(ACCOUNT, PASSWORD, SERVER):
            logging.info("Koneksi MT5 berhasil diinisialisasi dari run.py.")
            ambil_semua_bot() # Muat bot setelah koneksi berhasil
            atexit.register(shutdown_app) # Daftarkan shutdown HANYA jika koneksi berhasil
    except Exception as e:
        logging.critical(
            f"GAGAL total saat inisialisasi MT5 di run.py: {e}",
            exc_info=True
        )

    app.run(
        debug=os.getenv('FLASK_DEBUG', 'False').lower() == 'true',
        host=os.getenv('FLASK_HOST', '127.0.0.1'),
        port=int(os.getenv('FLASK_PORT', 5000)),
        use_reloader=False
    )