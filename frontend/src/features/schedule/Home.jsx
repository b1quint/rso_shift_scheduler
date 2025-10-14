import React from 'react'

function Home() {
  return (
    <div className="home">
      <h1>Welcome to Observatory Shift Scheduler</h1>
      <p>Manage staff shifts for astronomical observatory operations</p>

      <div className="feature-grid">
        <div className="feature-card">
          <div className="feature-icon">📅</div>
          <h3>Schedule Management</h3>
          <p>Create and manage shift schedules with ease</p>
        </div>

        <div className="feature-card">
          <div className="feature-icon">👥</div>
          <h3>Staff Management</h3>
          <p>Track staff availability and preferences</p>
        </div>

        <div className="feature-card">
          <div className="feature-icon">🌙</div>
          <h3>Night Shifts</h3>
          <p>Specialized handling for night observations</p>
        </div>

        <div className="feature-card">
          <div className="feature-icon">📊</div>
          <h3>Reports</h3>
          <p>Generate shift reports and analytics</p>
        </div>
      </div>

      <div className="status">
        <h3>System Status</h3>
        <ul>
          <li>Backend API: Running on port 8000</li>
          <li>Frontend: Running on port 5173</li>
          <li>Database: SQLite (Development)</li>
          <li>Authentication: JWT Ready</li>
        </ul>
      </div>
    </div>
  )
}

export default Home
