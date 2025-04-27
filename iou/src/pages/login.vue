<template>
  <v-container fluid class="fill-height bg-secondary-subtle">
    <v-row justify="center" align="center">
      <v-col cols="12" sm="8" md="4" lg="3">
        <v-card class="elevation-5 rounded-lg">
          <v-card-title class="text-center pt-6 pb-2">
            <h4 class="text-h4 font-weight-bold">Вход в систему</h4>
          </v-card-title>
          
          <v-card-text>
            <v-form ref="form" @submit.prevent="login">
              <v-text-field
                v-model="username"
                label="Имя пользователя"
                placeholder="Введите имя пользователя"
                prepend-inner-icon="mdi-account"
                :rules="[v => !!v || 'Имя пользователя обязательно']"
                required
                variant="outlined"
                class="mb-4"
              ></v-text-field>
              
              <v-text-field
                v-model="password"
                label="Пароль"
                placeholder="Введите пароль"
                prepend-inner-icon="mdi-lock"
                :append-inner-icon="showPassword ? 'mdi-eye-off' : 'mdi-eye'"
                :type="showPassword ? 'text' : 'password'"
                @click:append-inner="showPassword = !showPassword"
                :rules="[v => !!v || 'Пароль обязателен']"
                required
                variant="outlined"
                class="mb-4"
              ></v-text-field>
              
              <div class="mb-4 d-flex justify-space-between align-center">
                <v-checkbox 
                  v-model="rememberMe" 
                  label="Запомнить меня" 
                  color="primary" 
                  density="compact"
                ></v-checkbox>
                <a href="#" class="text-secondary text-decoration-none">Забыли пароль?</a>
              </div>
              
              <v-btn 
                color="primary" 
                block 
                size="large" 
                type="submit" 
                :loading="authStore.loading"
                class="mb-4"
              >
                Войти
              </v-btn>
            </v-form>
          </v-card-text>
          
          <v-divider></v-divider>
          
          <v-card-actions class="pa-4 justify-center">
            <span class="text-medium-emphasis">Нет аккаунта?</span>
            <v-btn variant="text" color="primary" to="/register">
              Зарегистрироваться
            </v-btn>
          </v-card-actions>
          
          <v-snackbar v-model="snackbar" :color="snackbarColor" timeout="3000">
            {{ snackbarText }}
            <template v-slot:actions>
              <v-btn variant="text" @click="snackbar = false">Закрыть</v-btn>
            </template>
          </v-snackbar>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

// Состояние формы
const form = ref(null)
const username = ref('')
const password = ref('')
const showPassword = ref(false)
const rememberMe = ref(false)

// Состояние уведомления
const snackbar = ref(false)
const snackbarText = ref('')
const snackbarColor = ref('error')

// При монтировании проверяем, есть ли запомненный пользователь
onMounted(() => {
  const rememberedUser = localStorage.getItem('rememberedUser')
  if (rememberedUser) {
    username.value = rememberedUser
    rememberMe.value = true
  }

  // Если пользователь уже авторизован, перенаправляем на dashboard
  if (authStore.isAuthenticated) {
    router.push('/dashboard')
  }
})

// Метод авторизации
const login = async () => {
  if (!form.value.validate()) return
  
  // Используем хранилище для аутентификации
  const result = await authStore.login({
    username: username.value,
    password: password.value
  })
  
  if (result.success) {
    // Если нужно запомнить пользователя
    if (rememberMe.value) {
      localStorage.setItem('rememberedUser', username.value)
    } else {
      localStorage.removeItem('rememberedUser')
    }
    
    // Показываем сообщение об успехе
    snackbarColor.value = 'success'
    snackbarText.value = 'Вы успешно вошли в систему'
    snackbar.value = true
    
    // Перенаправляем на главную страницу
    setTimeout(() => {
      router.push('/dashboard')
    }, 1000)
  } else {
    // Показываем сообщение об ошибке
    snackbarColor.value = 'error'
    snackbarText.value = authStore.error || 'Ошибка при входе в систему'
    snackbar.value = true
  }
}
</script>