/**
 * api/index.js
 * 
 * Модуль для взаимодействия с API бэкенда
 */

import axios from 'axios'

// Создаем экземпляр axios с базовым URL
const api = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json',
  }
})

// Перехватчик для добавления токена авторизации
api.interceptors.request.use(config => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Перехватчик для обработки ошибок
api.interceptors.response.use(
  response => response,
  error => {
    const { response } = error
    // Если получили ошибку 404 - Not Found
    if (response && response.status === 404) {
      console.error('Ресурс не найден:', response.config.url)
    }
    // Если получили ошибку 401 - Unauthorized
    if (response && response.status === 401) {
      // Можно перенаправить на страницу входа
      window.location = '/login'
    }
    return Promise.reject(error)
  }
)

// API для аутентификации
export const authApi = {
  login: (credentials) => api.post('/auth/token', credentials, {
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded'
    }
  }),
  register: (userData) => api.post('/auth/client/register', userData),
}

// API для работы с сотрудниками
export const employeesApi = {
  getProfile: () => api.get('/employees/me'),
  getList: () => api.get('/employees'),
  getAvailable: () => api.get('/employees/available'),
}

// API для работы с клиентами
export const clientsApi = {
  getProfile: () => api.get('/clients/me'),
  getList: () => api.get('/clients'),
  create: (data) => api.post('/clients', data),
  delete: (id) => api.delete(`/clients/${id}`),
}

// API для работы с коммуникациями
export const communicationsApi = {
  getList: (params) => api.get('/communications', { params }),
  create: (data) => api.post('/communications', data),
  update: (id, data) => api.put(`/communications/${id}`, data),
  feedback: (id, data) => api.put(`/communications/${id}/feedback`, data),
}

// API для работы с тестами
export const testsApi = {
  getList: () => api.get('/tests/multiple-choice'),
  create: (data) => api.post('/tests/multiple-choice/', data),
  toggleStatus: (id) => api.put(`/tests/multiple-choice/${id}/toggle-status`),
  delete: (id) => api.delete(`/tests/multiple-choice/${id}`),
  submit: (testId, answers) => api.post(`/tests/multiple-choice/${testId}/submit`, { answers }),
}

// API для работы с чатом
export const chatApi = {
  // Авторизация
  clientLogin: (credentials) => api.post('/chat/client/login', credentials, {
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded'
    }
  }),
  supportLogin: (credentials) => api.post('/chat/support/login', credentials, {
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded'
    }
  }),
  
  // Получить список активных чатов (для оператора)
  getActiveChats: () => {
    return api.get('/chat/active')
  },
  
  // Получить историю сообщений
  getHistory: (clientId) => {
    return api.get(`/chat/history/${clientId}`)
  },
  
  // Отправить отзыв о чате
  submitFeedback: (communicationId, feedbackData) => {
    return api.post(`/chat/feedback/${communicationId}`, feedbackData)
  },
  
  // Получение ID коммуникации
  getCommunicationId: (clientId) => api.get(`/chat/communication/${clientId}`),
  
  // WebSocket соединения (добавлены для информации, но будут использоваться напрямую)
  // clientWebSocket: (clientId) => `ws://${window.location.host}/api/chat/ws/client/${clientId}`,
  // supportWebSocket: (operatorId) => `ws://${window.location.host}/api/chat/ws/support/${operatorId}`,
}

// Экспортируем экземпляр api для прямого использования
export default api 