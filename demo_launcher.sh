#!/bin/bash

# 🎯 QUICK DEMO LAUNCHER
# Eye Blink Tracking System - Executive Demo
# Run this script to start all components for demo

echo "🚀 Starting Eye Blink Tracking System Demo..."
echo "This will launch all three components for executive demonstration"
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check prerequisites
echo -e "${BLUE}🔍 Checking prerequisites...${NC}"

if ! command_exists python3; then
    echo -e "${RED}❌ Python 3 is not installed${NC}"
    exit 1
fi

if ! command_exists node; then
    echo -e "${RED}❌ Node.js is not installed${NC}"
    exit 1
fi

if ! command_exists npm; then
    echo -e "${RED}❌ npm is not installed${NC}"
    exit 1
fi

echo -e "${GREEN}✅ All prerequisites met${NC}"
echo ""

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# Start Backend API
echo -e "${BLUE}🔧 Starting Backend API...${NC}"
cd "$SCRIPT_DIR/backend-api"

# Install Python dependencies if not already installed
if [ ! -f ".deps_installed" ]; then
    echo "Installing Python dependencies..."
    pip3 install -r requirements.txt
    touch .deps_installed
fi

# Start the FastAPI server in background
uvicorn app.main:app --reload --port 8002 &
BACKEND_PID=$!
echo -e "${GREEN}✅ Backend API started on http://localhost:8002${NC}"
echo -e "${YELLOW}📚 API Documentation: http://localhost:8002/docs${NC}"
echo ""

# Wait a moment for backend to start
sleep 3

# Start Web Dashboard
echo -e "${BLUE}🌐 Starting Web Dashboard...${NC}"
cd "$SCRIPT_DIR/web-dashboard"

# Install Node.js dependencies if not already installed
if [ ! -d "node_modules" ]; then
    echo "Installing Node.js dependencies..."
    npm install
fi

# Start the Vite dev server in background
npm run dev &
DASHBOARD_PID=$!
echo -e "${GREEN}✅ Web Dashboard started on http://localhost:5173${NC}"
echo ""

# Wait a moment for dashboard to start
sleep 3

# Start Desktop App
echo -e "${BLUE}💻 Starting Desktop Application...${NC}"
cd "$SCRIPT_DIR/desktop-app"

# Install Electron dependencies if not already installed
if [ ! -d "node_modules" ]; then
    echo "Installing Electron dependencies..."
    npm install
fi

# Start the Electron app in background
npm start &
DESKTOP_PID=$!
echo -e "${GREEN}✅ Desktop Application started${NC}"
echo ""

# Demo instructions
echo -e "${YELLOW}🎯 DEMO IS READY!${NC}"
echo ""
echo -e "${BLUE}📋 Demo Credentials:${NC}"
echo "   Email: demo@wellness.com"
echo "   Password: demo123"
echo ""
echo -e "${BLUE}🌐 Access Points:${NC}"
echo "   • Backend API: http://localhost:8002"
echo "   • API Docs: http://localhost:8002/docs"
echo "   • Web Dashboard: http://localhost:5173"
echo "   • Desktop App: Electron window (should open automatically)"
echo ""
echo -e "${BLUE}🎬 Demo Flow:${NC}"
echo "   1. Show API documentation at http://localhost:8002/docs"
echo "   2. Login to Web Dashboard at http://localhost:5173"
echo "   3. Login to Desktop App and start eye tracking"
echo "   4. View real-time data sync in Web Dashboard"
echo ""
echo -e "${YELLOW}⚠️  Important Notes:${NC}"
echo "   • Allow camera access when prompted in Desktop App"
echo "   • All three components must stay running during demo"
echo "   • Use the same login credentials for both apps"
echo ""
echo -e "${BLUE}🛑 To stop all services, press Ctrl+C${NC}"
echo ""

# Function to cleanup processes on exit
cleanup() {
    echo ""
    echo -e "${YELLOW}🛑 Stopping all services...${NC}"
    
    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null
        echo -e "${GREEN}✅ Backend API stopped${NC}"
    fi
    
    if [ ! -z "$DASHBOARD_PID" ]; then
        kill $DASHBOARD_PID 2>/dev/null
        echo -e "${GREEN}✅ Web Dashboard stopped${NC}"
    fi
    
    if [ ! -z "$DESKTOP_PID" ]; then
        kill $DESKTOP_PID 2>/dev/null
        echo -e "${GREEN}✅ Desktop Application stopped${NC}"
    fi
    
    # Kill any remaining processes on the ports
    lsof -ti:8002 | xargs kill -9 2>/dev/null
    lsof -ti:5173 | xargs kill -9 2>/dev/null
    
    echo -e "${GREEN}🎉 Demo cleanup complete!${NC}"
}

# Set trap to cleanup on script exit
trap cleanup EXIT

# Keep script running and show live status
echo -e "${GREEN}🟢 All services running - Demo is live!${NC}"
echo "Press Ctrl+C to stop all services"
echo ""

# Monitor services
while true; do
    # Check if processes are still running
    if ! kill -0 $BACKEND_PID 2>/dev/null; then
        echo -e "${RED}❌ Backend API stopped unexpectedly${NC}"
        break
    fi
    
    if ! kill -0 $DASHBOARD_PID 2>/dev/null; then
        echo -e "${RED}❌ Web Dashboard stopped unexpectedly${NC}"
        break
    fi
    
    if ! kill -0 $DESKTOP_PID 2>/dev/null; then
        echo -e "${RED}❌ Desktop App stopped unexpectedly${NC}"
        break
    fi
    
    # Show status every 30 seconds
    echo -e "${GREEN}🟢 All services running ($(date))${NC}"
    sleep 30
done

# If we get here, something went wrong
echo -e "${RED}❌ Demo stopped due to service failure${NC}"
cleanup
