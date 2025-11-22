@echo off
REM Install MSP NCE Pricing Tool as Windows Service using NSSM
REM Run this as Administrator

echo ========================================
echo MSP NCE Pricing Tool - Service Installer
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

REM Set service name
set SERVICE_NAME=MSPPricingTool

REM Get current directory
set APP_DIR=%~dp0
set EXE_PATH=%APP_DIR%MSP_NCE_Pricing_Tool.exe

echo Current directory: %APP_DIR%
echo EXE path: %EXE_PATH%
echo.

REM Check if EXE exists
if not exist "%EXE_PATH%" (
    echo ERROR: MSP_NCE_Pricing_Tool.exe not found!
    echo Please build the application first.
    pause
    exit /b 1
)

REM Check if NSSM exists
where nssm >nul 2>&1
if %errorLevel% neq 0 (
    echo ERROR: NSSM not found in PATH!
    echo.
    echo Please download NSSM from https://nssm.cc/download
    echo Extract nssm.exe to C:\Windows\System32 or add it to your PATH
    pause
    exit /b 1
)

REM Check if service already exists
sc query %SERVICE_NAME% >nul 2>&1
if %errorLevel% equ 0 (
    echo Service already exists. Removing old installation...
    nssm stop %SERVICE_NAME%
    timeout /t 2 /nobreak >nul
    nssm remove %SERVICE_NAME% confirm
    timeout /t 2 /nobreak >nul
)

echo Installing service...
nssm install %SERVICE_NAME% "%EXE_PATH%"

REM Configure service
echo Configuring service...
nssm set %SERVICE_NAME% AppDirectory "%APP_DIR%"
nssm set %SERVICE_NAME% DisplayName "MSP NCE Pricing Tool"
nssm set %SERVICE_NAME% Description "Microsoft NCE License-Based Pricing Tool for eMazzanti Technologies"
nssm set %SERVICE_NAME% Start SERVICE_AUTO_START
nssm set %SERVICE_NAME% AppStdout "%APP_DIR%logs\service_stdout.log"
nssm set %SERVICE_NAME% AppStderr "%APP_DIR%logs\service_stderr.log"
nssm set %SERVICE_NAME% AppRotateFiles 1
nssm set %SERVICE_NAME% AppRotateBytes 10485760

REM Configure firewall rule
echo Adding firewall rule...
netsh advfirewall firewall delete rule name="MSP Pricing Tool" >nul 2>&1
netsh advfirewall firewall add rule name="MSP Pricing Tool" dir=in action=allow protocol=TCP localport=5000

REM Start service
echo Starting service...
nssm start %SERVICE_NAME%

echo.
echo ========================================
echo Installation complete!
echo ========================================
echo.
echo Service Name: %SERVICE_NAME%
echo Web UI: http://localhost:5000
echo.
echo To manage the service:
echo   Start:   nssm start %SERVICE_NAME%
echo   Stop:    nssm stop %SERVICE_NAME%
echo   Restart: nssm restart %SERVICE_NAME%
echo   Remove:  nssm remove %SERVICE_NAME%
echo.
pause
