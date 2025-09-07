@echo off
REM Windows Bootstrap Script for Continuum_Overworld
REM Operating from: C:\Users\Password\
REM Purpose: Create canonical directory structure following THE_BRIDGE naming standard

setlocal enabledelayedexpansion

set ROOT=C:\Users\Password\Continuum_Overworld

echo.
echo 🌱 Bootstrapping Continuum_Overworld from Windows...
echo Environment: Windows %OS%
echo Working directory: %ROOT%
echo.

REM Check if structure already exists
if exist "%ROOT%\The_Bridge" (
    echo ⚠️  Structure already exists. Skipping directory creation.
    goto :skip_dirs
)

REM Create core directory structure
echo Creating directory structure...

mkdir "%ROOT%" 2>nul
mkdir "%ROOT%\The_Bridge\Console--Core__PROD@" 2>nul
mkdir "%ROOT%\The_Bridge\Playbooks" 2>nul
mkdir "%ROOT%\The_Bridge\RFCs" 2>nul
mkdir "%ROOT%\Pantheon\Orion" 2>nul
mkdir "%ROOT%\Pantheon\Omen" 2>nul
mkdir "%ROOT%\Aegis\Audit" 2>nul
mkdir "%ROOT%\Aegis\Playbooks" 2>nul
mkdir "%ROOT%\Atlas\Planner--Airfreight__KE-DE@v0.9.2" 2>nul
mkdir "%ROOT%\Forge\Ingestor--CSRD__EU-DE@v1.6.0" 2>nul
mkdir "%ROOT%\Forge\Builder--Code__WSL2@v1.0.0" 2>nul
mkdir "%ROOT%\Forge\Memory--Fabric__PROD@v0.1.0\server" 2>nul
mkdir "%ROOT%\Forge\Memory--Fabric__PROD@v0.1.0\client" 2>nul
mkdir "%ROOT%\Forge\Memory--Fabric__PROD@v0.1.0\config" 2>nul
mkdir "%ROOT%\Forge\Playbooks" 2>nul
mkdir "%ROOT%\Oracle\Forecaster--Demand__EU-Beans@v2.0.0" 2>nul
mkdir "%ROOT%\Oracle\Forecaster--ESG__PROD@v1.0.0" 2>nul
mkdir "%ROOT%\Meridian\Notifier--Companion__PWA@v0.1.0" 2>nul
mkdir "%ROOT%\Agora\Outreach--Buyers__DE-NL@v0.5.0" 2>nul
mkdir "%ROOT%\Ledger\Contracts--TermSheets__Global@v0.3.1" 2>nul
mkdir "%ROOT%\Archive\BACK_BURNER" 2>nul
mkdir "%ROOT%\.bridge" 2>nul
mkdir "%ROOT%\scripts" 2>nul
mkdir "%ROOT%\.github\workflows" 2>nul

echo ✅ Directory structure created!

:skip_dirs

REM Check if files already exist before creating
if exist "%ROOT%\.gitignore" (
    echo ⚠️  Configuration files already exist. Skipping file creation.
    goto :validation
)

echo.
echo Creating configuration files...

REM Note: Windows batch has limitations with multiline strings
REM These files were already created by the WSL2 script
REM This script primarily ensures Windows can access them

:validation

REM Create Windows validation wrapper
echo @echo off > "%ROOT%\scripts\validate.bat"
echo REM Windows validation wrapper >> "%ROOT%\scripts\validate.bat"
echo cd /d "%ROOT%" >> "%ROOT%\scripts\validate.bat"
echo python scripts\bridge-validate.py >> "%ROOT%\scripts\validate.bat"
echo if errorlevel 1 ( >> "%ROOT%\scripts\validate.bat"
echo     echo. >> "%ROOT%\scripts\validate.bat"
echo     echo ❌ Validation FAILED >> "%ROOT%\scripts\validate.bat"
echo     pause >> "%ROOT%\scripts\validate.bat"
echo     exit /b 1 >> "%ROOT%\scripts\validate.bat"
echo ) >> "%ROOT%\scripts\validate.bat"
echo echo. >> "%ROOT%\scripts\validate.bat"
echo echo ✅ Validation PASSED >> "%ROOT%\scripts\validate.bat"
echo pause >> "%ROOT%\scripts\validate.bat"

REM Create quick check script
echo @echo off > "%ROOT%\scripts\quick-check.bat"
echo REM Quick structure check >> "%ROOT%\scripts\quick-check.bat"
echo echo Checking Continuum_Overworld structure... >> "%ROOT%\scripts\quick-check.bat"
echo echo. >> "%ROOT%\scripts\quick-check.bat"
echo if exist "%ROOT%\The_Bridge" echo ✅ The_Bridge >> "%ROOT%\scripts\quick-check.bat"
echo if exist "%ROOT%\Pantheon" echo ✅ Pantheon >> "%ROOT%\scripts\quick-check.bat"
echo if exist "%ROOT%\Aegis" echo ✅ Aegis >> "%ROOT%\scripts\quick-check.bat"
echo if exist "%ROOT%\Atlas" echo ✅ Atlas >> "%ROOT%\scripts\quick-check.bat"
echo if exist "%ROOT%\Forge" echo ✅ Forge >> "%ROOT%\scripts\quick-check.bat"
echo if exist "%ROOT%\Oracle" echo ✅ Oracle >> "%ROOT%\scripts\quick-check.bat"
echo if exist "%ROOT%\Meridian" echo ✅ Meridian >> "%ROOT%\scripts\quick-check.bat"
echo if exist "%ROOT%\Agora" echo ✅ Agora >> "%ROOT%\scripts\quick-check.bat"
echo if exist "%ROOT%\Ledger" echo ✅ Ledger >> "%ROOT%\scripts\quick-check.bat"
echo if exist "%ROOT%\Archive" echo ✅ Archive >> "%ROOT%\scripts\quick-check.bat"
echo echo. >> "%ROOT%\scripts\quick-check.bat"
echo pause >> "%ROOT%\scripts\quick-check.bat"

REM Create WSL2 bridge script
echo @echo off > "%ROOT%\scripts\wsl-bridge.bat"
echo REM Execute commands in WSL2 from Windows >> "%ROOT%\scripts\wsl-bridge.bat"
echo wsl bash -c "cd /mnt/c/users/password/Continuum_Overworld && %*" >> "%ROOT%\scripts\wsl-bridge.bat"

REM Create Python launcher for Windows
echo @echo off > "%ROOT%\scripts\run-python.bat"
echo REM Run Python scripts from Windows >> "%ROOT%\scripts\run-python.bat"
echo cd /d "%ROOT%" >> "%ROOT%\scripts\run-python.bat"
echo python %* >> "%ROOT%\scripts\run-python.bat"

echo.
echo ✅ Windows scaffold ready!
echo.
echo 📁 Structure created under: %ROOT%
echo.
echo 🔧 Next steps:
echo   1. Run validation: scripts\validate.bat
echo   2. Quick check: scripts\quick-check.bat
echo   3. Bridge to WSL2: scripts\wsl-bridge.bat [command]
echo.
echo 🌉 Cross-platform bridge ready for Windows ↔ WSL2 collaboration
echo.
pause