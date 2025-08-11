@echo off
REM Quotescape Installation Script for Windows
REM This script sets up Quotescape with all necessary dependencies

setlocal enabledelayedexpansion

REM Colors (using echo with escape sequences doesn't work well in batch, so using simple text)
echo ========================================
echo     Quotescape Installation Script
echo         Generate Quote Wallpapers
echo ========================================
echo.

REM Check Python installation
echo [INFO] Checking Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH
    echo Please install Python 3.11 from https://python.org
    pause
    exit /b 1
)

REM Get Python version
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo [SUCCESS] Found Python %PYTHON_VERSION%

REM Check if Python version is 3.11+
for /f "tokens=1,2 delims=." %%a in ("%PYTHON_VERSION%") do (
    if %%a NEQ 3 (
        echo [ERROR] Python 3.11 or higher is required
        echo Please install Python 3.11 from https://python.org
        pause
        exit /b 1
    )
    if %%b LSS 11 (
        echo [ERROR] Python 3.11 or higher is required ^(found %%a.%%b^)
        echo Please install Python 3.11 from https://python.org
        pause
        exit /b 1
    )
)

REM Check if we're in the right directory
if not exist "setup.py" (
    echo [ERROR] Please run this script from the Quotescape project root directory
    pause
    exit /b 1
)

if not exist "requirements.txt" (
    echo [ERROR] requirements.txt not found in current directory
    pause
    exit /b 1
)

REM Create virtual environment
echo [INFO] Creating virtual environment...
if exist "venv" (
    echo [WARNING] Virtual environment already exists
    set /p RECREATE="Do you want to recreate it? (y/n): "
    if /i "!RECREATE!"=="y" (
        rmdir /s /q venv
        python -m venv venv
        echo [SUCCESS] Virtual environment recreated
    )
) else (
    python -m venv venv
    echo [SUCCESS] Virtual environment created
)

REM Activate virtual environment
echo [INFO] Activating virtual environment...
call venv\Scripts\activate.bat

REM Upgrade pip
echo [INFO] Upgrading pip...
python -m pip install --upgrade pip --quiet

REM Install dependencies
echo [INFO] Installing Python dependencies...
pip install -r requirements.txt --quiet
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install dependencies
    pause
    exit /b 1
)
echo [SUCCESS] Dependencies installed

REM Run setup script
echo [INFO] Running setup script...
python setup.py
if %errorlevel% neq 0 (
    echo [ERROR] Setup script failed
    pause
    exit /b 1
)

REM Create example configuration files
echo [INFO] Creating example configuration files...

REM Create example custom quotebook if it doesn't exist
if not exist "custom_quotebook.json" (
    (
        echo {
        echo   "Marcus Aurelius": [
        echo     "You have power over your mind - not outside events. Realize this, and you will find strength."
        echo   ],
        echo   "Maya Angelou": [
        echo     "I've learned that people will forget what you said, people will forget what you did, but people will never forget how you made them feel."
        echo   ]
        echo }
    ) > custom_quotebook.json
    echo [SUCCESS] Created example custom_quotebook.json
)

REM Create example Kindle secrets template
if not exist "kindle_secrets.json.template" (
    (
        echo {
        echo   "username": "your_amazon_email@example.com",
        echo   "password": "your_amazon_password"
        echo }
    ) > kindle_secrets.json.template
    echo [SUCCESS] Created kindle_secrets.json.template
)

REM Create convenience batch files
echo [INFO] Creating convenience scripts...

REM Create run.bat
(
    echo @echo off
    echo call venv\Scripts\activate.bat
    echo python run_quotescape.py %%*
) > run.bat
echo [SUCCESS] Created run.bat

REM Create run-random.bat
(
    echo @echo off
    echo echo source: random ^> quotescape.yaml
    echo call run.bat
) > run-random.bat
echo [SUCCESS] Created run-random.bat

REM Create run-custom.bat
(
    echo @echo off
    echo if not exist "custom_quotebook.json" ^(
    echo     echo [ERROR] custom_quotebook.json not found!
    echo     echo Please create it with your quotes
    echo     pause
    echo     exit /b 1
    echo ^)
    echo echo source: custom ^> quotescape.yaml
    echo call run.bat
) > run-custom.bat
echo [SUCCESS] Created run-custom.bat

REM Create run-kindle.bat
(
    echo @echo off
    echo if not exist "kindle_secrets.json" ^(
    echo     echo [ERROR] kindle_secrets.json not found!
    echo     echo Copy kindle_secrets.json.template to kindle_secrets.json
    echo     echo and add your Amazon credentials
    echo     pause
    echo     exit /b 1
    echo ^)
    echo echo source: kindle ^> quotescape.yaml
    echo call run.bat
) > run-kindle.bat
echo [SUCCESS] Created run-kindle.bat

REM Create uninstall.bat
(
    echo @echo off
    echo echo Removing Quotescape installation...
    echo rmdir /s /q venv 2^>nul
    echo del /q src\output\wallpapers\*.png 2^>nul
    echo del /q src\output\cache\*.json 2^>nul
    echo del run.bat 2^>nul
    echo del run-random.bat 2^>nul
    echo del run-custom.bat 2^>nul
    echo del run-kindle.bat 2^>nul
    echo del uninstall.bat 2^>nul
    echo echo [SUCCESS] Quotescape uninstalled
    echo echo Note: Configuration files were preserved
    echo pause
) > uninstall.bat
echo [SUCCESS] Created uninstall.bat

REM Final summary
echo.
echo ========================================
echo     Installation Complete!
echo ========================================
echo.
echo Quick Start:
echo -----------
echo 1. Run with random quotes (default):
echo    run.bat
echo.
echo 2. Run with custom quotes:
echo    - Edit custom_quotebook.json
echo    - Run: run-custom.bat
echo.
echo 3. Run with Kindle highlights:
echo    - Copy kindle_secrets.json.template to kindle_secrets.json
echo    - Add your Amazon credentials
echo    - Run: run-kindle.bat
echo.
echo Other Commands:
echo --------------
echo   run.bat --help          Show all options
echo   run.bat -v              Verbose mode
echo   uninstall.bat           Uninstall Quotescape
echo.
echo Configuration:
echo -------------
echo Edit quotescape.yaml to customize settings
echo Default location: %%APPDATA%%\quotescape\quotescape.yaml
echo.
echo [INFO] Virtual environment activated
echo [INFO] To deactivate, close this window or run: deactivate
echo.
pause