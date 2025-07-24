@echo off
REM 🎯 QUICK DEMO LAUNCHER - WINDOWS VERSION
REM Eye Blink Tracking System - Executive Demo
REM Run this batch file to start all components for demo

echo 🚀 Starting Eye Blink Tracking System Demo...
echo This will launch all three components for executive demonstration
echo.

REM Check prerequisites
echo 🔍 Checking prerequisites...

python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH
    pause
    exit /b 1
)

node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Node.js is not installed or not in PATH
    pause
    exit /b 1
)

npm --version >nul 2>&1
if errorlevel 1 (
    echo ❌ npm is not installed or not in PATH
    pause
    exit /b 1
)

echo ✅ All prerequisites met
echo.

REM Get current directory
set SCRIPT_DIR=%~dp0

REM Start Backend API
echo 🔧 Starting Backend API...
cd /d "%SCRIPT_DIR%backend-api"

REM Install Python dependencies if not already installed
if not exist ".deps_installed" (
    echo Installing Python dependencies...
    pip install -r requirements.txt
    echo. > .deps_installed
)

REM Start the FastAPI server
start "Backend API" cmd /k "uvicorn app.main:app --reload --port 8002"
echo ✅ Backend API starting on http://localhost:8002
echo 📚 API Documentation: http://localhost:8002/docs
echo.

REM Wait for backend to start
timeout /t 3 /nobreak >nul

REM Start Web Dashboard
echo 🌐 Starting Web Dashboard...
cd /d "%SCRIPT_DIR%web-dashboard"

REM Install Node.js dependencies if not already installed
if not exist "node_modules" (
    echo Installing Node.js dependencies...
    npm install
)

REM Start the Vite dev server
start "Web Dashboard" cmd /k "npm run dev"
echo ✅ Web Dashboard starting on http://localhost:5173
echo.

REM Wait for dashboard to start
timeout /t 3 /nobreak >nul

REM Start Desktop App
echo 💻 Starting Desktop Application...
cd /d "%SCRIPT_DIR%desktop-app"

REM Install Electron dependencies if not already installed
if not exist "node_modules" (
    echo Installing Electron dependencies...
    npm install
)

REM Start the Electron app
start "Desktop App" cmd /k "npm start"
echo ✅ Desktop Application starting
echo.

REM Demo instructions
echo 🎯 DEMO IS READY!
echo.
echo 📋 Demo Credentials:
echo    Email: demo@wellness.com
echo    Password: demo123
echo.
echo 🌐 Access Points:
echo    • Backend API: http://localhost:8002
echo    • API Docs: http://localhost:8002/docs
echo    • Web Dashboard: http://localhost:5173
echo    • Desktop App: Electron window (should open automatically)
echo.
echo 🎬 Demo Flow:
echo    1. Show API documentation at http://localhost:8002/docs
echo    2. Login to Web Dashboard at http://localhost:5173
echo    3. Login to Desktop App and start eye tracking
echo    4. View real-time data sync in Web Dashboard
echo.
echo ⚠️  Important Notes:
echo    • Allow camera access when prompted in Desktop App
echo    • All three components must stay running during demo
echo    • Use the same login credentials for both apps
echo    • Close the command windows to stop each service
echo.
echo 🟢 All services are starting up...
echo.
echo Press any key to open the demo URLs in your browser...
pause >nul

REM Open demo URLs in default browser
start http://localhost:8002/docs
timeout /t 2 /nobreak >nul
start http://localhost:5173

echo.
echo 🎉 Demo launched successfully!
echo.
echo To stop all services:
echo - Close all the command windows that opened
echo - Or use Task Manager to end Node.js and Python processes
echo.
pause
