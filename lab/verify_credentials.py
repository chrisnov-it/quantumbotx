# verify_credentials.py - Verify .env configuration for MT5
import os
from dotenv import load_dotenv

def verify_env_config():
    """Verify that .env file is properly configured for MT5 data download"""
    
    # Load environment variables
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    env_path = os.path.join(project_root, '.env')
    
    print(f"🔍 Checking environment configuration...")
    print(f"📁 Project root: {project_root}")
    print(f"📄 .env file path: {env_path}")
    
    if not os.path.exists(env_path):
        print("❌ .env file not found!")
        return False
    
    load_dotenv(env_path)
    
    # Check MT5 credentials
    mt5_login = os.getenv('MT5_LOGIN', '')
    mt5_password = os.getenv('MT5_PASSWORD', '')
    mt5_server = os.getenv('MT5_SERVER', '')
    
    print(f"\n📊 MT5 Configuration Status:")
    print(f"   Login: {'✅ Found' if mt5_login else '❌ Missing'} ({mt5_login if mt5_login else 'Not set'})")
    print(f"   Password: {'✅ Found' if mt5_password else '❌ Missing'} ({'*' * len(mt5_password) if mt5_password else 'Not set'})")
    print(f"   Server: {'✅ Found' if mt5_server else '❌ Missing'} ({mt5_server if mt5_server else 'Not set'})")
    
    # Check if all required credentials are present
    all_present = all([mt5_login, mt5_password, mt5_server])
    
    if all_present:
        print(f"\n🎉 All MT5 credentials are properly configured!")
        print(f"🔗 Ready to connect to: {mt5_server}")
        
        # Additional project configuration
        flask_debug = os.getenv('FLASK_DEBUG', 'false')
        db_name = os.getenv('DB_NAME', 'bots.db')
        
        print(f"\n⚙️ Additional Configuration:")
        print(f"   Flask Debug: {flask_debug}")
        print(f"   Database: {db_name}")
        
        return True
    else:
        print(f"\n❌ Missing MT5 credentials in .env file!")
        print(f"\n🔧 To fix this, add the following to your .env file:")
        if not mt5_login:
            print(f"   MT5_LOGIN=your_account_number")
        if not mt5_password:
            print(f"   MT5_PASSWORD=your_password")
        if not mt5_server:
            print(f"   MT5_SERVER=your_server_name")
        
        return False

if __name__ == "__main__":
    success = verify_env_config()
    
    if success:
        print(f"\n✅ Configuration verified! You can now run:")
        print(f"   python download_data.py")
        print(f"   python test_download.py")
    else:
        print(f"\n🔧 Please fix the configuration issues above first.")