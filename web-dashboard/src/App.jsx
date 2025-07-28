import React, { useState, useEffect } from 'react';
import LoginForm from './components/LoginForm.jsx';
import RegisterForm from './components/RegisterForm.jsx';
import BlinkChart from './components/BlinkChart.jsx';
import axios from 'axios';

const API_URL = 'http://localhost:8000';

export default function App() {
  const [token, setToken] = useState(localStorage.getItem('accessToken') || '');
  const [blinks, setBlinks] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [showRegister, setShowRegister] = useState(false);

  // Login handler
  const handleLogin = async (email, password) => {
    setError('');
    setLoading(true);
    try {
      const form = new FormData();
      form.append('username', email);
      form.append('password', password);
      const res = await axios.post(`${API_URL}/token`, form);
      setToken(res.data.access_token);
      localStorage.setItem('accessToken', res.data.access_token);
    } catch (err) {
      setError('Login failed. Please check your credentials.');
    } finally {
      setLoading(false);
    }
  };

  // Registration handler
  const handleRegister = async (userData) => {
    setError('');
    setLoading(true);
    try {
      await axios.post(`${API_URL}/register`, userData);
      await handleLogin(userData.email, userData.password);
    } catch (err) {
      if (err.response?.data?.detail) {
        setError(err.response.data.detail);
      } else {
        setError('Registration failed. Please try again.');
      }
    } finally {
      setLoading(false);
    }
  };

  // Logout handler
  const handleLogout = () => {
    setToken('');
    setBlinks([]);
    localStorage.removeItem('accessToken');
  };

  // Fetch blink data when logged in
  useEffect(() => {
    if (!token) return;
    setLoading(true);
    axios
      .get(`${API_URL}/blinks/user`, {
        headers: { Authorization: `Bearer ${token}` },
      })
      .then((res) => {
        setBlinks(res.data);
        setLoading(false);
      })
      .catch(() => {
        setError('Failed to fetch blink data.');
        setLoading(false);
      });
  }, [token]);

  if (!token) {
    return showRegister ? (
      <RegisterForm onRegister={handleRegister} error={error} onSwitchToLogin={() => setShowRegister(false)} />
    ) : (
      <LoginForm onLogin={handleLogin} error={error} onSwitchToRegister={() => setShowRegister(true)} />
    );
  }

  return (
    <div className="container">
      <h1>WaW Eye Blink Dashboard</h1>
      <button
        onClick={handleLogout}
        className="logout-btn"
        style={{
          background: 'linear-gradient(90deg, #3bc6f6 0%, #4fd1c5 100%)',
          color: '#fff',
          border: 'none',
          borderRadius: '6px',
          padding: '0.7em 1.5em',
          fontWeight: 600,
          fontSize: '1.1em',
          margin: '0.5em 0 1.5em 0',
          boxShadow: '0 2px 8px rgba(75,192,192,0.08)',
          cursor: 'pointer',
          transition: 'background 0.2s',
        }}
        onMouseOver={e => e.currentTarget.style.background = 'linear-gradient(90deg, #4fd1c5 0%, #3bc6f6 100%)'}
        onMouseOut={e => e.currentTarget.style.background = 'linear-gradient(90deg, #3bc6f6 0%, #4fd1c5 100%)'}
      >
        Logout
      </button>
      {loading ? (
        <p>Loading blink data...</p>
      ) : error ? (
        <p style={{ color: 'red' }}>{error}</p>
      ) : (
        <BlinkChart blinks={blinks} />
      )}
    </div>
  );
}
