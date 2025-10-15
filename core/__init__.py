# core/__init__.py

import os
import sys
import logging
import sqlite3
from logging.handlers import RotatingFileHandler
from flask import Flask, render_template, send_from_directory
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash

class RequestLogFilter(logging.Filter):
    """Filter untuk menghilangkan noise dari terminal log."""
    def filter(self, record):
        msg = record.getMessage()
        
        # Selalu tampilkan log non-HTTP (trading bot activities, errors, dll)
        if not any(x in msg for x in ["GET ", "POST ", "PUT ", "DELETE ", "PATCH "]):
            return True
        
        # Selalu tampilkan HTTP errors (4xx, 5xx)
        if any(status in msg for status in [" 4", " 5"]):
            return True
            
        # Selalu tampilkan POST, PUT, DELETE (important actions)
        if any(method in msg for method in ["POST ", "PUT ", "DELETE ", "PATCH "]):
            return True
        
        # Filter GET requests yang berisik
        noisy_get_paths = [
            # Notification requests (sangat berisik!)
            "GET /api/notifications/unread",
            
            # Bot polling requests
            "GET /api/bots/analysis",
            "GET /api/bots/status",
            
            # Dashboard polling (hanya jika 200 OK)
            "GET /api/dashboard/stats",
            "GET /api/dashboard/chart-data", 
            "GET /api/portfolio/performance",
            
            # Market data polling
            "GET /api/forex",
            "GET /api/stocks",
            "GET /api/chart",
            
            # Health checks dan favicon
            "GET /api/health",
            "GET /favicon.ico",
            
            # Static files
            "GET /static/"
        ]
        
        # Filter out GET requests yang berisik HANYA jika status 200/304
        if any(path in msg for path in noisy_get_paths):
            if " 200 -" in msg or " 304 -" in msg:
                return False
        
        # Tampilkan semua request lainnya (termasuk GET yang error)
        return True

def init_database():
    """Initialize database and create tables if they don't exist."""
    try:
        # Get the directory where the executable is located
        if getattr(sys, 'frozen', False):
            # Running as PyInstaller bundle
            base_dir = os.path.dirname(sys.executable)
            db_path = os.path.join(base_dir, 'bots.db')
        else:
            # Running as script
            base_dir = os.path.dirname(os.path.abspath(__file__))
            db_path = os.path.join(base_dir, '..', '..', 'bots.db')

        # Create connection
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Create users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                join_date DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Create bots table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS bots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                market TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'Dijeda',
                lot_size REAL NOT NULL DEFAULT 0.01,
                sl_pips INTEGER NOT NULL DEFAULT 100,
                tp_pips INTEGER NOT NULL DEFAULT 200,
                timeframe TEXT NOT NULL DEFAULT 'H1',
                check_interval_seconds INTEGER NOT NULL DEFAULT 60,
                strategy TEXT NOT NULL,
                strategy_params TEXT,
                enable_strategy_switching INTEGER NOT NULL DEFAULT 0
            )
        ''')

        # Create trade_history table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS trade_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                bot_id INTEGER NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                action TEXT NOT NULL,
                details TEXT,
                is_notification INTEGER NOT NULL DEFAULT 0,
                is_read INTEGER NOT NULL DEFAULT 0,
                FOREIGN KEY (bot_id) REFERENCES bots (id) ON DELETE CASCADE
            )
        ''')

        # Create backtest_results table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS backtest_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                strategy_name TEXT NOT NULL,
                data_filename TEXT NOT NULL,
                total_profit_usd REAL NOT NULL,
                total_trades INTEGER NOT NULL,
                win_rate_percent REAL NOT NULL,
                max_drawdown_percent REAL NOT NULL,
                wins INTEGER NOT NULL,
                losses INTEGER NOT NULL,
                equity_curve TEXT,
                trade_log TEXT,
                parameters TEXT
            )
        ''')

        # Create trading_sessions table (AI Mentor)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS trading_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_date DATE NOT NULL,
                user_id INTEGER DEFAULT 1,
                total_trades INTEGER NOT NULL DEFAULT 0,
                total_profit_loss REAL NOT NULL DEFAULT 0.0,
                emotions TEXT NOT NULL DEFAULT 'netral',
                market_conditions TEXT NOT NULL DEFAULT 'normal',
                personal_notes TEXT,
                risk_score INTEGER DEFAULT 5,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
            )
        ''')

        # Create ai_mentor_reports table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ai_mentor_reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id INTEGER NOT NULL,
                trading_patterns_analysis TEXT,
                emotional_analysis TEXT,
                risk_management_score INTEGER,
                recommendations TEXT,
                motivation_message TEXT,
                language TEXT DEFAULT 'bahasa_indonesia',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (session_id) REFERENCES trading_sessions (id) ON DELETE CASCADE
            )
        ''')

        # Create daily_trading_data table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS daily_trading_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id INTEGER NOT NULL,
                bot_id INTEGER NOT NULL,
                symbol TEXT NOT NULL,
                entry_time DATETIME,
                exit_time DATETIME,
                profit_loss REAL NOT NULL,
                lot_size REAL NOT NULL,
                stop_loss_used BOOLEAN DEFAULT 0,
                take_profit_used BOOLEAN DEFAULT 0,
                risk_percent REAL,
                strategy_used TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (session_id) REFERENCES trading_sessions (id) ON DELETE CASCADE,
                FOREIGN KEY (bot_id) REFERENCES bots (id) ON DELETE CASCADE
            )
        ''')

        # Check if default user exists
        cursor.execute('SELECT COUNT(*) FROM users')
        if cursor.fetchone()[0] == 0:
            # Insert default user
            default_password_hash = generate_password_hash('admin')
            cursor.execute(
                'INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)',
                ('Admin User', 'admin@quantumbotx.com', default_password_hash)
            )

        conn.commit()
        conn.close()

    except Exception as e:
        raise Exception(f"Database initialization failed: {e}")

# ============================
# APPLICATION FACTORY FUNCTION
# ============================
def create_app():
    """
    Membuat dan mengkonfigurasi instance aplikasi Flask.
    """
    load_dotenv()

    app = Flask(
        __name__,
        instance_relative_config=True,
        template_folder='../templates',
        static_folder='../static'
    )

    # Initialize database on startup
    try:
        init_database()
        app.logger.info("Database initialized successfully")
    except Exception as e:
        app.logger.error(f"Failed to initialize database: {e}")
        # Don't crash the app, but log the error
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-here')
    
    # Konfigurasi logging yang lebih bersih
    if os.getenv('FLASK_DEBUG', 'false').lower() != 'true':
        log_dir = os.path.join(app.root_path, '..', 'logs')
        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, 'app.log')
        file_handler = RotatingFileHandler(log_file, maxBytes=1024 * 1024 * 5, backupCount=5)
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
        
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        
        # Filter werkzeug noise secara menyeluruh
        werkzeug_logger = logging.getLogger('werkzeug')
        werkzeug_logger.setLevel(logging.WARNING)  # Hanya tampilkan warning dan error
        werkzeug_logger.addFilter(RequestLogFilter())
        
        app.logger.info("QuantumBotX dimulai dalam mode PRODUKSI - Log terminal dibersihkan!")
    else:
        # Bahkan dalam debug mode, tetap filter werkzeug noise
        werkzeug_logger = logging.getLogger('werkzeug')
        werkzeug_logger.setLevel(logging.WARNING)
        werkzeug_logger.addFilter(RequestLogFilter())
        
        app.logger.info("QuantumBotX dimulai dalam mode DEBUG - Log minimal.")

    from .routes.api_dashboard import api_dashboard
    from .routes.api_chart import api_chart
    from .routes.api_bots import api_bots
    from .routes.api_profile import api_profile
    from .routes.api_portfolio import api_portfolio
    from .routes.api_history import api_history
    from .routes.api_notifications import api_notifications
    from .routes.api_stocks import api_stocks
    from .routes.api_forex import api_forex
    from .routes.api_fundamentals import api_fundamentals
    from .routes.api_backtest import api_backtest
    from .routes.ai_mentor import ai_mentor_bp
    from .routes.api_strategy_switcher import api_strategy_switcher
    from .routes.api_ramadan import api_ramadan
    from .routes.api_holiday import api_holiday

    app.register_blueprint(api_dashboard)
    app.register_blueprint(api_chart)
    app.register_blueprint(api_bots)
    app.register_blueprint(api_profile)
    app.register_blueprint(api_portfolio)
    app.register_blueprint(api_history)
    app.register_blueprint(api_notifications)
    app.register_blueprint(api_stocks)
    app.register_blueprint(api_forex)
    app.register_blueprint(api_fundamentals)
    app.register_blueprint(api_backtest)
    app.register_blueprint(ai_mentor_bp)
    app.register_blueprint(api_strategy_switcher)
    app.register_blueprint(api_ramadan)
    app.register_blueprint(api_holiday)

    @app.route('/')
    def dashboard():
        return render_template('index.html', active_page='dashboard')

    @app.route('/trading_bots')
    def bots_page():
        return render_template('trading_bots.html', active_page='trading_bots')

    @app.route('/bots/<int:bot_id>')
    def bot_detail_page(bot_id):
        return render_template('bot_detail.html', active_page='trading_bots')

    @app.route('/backtesting')
    def backtesting_page():
        return render_template('backtesting.html', active_page='backtesting')

    @app.route('/backtest_history')
    def backtest_history_page():
        return render_template('backtest_history.html', active_page='backtesting')

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
        return render_template('profile.html', active_page='profile')

    @app.route('/notifications')
    def notifications_page():
        return render_template('notifications.html', active_page='notifications')

    @app.route('/stocks')
    def stocks_page():
        return render_template('stocks.html', active_page='stocks')

    @app.route('/forex')
    def forex_page():
        return render_template('forex.html', active_page='forex')

    @app.route('/strategy-switcher')
    def strategy_switcher_page():
        return render_template('strategy_switcher/dashboard.html', active_page='strategy_switcher')
        
    @app.route('/ramadan')
    def ramadan_page():
        return render_template('ramadan.html', active_page='ramadan')

    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('404.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        app.logger.error(f"Internal Server Error: {error}", exc_info=True)
        return render_template('500.html'), 500

    @app.route('/favicon.ico')
    def favicon():
        return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

    return app
