# QuantumBotX Windows Packaging Guide

This guide explains how to package your QuantumBotX trading application into a Windows installer for distribution to non-technical users.

## 🎯 What This Packaging Solution Provides

✅ **Single EXE Installer** - Professional Windows installer
✅ **One-Click Installation** - Simple for end users
✅ **Desktop Shortcuts** - Easy application access
✅ **Uninstaller** - Clean removal capability
✅ **Setup Wizard** - Automated first-time setup
✅ **User-Friendly Scripts** - Simple startup process
✅ **Comprehensive Documentation** - Clear instructions for users

## 📋 Prerequisites

### For Building the Package
1. **Python 3.8+** (already installed)
2. **PyInstaller** (already installed via this guide)
3. **NSIS (Optional)** - For creating the installer EXE
   - Download from: https://nsis.sourceforge.io/Download
   - Install and ensure `makensis` is in your PATH

### For End Users
1. **Windows 7+** (64-bit recommended)
2. **MetaTrader 5** - Must be installed separately
3. **Internet Connection** - For initial setup

## 🚀 Quick Start

### Option 1: Build Everything (Recommended)
```bash
python build_installer.py
```

### Option 2: Manual Build Process
```bash
# 1. Build with PyInstaller
pyinstaller --clean quantumbotx.spec

# 2. Create portable version (optional)
python -c "import zipfile; zipf=zipfile.ZipFile('QuantumBotX-Portable.zip','w',8); [zipf.write(f,f) for d in ['dist/QuantumBotX','.'] for f in [os.path.join(r,d) for r,_,fs in os.walk(d) for f in fs]]"

# 3. Create installer (requires NSIS)
makensis installer.nsi
```

## 📁 Generated Files

After successful build, you'll have:

```txt
QuantumBotX-Installer.exe      # Main Windows installer
QuantumBotX-Portable.zip      # Portable version (alternative)
dist/QuantumBotX/            # PyInstaller output (for troubleshooting)
```

## 🎮 For End Users

### Installation Process
1. **Download** `QuantumBotX-Installer.exe`
2. **Run** the installer (requires admin privileges)
3. **Follow** the setup wizard
4. **Launch** from desktop shortcut or start menu

### Daily Usage
1. **Start MetaTrader 5** first
2. **Launch QuantumBotX** via desktop shortcut or start menu
3. **Open browser** to http://127.0.0.1:5000
4. **Configure settings** if needed

## 🔧 Configuration Files

The installer includes these configuration files:

- **`.env.example`** - Template for environment variables
- **`start.bat`** - Windows startup script
- **`setup_quantumbotx.py`** - Setup wizard for first run
- **`QUICK_START_GUIDE.md`** - User instructions

## 🛠️ Troubleshooting

### Build Issues

**PyInstaller fails:**
```bash
# Clean and rebuild
pyinstaller --clean quantumbotx.spec
```

**NSIS not found:**
- Install NSIS from https://nsis.sourceforge.io/
- Or use the portable version instead

**Missing dependencies:**
```bash
pip install -r requirements.txt
```

### Runtime Issues

**Application won't start:**
- Check if MetaTrader 5 is running
- Verify `.env` file has correct credentials
- Check Windows Event Viewer for errors

**Port already in use:**
- Close other applications using port 5000
- Or modify `FLASK_PORT` in `.env` file

**MetaTrader 5 connection fails:**
- Verify MT5 credentials in `.env`
- Ensure MT5 is running and logged in
- Check MT5 terminal for connection status

## 📦 Distribution

### For Technical Users
- Share `QuantumBotX-Installer.exe` for full installation
- Or share `QuantumBotX-Portable.zip` for manual installation

### For Non-Technical Users
1. **Share the installer** `QuantumBotX-Installer.exe`
2. **Provide simple instructions:**
   - Double-click to install
   - Follow the setup wizard
   - Use desktop shortcut to launch
   - Ensure MetaTrader 5 is running

### System Requirements for End Users
- **OS:** Windows 7 SP1+ (64-bit recommended)
- **RAM:** 4GB minimum, 8GB recommended
- **Storage:** 500MB free space
- **Network:** Internet connection for initial setup
- **Software:** MetaTrader 5 (installed separately)

## 🔄 Updates and Maintenance

### Creating Updates
1. **Increment version** in `installer.nsi`
2. **Rebuild** using `python build_installer.py`
3. **Test** on clean system
4. **Distribute** new installer

### Uninstallation
- Use Windows Add/Remove Programs
- Or run `Uninstall.exe` from installation directory
- Or use the uninstall shortcut in Start Menu

## 🆘 Support

### Common User Questions

**"How do I configure my MT5 credentials?"**
- Copy `.env.example` to `.env`
- Edit `.env` with your MT5 account details
- Restart the application

**"The application says MT5 is not connected"**
- Ensure MetaTrader 5 is running
- Check MT5 login credentials
- Verify MT5 server settings

**"I can't access the web interface"**
- Check if the application is running
- Verify the URL: http://127.0.0.1:5000
- Check firewall settings

## 🎯 Advanced Configuration

### Customizing the Installer
Edit `installer.nsi` to:
- Change installation directory
- Modify shortcuts
- Add custom messages
- Include additional files

### Customizing PyInstaller
Edit `quantumbotx.spec` to:
- Add/remove files
- Change executable properties
- Modify hidden imports
- Customize build options

## 📞 Getting Help

1. **Check the logs** in the `logs/` directory
2. **Review** `QUICK_START_GUIDE.md`
3. **Consult** `README.md` for technical details
4. **Check** MetaTrader 5 documentation for connection issues

---

**🎉 Your application is now ready for distribution to non-technical users!**
