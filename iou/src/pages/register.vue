<template>
  <v-container fluid class="fill-height bg-secondary-subtle">
    <v-row justify="center" align="center">
      <v-col cols="12" sm="10" md="6" lg="5">
        <v-card class="elevation-5 rounded-lg">
          <v-card-title class="text-center pt-6 pb-2">
            <h4 class="text-h4 font-weight-bold">Регистрация клиента</h4>
          </v-card-title>
          
          <v-card-text>
            <v-form ref="form" @submit.prevent="register">
              <v-row>
                <v-col cols="12">
                  <v-text-field
                    v-model="name"
                    label="Имя"
                    placeholder="Введите ваше имя"
                    prepend-inner-icon="mdi-account"
                    :rules="[v => !!v || 'Имя обязательно']"
                    required
                    variant="outlined"
                  ></v-text-field>
                </v-col>
                
                <v-col cols="12" md="6">
                  <v-text-field
                    v-model="email"
                    label="Email"
                    placeholder="Введите ваш email"
                    prepend-inner-icon="mdi-email"
                    :rules="[
                      v => !!v || 'Email обязателен',
                      v => /.+@.+\..+/.test(v) || 'Email должен быть корректным'
                    ]"
                    required
                    variant="outlined"
                  ></v-text-field>
                </v-col>
                
                <v-col cols="12" md="6">
                  <v-text-field
                    v-model="phone"
                    label="Телефон"
                    placeholder="Введите ваш телефон"
                    prepend-inner-icon="mdi-phone"
                    :rules="[v => !!v || 'Телефон обязателен']"
                    required
                    variant="outlined"
                  ></v-text-field>
                </v-col>
                
                <v-col cols="12" md="6">
                  <v-text-field
                    v-model="password"
                    label="Пароль"
                    placeholder="Введите пароль"
                    prepend-inner-icon="mdi-lock"
                    :append-inner-icon="showPassword ? 'mdi-eye-off' : 'mdi-eye'"
                    :type="showPassword ? 'text' : 'password'"
                    @click:append-inner="showPassword = !showPassword"
                    :rules="[
                      v => !!v || 'Пароль обязателен',
                      v => v.length >= 6 || 'Пароль должен содержать не менее 6 символов'
                    ]"
                    required
                    variant="outlined"
                  ></v-text-field>
                </v-col>
                
                <v-col cols="12" md="6">
                  <v-text-field
                    v-model="confirmPassword"
                    label="Подтверждение пароля"
                    placeholder="Подтвердите пароль"
                    prepend-inner-icon="mdi-lock-check"
                    :type="showPassword ? 'text' : 'password'"
                    :rules="[
                      v => !!v || 'Подтверждение пароля обязательно',
                      v => v === password || 'Пароли должны совпадать'
                    ]"
                    required
                    variant="outlined"
                  ></v-text-field>
                </v-col>
                
                <v-col cols="12">
                  <v-checkbox
                    v-model="agreeTerms"
                    color="primary"
                    :rules="[v => !!v || 'Вы должны согласиться с условиями']"
                    required
                  >
                    <template v-slot:label>
                      <div>
                        Я принимаю <a href="#" class="text-primary">условия использования</a> и <a href="#" class="text-primary">политику конфиденциальности</a>
                      </div>
                    </template>
                  </v-checkbox>
                </v-col>
              </v-row>
              
              <v-btn 
                color="primary" 
                block 
                size="large" 
                type="submit" 
                :loading="loading"
                class="mt-2 mb-4"
              >
                Зарегистрироваться
              </v-btn>
            </v-form>
          </v-card-text>
          
          <v-divider></v-divider>
          
          <v-card-actions class="pa-4 justify-center">
            <span class="text-medium-emphasis">Уже есть аккаунт?</span>
            <v-btn variant="text" color="primary" to="/login">
              Войти
            </v-btn>
          </v-card-actions>
        </v-card>
      </v-col>
    </v-row>
    
    <v-snackbar v-model="snackbar" :color="snackbarColor" timeout="5000">
      {{ snackbarText }}
      <template v-slot:actions>
        <v-btn variant="text" @click="snackbar = false">Закрыть</v-btn>
      </template>
    </v-snackbar>
  </v-container>
</template>

<script setup>
import { ref, inject } from 'vue'
import { useRouter } from 'vue-router'

const auth = inject('auth')
const router = useRouter()

// Состояние формы
const form = ref(null)
const name = ref('')
const email = ref('')
const phone = ref('')
const password = ref('')
const confirmPassword = ref('')
const showPassword = ref(false)
const agreeTerms = ref(false)
const loading = ref(false)

// Состояние уведомления
const snackbar = ref(false)
const snackbarText = ref('')
const snackbarColor = ref('error')

// Метод регистрации
const register = async () => {
  if (!form.value.validate()) return
  
  loading.value = true
  
  try {
    // Формируем данные для запроса
    const userData = {
      name: name.value,
      email: email.value,
      phone: phone.value,
      password: password.value
    }
    
    // Выполняем запрос на регистрацию
    await auth.register(userData)
    
    // Показываем сообщение об успехе
    snackbarColor.value = 'success'
    snackbarText.value = 'Регистрация успешно завершена! Теперь вы можете войти в систему.'
    snackbar.value = true
    
    // Перенаправляем на страницу входа
    setTimeout(() => {
      router.push('/login')
    }, 2000)
  } catch (error) {
    console.error('Ошибка регистрации:', error)
    
    // Показываем сообщение об ошибке
    snackbarColor.value = 'error'
    
    if (error.response && error.response.data && error.response.data.detail) {
      snackbarText.value = 'Ошибка: ' + error.response.data.detail
    } else {
      snackbarText.value = 'Произошла ошибка при регистрации. Пожалуйста, попробуйте снова.'
    }
    
    snackbar.value = true
  } finally {
    loading.value = false
  }
}
</script>