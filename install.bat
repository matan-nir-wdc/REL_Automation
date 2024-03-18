@echo off

REM Check if Python 3 is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python 3 is not installed.
    goto :eof
)

REM Check if pip is available
pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo pip is not installed. Please install pip and try again.
    goto :eof
)

REM Install pandas package
echo Installing pandas package...
pip install pandas

REM Check if pandas installation was successful
if %errorlevel% equ 0 (
    echo pandas package installed successfully.
) else (
    echo Failed to install pandas package.
)

:eof
