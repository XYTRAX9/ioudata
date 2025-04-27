<template>
  <v-app>
    <router-view v-if="appReady"/>
    <v-container v-else class="fill-height" fluid>
      <v-row align="center" justify="center">
        <v-col cols="12" class="text-center">
          <v-progress-circular
            indeterminate
            color="primary"
            size="50"
          ></v-progress-circular>
          <div class="mt-4">Загрузка приложения...</div>
        </v-col>
      </v-row>
    </v-container>

    <!-- Глобальный снэкбар -->
    <v-snackbar
      v-model="snackbar.show"
      :color="snackbar.color"
      :timeout="snackbar.timeout"
    >
      {{ snackbar.text }}
      <template v-slot:actions>
        <v-btn
          variant="text"
          @click="hideSnackbar"
        >
          Закрыть
        </v-btn>
      </template>
    </v-snackbar>
  </v-app>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useTheme } from 'vuetify'
import { provideSnackbar } from '@/composables/useSnackbar'

const authStore = useAuthStore()
const appReady = ref(false)
const theme = useTheme()

// Предоставляем снэкбар для компонентов
const { snackbar, hideSnackbar } = provideSnackbar()

onMounted(async () => {
  // Принудительно устанавливаем тёмную тему
  theme.global.name.value = 'darkTheme'
  
  // Проверяем аутентификацию при запуске приложения
  if (localStorage.getItem('token')) {
    try {
      await authStore.loadUserProfile()
    } catch (error) {
      console.error('Ошибка загрузки профиля:', error)
    }
  }
  
  // Отмечаем, что приложение готово к отображению
  appReady.value = true
})
</script>