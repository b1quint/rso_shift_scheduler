import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom'
import './App.css'
import { AuthProvider, useAuth } from './contexts/AuthContext'
import Home from './features/schedule/Home'
import ScheduleCalendar from './features/schedule/ScheduleCalendar'
import StaffList from './features/staff/StaffList'
import ShiftList from './features/shifts/ShiftList'
import Login from './features/auth/Login'

function Navigation() {
  const { user, isAuthenticated, logout } = useAuth();

  return (
    <nav className="navbar">
      <div className="nav-container">
        <h1 className="nav-title">🔭 Observatory Shift Scheduler</h1>
        <ul className="nav-links">
          <li><Link to="/">Home</Link></li>
          <li><Link to="/schedule">Schedule</Link></li>
          <li><Link to="/staff">Staff</Link></li>
          <li><Link to="/shifts">Shifts</Link></li>
        </ul>
        <div className="nav-auth">
          {isAuthenticated ? (
            <>
              <span className="user-info">👤 {user?.username}</span>
              <button onClick={logout} className="logout-button">Logout</button>
            </>
          ) : (
            <Link to="/login" className="login-link">Login</Link>
          )}
        </div>
      </div>
    </nav>
  );
}

function AppContent() {
  return (
    <div className="app">
      <Navigation />
      <main className="main-content">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/schedule" element={<ScheduleCalendar />} />
          <Route path="/staff" element={<StaffList />} />
          <Route path="/shifts" element={<ShiftList />} />
          <Route path="/login" element={<Login />} />
        </Routes>
      </main>
    </div>
  );
}

function App() {
  return (
    <Router>
      <AuthProvider>
        <AppContent />
      </AuthProvider>
    </Router>
  )
}

export default App
