import React, { useState } from 'react';

export default function LoginForm({ onLogin, onSwitchToRegister, error, loading }) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!email || !password || loading) return;
    
    await onLogin(email, password);
  };

  return (
    <div className="login-container">
      <div className="login-background">
        <div className="background-shapes">
          <div className="shape shape-1"></div>
          <div className="shape shape-2"></div>
          <div className="shape shape-3"></div>
        </div>
      </div>
      
      <div className="login-content">
        <div className="login-form-wrapper">
          <div className="login-header">
            <div className="login-logo">
              <span className="logo-icon">👁️</span>
              <h1 className="logo-text">Eye Blink Analytics</h1>
            </div>
            <p className="login-subtitle">
              Track and analyze your eye blink patterns with precision
            </p>
          </div>

          <form className="login-form" onSubmit={handleSubmit}>
            <div className="form-group">
              <label className="form-label">Email Address</label>
              <div className="input-wrapper">
                <span className="input-icon">📧</span>
                <input
                  type="email"
                  className="form-input"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="Enter your email"
                  disabled={loading}
                  required
                />
              </div>
            </div>
            
            <div className="form-group">
              <label className="form-label">Password</label>
              <div className="input-wrapper">
                <span className="input-icon">🔒</span>
                <input
                  type="password"
                  className="form-input"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="Enter your password"
                  disabled={loading}
                  required
                />
              </div>
            </div>
            
            <button 
              type="submit" 
              className="login-btn"
              disabled={loading || !email || !password}
            >
              {loading && <span className="btn-spinner">⏳</span>}
              {loading ? 'Signing in...' : 'Sign In to Dashboard'}
            </button>
            
            {error && (
              <div className="error-message">
                <span className="error-icon">⚠️</span>
                {error}
              </div>
            )}
          </form>

          <div className="login-footer">
            <p className="footer-text">
              Don't have an account?{' '}
              <button 
                type="button" 
                className="link-btn" 
                onClick={onSwitchToRegister}
                disabled={loading}
              >
                Create one here
              </button>
            </p>
            <p className="footer-text">
              Secure authentication • Real-time tracking • Advanced analytics
            </p>
          </div>
        </div>
      </div>
    </div>
  );
} 