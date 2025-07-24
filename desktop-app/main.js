const { app, BrowserWindow, ipcMain } = require('electron');
const path = require('path');
const { spawn } = require('child_process');

let mainWindow;
let pythonProcess;

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 600,
    height: 500,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      contextIsolation: true,
      nodeIntegration: false,
    },
  });
  mainWindow.loadFile(path.join(__dirname, 'renderer', 'index.html'));
}

app.whenReady().then(createWindow);

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') app.quit();
});

// IPC: Start/Stop Python Eye Tracker
ipcMain.handle('start-eye-tracker', async (event) => {
  if (pythonProcess) return;
  pythonProcess = spawn('python3', [path.join(__dirname, 'python', 'eye_tracker.py')]);
  pythonProcess.stdout.on('data', (data) => {
    mainWindow.webContents.send('blink-count', data.toString());
  });
  pythonProcess.stderr.on('data', (data) => {
    console.error(`Eye Tracker Error: ${data}`);
  });
  pythonProcess.on('close', (code) => {
    pythonProcess = null;
    mainWindow.webContents.send('eye-tracker-stopped', code);
  });
});

ipcMain.handle('stop-eye-tracker', async (event) => {
  if (pythonProcess) {
    pythonProcess.kill();
    pythonProcess = null;
  }
}); 