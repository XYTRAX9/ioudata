<template>
  <v-container fluid>
    <v-row>
      <v-col cols="12" class="mb-4">
        <h1 class="text-h4">Коммуникации</h1>
        <p class="text-subtitle-1 mt-2">
          История взаимодействий с клиентами
        </p>
      </v-col>
    </v-row>
    
    <!-- Фильтры и поиск -->
    <v-row>
      <v-col cols="12">
        <v-card class="mb-4">
          <v-card-text>
            <v-row>
              <v-col cols="12" sm="4">
                <v-text-field
                  v-model="searchQuery"
                  label="Поиск"
                  placeholder="Поиск по имени клиента, ID..."
                  prepend-inner-icon="mdi-magnify"
                  variant="outlined"
                  density="comfortable"
                  hide-details
                  class="mb-3 mb-sm-0"
                  @update:model-value="applyFilters"
                ></v-text-field>
              </v-col>
              
              <v-col cols="6" sm="2">
                <v-select
                  v-model="filters.status"
                  label="Статус"
                  :items="statusOptions"
                  variant="outlined"
                  density="comfortable"
                  hide-details
                  class="mb-3 mb-sm-0"
                  @update:model-value="applyFilters"
                ></v-select>
              </v-col>
              
              <v-col cols="6" sm="2">
                <v-select
                  v-model="filters.type"
                  label="Тип"
                  :items="typeOptions"
                  variant="outlined"
                  density="comfortable"
                  hide-details
                  class="mb-3 mb-sm-0"
                  @update:model-value="applyFilters"
                ></v-select>
              </v-col>
              
              <v-col cols="6" sm="2">
                <v-select
                  v-model="filters.date"
                  label="Период"
                  :items="dateOptions"
                  variant="outlined"
                  density="comfortable"
                  hide-details
                  @update:model-value="applyFilters"
                ></v-select>
              </v-col>
              
              <v-col cols="6" sm="2" class="d-flex justify-end align-center">
                <v-btn
                  color="secondary"
                  variant="text"
                  @click="resetFilters"
                >
                  Сбросить
                </v-btn>
                
                <v-btn
                  color="primary"
                  class="ms-2"
                  prepend-icon="mdi-export"
                  @click="exportData"
                >
                  Экспорт
                </v-btn>
              </v-col>
            </v-row>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
    
    <!-- Таблица коммуникаций -->
    <v-row>
      <v-col cols="12">
        <v-card>
          <v-card-text v-if="loading" class="text-center py-5">
            <v-progress-circular indeterminate color="primary" size="64"></v-progress-circular>
            <div class="mt-4">Загрузка данных...</div>
          </v-card-text>
          
          <template v-else>
            <v-table v-if="filteredCommunications.length > 0">
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Клиент</th>
                  <th>Тип</th>
                  <th>Дата</th>
                  <th>Статус</th>
                  <th>Успешность</th>
                  <th>Действия</th>
                </tr>
              </thead>
              <tbody>
                <tr
                  v-for="comm in paginatedCommunications"
                  :key="comm.id"
                  class="communication-row"
                  @click="viewCommunication(comm.id)"
                >
                  <td>{{ comm.id }}</td>
                  <td>
                    <div class="d-flex align-center">
                      <v-avatar size="32" color="primary" class="me-2 text-white">
                        {{ getInitials(comm.client_name) }}
                      </v-avatar>
                      {{ comm.client_name }}
                    </div>
                  </td>
                  <td>
                    <v-chip
                      size="small"
                      :color="getTypeColor(comm.call_type)"
                      class="text-capitalize"
                    >
                      {{ comm.call_type }}
                    </v-chip>
                  </td>
                  <td>{{ formatDate(comm.timestamp) }}</td>
                  <td>
                    <v-chip
                      size="small"
                      :color="getStatusColor(comm.status)"
                    >
                      {{ getStatusText(comm.status) }}
                    </v-chip>
                  </td>
                  <td>
                    <v-progress-linear
                      :model-value="comm.success_rate"
                      height="8"
                      rounded
                      :color="getSuccessColor(comm.success_rate)"
                    ></v-progress-linear>
                    <div class="text-caption text-center mt-1">
                      {{ comm.success_rate || 0 }}%
                    </div>
                  </td>
                  <td>
                    <v-btn
                      icon
                      size="small"
                      variant="text"
                      @click.stop="viewCommunication(comm.id)"
                    >
                      <v-icon>mdi-eye</v-icon>
                    </v-btn>
                    
                    <v-btn
                      icon
                      size="small"
                      variant="text"
                      @click.stop="exportCommunication(comm.id)"
                    >
                      <v-icon>mdi-download</v-icon>
                    </v-btn>
                  </td>
                </tr>
              </tbody>
            </v-table>
            
            <div v-else class="text-center py-5">
              <v-icon size="64" color="grey">mdi-message-text-outline</v-icon>
              <h3 class="text-h5 mt-4">Нет данных</h3>
              <p class="text-body-1 mt-2">Коммуникации не найдены</p>
            </div>
          </template>
          
          <!-- Пагинация -->
          <v-divider v-if="filteredCommunications.length > 0"></v-divider>
          
          <v-card-actions v-if="filteredCommunications.length > 0">
            <span class="text-caption text-medium-emphasis">
              {{ startIndex + 1 }}-{{ endIndex }} из {{ filteredCommunications.length }} записей
            </span>
            
            <v-spacer></v-spacer>
            
            <v-pagination
              v-model="pagination.page"
              :length="pageCount"
              :total-visible="5"
            ></v-pagination>
            
            <v-spacer></v-spacer>
            
            <v-select
              v-model="pagination.itemsPerPage"
              label="Строк на странице"
              :items="[5, 10, 25, 50]"
              variant="outlined"
              density="compact"
              hide-details
              class="pagination-select"
            ></v-select>
          </v-card-actions>
        </v-card>
      </v-col>
    </v-row>
    
    <!-- Статистика -->
    <v-row class="mt-4">
      <v-col cols="12" md="4">
        <v-card>
          <v-card-title>Распределение по типам</v-card-title>
          <v-card-text>
            <v-list density="compact">
              <v-list-item
                v-for="(count, type) in stats.typeCounts"
                :key="type"
              >
                <template v-slot:prepend>
                  <v-avatar
                    size="32"
                    :color="getTypeColor(type)"
                    class="text-white"
                  >
                    <v-icon size="small">{{ getTypeIcon(type) }}</v-icon>
                  </v-avatar>
                </template>
                <v-list-item-title>{{ type }}</v-list-item-title>
                <template v-slot:append>
                  <div class="d-flex align-center">
                    <strong>{{ count }}</strong>
                    <div class="text-caption text-medium-emphasis ms-2">
                      ({{ Math.round(count / communications.length * 100) }}%)
                    </div>
                  </div>
                </template>
              </v-list-item>
            </v-list>
          </v-card-text>
        </v-card>
      </v-col>
      
      <v-col cols="12" md="4">
        <v-card>
          <v-card-title>Распределение по статусам</v-card-title>
          <v-card-text>
            <v-list density="compact">
              <v-list-item
                v-for="(count, status) in stats.statusCounts"
                :key="status"
              >
                <template v-slot:prepend>
                  <v-avatar
                    size="32"
                    :color="getStatusColor(status)"
                    class="text-white"
                  >
                    <v-icon size="small">{{ getStatusIcon(status) }}</v-icon>
                  </v-avatar>
                </template>
                <v-list-item-title>{{ getStatusText(status) }}</v-list-item-title>
                <template v-slot:append>
                  <div class="d-flex align-center">
                    <strong>{{ count }}</strong>
                    <div class="text-caption text-medium-emphasis ms-2">
                      ({{ Math.round(count / communications.length * 100) }}%)
                    </div>
                  </div>
                </template>
              </v-list-item>
            </v-list>
          </v-card-text>
        </v-card>
      </v-col>
      
      <v-col cols="12" md="4">
        <v-card>
          <v-card-title>Средние показатели</v-card-title>
          <v-card-text>
            <v-list density="compact">
              <v-list-item>
                <template v-slot:prepend>
                  <v-avatar
                    size="32"
                    color="primary"
                    class="text-white"
                  >
                    <v-icon size="small">mdi-percent</v-icon>
                  </v-avatar>
                </template>
                <v-list-item-title>Успешность</v-list-item-title>
                <template v-slot:append>
                  <div class="d-flex align-center">
                    <strong>{{ stats.averageSuccessRate.toFixed(1) }}%</strong>
                  </div>
                </template>
              </v-list-item>
              
              <v-list-item>
                <template v-slot:prepend>
                  <v-avatar
                    size="32"
                    color="primary"
                    class="text-white"
                  >
                    <v-icon size="small">mdi-clock</v-icon>
                  </v-avatar>
                </template>
                <v-list-item-title>Длительность</v-list-item-title>
                <template v-slot:append>
                  <div class="d-flex align-center">
                    <strong>{{ formatDuration(stats.averageDuration) }}</strong>
                  </div>
                </template>
              </v-list-item>
              
              <v-list-item>
                <template v-slot:prepend>
                  <v-avatar
                    size="32"
                    color="primary"
                    class="text-white"
                  >
                    <v-icon size="small">mdi-account-multiple</v-icon>
                  </v-avatar>
                </template>
                <v-list-item-title>Клиентов</v-list-item-title>
                <template v-slot:append>
                  <div class="d-flex align-center">
                    <strong>{{ stats.uniqueClients }}</strong>
                  </div>
                </template>
              </v-list-item>
            </v-list>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
    
    <!-- Уведомления -->
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
import { ref, computed, onMounted, watch, inject } from 'vue'
import { useRouter } from 'vue-router'

// Инъекция API сервисов
const communicationsApi = inject('communications')
const router = useRouter()

// Состояния
const loading = ref(true)
const communications = ref([])
const searchQuery = ref('')
const snackbar = ref(false)
const snackbarText = ref('')
const snackbarColor = ref('success')

// Фильтры
const filters = ref({
  status: 'all',
  type: 'all',
  date: 'all'
})

// Пагинация
const pagination = ref({
  page: 1,
  itemsPerPage: 10
})

// Опции для фильтров
const statusOptions = [
  { title: 'Все статусы', value: 'all' },
  { title: 'Завершен', value: 'completed' },
  { title: 'В процессе', value: 'in_progress' },
  { title: 'Запланирован', value: 'scheduled' },
  { title: 'Отменен', value: 'canceled' },
  { title: 'Ожидает', value: 'pending' }
]

const typeOptions = [
  { title: 'Все типы', value: 'all' },
  { title: 'Чат', value: 'chat' }
]

const dateOptions = [
  { title: 'Все время', value: 'all' },
  { title: 'Сегодня', value: 'today' },
  { title: 'Вчера', value: 'yesterday' },
  { title: 'Последние 7 дней', value: 'week' },
  { title: 'Последние 30 дней', value: 'month' }
]

// Получение данных о коммуникациях
const loadCommunications = async () => {
  loading.value = true
  
  try {
    // В реальном приложении здесь был бы запрос к API
    // const response = await communicationsApi.getList()
    // communications.value = response.data
    
    // Имитация загрузки данных
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    // Тестовые данные
    communications.value = [
      {
        id: 2,
        client_id: 102,
        client_name: 'Мария Иванова',
        call_type: 'chat',
        status: 'in_progress',
        timestamp: new Date() - 86400000 * 0.5,
        duration: null,
        success_rate: null,
        details: {
          messages: [
            { sender: 'employee', text: 'Добрый день! Чем я могу вам помочь?', timestamp: new Date(new Date() - 86400000 * 0.5).toISOString() },
            { sender: 'client', text: 'Здравствуйте! У меня возникла проблема с оплатой', timestamp: new Date(new Date() - 86400000 * 0.49).toISOString() },
            { sender: 'employee', text: 'Сожалею о возникшей проблеме. Расскажите, пожалуйста, подробнее о ситуации.', timestamp: new Date(new Date() - 86400000 * 0.48).toISOString() },
            { sender: 'client', text: 'Я пытался оплатить услугу, но платеж не прошел, а деньги списались', timestamp: new Date(new Date() - 86400000 * 0.47).toISOString() },
            { sender: 'employee', text: 'Давайте проверим статус платежа. Не могли бы вы сообщить номер заказа или дату операции?', timestamp: new Date(new Date() - 86400000 * 0.46).toISOString() }
          ]
        }
      },
      {
        id: 6,
        client_id: 105,
        client_name: 'Ольга Морозова',
        call_type: 'chat',
        status: 'completed',
        timestamp: new Date() - 86400000 * 2,
        duration: 600,
        success_rate: 80,
        details: {
          messages: [
            { sender: 'employee', text: 'Добрый день! Чем я могу вам помочь?', timestamp: new Date(new Date() - 86400000 * 2.1).toISOString() },
            { sender: 'client', text: 'Добрый день! Хочу уточнить информацию о тарифах', timestamp: new Date(new Date() - 86400000 * 2.09).toISOString() },
            { sender: 'employee', text: 'Конечно! Какой именно тариф вас интересует?', timestamp: new Date(new Date() - 86400000 * 2.08).toISOString() },
            { sender: 'client', text: 'Мне нужен тариф с большим объемом интернета', timestamp: new Date(new Date() - 86400000 * 2.07).toISOString() },
            { sender: 'employee', text: 'У нас есть несколько тарифов с большим объемом интернета. Могу порекомендовать тариф "Безлимит", который включает неограниченный интернет-трафик.', timestamp: new Date(new Date() - 86400000 * 2.06).toISOString() },
            { sender: 'client', text: 'Отлично! А сколько он стоит?', timestamp: new Date(new Date() - 86400000 * 2.05).toISOString() },
            { sender: 'employee', text: 'Тариф "Безлимит" стоит 890 рублей в месяц. В него также входит 600 минут звонков и 100 SMS.', timestamp: new Date(new Date() - 86400000 * 2.04).toISOString() },
            { sender: 'client', text: 'Спасибо за информацию! Я подумаю и сообщу о своем решении.', timestamp: new Date(new Date() - 86400000 * 2.03).toISOString() },
            { sender: 'employee', text: 'Буду рад помочь! Если у вас возникнут дополнительные вопросы, обращайтесь.', timestamp: new Date(new Date() - 86400000 * 2.02).toISOString() }
          ]
        }
      },
      {
        id: 10,
        client_id: 109,
        client_name: 'Анна Попова',
        call_type: 'chat',
        status: 'in_progress',
        timestamp: new Date() - 86400000 * 0.2,
        duration: null,
        success_rate: null,
        details: {
          messages: [
            { sender: 'employee', text: 'Добрый день! Чем я могу вам помочь?', timestamp: new Date(new Date() - 86400000 * 0.2).toISOString() },
            { sender: 'client', text: 'Здравствуйте! Мне нужна помощь с настройкой оборудования', timestamp: new Date(new Date() - 86400000 * 0.19).toISOString() },
            { sender: 'employee', text: 'Конечно, я помогу вам. О каком устройстве идет речь?', timestamp: new Date(new Date() - 86400000 * 0.18).toISOString() },
            { sender: 'client', text: 'У меня новый роутер, и я не могу подключиться к интернету', timestamp: new Date(new Date() - 86400000 * 0.17).toISOString() }
          ]
        }
      },
      {
        id: 11,
        client_id: 110,
        client_name: 'Константин Васильев',
        call_type: 'chat',
        status: 'completed',
        timestamp: new Date() - 86400000 * 1.5,
        duration: 450,
        success_rate: 85,
        details: {
          messages: [
            { sender: 'employee', text: 'Добрый день! Чем я могу вам помочь?', timestamp: new Date(new Date() - 86400000 * 1.6).toISOString() },
            { sender: 'client', text: 'Здравствуйте! Я хотел бы узнать о возможности расторжения договора', timestamp: new Date(new Date() - 86400000 * 1.59).toISOString() },
            { sender: 'employee', text: 'Я понимаю вашу ситуацию. Для расторжения договора необходимо подать заявление. Могу я узнать, по какой причине вы хотите расторгнуть договор?', timestamp: new Date(new Date() - 86400000 * 1.58).toISOString() },
            { sender: 'client', text: 'Я переезжаю в другой город', timestamp: new Date(new Date() - 86400000 * 1.57).toISOString() },
            { sender: 'employee', text: 'В таком случае, вам нужно будет предоставить документы, подтверждающие переезд. Вы можете подать заявление в любом нашем офисе или онлайн через личный кабинет.', timestamp: new Date(new Date() - 86400000 * 1.56).toISOString() },
            { sender: 'client', text: 'Спасибо за информацию! Я подам заявление через личный кабинет.', timestamp: new Date(new Date() - 86400000 * 1.55).toISOString() },
            { sender: 'employee', text: 'Отлично! Если у вас возникнут вопросы в процессе заполнения заявления, обращайтесь. Также хочу отметить, что в нашей компании есть специальные предложения для клиентов, которые переезжают.', timestamp: new Date(new Date() - 86400000 * 1.54).toISOString() },
            { sender: 'client', text: 'Спасибо за помощь!', timestamp: new Date(new Date() - 86400000 * 1.53).toISOString() },
            { sender: 'employee', text: 'Всегда рады помочь! Хорошего вам дня!', timestamp: new Date(new Date() - 86400000 * 1.52).toISOString() }
          ]
        }
      },
      {
        id: 12,
        client_id: 111,
        client_name: 'Елена Зайцева',
        call_type: 'chat',
        status: 'completed',
        timestamp: new Date() - 86400000 * 3.5,
        duration: 380,
        success_rate: 92,
        details: {
          messages: [
            { sender: 'employee', text: 'Добрый день! Чем я могу вам помочь?', timestamp: new Date(new Date() - 86400000 * 3.6).toISOString() },
            { sender: 'client', text: 'Здравствуйте! У меня вопрос по поводу подключения дополнительных услуг', timestamp: new Date(new Date() - 86400000 * 3.59).toISOString() },
            { sender: 'employee', text: 'Я с радостью помогу вам разобраться с дополнительными услугами. Какие именно услуги вас интересуют?', timestamp: new Date(new Date() - 86400000 * 3.58).toISOString() },
            { sender: 'client', text: 'Мне нужен антивирус и родительский контроль', timestamp: new Date(new Date() - 86400000 * 3.57).toISOString() },
            { sender: 'employee', text: 'У нас есть отличные предложения по антивирусной защите и родительскому контролю. Я могу предложить вам пакет "Безопасный интернет", который включает обе эти услуги за 350 рублей в месяц.', timestamp: new Date(new Date() - 86400000 * 3.56).toISOString() },
            { sender: 'client', text: 'Это звучит отлично! Как я могу подключить этот пакет?', timestamp: new Date(new Date() - 86400000 * 3.55).toISOString() },
            { sender: 'employee', text: 'Я могу подключить его прямо сейчас. Нужно только подтверждение с вашей стороны.', timestamp: new Date(new Date() - 86400000 * 3.54).toISOString() },
            { sender: 'client', text: 'Да, я согласна на подключение пакета "Безопасный интернет"', timestamp: new Date(new Date() - 86400000 * 3.53).toISOString() },
            { sender: 'employee', text: 'Отлично! Я подключил пакет "Безопасный интернет" к вашему аккаунту. Услуга будет активна в течение 15 минут. Для установки антивируса и настройки родительского контроля вам нужно будет зайти в личный кабинет и выбрать соответствующие опции.', timestamp: new Date(new Date() - 86400000 * 3.52).toISOString() },
            { sender: 'client', text: 'Большое спасибо за помощь!', timestamp: new Date(new Date() - 86400000 * 3.51).toISOString() },
            { sender: 'employee', text: 'Всегда рады помочь! Если у вас возникнут вопросы по настройке или использованию этих услуг, обращайтесь.', timestamp: new Date(new Date() - 86400000 * 3.5).toISOString() }
          ]
        }
      }
    ]
    
    // Сбрасываем страницу пагинации при загрузке новых данных
    pagination.value.page = 1
  } catch (error) {
    console.error('Ошибка загрузки коммуникаций:', error)
    
    snackbarColor.value = 'error'
    snackbarText.value = 'Ошибка загрузки данных'
    snackbar.value = true
  } finally {
    loading.value = false
  }
}

// Фильтрация коммуникаций
const filteredCommunications = computed(() => {
  let result = [...communications.value]
  
  // Фильтр по статусу
  if (filters.value.status !== 'all') {
    result = result.filter(c => c.status === filters.value.status)
  }
  
  // Фильтр по типу
  if (filters.value.type !== 'all') {
    result = result.filter(c => c.call_type === filters.value.type)
  }
  
  // Фильтр по дате
  const now = new Date()
  const today = new Date(now.getFullYear(), now.getMonth(), now.getDate())
  const yesterday = new Date(today)
  yesterday.setDate(yesterday.getDate() - 1)
  const week = new Date(today)
  week.setDate(week.getDate() - 7)
  const month = new Date(today)
  month.setDate(month.getDate() - 30)
  
  if (filters.value.date !== 'all') {
    switch (filters.value.date) {
      case 'today':
        result = result.filter(c => new Date(c.timestamp) >= today)
        break
      case 'yesterday':
        result = result.filter(c => {
          const date = new Date(c.timestamp)
          return date >= yesterday && date < today
        })
        break
      case 'week':
        result = result.filter(c => new Date(c.timestamp) >= week)
        break
      case 'month':
        result = result.filter(c => new Date(c.timestamp) >= month)
        break
    }
  }
  
  // Поиск
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    result = result.filter(c => 
      c.client_name.toLowerCase().includes(query) || 
      c.client_id.toString().includes(query) ||
      c.id.toString().includes(query)
    )
  }
  
  return result
})

// Пагинация
const pageCount = computed(() => {
  return Math.ceil(filteredCommunications.value.length / pagination.value.itemsPerPage)
})

const startIndex = computed(() => {
  return (pagination.value.page - 1) * pagination.value.itemsPerPage
})

const endIndex = computed(() => {
  const end = startIndex.value + pagination.value.itemsPerPage
  return end > filteredCommunications.value.length 
    ? filteredCommunications.value.length 
    : end
})

const paginatedCommunications = computed(() => {
  return filteredCommunications.value.slice(startIndex.value, endIndex.value)
})

// Статистика
const stats = computed(() => {
  const typeCounts = {}
  const statusCounts = {}
  let totalSuccessRate = 0
  let successRateCount = 0
  let totalDuration = 0
  let durationCount = 0
  const clientIds = new Set()
  
  communications.value.forEach(comm => {
    // Подсчет по типам
    typeCounts[comm.call_type] = (typeCounts[comm.call_type] || 0) + 1
    
    // Подсчет по статусам
    statusCounts[comm.status] = (statusCounts[comm.status] || 0) + 1
    
    // Расчет среднего показателя успешности
    if (comm.success_rate !== null && comm.success_rate !== undefined) {
      totalSuccessRate += comm.success_rate
      successRateCount++
    }
    
    // Расчет средней длительности
    if (comm.duration) {
      totalDuration += comm.duration
      durationCount++
    }
    
    // Подсчет уникальных клиентов
    clientIds.add(comm.client_id)
  })
  
  return {
    typeCounts,
    statusCounts,
    averageSuccessRate: successRateCount > 0 ? totalSuccessRate / successRateCount : 0,
    averageDuration: durationCount > 0 ? totalDuration / durationCount : 0,
    uniqueClients: clientIds.size
  }
})

// Методы
const applyFilters = () => {
  pagination.value.page = 1 // Сбрасываем страницу при применении фильтров
}

const resetFilters = () => {
  searchQuery.value = ''
  filters.value = {
    status: 'all',
    type: 'all',
    date: 'all'
  }
  pagination.value.page = 1
}

const viewCommunication = (id) => {
  router.push(`/communications/${id}`)
}

const exportCommunication = (id) => {
  snackbarColor.value = 'success'
  snackbarText.value = 'Экспорт коммуникации #' + id + ' начат'
  snackbar.value = true
}

const exportData = () => {
  snackbarColor.value = 'success'
  snackbarText.value = 'Экспорт данных начат'
  snackbar.value = true
}

// Вспомогательные функции
function formatDate(timestamp) {
  const date = new Date(timestamp)
  return date.toLocaleDateString('ru-RU', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

function formatDuration(seconds) {
  if (!seconds) return '0:00'
  const minutes = Math.floor(seconds / 60)
  const secs = seconds % 60
  return `${minutes}:${secs.toString().padStart(2, '0')}`
}

function getInitials(name) {
  if (!name) return ''
  return name.split(' ').map(n => n[0]).join('').toUpperCase()
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

function getStatusText(status) {
  const textMap = {
    'completed': 'Завершен',
    'in_progress': 'В процессе',
    'scheduled': 'Запланирован',
    'canceled': 'Отменен',
    'pending': 'Ожидает'
  }
  return textMap[status] || status
}

function getTypeColor(type) {
  const typeMap = {
    'phone': 'indigo',
    'chat': 'cyan',
    'email': 'amber',
    'video': 'deep-purple'
  }
  return typeMap[type] || 'grey'
}

function getTypeIcon(type) {
  const iconMap = {
    'phone': 'mdi-phone',
    'chat': 'mdi-chat',
    'email': 'mdi-email',
    'video': 'mdi-video'
  }
  return iconMap[type] || 'mdi-help-circle'
}

function getSuccessColor(rate) {
  if (rate === null || rate === undefined) return 'grey'
  if (rate >= 80) return 'success'
  if (rate >= 60) return 'warning'
  return 'error'
}

// Инициализация
onMounted(() => {
  loadCommunications()
})

// Слежение за изменениями
watch(pagination, () => {
  // Можно добавить логику для подгрузки данных с сервера при изменении страницы
}, { deep: true })
</script>

<style scoped>
.communication-row {
  cursor: pointer;
}

.communication-row:hover {
  background-color: rgb(var(--v-theme-surface-variant));
}

.pagination-select {
  max-width: 150px;
}
</style> 