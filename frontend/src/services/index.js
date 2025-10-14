import api from './api'

// Authentication
export const authService = {
  login: async (username, password) => {
    const response = await api.post('/auth/login/', { username, password })
    if (response.data.access) {
      localStorage.setItem('access_token', response.data.access)
      localStorage.setItem('refresh_token', response.data.refresh)
    }
    return response.data
  },

  logout: () => {
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
  },

  isAuthenticated: () => {
    return !!localStorage.getItem('access_token')
  },
}

// Staff
export const staffService = {
  getAll: () => api.get('/staff/'),
  getById: (id) => api.get(`/staff/${id}/`),
  create: (data) => api.post('/staff/', data),
  update: (id, data) => api.put(`/staff/${id}/`, data),
  delete: (id) => api.delete(`/staff/${id}/`),
}

// Shifts
export const shiftService = {
  getAll: () => api.get('/shifts/'),
  getById: (id) => api.get(`/shifts/${id}/`),
  create: (data) => api.post('/shifts/', data),
  update: (id, data) => api.put(`/shifts/${id}/`, data),
  delete: (id) => api.delete(`/shifts/${id}/`),
}

// Schedules
export const scheduleService = {
  getAll: () => api.get('/schedules/'),
  getById: (id) => api.get(`/schedules/${id}/`),
  create: (data) => api.post('/schedules/', data),
  update: (id, data) => api.put(`/schedules/${id}/`, data),
  delete: (id) => api.delete(`/schedules/${id}/`),
}
