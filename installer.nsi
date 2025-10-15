; QuantumBotX Windows Installer
; This script creates a Windows installer for the QuantumBotX trading application

!include "MUI2.nsh"
!include "FileFunc.nsh"
!include "LogicLib.nsh"

; General
Name "QuantumBotX Trading Bot"
OutFile "QuantumBotX-Installer.exe"
Unicode True
InstallDir "C:\QuantumBotX"
InstallDirRegKey HKCU "Software\QuantumBotX" ""
RequestExecutionLevel admin

; Modern UI Configuration
!define MUI_ABORTWARNING
!define MUI_ICON "static\favicon.ico"
!define MUI_UNICON "static\favicon.ico"

; Pages
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_LICENSE "LICENSE.md"

; Custom prerequisites page
Page custom PrerequisitesPage PrerequisitesPageLeave

!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_UNPAGE_WELCOME
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES
!insertmacro MUI_UNPAGE_FINISH

; Languages
!insertmacro MUI_LANGUAGE "English"
!insertmacro MUI_LANGUAGE "Indonesian"

; Version Information
VIProductVersion "2.0.0.0"
VIAddVersionKey "ProductName" "QuantumBotX Trading Bot"
VIAddVersionKey "CompanyName" "Chrisnov IT Solutions"
VIAddVersionKey "FileVersion" "2.0.0.0"
VIAddVersionKey "ProductVersion" "2.0.0.0"
VIAddVersionKey "FileDescription" "Professional Trading Bot Application"
VIAddVersionKey "LegalCopyright" "Copyright (c) 2025 Reynov Christian - Chrisnov IT Solutions"
VIAddVersionKey "Contact" "contact@chrisnov.com"

Section "Install"
    SetOutPath "$INSTDIR"

    ; Stop any running instances
    DetailPrint "Stopping any running instances..."
    nsExec::Exec 'taskkill /f /im "QuantumBotX.exe"'

    ; Create installation directory
    CreateDirectory "$INSTDIR"

    ; Copy main files
    File "dist\QuantumBotX\QuantumBotX.exe"
    File /r "dist\QuantumBotX\_internal"
    File "start.bat"
    File "start.sh"
    File "setup_quantumbotx.py"
    File "requirements.txt"
    File ".env.example"
    File "README.md"
    File "QUICK_START_GUIDE.md"
    File "MT5_SETUP_GUIDE.md"
    File /r "templates"
    File /r "static"
    File /r "core"

    ; Create data directories
    CreateDirectory "$INSTDIR\logs"
    CreateDirectory "$INSTDIR\lab"
    CreateDirectory "$INSTDIR\testing"
    CreateDirectory "$INSTDIR\docs"

    ; Copy optional directories if they exist
    IfFileExists "docs\*.*" 0 +2
        File /r "docs"

    IfFileExists "lab\*.*" 0 +2
        File /r "lab"

    IfFileExists "testing\*.*" 0 +2
        File /r "testing"

    ; Create desktop shortcut
    CreateShortCut "$DESKTOP\QuantumBotX.lnk" "$INSTDIR\start.bat" "" "$INSTDIR\start.bat" 0

    ; Create start menu entries
    CreateDirectory "$SMPROGRAMS\QuantumBotX"
    CreateShortCut "$SMPROGRAMS\QuantumBotX\QuantumBotX.lnk" "$INSTDIR\start.bat" "" "$INSTDIR\start.bat" 0
    CreateShortCut "$SMPROGRAMS\QuantumBotX\Uninstall.lnk" "$INSTDIR\Uninstall.exe" "" "$INSTDIR\Uninstall.exe" 0

    ; Store installation folder
    WriteRegStr HKCU "Software\QuantumBotX" "" $INSTDIR

    ; Create uninstaller
    WriteUninstaller "$INSTDIR\Uninstall.exe"

    ; Write registry for Add/Remove Programs
    WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\QuantumBotX" "DisplayName" "QuantumBotX Trading Bot"
    WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\QuantumBotX" "UninstallString" "$INSTDIR\Uninstall.exe"
    WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\QuantumBotX" "DisplayVersion" "2.0.0"
    WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\QuantumBotX" "Publisher" "Chrisnov IT Solutions"
    WriteRegDWord HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\QuantumBotX" "NoModify" 1
    WriteRegDWord HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\QuantumBotX" "NoRepair" 1

SectionEnd

Section "Uninstall"
    ; Remove files and directories
    Delete "$INSTDIR\Uninstall.exe"
    Delete "$INSTDIR\QuantumBotX.exe"
    RMDir /r "$INSTDIR\_internal"
    RMDir /r "$INSTDIR\templates"
    RMDir /r "$INSTDIR\static"
    RMDir /r "$INSTDIR\core"
    RMDir /r "$INSTDIR\docs"
    RMDir /r "$INSTDIR\lab"
    RMDir /r "$INSTDIR\testing"
    RMDir /r "$INSTDIR\logs"
    Delete "$INSTDIR\*.*"
    RMDir "$INSTDIR"

    ; Remove shortcuts
    Delete "$DESKTOP\QuantumBotX.lnk"
    RMDir /r "$SMPROGRAMS\QuantumBotX"

    ; Remove registry entries
    DeleteRegKey HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\QuantumBotX"
    DeleteRegKey /ifempty HKCU "Software\QuantumBotX"

    ; Stop running instances before uninstall
    nsExec::Exec 'taskkill /f /im "QuantumBotX.exe"'
    nsExec::Exec 'taskkill /f /im "python.exe"'

SectionEnd

Function .onInit
    ; Check if already installed
    ReadRegStr $R0 HKCU "Software\QuantumBotX" ""
    ${If} $R0 != ""
        MessageBox MB_YESNO "QuantumBotX is already installed. Do you want to reinstall?" IDYES continue
        Abort
        continue:
    ${EndIf}

FunctionEnd

Function PrerequisitesPage
    !insertmacro MUI_HEADER_TEXT "Prerequisites" "Important setup information"

    nsDialogs::Create 1018
    Pop $0

    ${NSD_CreateLabel} 0 0 100% 24u "Before using QuantumBotX, you need to:"
    Pop $0

    ${NSD_CreateLabel} 0 30u 100% 60u "1. Install MetaTrader 5 from https://www.metatrader5.com/$\n2. Create a demo or live trading account$\n3. Keep MT5 running in background when using QuantumBotX$\n$\n⚠️ Python is NOT required - it's already bundled in this installer!"
    Pop $0

    ${NSD_CreateLabel} 0 100u 100% 24u "System Requirements:"
    Pop $0

    ${NSD_CreateLabel} 0 130u 100% 40u "• Windows 7 SP1 or later (64-bit recommended)$\n• 4GB RAM minimum (8GB recommended)$\n• 500MB free disk space$\n• Internet connection for initial setup"
    Pop $0

    nsDialogs::Show
FunctionEnd

Function PrerequisitesPageLeave
    # This function is called when leaving the prerequisites page
    # We could add validation here if needed
FunctionEnd

Function .onInstSuccess
    MessageBox MB_YESNO "Installation completed successfully! $\n$\nDo you want to run the setup wizard now?" IDNO end
    Exec '"$INSTDIR\setup_quantumbotx.py"'
    end:
FunctionEnd
