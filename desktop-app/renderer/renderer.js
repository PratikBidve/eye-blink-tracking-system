const API_URL = 'http://localhost:8000'; // Backend API URL

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

function updateBlinkCount(count) {
  blinkCount = parseInt(count, 10);
  blinkCountSpan.textContent = blinkCount;
  // Save blink data locally for sync
  unsyncedBlinks.push({ blink_count: blinkCount, timestamp: new Date().toISOString() });
  localStorage.setItem('unsyncedBlinks', JSON.stringify(unsyncedBlinks));
  setSyncStatus('Blink data saved locally (offline mode)', false);
  syncUnsyncedBlinks();
}

async function syncUnsyncedBlinks() {
  if (!accessToken || unsyncedBlinks.length === 0) return;
  for (let i = 0; i < unsyncedBlinks.length; i++) {
    try {
      const res = await fetch(`${API_URL}/blinks/upload`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${accessToken}`,
        },
        body: JSON.stringify(unsyncedBlinks[i]),
      });
      if (res.ok) {
        unsyncedBlinks.splice(i, 1);
        i--;
        setSyncStatus('Blink data synced to cloud', false);
      } else {
        setSyncStatus('Failed to sync blink data', true);
      }
    } catch (err) {
      setSyncStatus('Offline: will sync when online', true);
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
});

// On load
if (accessToken) {
  showMain();
  syncUnsyncedBlinks();
} else {
  showLogin();
} 