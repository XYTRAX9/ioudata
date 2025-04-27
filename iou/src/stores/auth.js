import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authApi, employeesApi, clientsApi } from '@/api'

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem('token') || '')
  const user = ref(null)
  const loading = ref(false)
  const error = ref(null)
  
  const isAuthenticated = computed(() => !!token.value)
  
  // Загружаем данные пользователя при инициализации
  async function loadUserProfile() {
    if (!token.value) return
    
    loading.value = true
    error.value = null
    
    try {
      // Пробуем получить профиль сотрудника
      const response = await employeesApi.getProfile()
      user.value = { ...response.data, role: 'employee' }
    } catch (err) {
      if (err.response?.status === 401) {
        // Если не сотрудник, пробуем получить профиль клиента
        try {
          const response = await clientsApi.getProfile()
          user.value = { ...response.data, role: 'client' }
        } catch (clientErr) {
          // Если ошибка аутентификации для обоих типов - выходим
          if (clientErr.response?.status === 401) {
            await logout()
          }
          error.value = clientErr
        }
      } else {
        error.value = err
      }
    } finally {
      loading.value = false
    }
  }
  
  // Авторизация
  async function login(credentials) {
    loading.value = true
    error.value = null
    
    try {
      const formData = new URLSearchParams()
      formData.append('username', credentials.username)
      formData.append('password', credentials.password)
      
      const response = await authApi.login(formData)
      token.value = response.data.access_token
      localStorage.setItem('token', token.value)
      
      // Загружаем профиль пользователя
      await loadUserProfile()
      return { success: true }
    } catch (err) {
      error.value = err.response?.data?.detail || 'Ошибка авторизации'
      return { success: false, error: error.value }
    } finally {
      loading.value = false
    }
  }
  
  // Выход
  async function logout() {
    token.value = ''
    user.value = null
    localStorage.removeItem('token')
  }
  
  // Проверка актуальности токена
  async function checkAuth() {
    if (!token.value) return false
    await loadUserProfile()
    return !!user.value
  }
  
  return {
    token,
    user,
    loading,
    error,
    isAuthenticated,
    login,
    logout,
    loadUserProfile,
    checkAuth
  }
}) 