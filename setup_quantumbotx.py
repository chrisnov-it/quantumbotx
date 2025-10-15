#!/usr/bin/env python3
"""
QuantumBotX Setup Script
Automated setup for non-technical users
"""

import os
import subprocess
from pathlib import Path

def run_command(command, shell=True):
    """Run a command and return the result."""
    try:
        result = subprocess.run(command, shell=shell, capture_output=True, text=True)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def check_python():
    """Check if Python is installed."""
    success, _, _ = run_command("python --version")
    return success

def install_requirements():
    """Install Python requirements."""
    print("Installing Python dependencies...")
    success, stdout, stderr = run_command("pip install -r requirements.txt")
    if not success:
        print(f"Error installing requirements: {stderr}")
        return False
    print("✓ Python dependencies installed successfully")
    return True

def create_startup_scripts():
    """Create user-friendly startup scripts."""
    print("Creating startup scripts...")

    # Create start.bat
    start_bat = '''@echo off
echo Starting QuantumBotX Trading Application...
echo =========================================
echo.
echo Make sure MetaTrader 5 is running before continuing!
echo.
pause
echo.
python run.py
pause
'''

    with open('start.bat', 'w') as f:
        f.write(start_bat)

    # Create start.sh for Unix-like systems (if needed)
    start_sh = '''#!/bin/bash
echo "Starting QuantumBotX Trading Application..."
echo "========================================"
echo ""
echo "Make sure MetaTrader 5 is running before continuing!"
echo ""
read -p "Press Enter to continue..."
echo ""
python3 run.py
'''

    with open('start.sh', 'w') as f:
        f.write(start_sh)

    # Make start.sh executable on Unix systems
    try:
        os.chmod('start.sh', 0o755)
    except:
        pass  # Windows doesn't need this

    print("✓ Startup scripts created")
    return True

def create_desktop_shortcut():
    """Create desktop shortcut (Windows only)."""
    print("Creating desktop shortcut...")

    try:
        # Get user's desktop path
        desktop = Path.home() / "Desktop"
        shortcut_path = desktop / "QuantumBotX.lnk"

        # Create a simple batch file that will be the shortcut target
        shortcut_bat = '''@echo off
cd /d "%~dp0"
start.bat
'''

        with open('quantum_botx_shortcut.bat', 'w') as f:
            f.write(shortcut_bat)

        print("✓ Desktop shortcut script created")
        print(f"  You can manually create a shortcut to: {os.path.abspath('quantum_botx_shortcut.bat')}")
        print("  And place it on your desktop")

    except Exception as e:
        print(f"Note: Could not create desktop shortcut automatically: {e}")
        print("  You can manually create a shortcut to start.bat on your desktop")
        return True

def create_user_instructions():
    """Create user-friendly instructions."""
    print("Creating user instructions...")

    instructions = '''# QuantumBotX - Quick Start Guide

## First Time Setup

1. **Install MetaTrader 5**
   - Download from: https://www.metatrader5.com/
   - Install and create a demo account
   - Keep MT5 running in the background

2. **Configure Your Settings**
   - Copy `.env.example` to `.env`
   - Edit `.env` with your MT5 credentials:
     ```
     MT5_LOGIN=your_account_number
     MT5_PASSWORD=your_password
     MT5_SERVER=your_server_name
     ```

3. **Start the Application**
   - Double-click `start.bat` (Windows)
   - Open http://127.0.0.1:5000 in your browser

## Daily Use

1. Start MetaTrader 5 first
2. Run `start.bat`
3. Open your web browser to http://127.0.0.1:5000

## Troubleshooting

- Make sure MetaTrader 5 is running
- Check your .env file has correct credentials
- If the app won't start, try running `python run.py` directly

## Support

If you need help, check the README.md file or contact support.
'''

    with open('QUICK_START_GUIDE.md', 'w') as f:
        f.write(instructions)

    print("✓ User instructions created")
    return True

def main():
    """Main setup function."""
    print("QuantumBotX Setup Wizard")
    print("========================")
    print()

    # Check Python
    if not check_python():
        print("❌ Python is not installed or not in PATH")
        print("Please install Python 3.8 or higher from https://python.org")
        input("Press Enter to exit...")
        return

    print("✓ Python found")

    # Install requirements
    if not install_requirements():
        print("❌ Failed to install requirements")
        input("Press Enter to exit...")
        return

    # Create startup scripts
    if not create_startup_scripts():
        print("❌ Failed to create startup scripts")
        input("Press Enter to exit...")
        return

    # Create desktop shortcut
    create_desktop_shortcut()

    # Create user instructions
    if not create_user_instructions():
        print("❌ Failed to create user instructions")
        input("Press Enter to exit...")
        return

    print()
    print("🎉 Setup Complete!")
    print("==================")
    print()
    print("Next steps:")
    print("1. Install and configure MetaTrader 5")
    print("2. Copy .env.example to .env and configure your credentials")
    print("3. Run start.bat to launch the application")
    print("4. Open http://127.0.0.1:5000 in your browser")
    print()
    print("See QUICK_START_GUIDE.md for detailed instructions")
    print()
    input("Press Enter to exit...")

if __name__ == "__main__":
    main()
