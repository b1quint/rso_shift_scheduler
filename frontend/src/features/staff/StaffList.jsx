import React, { useState, useEffect } from 'react'
import { staffService } from '../../services'
import './StaffList.css'

function StaffList() {
  const [staff, setStaff] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [filters, setFilters] = useState({
    role: '',
    status: '',
    search: ''
  })

  useEffect(() => {
    fetchStaff()
  }, [filters])

  const fetchStaff = async () => {
    try {
      setLoading(true)
      setError(null)
      
      // Build query params
      const params = new URLSearchParams()
      if (filters.role) params.append('role', filters.role)
      if (filters.status) params.append('status', filters.status)
      if (filters.search) params.append('search', filters.search)
      
      const response = await staffService.getAll(`?${params.toString()}`)
      setStaff(response.data.results || response.data)
      setLoading(false)
    } catch (err) {
      console.error('Error fetching staff:', err)
      setError('Failed to load staff members. Make sure the Django server is running.')
      setLoading(false)
    }
  }

  const handleFilterChange = (e) => {
    setFilters({
      ...filters,
      [e.target.name]: e.target.value
    })
  }

  const getRoleBadgeColor = (role) => {
    const colors = {
      astronomer: '#3b82f6',
      telescope_operator: '#8b5cf6',
      support_scientist: '#10b981',
      night_assistant: '#f59e0b',
      day_crew: '#6366f1',
      maintenance: '#ef4444',
      admin: '#ec4899'
    }
    return colors[role] || '#6b7280'
  }

  const getStatusBadgeColor = (status) => {
    const colors = {
      active: '#10b981',
      on_leave: '#f59e0b',
      inactive: '#ef4444'
    }
    return colors[status] || '#6b7280'
  }

  if (loading) {
    return (
      <div className="staff-list">
        <h2>Staff Members</h2>
        <div className="loading">Loading staff members...</div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="staff-list">
        <h2>Staff Members</h2>
        <div className="error">
          <p>{error}</p>
          <button onClick={fetchStaff}>Retry</button>
        </div>
      </div>
    )
  }

  return (
    <div className="staff-list">
      <div className="staff-header">
        <h2>Staff Members</h2>
        <button className="btn-primary">+ Add Staff</button>
      </div>

      <div className="filters">
        <input
          type="text"
          name="search"
          placeholder="Search by name or employee ID..."
          value={filters.search}
          onChange={handleFilterChange}
          className="search-input"
        />
        
        <select
          name="role"
          value={filters.role}
          onChange={handleFilterChange}
          className="filter-select"
        >
          <option value="">All Roles</option>
          <option value="astronomer">Astronomer</option>
          <option value="telescope_operator">Telescope Operator</option>
          <option value="support_scientist">Support Scientist</option>
          <option value="night_assistant">Night Assistant</option>
          <option value="day_crew">Day Crew</option>
          <option value="maintenance">Maintenance</option>
          <option value="admin">Administrator</option>
        </select>

        <select
          name="status"
          value={filters.status}
          onChange={handleFilterChange}
          className="filter-select"
        >
          <option value="">All Status</option>
          <option value="active">Active</option>
          <option value="on_leave">On Leave</option>
          <option value="inactive">Inactive</option>
        </select>
      </div>

      <div className="staff-count">
        {staff.length} staff member{staff.length !== 1 ? 's' : ''} found
      </div>

      <div className="staff-grid">
        {staff.map((member) => (
          <div key={member.id} className="staff-card">
            <div className="staff-card-header">
              <div>
                <h3>{member.full_name}</h3>
                <p className="employee-id">{member.employee_id}</p>
              </div>
              <div className="badges">
                <span 
                  className="badge"
                  style={{ backgroundColor: getRoleBadgeColor(member.role) }}
                >
                  {member.role.replace(/_/g, ' ')}
                </span>
                <span 
                  className="badge"
                  style={{ backgroundColor: getStatusBadgeColor(member.status) }}
                >
                  {member.status.replace(/_/g, ' ')}
                </span>
              </div>
            </div>

            <div className="staff-card-body">
              <div className="info-row">
                <span className="label">Email:</span>
                <span>{member.user?.email || 'N/A'}</span>
              </div>
              {member.phone && (
                <div className="info-row">
                  <span className="label">Phone:</span>
                  <span>{member.phone}</span>
                </div>
              )}
              <div className="info-row">
                <span className="label">Hire Date:</span>
                <span>{new Date(member.hire_date).toLocaleDateString()}</span>
              </div>
              <div className="info-row">
                <span className="label">Night Shifts:</span>
                <span>{member.prefers_night_shifts ? '✓ Yes' : '✗ No'}</span>
              </div>
            </div>

            <div className="staff-card-footer">
              <button className="btn-secondary">View Details</button>
              <button className="btn-secondary">Edit</button>
            </div>
          </div>
        ))}
      </div>

      {staff.length === 0 && (
        <div className="empty-state">
          <p>No staff members found matching your filters.</p>
        </div>
      )}
    </div>
  )
}

export default StaffList
