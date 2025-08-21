# core/__init__.py

import os
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask, render_template, send_from_directory
from dotenv import load_dotenv

class RequestLogFilter(logging.Filter):
    def filter(self, record):
        msg = record.getMessage()
        paths_to_ignore = [
            "GET /api/notifications/unread-count",
            "GET /api/bots/analysis"
        ]
        return not any(path in msg for path in paths_to_ignore)

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
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-here')
    
    # Hanya konfigurasi logging ke file jika TIDAK dalam mode debug
    if os.getenv('FLASK_DEBUG', 'false').lower() != 'true':
        log_dir = os.path.join(app.root_path, '..', 'logs')
        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, 'app.log')
        file_handler = RotatingFileHandler(log_file, maxBytes=1024 * 1024 * 5, backupCount=5)
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
        
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        werkzeug_logger = logging.getLogger('werkzeug')
        werkzeug_logger.addFilter(RequestLogFilter())
        app.logger.info("Aplikasi QuantumBotX dimulai dalam mode PRODUKSI.")
    else:
        app.logger.info("Aplikasi QuantumBotX dimulai dalam mode DEBUG.")

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