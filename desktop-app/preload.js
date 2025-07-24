const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('eyeAPI', {
  startEyeTracker: () => ipcRenderer.invoke('start-eye-tracker'),
  stopEyeTracker: () => ipcRenderer.invoke('stop-eye-tracker'),
  onBlinkCount: (callback) => ipcRenderer.on('blink-count', (event, data) => callback(data)),
  onEyeTrackerStopped: (callback) => ipcRenderer.on('eye-tracker-stopped', (event, code) => callback(code)),
}); 