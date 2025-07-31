# app.py - FINAL VERSION
import os
import logging
from logging.handlers import RotatingFileHandler
import atexit  # <-- 1. Impor modul atexit
from flask import Flask, render_template, send_from_directory
from dotenv import load_dotenv

# Import modul inti yang diperlukan saat startup
import MetaTrader5 as mt5  # <-- 2. Impor MT5 secara langsung
from core.utils.mt5 import initialize_mt5
from core.bots.controller import ambil_semua_bot

# --- Konfigurasi Awal ---
# Muat environment variables dari file .env
load_dotenv()

# Siapkan sistem logging
log_dir = os.path.join(os.path.dirname(__file__), 'logs')
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, 'app.log')

file_handler = RotatingFileHandler(log_file, maxBytes=1024 * 1024 * 5, backupCount=5)
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(file_handler)

# --- Inisialisasi Aplikasi Flask ---
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-here')

# --- Registrasi Blueprints ---
# Impor blueprints setelah 'app' dibuat untuk menghindari circular import
from core.routes.api_dashboard import api_dashboard  # noqa: E402
from core.routes.api_chart import api_chart  # noqa: E402
from core.routes.api_bots import api_bots  # noqa: E402
from core.routes.api_profile import api_profile  # noqa: E402
from core.routes.api_portfolio import api_portfolio  # noqa: E402
from core.routes.api_history import api_history  # noqa: E402
from core.routes.api_notifications import api_notifications  # noqa: E402
from core.routes.api_stocks import api_stocks  # noqa: E402
from core.routes.api_forex import api_forex  # noqa: E402
from core.routes.api_crypto import api_crypto  # noqa: E402
from core.routes.api_fundamentals import api_fundamentals  # noqa: E402

# Buat daftar semua blueprints untuk registrasi yang lebih rapi
blueprints = [
    api_dashboard, api_chart, api_bots, api_profile, api_portfolio, api_history,
    api_notifications, api_stocks, api_forex, api_crypto, api_fundamentals
]

# Daftarkan setiap blueprint ke aplikasi
for blueprint in blueprints:
    app.register_blueprint(blueprint)

# --- Rute Halaman (Views) ---
@app.route('/')
def dashboard():
    return render_template('index.html')

@app.route('/trading_bots')
def bots_page():
    return render_template('trading_bots.html')

@app.route('/bots/<int:bot_id>')
def bot_detail_page(bot_id):
    return render_template('bot_detail.html')

# ... (rute-rute halaman lainnya tetap sama) ...
@app.route('/portfolio')
def portfolio_page():
    return render_template('portfolio.html')

@app.route('/history')
def history_page():
    return render_template('history.html')

@app.route('/settings')
def settings_page():
    return render_template('settings.html')

@app.route('/profile')
def profile_page():
    return render_template('profile.html')

@app.route('/notifications')
def notifications_page():
    return render_template('notifications.html')

@app.route('/cryptocurrency')
def crypto_page():
    return render_template('cryptocurrency.html')

@app.route('/stocks')
def stocks_page():
    return render_template('stocks.html')

@app.route('/forex')
def forex_page():
    return render_template('forex.html')

# --- Error Handlers & Rute Lain-lain ---
@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    # Mencatat error ke log untuk debugging
    logger.error(f"Internal Server Error: {error}", exc_info=True)
    return render_template('500.html'), 500

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

# --- Fungsi Shutdown ---
def shutdown_handler():
    """Fungsi yang akan dipanggil saat aplikasi akan keluar."""
    logger.info("Menerima sinyal shutdown. Memulai proses pembersihan...")
    
    # Impor controller di sini untuk menghindari circular import
    from core.bots import controller
    
    # Hentikan semua bot yang aktif
    active_bot_ids = list(controller.active_bots.keys())
    for bot_id in active_bot_ids:
        controller.stop_bot(bot_id)
    
    mt5.shutdown()
    logger.info("Koneksi MetaTrader 5 ditutup. Shutdown selesai.")

# --- Titik Eksekusi Utama ---
if __name__ == '__main__':
    # Memuat kredensial MT5 dari .env dengan aman
    try:
        ACCOUNT = int(os.getenv('MT5_LOGIN'))
        PASSWORD = os.getenv('MT5_PASSWORD')
        SERVER = os.getenv('MT5_SERVER', 'MetaQuotes-Demo')

        if not all([ACCOUNT, PASSWORD, SERVER]):
            logger.critical("Kredensial MT5 (LOGIN/PASSWORD/SERVER) tidak lengkap di file .env.")
            exit(1)

    except (ValueError, TypeError):
        logger.critical("Kredensial MT5_LOGIN harus berupa angka di file .env.")
        exit(1)

    # Inisialisasi koneksi ke MetaTrader 5
    if not initialize_mt5(ACCOUNT, PASSWORD, SERVER):
        logger.critical("GAGAL terhubung ke MetaTrader 5. Pastikan kredensial benar dan terminal berjalan.")
        exit(1)
    else:
        logger.info("Berhasil terhubung ke MetaTrader 5.")

        # Muat semua bot yang ada di database
        try:
            ambil_semua_bot()
            logger.info("Semua bot dari database berhasil dimuat.")
        except Exception as e:
            logger.error(f"Terjadi kesalahan saat memuat bot: {e}", exc_info=True)

        # --- 3. Daftarkan fungsi shutdown ---
        atexit.register(shutdown_handler)

        # Jalankan aplikasi Flask
        app.run(
            debug=os.getenv('FLASK_DEBUG', 'False').lower() == 'true',
            host=os.getenv('FLASK_HOST', '127.0.0.1'),
            port=int(os.getenv('FLASK_PORT', 5000)),
            use_reloader=False  # Penting: False untuk mencegah eksekusi ganda pada background thread
        )
