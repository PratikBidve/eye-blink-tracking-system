# Wellness at Work: Cloud-Synced Eye Tracker

## Overview
A cross-platform desktop application for real-time eye-blink tracking, cloud-synced for wellness analytics, with a secure backend and web dashboard. GDPR compliant.

## Project Structure
```
/Eye_Blink_test_case
│
├── desktop-app/         # Electron + Python eye tracker
├── backend-api/         # FastAPI backend + PostgreSQL
├── web-dashboard/       # React web dashboard
├── README.md
└── .github/workflows/   # CI/CD pipelines
```

## Architecture Diagram
```mermaid
graph TD
    A[Desktop App (Electron + Python)] -- REST API --> B[Cloud Backend (FastAPI/Express)]
    B -- SQL --> C[Database (PostgreSQL)]
    D[Web Dashboard (React)] -- REST API --> B
    A -- Local Storage --> E[Offline Data Store
```

## Technology Choices
- **Desktop App:** Electron (cross-platform UI), Python (eye tracking), Node.js (API, local storage)
- **Backend:** FastAPI (Python, async, secure), PostgreSQL (robust, relational)
- **Web Dashboard:** React (modern, fast), Chart.js (visualization)
- **CI/CD:** GitHub Actions (test, lint, build)

## API Usage & Testing

### Accessing Swagger UI
- When the backend is running, open [http://localhost:8000/docs](http://localhost:8000/docs) in your browser.
- This provides an interactive Swagger UI to test all endpoints.

### API Endpoints

#### 1. Register a User
- **POST** `/register`
- **Body (JSON):**
```json
{
  "email": "user@example.com",
  "password": "yourpassword",
  "consent": true
}
```
- **Response:** User object (id, email, consent, created_at)

#### 2. Login (Get JWT Token)
- **POST** `/token`
- **Body (form-data):**
  - `username`: user email
  - `password`: user password
- **Response:**
```json
{
  "access_token": "<JWT_TOKEN>",
  "token_type": "bearer"
}
```

#### 3. Upload Blink Data
- **POST** `/blinks/upload`
- **Headers:**
  - `Authorization: Bearer <JWT_TOKEN>`
- **Body (JSON):**
```json
{
  "blink_count": 5,
  "timestamp": "2024-06-01T12:34:56.789Z"  // optional, defaults to now
}
```
- **Response:** Blink data object

#### 4. Get User Blink Data
- **GET** `/blinks/user`
- **Headers:**
  - `Authorization: Bearer <JWT_TOKEN>`
- **Response:** Array of blink data objects

### Example Workflow in Swagger UI
1. Register a user with `/register`.
2. Login with `/token` to get your JWT token.
3. Click "Authorize" in Swagger UI and paste your token as `Bearer <token>`.
4. Use `/blinks/upload` to send blink data.
5. Use `/blinks/user` to fetch your blink history.

---

## GDPR & Security
- **GDPR:**
  - Explicit user consent for data collection
  - Data minimization (only blink data, email, consent)
  - Right to erasure (user data can be deleted)
  - Local encryption and secure transmission (HTTPS)
  - Clear privacy policy (to be provided)
- **Security:**
  - JWT authentication for all endpoints
  - Passwords hashed with bcrypt
  - HTTPS enforced (production)
  - Input validation and CORS
  - Least privilege for database access

## Test Cases (for CI/CD)
- **Backend:**
  - User registration/login (success/failure)
  - Blink data upload (valid/invalid token)
  - Offline data sync (simulate offline, then online)
  - Web dashboard: fetch and display data for authenticated user
- **Web Dashboard:**
  - Login with valid/invalid credentials
  - Data visualization loads for authenticated user
- **Desktop App:**
  - Eye tracker subprocess starts/stops
  - Blink count updates in UI
  - Data is saved locally when offline and synced when online

## Setup Instructions
*See each component's README for local setup and build instructions.*

## Distribution
- **Windows:** Electron-builder for .exe installer
- **macOS:** Electron-builder for .app bundle (App Sandbox enabled)
- **Testers:** Distribution files or TestFlight invitation to ishaan80@gmail.com and mehul.bhardwaj@outlook.com 