import React, { useState, useEffect } from 'react'
import { shiftService } from '../../services'
import './ShiftList.css'

function ShiftList() {
  const [shifts, setShifts] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    fetchShifts()
  }, [])

  const fetchShifts = async () => {
    try {
      setLoading(true)
      setError(null)
      const response = await shiftService.getAll()
      setShifts(response.data.results || response.data)
      setLoading(false)
    } catch (err) {
      console.error('Error fetching shifts:', err)
      setError('Failed to load shifts. Make sure the Django server is running.')
      setLoading(false)
    }
  }

  const getShiftTypeColor = (type) => {
    const colors = {
      day: '#3b82f6',
      night: '#8b5cf6',
      twilight: '#f59e0b',
      on_call: '#10b981'
    }
    return colors[type] || '#6b7280'
  }

  const getStatusColor = (status) => {
    const colors = {
      scheduled: '#3b82f6',
      confirmed: '#10b981',
      in_progress: '#f59e0b',
      completed: '#6b7280',
      cancelled: '#ef4444'
    }
    return colors[status] || '#6b7280'
  }

  const formatDate = (dateString) => {
    const date = new Date(dateString)
    return date.toLocaleString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  if (loading) {
    return (
      <div className="shift-list">
        <h2>Shifts</h2>
        <div className="loading">Loading shifts...</div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="shift-list">
        <h2>Shifts</h2>
        <div className="error">
          <p>{error}</p>
          <button onClick={fetchShifts}>Retry</button>
        </div>
      </div>
    )
  }

  return (
    <div className="shift-list">
      <div className="shift-header">
        <h2>Shifts Schedule</h2>
        <button className="btn-primary">+ Add Shift</button>
      </div>

      <div className="shift-count">
        {shifts.length} shift{shifts.length !== 1 ? 's' : ''} scheduled
      </div>

      <div className="shifts-table">
        <table>
          <thead>
            <tr>
              <th>Date & Time</th>
              <th>Type</th>
              <th>Staff Member</th>
              <th>Telescope</th>
              <th>Duration</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            {shifts.map((shift) => (
              <tr key={shift.id}>
                <td>
                  <div className="date-cell">
                    <div>{formatDate(shift.start_time)}</div>
                    <div className="end-time">to {formatDate(shift.end_time)}</div>
                  </div>
                </td>
                <td>
                  <span 
                    className="badge"
                    style={{ backgroundColor: getShiftTypeColor(shift.shift_type) }}
                  >
                    {shift.shift_type}
                  </span>
                </td>
                <td>{shift.staff_name || 'Unassigned'}</td>
                <td>{shift.telescope_name || 'N/A'}</td>
                <td>{shift.duration_hours?.toFixed(1)}h</td>
                <td>
                  <span 
                    className="badge"
                    style={{ backgroundColor: getStatusColor(shift.status) }}
                  >
                    {shift.status.replace(/_/g, ' ')}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {shifts.length === 0 && (
        <div className="empty-state">
          <p>No shifts scheduled yet.</p>
        </div>
      )}
    </div>
  )
}

export default ShiftList
