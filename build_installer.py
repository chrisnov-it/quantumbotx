#!/usr/bin/env python3
"""
QuantumBotX Windows Installer Builder
Builds the complete installer package for distribution
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def run_command(command, shell=True, cwd=None):
    """Run a command and return the result."""
    try:
        print(f"Running: {command}")
        result = subprocess.run(command, shell=shell, cwd=cwd, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(result.stderr, file=sys.stderr)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def check_requirements():
    """Check if all required tools are installed."""
    print("Checking requirements...")

    # Check PyInstaller
    success, _, _ = run_command("pyinstaller --version")
    if not success:
        print("❌ PyInstaller not found. Installing...")
        run_command("pip install pyinstaller")

    # Check NSIS (we'll assume it's installed or provide instructions)
    print("✓ PyInstaller found")

    # Check if favicon exists for installer icon
    if not os.path.exists("static/favicon.ico"):
        print("⚠️  Warning: static/favicon.ico not found. Installer will use default icon.")

    return True

def clean_previous_builds():
    """Clean previous build artifacts."""
    print("Cleaning previous builds...")

    directories_to_clean = [
        "build",
        "dist",
        "__pycache__",
        "*.spec~"
    ]

    for path in directories_to_clean:
        if os.path.exists(path):
            if os.path.isfile(path):
                os.remove(path)
            else:
                shutil.rmtree(path)
            print(f"  Cleaned: {path}")

    # Clean Python cache
    for root, dirs, files in os.walk("."):
        for dir_name in dirs:
            if dir_name == "__pycache__":
                pycache_path = os.path.join(root, dir_name)
                shutil.rmtree(pycache_path)
                print(f"  Cleaned: {pycache_path}")

def build_with_pyinstaller():
    """Build the application using PyInstaller."""
    print("Building with PyInstaller...")

    # Build the executable
    success, stdout, stderr = run_command("pyinstaller --clean quantumbotx.spec")

    if not success:
        print(f"❌ PyInstaller build failed: {stderr}")
        return False

    print("✓ PyInstaller build completed successfully")
    return True

def create_installer():
    """Create the Windows installer using NSIS."""
    print("Creating Windows installer...")

    # Check if NSIS is installed
    success, _, _ = run_command("makensis /VERSION")
    if not success:
        print("❌ NSIS not found!")
        print("Please install NSIS from: https://nsis.sourceforge.io/Download")
        print("Or download from: https://nsis.sourceforge.io/Download")
        print()
        print("Alternative: You can manually install the application by:")
        print("1. Running the PyInstaller build")
        print("2. Copying the dist/QuantumBotX folder to the target computer")
        print("3. Running setup_quantumbotx.py on the target computer")
        return False

    # Create the installer
    success, stdout, stderr = run_command("makensis installer.nsi")

    if not success:
        print(f"❌ NSIS build failed: {stderr}")
        return False

    print("✓ Windows installer created successfully")
    return True

def create_portable_package():
    """Create a portable ZIP package as alternative."""
    print("Creating portable ZIP package...")

    try:
        import zipfile

        # Create portable package
        portable_name = "QuantumBotX-Portable.zip"

        with zipfile.ZipFile(portable_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Add the main executable and supporting files
            dist_path = Path("dist/QuantumBotX")
            if dist_path.exists():
                for file_path in dist_path.rglob("*"):
                    if file_path.is_file():
                        arcname = file_path.relative_to("dist")
                        zipf.write(file_path, arcname)

                # Add additional files
                additional_files = [
                    "start.bat",
                    "start.sh",
                    "setup_quantumbotx.py",
                    "requirements.txt",
                    ".env.example",
                    "README.md",
                    "QUICK_START_GUIDE.md",
                    "MT5_SETUP_GUIDE.md"
                ]

                for file_name in additional_files:
                    if os.path.exists(file_name):
                        zipf.write(file_name, file_name)

        print(f"✓ Portable package created: {portable_name}")
        return True

    except ImportError:
        print("⚠️  zipfile not available, skipping portable package")
        return False
    except Exception as e:
        print(f"❌ Error creating portable package: {e}")
        return False

def main():
    """Main build function."""
    print("QuantumBotX Windows Installer Builder")
    print("====================================")
    print()

    # Check requirements
    if not check_requirements():
        print("❌ Requirements check failed")
        input("Press Enter to exit...")
        return

    # Clean previous builds
    clean_previous_builds()

    # Build with PyInstaller
    if not build_with_pyinstaller():
        print("❌ PyInstaller build failed")
        input("Press Enter to exit...")
        return

    # Create installer
    installer_created = create_installer()

    # Create portable package as backup
    create_portable_package()

    print()
    if installer_created:
        print("🎉 Build Complete!")
        print("==================")
        print("✓ Windows installer: QuantumBotX-Installer.exe")
        print("✓ Portable package: QuantumBotX-Portable.zip")
        print()
        print("Distribution files are ready in the current directory.")
        print()
        print("To test the installer:")
        print("1. Copy QuantumBotX-Installer.exe to a test computer")
        print("2. Run the installer")
        print("3. Follow the setup wizard")
        print()
    else:
        print("⚠️  Build Complete (Installer not available)")
        print("=============================================")
        print("✓ Application executable: dist/QuantumBotX/")
        print("✓ Portable package: QuantumBotX-Portable.zip")
        print()
        print("Since NSIS is not installed, you have these options:")
        print("1. Install NSIS and run this script again")
        print("2. Use the portable version (dist/QuantumBotX/)")
        print("3. Manually copy files to target computer")
        print()

    print("Next steps for end users:")
    print("1. Install MetaTrader 5")
    print("2. Configure .env file with MT5 credentials")
    print("3. Run start.bat to launch the application")
    print()

    input("Press Enter to exit...")

if __name__ == "__main__":
    main()
