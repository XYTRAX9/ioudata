/**
 * router/index.ts
 *
 * Automatic routes for `./src/pages/*.vue`
 */

// Composables
import { createRouter, createWebHistory } from 'vue-router/auto'
import { setupLayouts } from 'virtual:generated-layouts'
import { routes } from 'vue-router/auto-routes'
import { useAuthStore } from '@/stores/auth'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: setupLayouts(routes),
})

// Гостевые маршруты (доступные без авторизации)
const publicRoutes = ['/login', '/register', '/']

// Хук для проверки авторизации
router.beforeEach(async (to, from, next) => {
  // Проверяем, требуется ли авторизация для маршрута
  const requiresAuth = !publicRoutes.includes(to.path)
  
  // Получаем текущий токен из localStorage
  const token = localStorage.getItem('token')
  
  if (requiresAuth && !token) {
    // Если маршрут требует авторизации, но токена нет, перенаправляем на страницу входа
    next('/login')
    return
  }
  
  // Проверка доступа к административным маршрутам
  if (to.path.startsWith('/admin')) {
    const authStore = useAuthStore()
    // Если пользователь не загружен, загружаем его профиль
    if (!authStore.user) {
      await authStore.loadUserProfile()
    }
    
    // Проверяем, является ли пользователь администратором (is_superuser)
    if (!authStore.user?.is_superuser) {
      // Если нет, перенаправляем на дашборд
      next('/dashboard')
      return
    }
  }
  
  // В остальных случаях разрешаем переход
  next()
})

// Workaround for https://github.com/vitejs/vite/issues/11804
router.onError((err, to) => {
  if (err?.message?.includes?.('Failed to fetch dynamically imported module')) {
    if (!localStorage.getItem('vuetify:dynamic-reload')) {
      console.log('Reloading page to fix dynamic import error')
      localStorage.setItem('vuetify:dynamic-reload', 'true')
      location.assign(to.fullPath)
    } else {
      console.error('Dynamic import error, reloading page did not fix it', err)
    }
  } else {
    console.error(err)
  }
})

router.isReady().then(() => {
  localStorage.removeItem('vuetify:dynamic-reload')
})

export default router
