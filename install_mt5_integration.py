#!/usr/bin/env python3
"""
QuantumBotX MT5 Integration Installer
Automated setup for MT5 data downloading and integration

Usage: python install_mt5_integration.py
"""

import os
import sys
import subprocess
import platform
import json
import urllib.request
from pathlib import Path

class MT5IntegrationInstaller:
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.system = platform.system().lower()
        self.arch = platform.machine().lower()

    def print_header(self):
        """Print installation header"""
        print("=" * 60)
        print("🚀 QuantumBotX MT5 Integration Setup")
        print("=" * 60)
        print()

    def check_python_version(self):
        """Check Python version compatibility"""
        print("🐍 Checking Python version...")
        version = sys.version_info
        if version.major == 3 and version.minor >= 8:
            print(f"✅ Python {version.major}.{version.minor}.{version.micro} - Compatible")
            return True
        else:
            print(f"❌ Python {version.major}.{version.minor}.{version.micro} - Requires Python 3.8+")
            return False

    def check_mt5_library(self):
        """Check if MetaTrader5 library is installed"""
        print("\n📦 Checking MT5 Python library...")
        try:
            import MetaTrader5 as mt5
            version = getattr(mt5, '__version__', 'unknown')
            print(f"✅ MetaTrader5 library installed (v{version})")
            return True
        except ImportError:
            print("❌ MetaTrader5 library not found")
            return False

    def install_mt5_library(self):
        """Attempt to install MetaTrader5 library"""
        print("\n🚀 Installing MetaTrader5 library...")

        # Try pip installation first
        try:
            print("Trying standard pip installation...")
            subprocess.check_call([
                sys.executable, "-m", "pip", "install",
                "--prefer-binary", "MetaTrader5"
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print("✅ Successfully installed MetaTrader5 via pip")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Standard pip installation failed: {e}")

            # Try alternative installation methods
            if self._install_mt5_alternatives():
                return True

            return False

    def _install_mt5_alternatives(self):
        """Alternative MT5 installation methods"""
        print("\n🔄 Trying alternative installation methods...")

        # Method 1: Pre-compiled wheel
        wheel_urls = {
            'windows': {
                'amd64': [
                    'https://files.pythonhosted.org/packages/78/bb/e59deb5a4106b89d7d0b5ef8c3c61580a7d04378a5a5bbcef5234e8ad5632c6/MetaTrader5-5.0.45-cp39-cp39-win_amd64.whl',
                    'https://files.pythonhosted.org/packages/d9/a9/a7fe0c98bf74ec5c1b70e7b10b2f4cf5be58ead3b024902ab31a4afe81a0798/MetaTrader5-5.0.45-cp38-cp38-win_amd64.whl',
                    'https://files.pythonhosted.org/packages/f5/b7/3835fbab7dadbd1659eb0b90d22e92e3c9ddd2ce4a56fc2c3837ec415edde25/MetaTrader5-5.0.42-cp37-cp37m-win_amd64.whl'
                ]
            }
        }

        if self.system == 'windows' and 'amd64' in self.arch:
            print("💾 Trying pre-compiled wheel for Windows...")
            for wheel_url in wheel_urls['windows']['amd64']:
                try:
                    # Download and install wheel
                    wheel_name = wheel_url.split('/')[-1]
                    wheel_path = self.project_root / wheel_name

                    print(f"Downloading {wheel_name}...")
                    urllib.request.urlretrieve(wheel_url, wheel_path)

                    subprocess.check_call([
                        sys.executable, "-m", "pip", "install", str(wheel_path)
                    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

                    # Clean up
                    wheel_path.unlink(missing_ok=True)

                    print("✅ Successfully installed MetaTrader5 via wheel")
                    return True

                except Exception as e:
                    print(f"Wheel installation failed: {e}")
                    if wheel_path.exists():
                        wheel_path.unlink(missing_ok=True)
                    continue

        return False

    def create_env_template(self):
        """Create/update .env file with MT5 configuration"""
        print("\n⚙️  Configuring .env file...")

        env_file = self.project_root / '.env'
        env_example = self.project_root / '.env.example'

        if not env_example.exists():
            print("❌ .env.example not found!")
            return False

        # Read existing .env or create new one
        if env_file.exists():
            print("📄 Existing .env file found - backing up")
            backup = env_file.with_suffix('.env.backup')
            env_file.rename(backup)

        # Copy example file
        env_file.write_text(env_example.read_text())
        print("✅ Created .env file with MT5 configuration template")

        # Interactive configuration
        print("\n" + "="*50)
        print("📝 MT5 Configuration Required")
        print("="*50)
        print("Edit your .env file with your MT5 credentials:")
        print()
        print("Required settings:")
        print("- MT5_LOGIN=your_account_number")
        print("- MT5_PASSWORD=your_password")
        print("- MT5_SERVER=your_broker_server (e.g., FBS-Demo)")
        print()
        print("Example .env entries:")
        print("MT5_LOGIN=12345678")
        print("MT5_PASSWORD=mySecurePass123")
        print("MT5_SERVER=FBS-Demo")
        print()

        return True

    def check_mt5_installation(self):
        """Check if MetaTrader 5 platform is installed"""
        print("\n🏦 Checking MT5 platform installation...")

        mt5_paths = [
            r"C:\Program Files\MetaTrader 5",
            r"C:\Program Files (x86)\MetaTrader 5",
            os.path.expanduser(r"~\AppData\Local\MetaTrader 5"),
            os.path.expanduser(r"~\AppData\Roaming\MetaTrader 5")
        ]

        for path in mt5_paths:
            if os.path.exists(path) and os.path.isdir(path):
                terminal_exe = os.path.join(path, "terminal64.exe")
                if os.path.exists(terminal_exe):
                    print(f"✅ MT5 Platform found at: {path}")
                    print(f"   Executable: {terminal_exe}")
                    return True

        print("❓ MT5 Platform not found in common locations")
        print("💡 Download from: https://www.metatrader5.com/en/download")
        return False

    def create_download_test(self):
        """Create a test script to verify MT5 setup"""
        print("\n🧪 Creating MT5 connection test...")

        test_script = '''#!/usr/bin/env python3
"""
MT5 Connection Test Script
Run this to verify your MT5 setup works correctly
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Check credentials
login = os.getenv('MT5_LOGIN')
password = os.getenv('MT5_PASSWORD')
server = os.getenv('MT5_SERVER')

print("🧪 Testing MT5 Integration...")

if not all([login, password, server]):
    print("❌ Missing MT5 credentials in .env file!")
    print("Required: MT5_LOGIN, MT5_PASSWORD, MT5_SERVER")
    exit(1)

print("✅ Credentials found")

# Test MT5 import
try:
    import MetaTrader5 as mt5
    print("✅ MetaTrader5 library imported successfully")
except ImportError:
    print("❌ MetaTrader5 library not installed")
    exit(1)

# Test connection
print("🔗 Testing MT5 connection...")
if not mt5.initialize(login=int(login), password=password, server=server):
    error = mt5.last_error()
    print(f"❌ Failed to connect to MT5: {error}")
    exit(1)

print("✅ Successfully connected to MT5!")
print(f"📡 Server: {server}")
print(f"👤 Account: {login}")

# Test data download
print("\\n📊 Testing EURUSD data download...")
import pandas as pd
from datetime import datetime

try:
    rates = mt5.copy_rates_range("EURUSD", mt5.TIMEFRAME_H1, datetime(2024, 1, 1), datetime.now())

    if rates is None or len(rates) == 0:
        print("❌ No data received from MT5")
        exit(1)

    df = pd.DataFrame(rates)
    print(f"✅ Successfully downloaded {len(df)} EURUSD H1 bars")
    print(f"   📅 Date range: {df['time'].min()} to {df['time'].max()}")

except Exception as e:
    print(f"❌ Data download test failed: {e}")
    exit(1)

mt5.shutdown()
print("\\n🎉 All tests passed! MT5 integration is working correctly.")
'''

        test_file = self.project_root / 'test_mt5_connection.py'
        test_file.write_text(test_script)
        test_file.chmod(0o755)  # Make executable

        print("✅ Created test script: test_mt5_connection.py")
        print("🏃 Run with: python test_mt5_connection.py")

        return True

    def main(self):
        """Main installation process"""
        self.print_header()

        if not self.check_python_version():
            return False

        # Check if MT5 library is already installed
        mt5_installed = self.check_mt5_library()

        if not mt5_installed:
            print("\n" + "!"*60)
            print("❌ MT5 Python Library Required")
            print("!"*60)
            print()
            print("The MetaTrader5 Python library needs to be installed.")
            print("This requires:")
            print("• Administrator privileges (Windows)")
            print("• Visual C++ Redistributables (if missing)")
            print("• Internet connection for download")
            print()

            if not self.ask_user("Continue with automatic installation?"):
                print("Installation cancelled. Please install manually:")
                print("pip install MetaTrader5")
                return False

            if not self.install_mt5_library():
                print("❌ Automatic installation failed.")
                print("Try manual installation:")
                print("pip install MetaTrader5")
                return False

        # Verify installation worked
        if not self.check_mt5_library():
            print("❌ Library installation verification failed")
            return False

        # MT5 Platform check
        self.check_mt5_installation()

        # Environment configuration
        if not self.create_env_template():
            return False

        # Create test script
        self.create_download_test()

        # Final instructions
        print("\n" + "="*60)
        print("🎉 MT5 Integration Installed!")
        print("="*60)
        print()
        print("Next steps:")
        print("1. 📝 Edit your .env file with MT5 credentials")
        print("2. 🏦 Launch MT5 and login (demo account recommended)")
        print("3. 🧪 Test connection: python test_mt5_connection.py")
        print("4. 📊 Download data: python lab/download_data.py")
        print("   Or use the web interface: 'Download Data MT5' button")
        print()
        print("📖 Need help? Check MT5_SETUP_GUIDE.md")
        print()

        return True

    def ask_user(self, question):
        """Ask for user confirmation"""
        while True:
            response = input(f"{question} (y/n): ").lower().strip()
            if response in ['y', 'yes']:
                return True
            elif response in ['n', 'no']:
                return False
            print("Please enter 'y' or 'n'")

if __name__ == "__main__":
    installer = MT5IntegrationInstaller()

    try:
        success = installer.main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nInstallation cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Installation failed with error: {e}")
        sys.exit(1)
