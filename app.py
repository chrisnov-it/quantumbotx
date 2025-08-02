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
from core.routes.api_dashboard import api_dashboard
from core.routes.api_chart import api_chart
from core.routes.api_bots import api_bots
from core.routes.api_profile import api_profile
from core.routes.api_portfolio import api_portfolio
from core.routes.api_history import api_history
from core.routes.api_notifications import api_notifications
from core.routes.api_stocks import api_stocks
from core.routes.api_forex import api_forex
from core.routes.api_fundamentals import api_fundamentals
from core.routes.api_backtest import api_backtest

# Buat daftar semua blueprints untuk registrasi yang lebih rapi
blueprints = [
    api_dashboard, api_chart, api_bots, api_profile, api_portfolio, api_history,
    api_notifications, api_stocks, api_forex, api_fundamentals, api_backtest
]

# Daftarkan setiap blueprint ke aplikasi
for blueprint in blueprints:
    app.register_blueprint(blueprint)

# --- Rute Halaman (Views) ---
@app.route('/')
def dashboard():
    return render_template('index.html', active_page='dashboard')

@app.route('/trading_bots')
def bots_page():
    return render_template('trading_bots.html', active_page='trading_bots')

@app.route('/bots/<int:bot_id>')
def bot_detail_page(bot_id):
    return render_template('bot_detail.html', active_page='trading_bots') # Tetap di menu trading_bots

@app.route('/backtesting')
def backtesting_page():
    return render_template('backtesting.html', active_page='backtesting')

@app.route('/portfolio')
def portfolio_page():
    return render_template('portfolio.html', active_page='portfolio')

@app.route('/history')
def history_page():
    return render_template('history.html', active_page='history')

@app.route('/settings')
def settings_page():
    return render_template('settings.html', active_page='settings')

@app.route('/profile')
def profile_page():
    return render_template('profile.html', active_page='profile') # Asumsi profile punya menu sendiri

@app.route('/notifications')
def notifications_page():
    return render_template('notifications.html', active_page='notifications')

@app.route('/stocks')
def stocks_page():
    return render_template('stocks.html', active_page='stocks')

@app.route('/forex')
def forex_page():
    return render_template('forex.html', active_page='forex')

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
    if active_bot_ids:
        logger.info(f"Menghentikan {len(active_bot_ids)} bot yang aktif...")
    
    for bot_id in active_bot_ids:
        try:
            logger.info(f"Memberi sinyal berhenti untuk bot ID {bot_id}...")
            controller.stop_bot(bot_id)
        except KeyboardInterrupt:
            # Abaikan Ctrl+C tambahan saat proses shutdown sedang berlangsung.
            logger.warning(f"KeyboardInterrupt diterima saat menghentikan bot {bot_id}. Melanjutkan proses shutdown.")
            continue
        except Exception as e:
            logger.error(f"Error tak terduga saat menghentikan bot {bot_id} selama shutdown: {e}")
    
    mt5.shutdown() # Pastikan koneksi MT5 selalu ditutup
    logger.info("Koneksi MetaTrader 5 ditutup. Proses shutdown selesai.")

# --- Filter Log Kustom ---
class RequestLogFilter(logging.Filter):
    """
    Filter untuk menyembunyikan log permintaan (polling) yang tidak penting dari terminal.
    """
    def filter(self, record):
        # Pesan log dari Werkzeug terlihat seperti: "GET /api/path HTTP/1.1" 200 -
        msg = record.getMessage()
        # Daftar path yang ingin kita sembunyikan dari log konsol
        paths_to_ignore = [
            "GET /api/notifications/unread-count",
            "GET /api/bots/analysis" # <-- Ini juga sering di-poll
        ]
        return not any(path in msg for path in paths_to_ignore)

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
    # PERBAIKAN: Jangan langsung exit. Coba hubungkan, tapi biarkan aplikasi tetap berjalan jika gagal.
    # Koneksi akan dicoba lagi saat bot pertama kali dimulai.
    if initialize_mt5(ACCOUNT, PASSWORD, SERVER):
        logger.info("Berhasil terhubung ke MetaTrader 5.")
        # Muat semua bot yang ada di database
        try:
            ambil_semua_bot()
            logger.info("Semua bot dari database berhasil dimuat.")
        except Exception as e:
            logger.error(f"Terjadi kesalahan saat memuat bot: {e}", exc_info=True)
    else:
        logger.warning("GAGAL terhubung ke MetaTrader 5 saat startup. Aplikasi akan berjalan tanpa koneksi live.")
        logger.warning("Fitur bot live tidak akan berfungsi sampai koneksi MT5 pulih.")

    # --- Terapkan Filter Log ---
    # Dapatkan logger bawaan Werkzeug dan tambahkan filter kita
    werkzeug_logger = logging.getLogger('werkzeug')
    werkzeug_logger.addFilter(RequestLogFilter())
 
    # --- 3. Daftarkan fungsi shutdown ---
    # PERBAIKAN: Pindahkan ke luar blok if/else agar selalu dijalankan.
    atexit.register(shutdown_handler)
 
    # Jalankan aplikasi Flask
    # PERBAIKAN: Pindahkan ke luar blok if/else agar server selalu berjalan.
    app.run(
        debug=os.getenv('FLASK_DEBUG', 'False').lower() == 'true',
        host=os.getenv('FLASK_HOST', '127.0.0.1'),
        port=int(os.getenv('FLASK_PORT', 5000)),
        use_reloader=False  # Penting: False untuk mencegah eksekusi ganda pada background thread
    )
