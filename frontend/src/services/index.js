import api from './api'

// Authentication
export const authService = {
  login: (username, password) => api.post('/auth/login/', { username, password }),
  logout: (refreshToken) => api.post('/auth/logout/', { refresh: refreshToken }),
  getCurrentUser: () => api.get('/auth/me/'),
  refreshToken: (refresh) => api.post('/auth/refresh/', { refresh }),
}

// Staff
export const staffService = {
  getAll: (params = {}) => api.get('/staff/members/', { params }),
  getById: (id) => api.get(`/staff/members/${id}/`),
  create: (data) => api.post('/staff/members/', data),
  update: (id, data) => api.put(`/staff/members/${id}/`, data),
  delete: (id) => api.delete(`/staff/members/${id}/`),
}

// Shifts
export const shiftService = {
  getAll: (params = {}) => api.get('/shifts/', { params }),
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
