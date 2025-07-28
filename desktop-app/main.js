const { app, BrowserWindow, ipcMain } = require('electron');
const path = require('path');

let mainWindow;

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 800,
    height: 700,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      contextIsolation: true,
      nodeIntegration: false,
    },
  });
  mainWindow.loadFile(path.join(__dirname, 'renderer', 'index_websocket.html'));
}

app.whenReady().then(createWindow);

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') app.quit();
});

// IPC: Eye tracker connects to backend WebSocket service
ipcMain.handle('start-eye-tracker', async (event) => {
  console.log('🚀 Eye tracker will connect to backend WebSocket service');
  return { success: true, message: 'Connecting to backend eye tracker service' };
});

ipcMain.handle('stop-eye-tracker', async (event) => {
  console.log('🛑 Eye tracker will disconnect from backend WebSocket service');
  return { success: true, message: 'Disconnected from backend eye tracker service' };
}); 