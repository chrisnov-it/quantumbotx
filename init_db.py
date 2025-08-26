import sqlite3
import os
import sys
from werkzeug.security import generate_password_hash

# Nama file database
DB_FILE = "bots.db"

def create_connection(db_file):
    """ Membuat koneksi ke database SQLite """ 
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        print(f"Berhasil terhubung ke SQLite versi {sqlite3.version}")
        return conn
    except sqlite3.Error as e:
        print(e)
    return conn

def create_table(conn, create_table_sql):
    """ Membuat tabel dari statement SQL """ 
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
        print("Tabel berhasil dibuat.")
    except sqlite3.Error as e:
        print(e)

def main():
    # Only remove database if explicitly requested
    if '--force' in sys.argv:
        if os.path.exists(DB_FILE):
            try:
                os.remove(DB_FILE)
                print(f"File database lama '{DB_FILE}' telah dihapus.")
            except PermissionError:
                print(f"WARNING: Database '{DB_FILE}' sedang digunakan. Melanjutkan tanpa menghapus...")

    # SQL statement untuk membuat tabel 'users'
    sql_create_users_table = """
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE,
        password_hash TEXT NOT NULL,
        join_date DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    """

    # SQL statement untuk membuat tabel 'bots'
    sql_create_bots_table = """
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
        strategy_params TEXT
    );
    """

    # SQL statement untuk membuat tabel 'trade_history'
    sql_create_history_table = """
    CREATE TABLE IF NOT EXISTS trade_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        bot_id INTEGER NOT NULL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        action TEXT NOT NULL,
        details TEXT,
        is_notification INTEGER NOT NULL DEFAULT 0,
        is_read INTEGER NOT NULL DEFAULT 0,
        FOREIGN KEY (bot_id) REFERENCES bots (id) ON DELETE CASCADE
    );
    """

    # SQL statement untuk membuat tabel 'backtest_results'
    sql_create_backtest_results_table = """
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
        equity_curve TEXT, -- Disimpan sebagai JSON
        trade_log TEXT,    -- Disimpan sebagai JSON
        parameters TEXT    -- Disimpan sebagai JSON
    );
    """

    # SQL statement untuk membuat tabel 'trading_sessions' (AI Mentor)
    sql_create_trading_sessions_table = """
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
    );
    """

    # SQL statement untuk membuat tabel 'ai_mentor_reports' 
    sql_create_mentor_reports_table = """
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
    );
    """

    # SQL statement untuk membuat tabel 'daily_trading_data' (untuk analisis AI)
    sql_create_daily_trading_data_table = """
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
    );
    """

    # Buat koneksi database
    conn = create_connection(DB_FILE)

    # Buat tabel-tabel
    if conn is not None:
        print("\nMembuat tabel 'users'...")
        create_table(conn, sql_create_users_table)

        print("\nMembuat tabel 'bots'...")
        create_table(conn, sql_create_bots_table)

        print("\nMembuat tabel 'trade_history'...")
        create_table(conn, sql_create_history_table)

        print("\nMembuat tabel 'backtest_results'...")
        create_table(conn, sql_create_backtest_results_table)

        print("\nMembuat tabel 'trading_sessions' (AI Mentor)...")
        create_table(conn, sql_create_trading_sessions_table)

        print("\nMembuat tabel 'ai_mentor_reports'...")
        create_table(conn, sql_create_mentor_reports_table)

        print("\nMembuat tabel 'daily_trading_data' (AI Analysis)...")
        create_table(conn, sql_create_daily_trading_data_table)

        # Masukkan pengguna default
        try:
            print("\nMemasukkan pengguna default...")
            cursor = conn.cursor()
            # Gunakan password default 'admin' untuk pengguna pertama
            default_password_hash = generate_password_hash('admin')
            cursor.execute("INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)", 
                           ('Admin User', 'admin@quantumbotx.com', default_password_hash))
            conn.commit()
            print("Pengguna default berhasil dimasukkan.")
        except sqlite3.Error as e:
            print(f"Gagal memasukkan pengguna default: {e}")

        conn.close()
        print(f"\nDatabase '{DB_FILE}' berhasil dibuat dengan semua tabel yang diperlukan.")
    else:
        print("Error! Tidak dapat membuat koneksi database.")

if __name__ == '__main__':
    main()
