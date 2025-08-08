import sqlite3
import os

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
    # Hapus database lama jika ada, untuk memastikan mulai dari awal
    if os.path.exists(DB_FILE):
        os.remove(DB_FILE)
        print(f"File database lama '{DB_FILE}' telah dihapus.")

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

    # Buat koneksi database
    conn = create_connection(DB_FILE)

    # Buat tabel-tabel
    if conn is not None:
        print("\nMembuat tabel 'bots'...")
        create_table(conn, sql_create_bots_table)

        print("\nMembuat tabel 'trade_history'...")
        create_table(conn, sql_create_history_table)     
        
        # --- TAMBAHKAN INI ---
        print("\nMembuat tabel 'backtest_results'...")
        sql_create_backtest_results_table = """
        CREATE TABLE IF NOT EXISTS backtest_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            strategy_name TEXT NOT NULL,
            data_filename TEXT NOT NULL,
            total_profit_pips REAL NOT NULL,
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
        create_table(conn, sql_create_backtest_results_table)
        # --- SELESAI PENAMBAHAN ---

        conn.close()
        print(f"\nDatabase '{DB_FILE}' berhasil dibuat dengan semua tabel yang diperlukan.")
    else:
        print("Error! Tidak dapat membuat koneksi database.")

if __name__ == '__main__':
    main()