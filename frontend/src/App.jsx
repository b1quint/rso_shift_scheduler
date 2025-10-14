import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom'
import './App.css'
import Home from './features/schedule/Home'

function App() {
  return (
    <Router>
      <div className="app">
        <nav className="navbar">
          <div className="nav-container">
            <h1 className="nav-title">🔭 Observatory Shift Scheduler</h1>
            <ul className="nav-links">
              <li><Link to="/">Home</Link></li>
              <li><Link to="/schedule">Schedule</Link></li>
              <li><Link to="/staff">Staff</Link></li>
              <li><Link to="/shifts">Shifts</Link></li>
            </ul>
          </div>
        </nav>

        <main className="main-content">
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/schedule" element={<div>Schedule View (Coming Soon)</div>} />
            <Route path="/staff" element={<div>Staff Management (Coming Soon)</div>} />
            <Route path="/shifts" element={<div>Shift Management (Coming Soon)</div>} />
          </Routes>
        </main>
      </div>
    </Router>
  )
}

export default App
