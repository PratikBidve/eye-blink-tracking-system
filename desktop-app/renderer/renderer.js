const API_URL = 'http://127.0.0.1:8000'; // Backend API URL

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

let blinkCount = 0;
let accessToken = localStorage.getItem('accessToken');
let unsyncedBlinks = JSON.parse(localStorage.getItem('unsyncedBlinks') || '[]');

// Clean up any corrupted data
function cleanupUnsyncedBlinks() {
  const cleaned = unsyncedBlinks.filter(item => {
    return item && 
           typeof item.blink_count === 'number' && 
           !isNaN(item.blink_count) && 
           item.blink_count >= 0;
  });
  
  if (cleaned.length !== unsyncedBlinks.length) {
    console.log(`Cleaned up ${unsyncedBlinks.length - cleaned.length} corrupted blink entries`);
    unsyncedBlinks = cleaned;
    localStorage.setItem('unsyncedBlinks', JSON.stringify(unsyncedBlinks));
  }
}

// Clean up on startup
cleanupUnsyncedBlinks();

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
    syncUnsyncedBlinks();
  } catch (err) {
    loginError.textContent = err.message;
    loginError.classList.remove('hidden');
  }
}

function logout() {
  accessToken = null;
  localStorage.removeItem('accessToken');
  showLogin();
}

function updateBlinkCount(data) {
  try {
    console.log('Raw data received:', data);
    
    // Parse JSON data from Python script
    let count;
    if (typeof data === 'string') {
      // Try to parse JSON first
      try {
        const jsonData = JSON.parse(data);
        count = jsonData.blink_count || jsonData.count || parseInt(data, 10);
        console.log('Parsed JSON data:', jsonData, 'extracted count:', count);
      } catch (e) {
        // If not JSON, try to parse as number
        count = parseInt(data, 10);
        console.log('Parsed as number:', count);
      }
    } else {
      count = parseInt(data, 10);
      console.log('Direct parse:', count);
    }
    
    if (!isNaN(count)) {
      blinkCount = count;
      blinkCountSpan.textContent = blinkCount;
      
      // Save blink data locally for sync (but don't spam the API)
      const blinkData = { 
        blink_count: blinkCount  // Ensure it's a valid number
      };
      
      console.log('Blink data to save:', blinkData);
      
      // Only save every 5th blink to avoid API spam
      if (blinkCount % 5 === 0 || blinkCount === 1) {
        unsyncedBlinks.push(blinkData);
        localStorage.setItem('unsyncedBlinks', JSON.stringify(unsyncedBlinks));
        setSyncStatus('Blink data saved locally', false);
        
        // Try to sync with a small delay to avoid overwhelming the API
        setTimeout(() => syncUnsyncedBlinks(), 1000);
      }
    } else {
      console.warn('Invalid blink count received:', data);
    }
  } catch (error) {
    console.error('Error updating blink count:', error, 'Data:', data);
  }
}

async function syncUnsyncedBlinks() {
  if (!accessToken) {
    setSyncStatus('Not logged in - data saved locally', false);
    return;
  }
  
  if (unsyncedBlinks.length === 0) {
    setSyncStatus('All data synced', false);
    return;
  }
  
  console.log(`Syncing ${unsyncedBlinks.length} blink entries...`);
  console.log('Unsynced blinks array:', unsyncedBlinks);
  
  for (let i = 0; i < unsyncedBlinks.length; i++) {
    try {
      const blinkData = unsyncedBlinks[i];
      console.log('Syncing blink data:', blinkData);
      
      // Validate data before sending
      if (!blinkData || typeof blinkData.blink_count !== 'number' || isNaN(blinkData.blink_count)) {
        console.error('Invalid blink data, skipping:', blinkData);
        unsyncedBlinks.splice(i, 1);
        i--;
        continue;
      }
      
      // Send only blink_count, no timestamp
      const payload = {
        blink_count: blinkData.blink_count
      };
      
      console.log('Sending payload:', payload);
      
      const res = await fetch(`${API_URL}/blinks/upload`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${accessToken}`,
        },
        body: JSON.stringify(payload),
      });
      
      if (res.ok) {
        const result = await res.json();
        console.log('Sync successful:', result);
        unsyncedBlinks.splice(i, 1);
        i--;
        setSyncStatus(`Synced to cloud (${unsyncedBlinks.length} pending)`, false);
      } else {
        const errorText = await res.text();
        console.error('Sync failed:', res.status, errorText);
        console.error('Data that failed:', JSON.stringify(unsyncedBlinks[i]));
        console.error('Request headers:', {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${accessToken.substring(0, 20)}...`,
        });
        setSyncStatus(`Sync failed: ${res.status} ${res.statusText}`, true);
        break; // Stop trying if there's an auth or server error
      }
    } catch (err) {
      console.error('Network error during sync:', err);
      setSyncStatus('Network error - will retry when online', true);
      break;
    }
  }
  localStorage.setItem('unsyncedBlinks', JSON.stringify(unsyncedBlinks));
}

loginBtn.onclick = login;
logoutBtn.onclick = logout;

startBtn.onclick = () => {
  window.eyeAPI.startEyeTracker();
  startBtn.disabled = true;
  stopBtn.disabled = false;
};

stopBtn.onclick = () => {
  window.eyeAPI.stopEyeTracker();
  startBtn.disabled = false;
  stopBtn.disabled = true;
};

window.eyeAPI.onBlinkCount((data) => {
  updateBlinkCount(data);
});

window.eyeAPI.onEyeTrackerStopped(() => {
  startBtn.disabled = false;
  stopBtn.disabled = true;
  setSyncStatus('Eye tracker stopped', false);
});

// Handle eye tracker errors with cleaner logging
window.eyeAPI.onEyeTrackerError && window.eyeAPI.onEyeTrackerError((error) => {
  // Filter out harmless warnings
  if (error.includes('WARNING') || 
      error.includes('UserWarning') || 
      error.includes('deprecated') ||
      error.includes('absl::InitializeLog') ||
      error.includes('GL version') ||
      error.includes('TensorFlow Lite') ||
      error.includes('feedback manager')) {
    return; // Ignore these warnings
  }
  
  console.error('Eye Tracker Error:', error);
  setSyncStatus(`Eye tracker error: ${error}`, true);
  startBtn.disabled = false;
  stopBtn.disabled = true;
});

// On load
if (accessToken) {
  showMain();
  syncUnsyncedBlinks();
} else {
  showLogin();
} 