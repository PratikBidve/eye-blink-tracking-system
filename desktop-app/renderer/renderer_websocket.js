const API_URL = 'http://127.0.0.1:8000'; // Backend API URL
const WS_URL = 'ws://127.0.0.1:8000'; // WebSocket URL

const loginSection = document.getElementById('loginSection');
const mainSection = document.getElementById('mainSection');
const loginBtn = document.getElementById('loginBtn');
const logoutBtn = document.getElementById('logoutBtn');
const emailInput = document.getElementById('email');
const passwordInput = document.getElementById('password');
const loginError = document.getElementById('loginError');
const blinkCountSpan = document.getElementById('blinkCount');
const startBtn = document.getElementById('startBtn');
const stopBtn = document.getElementById('stopBtn');
const syncStatus = document.getElementById('syncStatus');
const videoElement = document.getElementById('videoStream');
const dashboardSection = document.getElementById('dashboard');

let blinkCount = 0;
let accessToken = localStorage.getItem('accessToken');
let websocket = null;
let startTime = null;
let blinkHistory = [];

function showLogin() {
  loginSection.classList.remove('hidden');
  mainSection.classList.add('hidden');
}

function showMain() {
  loginSection.classList.add('hidden');
  mainSection.classList.remove('hidden');
}

function setSyncStatus(msg, error = false) {
  syncStatus.textContent = msg;
  syncStatus.style.color = error ? 'red' : 'green';
}

function updateDashboard(data) {
  // Update blink count
  blinkCount = data.blink_count;
  blinkCountSpan.textContent = blinkCount;
  
  // Update dashboard statistics
  if (startTime) {
    const elapsed = (new Date() - startTime) / 1000; // seconds
    const blinksPerMinute = elapsed > 0 ? (blinkCount / elapsed * 60).toFixed(1) : 0;
    
    document.getElementById('totalBlinks').textContent = blinkCount;
    document.getElementById('blinksPerMinute').textContent = blinksPerMinute;
    document.getElementById('sessionTime').textContent = Math.floor(elapsed / 60) + ':' + 
                                                       (Math.floor(elapsed % 60)).toString().padStart(2, '0');
    document.getElementById('lastUpdate').textContent = new Date().toLocaleTimeString('en-IN', {
      timeZone: 'Asia/Kolkata',
      hour12: false
    });
  }
  
  // Update blink history for chart
  if (data.blink_changed) {
    blinkHistory.push({
      count: blinkCount,
      time: new Date(),
      timestamp: data.timestamp
    });
    
    // Keep only last 50 blinks for performance
    if (blinkHistory.length > 50) {
      blinkHistory = blinkHistory.slice(-50);
    }
    
    updateBlinkChart();
  }
}

function updateBlinkChart() {
  const chartContainer = document.getElementById('blinkChart');
  const times = blinkHistory.map(h => h.time.toLocaleTimeString());
  const counts = blinkHistory.map(h => h.count);
  
  // Simple text-based chart for now
  let chartHTML = '<div class="chart-container">';
  chartHTML += '<h4>Blink Timeline (Last 10)</h4>';
  chartHTML += '<div class="chart-bars">';
  
  const last10 = blinkHistory.slice(-10);
  last10.forEach((item, index) => {
    const height = Math.max(10, (item.count / Math.max(...counts) * 100));
    chartHTML += `
      <div class="chart-bar" style="height: ${height}px; background: linear-gradient(to top, #007bff, #00d4ff)">
        <div class="bar-label">${item.count}</div>
        <div class="bar-time">${item.time.toLocaleTimeString().slice(0,5)}</div>
      </div>
    `;
  });
  
  chartHTML += '</div></div>';
  chartContainer.innerHTML = chartHTML;
}

async function login() {
  loginError.classList.add('hidden');
  try {
    const form = new FormData();
    form.append('username', emailInput.value);
    form.append('password', passwordInput.value);
    const res = await fetch(`${API_URL}/token`, {
      method: 'POST',
      body: form,
    });
    if (!res.ok) throw new Error('Invalid credentials');
    const data = await res.json();
    accessToken = data.access_token;
    localStorage.setItem('accessToken', accessToken);
    showMain();
    setSyncStatus('Logged in successfully - Ready to start tracking', false);
  } catch (err) {
    loginError.textContent = err.message;
    loginError.classList.remove('hidden');
  }
}

function logout() {
  console.log('🚪 Logging out...');
  
  // First stop eye tracking if running (this will stop the backend camera)
  if (websocket) {
    console.log('🛑 Stopping eye tracking before logout...');
    stopEyeTracker();
    
    // Give a moment for the stop command to be processed
    setTimeout(() => {
      completeLogout();
    }, 500);
  } else {
    completeLogout();
  }
}

function completeLogout() {
  console.log('🧹 Completing logout process...');
  
  // Clear all state
  accessToken = null;
  localStorage.removeItem('accessToken');
  blinkHistory = [];
  blinkCount = 0;
  startTime = null;
  
  // Reset UI
  blinkCountSpan.textContent = '0';
  dashboardSection.classList.add('hidden');
  
  // Clear video element
  if (videoElement) {
    videoElement.src = '';
    videoElement.alt = 'Live video stream will appear here';
  }
  
  setSyncStatus('Logged out successfully - camera stopped', false);
  showLogin();
}

function startEyeTracker() {
  console.log('🚀 Starting eye tracker...');
  
  if (!accessToken) {
    setSyncStatus('Please login first', true);
    return;
  }

  // Force cleanup any existing connection
  if (websocket) {
    console.log('🧹 Cleaning up existing WebSocket connection...');
    websocket.close();
    websocket = null;
    // Add small delay to ensure cleanup
    setTimeout(() => startEyeTracker(), 100);
    return;
  }

  // Reset state
  startTime = new Date();
  blinkHistory = [];
  blinkCount = 0;
  blinkCountSpan.textContent = '0';

  // Disable start button immediately to prevent double clicks
  startBtn.disabled = true;
  setSyncStatus('🔄 Connecting to eye tracker...', false);

  try {
    // Create WebSocket connection
    websocket = new WebSocket(`${WS_URL}/ws/eye-tracker/${accessToken}`);
    
    websocket.onopen = () => {
      console.log('🚀 WebSocket connected');
      setSyncStatus('🎥 Live eye tracking started - Video streaming...', false);
      startBtn.disabled = true;
      stopBtn.disabled = false;
      dashboardSection.classList.remove('hidden');
    };
    
    websocket.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        
        if (data.error) {
          console.error('WebSocket error:', data.error);
          setSyncStatus(`❌ Error: ${data.error}`, true);
          stopEyeTracker();
          return;
        }
        
        if (data.type === 'stop_confirmed') {
          console.log('✅ Backend confirmed eye tracker stopped');
          setSyncStatus('Eye tracker stopped - camera released on server', false);
          return;
        }
        
        if (data.type === 'frame_data') {
          // Update dashboard with real-time data
          updateDashboard(data);
          
          // Display video frame if available
          if (data.video_frame) {
            videoElement.src = `data:image/jpeg;base64,${data.video_frame}`;
          }
          
          setSyncStatus(`🎯 Tracking active - Blinks: ${data.blink_count} (Auto-saved)`, false);
        }
      } catch (error) {
        console.error('Error parsing WebSocket message:', error);
        setSyncStatus('Error processing video data', true);
      }
    };
    
    websocket.onclose = (event) => {
      console.log('🛑 WebSocket closed:', event.code, event.reason);
      // Always clean up state
      websocket = null;
      startBtn.disabled = false;
      stopBtn.disabled = true;
      dashboardSection.classList.add('hidden');
      
      if (event.code !== 1000) {
        setSyncStatus('Connection lost - click Start to reconnect', true);
      } else {
        setSyncStatus('Eye tracker stopped - ready to restart', false);
      }
    };
    
    websocket.onerror = (error) => {
      console.error('WebSocket error:', error);
      setSyncStatus('WebSocket connection failed - click Start to retry', true);
      // Don't call stopEyeTracker here as it will be handled by onclose
    };
    
  } catch (error) {
    console.error('Failed to start WebSocket:', error);
    setSyncStatus('Failed to start eye tracker', true);
  }
}

function stopEyeTracker() {
  console.log('🛑 Stopping eye tracker...');
  
  // First, call backend REST API to explicitly stop the eye tracker service
  if (accessToken) {
    console.log('📡 Sending stop command to backend...');
    fetch(`${API_URL}/eye-tracker/stop`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${accessToken}`,
        'Content-Type': 'application/json'
      }
    })
    .then(response => response.json())
    .then(data => {
      console.log('✅ Backend eye tracker stopped:', data.message);
      setSyncStatus('Eye tracker stopped - camera released on server', false);
    })
    .catch(error => {
      console.error('❌ Error stopping backend eye tracker:', error);
      setSyncStatus('Eye tracker stopped locally (check server)', false);
    });
  }
  
  // Close WebSocket connection gracefully
  if (websocket) {
    try {
      // Send stop signal before closing
      if (websocket.readyState === WebSocket.OPEN) {
        websocket.send(JSON.stringify({ 
          type: 'stop_command', 
          message: 'User requested stop' 
        }));
      }
      
      // Close with proper code
      websocket.close(1000, 'User stopped tracking');
      console.log('📡 WebSocket closed gracefully');
    } catch (error) {
      console.error('Error closing WebSocket:', error);
    }
    websocket = null;
  }
  
  // Reset UI state
  startBtn.disabled = false;
  stopBtn.disabled = true;
  dashboardSection.classList.add('hidden');
  startTime = null;
  blinkCount = 0;
  blinkHistory = [];
  
  // Clear display
  blinkCountSpan.textContent = '0';
  
  // Clear video element and reset
  if (videoElement) {
    videoElement.src = '';
    videoElement.alt = 'Live video stream will appear here';
  }
  
  // Reset dashboard values
  document.getElementById('totalBlinks').textContent = '0';
  document.getElementById('blinksPerMinute').textContent = '0';
  document.getElementById('sessionTime').textContent = '0:00';
  document.getElementById('lastUpdate').textContent = '--:--';
}

// Event listeners
loginBtn.onclick = login;
logoutBtn.onclick = logout;
startBtn.onclick = startEyeTracker;
stopBtn.onclick = stopEyeTracker;

// Cleanup on page unload
window.addEventListener('beforeunload', () => {
  console.log('🔄 Page unloading - cleaning up...');
  if (websocket) {
    stopEyeTracker();
  }
});

// Cleanup on window close
window.addEventListener('unload', () => {
  console.log('🔄 Window closing - cleaning up...');
  if (websocket) {
    websocket.close(1001, 'Page unloading');
    websocket = null;
  }
});

// On load
if (accessToken) {
  showMain();
  setSyncStatus('Ready to start eye tracking', false);
} else {
  showLogin();
}
