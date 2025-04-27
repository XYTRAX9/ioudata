<template>
  <v-container fluid>
    <v-row>
      <v-col cols="12" class="mb-4">
        <h1 class="text-h4">Профиль сотрудника</h1>
      </v-col>
    </v-row>
    
    <v-row v-if="loading">
      <v-col cols="12" class="text-center">
        <v-progress-circular
          indeterminate
          color="primary"
          size="64"
        ></v-progress-circular>
        <div class="mt-4">Загрузка данных профиля...</div>
      </v-col>
    </v-row>
    
    <template v-else>
      <v-row>
        <!-- Основная информация о сотруднике -->
        <v-col cols="12" md="4">
          <v-card class="mb-4">
            <v-card-title class="d-flex justify-space-between align-center">
              <span>Персональные данные</span>
              <v-btn 
                icon 
                variant="text" 
                @click="editMode = !editMode"
                :color="editMode ? 'success' : 'secondary'"
              >
                <v-icon>{{ editMode ? 'mdi-check' : 'mdi-pencil' }}</v-icon>
              </v-btn>
            </v-card-title>
            
            <v-divider></v-divider>
            
            <v-card-text>
              <v-avatar size="120" color="primary" class="mb-4 mx-auto d-block">
                <v-icon size="64" dark>mdi-account</v-icon>
              </v-avatar>
              
              <v-form ref="form">
                <v-text-field
                  v-model="profile.name"
                  label="Имя"
                  :readonly="!editMode"
                  variant="outlined"
                  density="comfortable"
                  class="mb-2"
                ></v-text-field>
                
                <v-text-field
                  v-model="profile.email"
                  label="Email"
                  :readonly="!editMode"
                  variant="outlined"
                  density="comfortable"
                  class="mb-2"
                ></v-text-field>
                
                <template v-if="editMode">
                  <v-text-field
                    v-model="newPassword"
                    label="Новый пароль"
                    type="password"
                    hint="Оставьте пустым, если не хотите менять"
                    variant="outlined"
                    density="comfortable"
                    class="mb-2"
                  ></v-text-field>
                  
                  <v-text-field
                    v-model="confirmPassword"
                    label="Подтвердите пароль"
                    type="password"
                    :rules="[v => !newPassword || v === newPassword || 'Пароли должны совпадать']"
                    variant="outlined"
                    density="comfortable"
                    class="mb-2"
                  ></v-text-field>
                </template>
                
                <div class="d-flex justify-space-between align-center my-2">
                  <div class="text-subtitle-1">ID сотрудника</div>
                  <div class="text-body-1">{{ profile.id }}</div>
                </div>
                
                <v-divider class="my-4"></v-divider>
                
                <div class="d-flex align-center mb-2">
                  <v-chip
                    label
                    :color="profile.is_active ? 'success' : 'error'"
                    class="mr-2"
                  >
                    {{ profile.is_active ? 'Активен' : 'Неактивен' }}
                  </v-chip>
                  
                  <v-chip
                    label
                    color="info"
                    v-if="profile.is_superuser"
                  >
                    Администратор
                  </v-chip>
                </div>
                
                <v-btn 
                  v-if="editMode" 
                  color="primary" 
                  block 
                  class="mt-4"
                  @click="saveProfile"
                  :loading="saving"
                >
                  Сохранить изменения
                </v-btn>
              </v-form>
            </v-card-text>
          </v-card>
          
          <v-card>
            <v-card-title>Уровень стресса</v-card-title>
            <v-divider></v-divider>
            <v-card-text class="text-center py-4">
              <v-progress-linear
                :model-value="profile.stress_level * 20"
                :color="getStressColor(profile.stress_level)"
                height="25"
                rounded
                class="mb-3"
              >
                <template v-slot:default>
                  <strong>{{ profile.stress_level }}/5</strong>
                </template>
              </v-progress-linear>
              
              <div class="text-body-1 mb-4">
                {{ getStressDescription(profile.stress_level) }}
              </div>
              
              <v-chip :color="getGroupColor(profile.group)" class="mb-3">
                Группа: {{ getGroupName(profile.group) }}
              </v-chip>
              
              <div class="text-body-2 mt-2">
                Последнее обновление: {{ lastUpdate }}
              </div>
            </v-card-text>
          </v-card>
        </v-col>
        
        <!-- Тесты и Коммуникации -->
        <v-col cols="12" md="8">
          <v-card class="mb-4">
            <v-tabs v-model="activeTab">
              <v-tab value="tests">
                <v-icon start>mdi-clipboard-text</v-icon>
                Тесты
              </v-tab>
              <v-tab value="communications">
                <v-icon start>mdi-message-text</v-icon>
                Коммуникации
              </v-tab>
            </v-tabs>
            
            <v-divider></v-divider>
            
            <v-window v-model="activeTab">
              <!-- Вкладка с тестами -->
              <v-window-item value="tests">
                <v-card-text v-if="tests.length === 0" class="text-center py-4">
                  <v-icon size="large" color="grey">mdi-test-tube</v-icon>
                  <div class="mt-2 text-medium-emphasis">Нет пройденных тестов</div>
                  <v-btn color="primary" variant="text" class="mt-4" to="/tests">
                    Пройти тест
                  </v-btn>
                </v-card-text>
                
                <v-list v-else>
                  <v-list-item
                    v-for="(test, index) in tests"
                    :key="index"
                  >
                    <v-list-item-title>
                      {{ test.test_type }}
                    </v-list-item-title>
                    
                    <v-list-item-subtitle>
                      Результат: {{ test.score }}% • {{ formatDate(test.timestamp) }}
                    </v-list-item-subtitle>
                    
                    <template v-slot:append>
                      <v-chip
                        :color="test.score >= 70 ? 'success' : test.score >= 40 ? 'warning' : 'error'"
                        size="small"
                        class="ms-2"
                      >
                        {{ test.score }}%
                      </v-chip>
                    </template>
                  </v-list-item>
                </v-list>
              </v-window-item>
              
              <!-- Вкладка с коммуникациями -->
              <v-window-item value="communications">
                <v-card-text v-if="communications.length === 0" class="text-center py-4">
                  <v-icon size="large" color="grey">mdi-message-text-outline</v-icon>
                  <div class="mt-2 text-medium-emphasis">Нет записей о коммуникациях</div>
                </v-card-text>
                
                <v-list v-else>
                  <v-list-item
                    v-for="(comm, index) in communications"
                    :key="index"
                    :to="`/communications/${comm.id}`"
                  >
                    <template v-slot:prepend>
                      <v-avatar size="40" :color="getStatusColor(comm.status)" class="mr-3">
                        <v-icon dark>{{ getStatusIcon(comm.status) }}</v-icon>
                      </v-avatar>
                    </template>
                    
                    <v-list-item-title>
                      Клиент #{{ comm.client_id }} • {{ comm.call_type }}
                    </v-list-item-title>
                    
                    <v-list-item-subtitle>
                      {{ formatDate(comm.timestamp) }} • {{ comm.status }}
                      <template v-if="comm.duration">
                        • {{ formatDuration(comm.duration) }}
                      </template>
                    </v-list-item-subtitle>
                    
                    <template v-slot:append>
                      <v-chip
                        v-if="comm.success_rate !== null"
                        :color="comm.success_rate >= 70 ? 'success' : comm.success_rate >= 40 ? 'warning' : 'error'"
                        size="small"
                        class="ms-2"
                      >
                        {{ comm.success_rate }}%
                      </v-chip>
                    </template>
                  </v-list-item>
                </v-list>
              </v-window-item>
            </v-window>
          </v-card>
        </v-col>
      </v-row>
    </template>
    
    <!-- Уведомление -->
    <v-snackbar
      v-model="snackbar"
      :color="snackbarColor"
      :timeout="3000"
    >
      {{ snackbarText }}
      <template v-slot:actions>
        <v-btn variant="text" @click="snackbar = false">Закрыть</v-btn>
      </template>
    </v-snackbar>
  </v-container>
</template>

<script setup>
import { ref, onMounted, inject, computed } from 'vue'

// Инъекция API сервисов
const employeesApi = inject('employees')
const communicationsApi = inject('communications')

// Состояния
const profile = ref({
  id: 0,
  name: '',
  email: '',
  is_active: true,
  is_superuser: false,
  group: 'normal',
  stress_level: 1
})

const newPassword = ref('')
const confirmPassword = ref('')
const tests = ref([])
const communications = ref([])
const loading = ref(true)
const saving = ref(false)
const editMode = ref(false)
const activeTab = ref('tests')
const form = ref(null)

// Состояние уведомления
const snackbar = ref(false)
const snackbarText = ref('')
const snackbarColor = ref('success')

// Вычисляемые свойства
const lastUpdate = computed(() => {
  return formatDate(new Date())
})

// Загрузка данных профиля
const loadProfileData = async () => {
  loading.value = true
  
  try {
    // Загружаем данные профиля
    const response = await employeesApi.getProfile()
    profile.value = response.data
    
    // Загружаем тесты и коммуникации
    // В реальном приложении здесь были бы отдельные запросы
    // Имитация данных
    tests.value = [
      { test_type: 'Психологический тест', score: 85, timestamp: new Date() - 86400000 * 3 },
      { test_type: 'Тест на коммуникативность', score: 92, timestamp: new Date() - 86400000 * 10 },
      { test_type: 'Оценка стрессоустойчивости', score: 78, timestamp: new Date() - 86400000 * 20 }
    ]
    
    communications.value = [
      { id: 1, client_id: 101, call_type: 'Телефон', status: 'completed', timestamp: new Date() - 86400000, duration: 420, success_rate: 95 },
      { id: 2, client_id: 102, call_type: 'Чат', status: 'in_progress', timestamp: new Date() - 86400000 * 2, duration: null, success_rate: null },
      { id: 3, client_id: 103, call_type: 'Email', status: 'canceled', timestamp: new Date() - 86400000 * 5, duration: 180, success_rate: 40 }
    ]
  } catch (error) {
    console.error('Ошибка загрузки данных профиля:', error)
    
    snackbarColor.value = 'error'
    snackbarText.value = 'Ошибка загрузки данных профиля'
    snackbar.value = true
  } finally {
    loading.value = false
  }
}

// Сохранение профиля
const saveProfile = async () => {
  if (!form.value.validate()) return
  
  saving.value = true
  
  try {
    // Здесь был бы запрос к API для обновления профиля
    
    // Имитация сохранения профиля
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    editMode.value = false
    newPassword.value = ''
    confirmPassword.value = ''
    
    snackbarColor.value = 'success'
    snackbarText.value = 'Профиль успешно обновлен'
    snackbar.value = true
  } catch (error) {
    console.error('Ошибка сохранения профиля:', error)
    
    snackbarColor.value = 'error'
    snackbarText.value = 'Ошибка сохранения профиля'
    snackbar.value = true
  } finally {
    saving.value = false
  }
}

// Вспомогательные функции
function formatDate(dateString) {
  const date = dateString instanceof Date ? dateString : new Date(dateString)
  return date.toLocaleDateString('ru-RU', { 
    day: '2-digit', 
    month: '2-digit', 
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

function formatDuration(seconds) {
  const minutes = Math.floor(seconds / 60)
  const secs = seconds % 60
  return `${minutes}:${secs.toString().padStart(2, '0')}`
}

function getStressColor(level) {
  const colorMap = {
    1: 'success',
    2: 'light-green',
    3: 'warning',
    4: 'orange',
    5: 'error'
  }
  return colorMap[level] || 'grey'
}

function getStressDescription(level) {
  const descMap = {
    1: 'Нормальный уровень стресса',
    2: 'Незначительный стресс',
    3: 'Средний уровень стресса',
    4: 'Повышенный уровень стресса',
    5: 'Критический уровень стресса'
  }
  return descMap[level] || 'Неизвестный уровень стресса'
}

function getGroupName(group) {
  const groupMap = {
    'normal': 'Норма',
    'slightly_below': 'Чуть ниже нормы',
    'significantly_below': 'Значительно ниже нормы'
  }
  return groupMap[group] || 'Неизвестная группа'
}

function getGroupColor(group) {
  const groupColorMap = {
    'normal': 'success',
    'slightly_below': 'warning',
    'significantly_below': 'error'
  }
  return groupColorMap[group] || 'grey'
}

function getStatusColor(status) {
  const statusMap = {
    'completed': 'success',
    'in_progress': 'info',
    'scheduled': 'primary',
    'canceled': 'error',
    'pending': 'warning'
  }
  return statusMap[status] || 'grey'
}

function getStatusIcon(status) {
  const iconMap = {
    'completed': 'mdi-check-circle',
    'in_progress': 'mdi-progress-clock',
    'scheduled': 'mdi-calendar-clock',
    'canceled': 'mdi-cancel',
    'pending': 'mdi-clock-outline'
  }
  return iconMap[status] || 'mdi-help-circle'
}

// Хук жизненного цикла
onMounted(() => {
  loadProfileData()
})
</script>