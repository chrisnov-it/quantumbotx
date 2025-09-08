import sqlite3
import os

# Nama file database
DB_FILE = "bots.db"

def migrate_database():
    """Migrate the database to add the enable_strategy_switching column"""
    try:
        # Check if database exists
        if not os.path.exists(DB_FILE):
            print(f"Database file '{DB_FILE}' not found. Run init_db.py first.")
            return False
            
        # Connect to database
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        # Check if the column already exists
        cursor.execute("PRAGMA table_info(bots)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'enable_strategy_switching' in columns:
            print("Column 'enable_strategy_switching' already exists in bots table.")
            conn.close()
            return True
            
        # Add the new column
        cursor.execute("ALTER TABLE bots ADD COLUMN enable_strategy_switching INTEGER NOT NULL DEFAULT 0")
        conn.commit()
        print("Successfully added 'enable_strategy_switching' column to bots table.")
        
        conn.close()
        return True
        
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return False
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == '__main__':
    print("Migrating database to add strategy switching support...")
    success = migrate_database()
    if success:
        print("Database migration completed successfully!")
    else:
        print("Database migration failed!")