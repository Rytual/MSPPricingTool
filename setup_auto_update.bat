@echo off
REM Setup automatic weekly updates via Windows Task Scheduler
REM Run this as Administrator

echo ========================================
echo MSP NCE Pricing Tool - Auto Update Setup
echo ========================================
echo.

REM Check for admin privileges
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo ERROR: This script must be run as Administrator!
    echo Right-click and select "Run as administrator"
    pause
    exit /b 1
)

set TASK_NAME=MSPPricingAutoUpdate
set APP_DIR=%~dp0
set PYTHON_SCRIPT=%APP_DIR%auto_update.py

echo Script location: %PYTHON_SCRIPT%
echo.

REM Check if Python is available
where python >nul 2>&1
if %errorLevel% neq 0 (
    echo WARNING: Python not found in PATH
    echo If using the EXE version, this is expected
    echo Auto-update will need to be triggered manually via the tray icon
    pause
    exit /b 0
)

REM Delete existing task if it exists
schtasks /query /tn %TASK_NAME% >nul 2>&1
if %errorLevel% equ 0 (
    echo Removing existing scheduled task...
    schtasks /delete /tn %TASK_NAME% /f
)

REM Create new scheduled task - runs weekly on Sundays at 2 AM
echo Creating scheduled task...
schtasks /create /tn %TASK_NAME% /tr "python \"%PYTHON_SCRIPT%\"" /sc weekly /d SUN /st 02:00 /rl highest /f

if %errorLevel% equ 0 (
    echo.
    echo ========================================
    echo Auto-update scheduled successfully!
    echo ========================================
    echo.
    echo Task Name: %TASK_NAME%
    echo Schedule: Weekly on Sundays at 2:00 AM
    echo.
    echo To manage the task:
    echo   View:   schtasks /query /tn %TASK_NAME% /v
    echo   Run:    schtasks /run /tn %TASK_NAME%
    echo   Delete: schtasks /delete /tn %TASK_NAME% /f
    echo.
    echo Or use Task Scheduler GUI (taskschd.msc)
    echo.
) else (
    echo ERROR: Failed to create scheduled task
)

pause
