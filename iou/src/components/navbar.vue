<template>
  <v-app-bar :elevation="1" color="surface">
    <v-app-bar-title>
      <router-link to="/" class="d-flex align-center text-decoration-none">
        <v-img 
          src="@/assets/logo.png" 
          alt="Logo" 
          max-height="40" 
          max-width="40" 
          class="me-2" 
        />
      </router-link>
    </v-app-bar-title>

    <v-spacer></v-spacer>

    <!-- Навигационные ссылки для авторизованных пользователей -->
    <template v-if="authStore.isAuthenticated">
      <!-- Общие ссылки для всех пользователей -->
      <v-btn to="/dashboard" variant="text">
        Панель управления
      </v-btn>
      
      <!-- Ссылки для сотрудников (операторов и администраторов) -->
      <template v-if="isEmployee">
        <v-btn to="/tests" variant="text">
          Тесты
        </v-btn>
        
        <v-btn to="/chat" variant="text">
          Чат
        </v-btn>
        
        <!-- Дополнительные ссылки только для администраторов -->
        <template v-if="isAdmin">
          <v-btn to="/admin/clients" variant="text">
            Клиенты
          </v-btn>
          <v-btn to="/admin/employees" variant="text">
            Сотрудники
          </v-btn>
          <v-btn to="/admin/statistics" variant="text">
            Статистика
          </v-btn>
        </template>
      </template>
      
      <!-- Ссылки для клиентов -->
      <template v-else-if="isClient">
        <v-btn to="/support" variant="text">
          Поддержка
        </v-btn>
        <v-btn to="/chat" variant="text">
          Чат
        </v-btn>
      </template>
      
      <v-divider vertical class="mx-4"></v-divider>
      
      <v-menu transition="scale-transition" location="bottom">
        <template v-slot:activator="{ props }">
          <v-btn v-bind="props" class="text-none" variant="text">
            {{ authStore.user?.name || 'Профиль' }} 
            <v-icon end>mdi-chevron-down</v-icon>
          </v-btn>
        </template>
        <v-list>
          <v-list-item to="/profile">
            <v-list-item-title>Мой профиль</v-list-item-title>
          </v-list-item>
          <v-divider></v-divider>
          <v-list-item @click="logout">
            <v-list-item-title>Выйти</v-list-item-title>
          </v-list-item>
        </v-list>
      </v-menu>
    </template>
    
    <!-- Навигационные ссылки для неавторизованных пользователей -->
    <template v-else>
      <v-btn to="/login" variant="text">
        Войти
      </v-btn>
      <v-btn to="/register" color="primary" variant="flat" class="ml-2">
        Регистрация
      </v-btn>
    </template>
  </v-app-bar>
</template>

<script setup>
import { useAuthStore } from '@/stores/auth'
import { useRouter } from 'vue-router'
import { computed } from 'vue'

const authStore = useAuthStore()
const router = useRouter()

// Определяем роли пользователя через вычисляемые свойства
const isAdmin = computed(() => authStore.user?.role === 'employee' && authStore.user?.is_admin)
const isEmployee = computed(() => authStore.user?.role === 'employee')
const isClient = computed(() => authStore.user?.role === 'client')

async function logout() {
  await authStore.logout()
  router.push('/login')
}
</script>
