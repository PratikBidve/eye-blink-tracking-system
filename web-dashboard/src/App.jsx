import React, { useState } from 'react';
import LoginForm from './components/LoginForm.jsx';
import BlinkChart from './components/BlinkChart.jsx';
import axios from 'axios';

const API_URL = 'http://localhost:8000';

export default function App() {
  const [token, setToken] = useState(localStorage.getItem('accessToken') || '');
  const [blinks, setBlinks] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleLogin = async (email, password) => {
    setError('');
    try {
      const form = new FormData();
      form.append('username', email);
      form.append('password', password);
      const res = await axios.post(`${API_URL}/token`, form);
      setToken(res.data.access_token);
      localStorage.setItem('accessToken', res.data.access_token);
    } catch (err) {
      setError('Login failed.');
    }
  };

  const handleLogout = () => {
    setToken('');
    setBlinks([]);
    localStorage.removeItem('accessToken');
  };

  React.useEffect(() => {
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
    return <LoginForm onLogin={handleLogin} error={error} />;
  }

  return (
    <div className="container">
      <h1>WaW Eye Blink Dashboard</h1>
      <button onClick={handleLogout}>Logout</button>
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