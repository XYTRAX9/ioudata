<template>
  <v-container fluid>
    <v-row class="mb-4">
      <v-col cols="12">
        <v-card class="px-4 py-2">
          <v-card-title class="text-h5">
            Добро пожаловать, {{ userData.name }}!
          </v-card-title>
          <v-card-subtitle>
            {{ roleText }} | Последний вход: {{ lastLoginDate }}
          </v-card-subtitle>
        </v-card>
      </v-col>
    </v-row>

    <v-row>
      <!-- Карточки с основной статистикой -->
      <v-col cols="12" md="4">
        <v-card class="dashboard-card">
          <v-card-text class="d-flex align-center">
            <v-avatar size="50" color="primary" class="mr-4">
              <v-icon size="x-large" color="white">mdi-briefcase-variant</v-icon>
            </v-avatar>
            <div>
              <div class="text-overline mb-1">Коммуникаций</div>
              <div class="text-h5">{{ statistics.communications }}</div>
            </div>
          </v-card-text>
          <v-divider></v-divider>
          <v-card-actions>
            <v-btn variant="text" to="/communications">
              Просмотреть все
              <v-icon right>mdi-arrow-right</v-icon>
            </v-btn>
          </v-card-actions>
        </v-card>
      </v-col>

      <v-col cols="12" md="4">
        <v-card class="dashboard-card">
          <v-card-text class="d-flex align-center">
            <v-avatar size="50" color="success" class="mr-4">
              <v-icon size="x-large" color="white">mdi-account-group</v-icon>
            </v-avatar>
            <div>
              <div class="text-overline mb-1">Клиентов</div>
              <div class="text-h5">{{ statistics.clients }}</div>
            </div>
          </v-card-text>
          <v-divider></v-divider>
          <v-card-actions>
            <v-btn variant="text" to="/clients">
              Просмотреть всех
              <v-icon right>mdi-arrow-right</v-icon>
            </v-btn>
          </v-card-actions>
        </v-card>
      </v-col>

      <v-col cols="12" md="4">
        <v-card class="dashboard-card">
          <v-card-text class="d-flex align-center">
            <v-avatar size="50" color="warning" class="mr-4">
              <v-icon size="x-large" color="white">mdi-clipboard-text</v-icon>
            </v-avatar>
            <div>
              <div class="text-overline mb-1">Тестов</div>
              <div class="text-h5">{{ statistics.tests }}</div>
            </div>
          </v-card-text>
          <v-divider></v-divider>
          <v-card-actions>
            <v-btn variant="text" to="/tests">
              Посмотреть тесты
              <v-icon right>mdi-arrow-right</v-icon>
            </v-btn>
          </v-card-actions>
        </v-card>
      </v-col>
    </v-row>

    <v-row class="mt-4">
      <v-col cols="12" md="8">
        <v-card>
          <v-card-title class="d-flex justify-space-between align-center">
            <span>Недавние коммуникации</span>
            <v-btn variant="text" color="primary" to="/communications">Все</v-btn>
          </v-card-title>
          
          <v-divider></v-divider>
          
          <v-card-text v-if="loading" class="text-center py-4">
            <v-progress-circular indeterminate color="primary"></v-progress-circular>
            <div class="mt-2">Загрузка данных...</div>
          </v-card-text>
          
          <template v-else>
            <v-list v-if="recentCommunications.length > 0">
              <v-list-item
                v-for="comm in recentCommunications"
                :key="comm.id"
                :to="`/communications/${comm.id}`"
              >
                <template v-slot:prepend>
                  <v-avatar size="40" :color="getStatusColor(comm.status)" class="mr-3">
                    <v-icon color="white">{{ getStatusIcon(comm.status) }}</v-icon>
                  </v-avatar>
                </template>
                
                <v-list-item-title>
                  {{ comm.client_name || 'Клиент #' + comm.client_id }}
                </v-list-item-title>
                
                <v-list-item-subtitle>
                  {{ formatDate(comm.timestamp) }} • {{ comm.call_type }} • {{ comm.status }}
                </v-list-item-subtitle>
                
                <template v-slot:append>
                  <v-chip
                    :color="comm.success_rate >= 70 ? 'success' : comm.success_rate >= 40 ? 'warning' : 'error'"
                    size="small"
                    class="ms-2"
                  >
                    {{ comm.success_rate || 0 }}%
                  </v-chip>
                </template>
              </v-list-item>
            </v-list>
            
            <v-card-text v-else class="text-center py-4">
              <v-icon size="large" color="grey">mdi-message-outline</v-icon>
              <div class="mt-2 text-medium-emphasis">Нет недавних коммуникаций</div>
            </v-card-text>
          </template>
        </v-card>
      </v-col>

      <v-col cols="12" md="4">
        <v-card>
          <v-card-title>
            Уровень стресса
            <v-tooltip location="top" text="Показывает ваш текущий уровень стресса">
              <template v-slot:activator="{ props }">
                <v-icon class="ms-2" size="small" v-bind="props">mdi-help-circle-outline</v-icon>
              </template>
            </v-tooltip>
          </v-card-title>
          
          <v-divider></v-divider>
          
          <v-card-text class="pt-4">
            <div class="text-center mb-4">
              <v-sheet class="mx-auto" max-width="300">
                <v-progress-circular
                  :model-value="userData.stress_level * 20"
                  :color="getStressColor(userData.stress_level)"
                  size="150"
                  width="15"
                >
                  <div class="text-h4">{{ userData.stress_level }}/5</div>
                </v-progress-circular>
              </v-sheet>
              
              <div class="text-subtitle-1 mt-4">{{ getStressDescription(userData.stress_level) }}</div>
            </div>
            
            <v-divider class="mb-4"></v-divider>
            
            <div class="text-subtitle-1 font-weight-bold mb-2">Группа сотрудника</div>
            <v-chip
              :color="getGroupColor(userData.group)"
              class="mb-4"
            >
              {{ getGroupName(userData.group) }}
            </v-chip>
            
            <div class="text-body-2">
              Рекомендуется регулярно проходить тесты для контроля уровня стресса и поддержания эффективности работы.
            </div>
            
            <v-btn
              color="primary"
              variant="text"
              class="mt-4"
              to="/tests"
              block
            >
              Пройти тест
            </v-btn>
          </v-card-text>
        </v-card>
        
        <v-card class="mt-4">
          <v-card-title>Быстрые действия</v-card-title>
          <v-divider></v-divider>
          <v-list>
            <v-list-item prepend-icon="mdi-account" title="Профиль" to="/profile"></v-list-item>
            <v-list-item prepend-icon="mdi-message-text" title="Перейти к чату" to="/chat"></v-list-item>
            <v-list-item prepend-icon="mdi-clipboard-text" title="Пройти тест" to="/tests"></v-list-item>
          </v-list>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup>
import { ref, onMounted, inject, computed } from 'vue'

// Инъекция API сервисов
const employeesApi = inject('employees')
const communicationsApi = inject('communications')

// Состояния
const userData = ref({
  id: 0,
  name: 'Сотрудник',
  email: '',
  group: 'normal',
  stress_level: 1,
  is_superuser: false
})

const statistics = ref({
  communications: 0,
  clients: 0,
  tests: 0
})

const recentCommunications = ref([])
const loading = ref(true)
const lastLoginDate = ref(formatDate(new Date()))

// Вычисляемое свойство для текста роли
const roleText = computed(() => {
  return userData.value.is_superuser ? 'Администратор' : 'Сотрудник'
})

// Методы
const loadDashboardData = async () => {
  loading.value = true
  
  try {
    // Загружаем данные профиля
    const profileResponse = await employeesApi.getProfile()
    userData.value = profileResponse.data
    
    // Загружаем последние коммуникации
    const commsResponse = await communicationsApi.getList({ limit: 5 })
    recentCommunications.value = commsResponse.data
    
    // Получаем статистику (в реальном проекте это был бы отдельный API-запрос)
    statistics.value = {
      communications: Math.floor(Math.random() * 100),
      clients: Math.floor(Math.random() * 50),
      tests: Math.floor(Math.random() * 20)
    }
  } catch (error) {
    console.error("Ошибка загрузки данных дашборда:", error)
  } finally {
    loading.value = false
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

// Хук жизненного цикла
onMounted(() => {
  loadDashboardData()
})
</script>

<style scoped>
.dashboard-card {
  transition: transform 0.3s ease;
}

.dashboard-card:hover {
  transform: translateY(-5px);
}
</style> 