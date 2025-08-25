# run.py

import os
import sys
import atexit
import logging
import MetaTrader5 as mt5
from flask import jsonify
from core import create_app
from core.utils.mt5 import initialize_mt5
from core.bots.controller import shutdown_all_bots, ambil_semua_bot
from dotenv import load_dotenv

load_dotenv()

# Konfigurasi logging bersih dari awal
logging.getLogger('werkzeug').setLevel(logging.WARNING)

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
        # Ambil kredensial MT5 dari environment variables dengan validasi
        account_str = os.getenv('MT5_LOGIN')
        password = os.getenv('MT5_PASSWORD')
        server = os.getenv('MT5_SERVER', 'MetaQuotes-Demo')
        
        # Validasi kredensial tidak kosong
        if not account_str or not password:
            logging.error("Error: MT5_LOGIN dan MT5_PASSWORD harus diisi di file .env")
            sys.exit(1)
        
        # Convert account to integer dengan error handling
        try:
            account = int(account_str)
        except ValueError:
            logging.error(f"Error: MT5_LOGIN harus berupa angka, ditemukan: {account_str}")
            sys.exit(1)
            
        if initialize_mt5(account, password, server):
            logging.info("Koneksi MT5 berhasil diinisialisasi dari run.py.")
            
            # Load bots - automatic broker migration happens here
            ambil_semua_bot() 
            atexit.register(shutdown_app) # Daftarkan shutdown HANYA jika koneksi berhasil
        else:
            logging.error("Error: Gagal terhubung ke MT5. Pastikan MT5 terminal berjalan dan kredensial benar.")
            sys.exit(1)
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