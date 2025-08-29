# clean_data.py - Clean existing CSV files for QuantumBotX backtesting compatibility
import pandas as pd
import os
import glob

def clean_csv_file(file_path):
    """
    Clean a CSV file to match QuantumBotX backtesting engine requirements
    Expected columns: time, open, high, low, close, volume
    """
    try:
        # Read the CSV file
        df = pd.read_csv(file_path)
        
        print(f"📁 Processing: {os.path.basename(file_path)}")
        print(f"   Original columns: {list(df.columns)}")
        print(f"   Original rows: {len(df)}")
        
        # Check if already in correct format
        expected_columns = ['time', 'open', 'high', 'low', 'close', 'volume']
        if list(df.columns) == expected_columns:
            print(f"   ✅ Already in correct format!")
            return True
        
        # Clean and standardize columns
        if 'tick_volume' in df.columns:
            df = df.rename(columns={'tick_volume': 'volume'})
        
        # Remove unnecessary columns
        keep_columns = ['time', 'open', 'high', 'low', 'close', 'volume']
        available_columns = [col for col in keep_columns if col in df.columns]
        
        if len(available_columns) < 5:  # Need at least time, ohlc
            print(f"   ❌ Missing required columns. Available: {available_columns}")
            return False
        
        # Keep only the required columns
        df_cleaned = df[available_columns].copy()
        
        # Ensure volume column exists (use 0 if not available)
        if 'volume' not in df_cleaned.columns:
            df_cleaned['volume'] = 0
            print(f"   ⚠️ Added missing volume column (set to 0)")
        
        # Ensure proper column order
        df_cleaned = df_cleaned[expected_columns]
        
        # Save the cleaned file (backup original with .bak extension)
        backup_path = file_path + '.bak'
        if not os.path.exists(backup_path):
            os.rename(file_path, backup_path)
            print(f"   📋 Backed up original to: {os.path.basename(backup_path)}")
        
        # Save cleaned data
        df_cleaned.to_csv(file_path, index=False)
        
        print(f"   ✅ Cleaned! New columns: {list(df_cleaned.columns)}")
        print(f"   📊 Final rows: {len(df_cleaned)}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Error cleaning {file_path}: {e}")
        return False

def main():
    """Clean all CSV files in the lab directory"""
    
    # Find all CSV files in lab directory
    csv_files = glob.glob("*.csv")
    
    if not csv_files:
        print("❌ No CSV files found in current directory")
        return
    
    print(f"🧹 Found {len(csv_files)} CSV files to clean")
    print("="*50)
    
    success_count = 0
    
    for csv_file in csv_files:
        if clean_csv_file(csv_file):
            success_count += 1
        print()  # Empty line for readability
    
    print("="*50)
    print(f"🎉 Cleaning Complete!")
    print(f"✅ Successfully cleaned: {success_count}/{len(csv_files)} files")
    
    if success_count > 0:
        print("\n💡 Tips:")
        print("   • Original files backed up with .bak extension")
        print("   • Files now compatible with QuantumBotX backtesting")
        print("   • Upload via web interface for backtesting")
        
        # Show example of cleaned file
        sample_file = csv_files[0]
        if os.path.exists(sample_file):
            print(f"\n📋 Sample cleaned data from {sample_file}:")
            df_sample = pd.read_csv(sample_file)
            print(f"   Columns: {list(df_sample.columns)}")
            print(f"   First 3 rows:")
            print("   " + "\n   ".join(df_sample.head(3).to_string().split('\n')))

if __name__ == "__main__":
    main()