<template>
  <v-container fluid class="pa-0 h-100">
    <v-row class="h-100 ma-0">
      <!-- Список контактов для операторов -->
      <v-col
        v-if="isOperator"
        cols="12"
        sm="4"
        md="3"
        class="h-100 pa-0 border-end"
      >
        <v-card class="h-100 rounded-0">
          <v-card-title class="px-4 py-3 d-flex align-center">
            <span>Клиенты</span>
            <v-spacer></v-spacer>
            <v-badge
              :content="onlineClients"
              color="success"
              offset-x="12"
              offset-y="12"
            >
              <v-icon>mdi-account-multiple</v-icon>
            </v-badge>
          </v-card-title>
          
          <v-divider></v-divider>
          
          <v-card-text class="px-0 py-0">
            <v-list>
              <v-list-subheader>Активные чаты</v-list-subheader>
              
              <v-list-item
                v-for="client in filteredClients"
                :key="client.id"
                :active="selectedClient.id === client.id"
                @click="selectClient(client)"
                :class="{ 'bg-secondary-subtle': selectedClient.id === client.id }"
              >
                <template v-slot:prepend>
                  <v-badge
                    :color="client.online ? 'success' : 'grey'"
                    dot
                    location="bottom right"
                    offset-x="3"
                    offset-y="3"
                  >
                    <v-avatar size="40" color="primary" class="text-white">
                      {{ client.name.charAt(0).toUpperCase() }}
                    </v-avatar>
                  </v-badge>
                </template>
                
                <v-list-item-title>{{ client.name }}</v-list-item-title>
                <v-list-item-subtitle class="text-truncate">
                  {{ client.lastMessage }}
                </v-list-item-subtitle>
                
                <template v-slot:append>
                  <div class="d-flex flex-column align-end">
                    <div class="text-caption">{{ formatTime(client.lastTime) }}</div>
                    <v-badge
                      v-if="client.unread > 0"
                      :content="client.unread"
                      color="error"
                      class="mt-1"
                    ></v-badge>
                  </div>
                </template>
              </v-list-item>
              
              <v-divider v-if="filteredClients.length > 0"></v-divider>
              
              <v-list-item
                v-if="filteredClients.length === 0"
                class="text-center"
              >
                <v-list-item-subtitle>
                  Нет активных чатов
                </v-list-item-subtitle>
              </v-list-item>
            </v-list>
          </v-card-text>
        </v-card>
      </v-col>
      
      <!-- Область чата -->
      <v-col cols class="h-100 pa-0 d-flex flex-column">
        <v-card class="h-100 rounded-0 d-flex flex-column">
          <!-- Заголовок чата -->
          <v-card-title class="px-4 py-3 d-flex align-center border-bottom">
            <template v-if="isOperator">
              <v-avatar size="36" color="primary" class="text-white me-3" v-if="selectedClient.id">
                {{ selectedClient.name.charAt(0).toUpperCase() }}
              </v-avatar>
              <div>
                <div>{{ selectedClient.id ? selectedClient.name : 'Выберите клиента' }}</div>
                <div class="text-caption" v-if="selectedClient.online">
                  <v-icon size="small" color="success">mdi-circle</v-icon> Онлайн
                </div>
              </div>
            </template>
            <template v-else>
              <v-avatar size="36" color="primary" class="text-white me-3">
                <v-icon>mdi-headset</v-icon>
              </v-avatar>
              <div>
                <div>{{ operatorInfo.name || 'Оператор' }}</div>
                <div class="text-caption">
                  <v-icon size="small" :color="connectionStatus === 'connected' ? 'success' : 'warning'">
                    mdi-circle
                  </v-icon>
                  {{ connectionStatus === 'connected' ? 'В сети' : 'Подключение...' }}
                </div>
              </div>
            </template>
            
            <v-spacer></v-spacer>
            
            <v-btn icon variant="text" @click="showInfo = !showInfo">
              <v-icon>mdi-information-outline</v-icon>
            </v-btn>
          </v-card-title>
          
          <!-- Область сообщений -->
          <v-card-text class="flex-grow-1 overflow-auto pa-4" ref="messagesContainer">
            <div v-if="!isOperator && !operatorInfo.id" class="text-center my-5">
              <v-icon size="64" color="primary">mdi-headset</v-icon>
              <h3 class="mt-3">Ожидание оператора</h3>
              <p class="text-body-1 mt-2">Пожалуйста, подождите, оператор скоро подключится</p>
              <v-progress-linear
                indeterminate
                color="primary"
                class="mt-4"
              ></v-progress-linear>
            </div>
            
            <div v-else-if="isOperator && !selectedClient.id" class="text-center my-5">
              <v-icon size="64" color="primary">mdi-message-text-outline</v-icon>
              <h3 class="mt-3">Выберите клиента</h3>
              <p class="text-body-1 mt-2">Выберите клиента из списка слева для начала общения</p>
            </div>
            
            <template v-else>
              <div v-if="messages.length === 0" class="text-center my-5">
                <v-icon size="64" color="grey">mdi-message-text-outline</v-icon>
                <h3 class="mt-3">Начните общение</h3>
                <p class="text-body-1 mt-2">
                  {{ isOperator ? 'Напишите сообщение клиенту' : 'Напишите свой вопрос' }}
                </p>
              </div>
              
              <div v-else>
                <div
                  v-for="(message, index) in messages"
                  :key="index"
                  class="mb-4"
                >
                  <div
                    class="d-flex"
                    :class="message.isUser ? 'justify-end' : 'justify-start'"
                  >
                    <div
                      class="message rounded-lg pa-3"
                      :class="message.isUser ? 'user-message' : 'other-message'"
                      style="max-width: 70%;"
                    >
                      <div class="text-body-1">{{ message.text }}</div>
                      <div class="text-caption text-right mt-1">
                        {{ formatTime(message.timestamp) }}
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </template>
          </v-card-text>
          
          <!-- Поле ввода сообщения -->
          <v-card-actions
            class="pa-3 border-top"
            v-if="(isOperator && selectedClient.id) || 
                (!isOperator && operatorInfo.id && connectionStatus === 'connected')"
          >
            <v-textarea
              v-model="newMessage"
              class="chat-input"
              rows="1"
              auto-grow
              variant="outlined"
              density="comfortable"
              hide-details
              placeholder="Введите сообщение..."
              @keydown.enter.prevent="sendMessage"
            ></v-textarea>
            
            <v-btn
              icon
              color="primary"
              class="ms-2"
              :disabled="!newMessage.trim()"
              @click="sendMessage"
            >
              <v-icon>mdi-send</v-icon>
            </v-btn>
          </v-card-actions>
          
          <!-- Информация о завершении чата -->
          <v-card-actions
            class="pa-3 border-top"
            v-if="!isOperator && chatEnded"
          >
            <v-alert
              type="info"
              title="Чат завершен"
              text="Оператор завершил чат. Оцените качество обслуживания."
              class="w-100 mb-0"
            >
              <div class="mt-3">
                <v-rating
                  v-model="chatRating"
                  density="comfortable"
                  color="warning"
                  size="small"
                ></v-rating>
              </div>
              
              <div class="mt-3">
                <v-textarea
                  v-model="feedbackText"
                  label="Комментарий"
                  rows="2"
                  variant="outlined"
                  hide-details
                ></v-textarea>
              </div>
              
              <template v-slot:append>
                <v-btn
                  color="primary"
                  @click="submitFeedback"
                  :loading="submittingFeedback"
                >
                  Отправить отзыв
                </v-btn>
              </template>
            </v-alert>
          </v-card-actions>
        </v-card>
      </v-col>
      
      <!-- Боковая панель с информацией -->
      <v-navigation-drawer
        v-model="showInfo"
        :width="320"
        temporary
        location="right"
      >
        <v-card flat class="h-100">
          <v-card-title class="d-flex align-center">
            <span>Информация</span>
            <v-spacer></v-spacer>
            <v-btn icon variant="text" @click="showInfo = false">
              <v-icon>mdi-close</v-icon>
            </v-btn>
          </v-card-title>
          
          <v-divider></v-divider>
          
          <v-card-text>
            <template v-if="isOperator && selectedClient.id">
              <h3 class="text-h6 mb-2">Информация о клиенте</h3>
              
              <v-list density="compact">
                <v-list-item>
                  <template v-slot:prepend>
                    <v-icon color="primary">mdi-account</v-icon>
                  </template>
                  <v-list-item-title>{{ selectedClient.name }}</v-list-item-title>
                  <v-list-item-subtitle>Имя</v-list-item-subtitle>
                </v-list-item>
                
                <v-list-item>
                  <template v-slot:prepend>
                    <v-icon color="primary">mdi-email</v-icon>
                  </template>
                  <v-list-item-title>{{ selectedClient.email }}</v-list-item-title>
                  <v-list-item-subtitle>Email</v-list-item-subtitle>
                </v-list-item>
                
                <v-list-item>
                  <template v-slot:prepend>
                    <v-icon color="primary">mdi-phone</v-icon>
                  </template>
                  <v-list-item-title>{{ selectedClient.phone }}</v-list-item-title>
                  <v-list-item-subtitle>Телефон</v-list-item-subtitle>
                </v-list-item>
                
                <v-list-item>
                  <template v-slot:prepend>
                    <v-icon color="primary">mdi-history</v-icon>
                  </template>
                  <v-list-item-title>{{ selectedClient.contactCount || 0 }}</v-list-item-title>
                  <v-list-item-subtitle>Предыдущих обращений</v-list-item-subtitle>
                </v-list-item>
              </v-list>
              
              <v-divider class="my-4"></v-divider>
              
              <h3 class="text-h6 mb-2">Действия</h3>
              
              <v-btn
                block
                color="error"
                variant="flat"
                class="mb-2"
                @click="endChat"
              >
                <v-icon start>mdi-close-circle</v-icon>
                Завершить чат
              </v-btn>
            </template>
            
            <template v-else-if="!isOperator && operatorInfo.id">
              <h3 class="text-h6 mb-2">Информация об операторе</h3>
              
              <v-list density="compact">
                <v-list-item>
                  <template v-slot:prepend>
                    <v-icon color="primary">mdi-account</v-icon>
                  </template>
                  <v-list-item-title>{{ operatorInfo.name }}</v-list-item-title>
                  <v-list-item-subtitle>Имя</v-list-item-subtitle>
                </v-list-item>
                
                <v-list-item>
                  <template v-slot:prepend>
                    <v-icon color="primary">mdi-star</v-icon>
                  </template>
                  <v-list-item-title>{{ operatorInfo.rating || 'Нет оценок' }}</v-list-item-title>
                  <v-list-item-subtitle>Рейтинг</v-list-item-subtitle>
                </v-list-item>
              </v-list>
            </template>
            
            <div class="mt-4" v-if="showInfo">
              <h3 class="text-h6 mb-2">Информация о чате</h3>
              
              <v-list density="compact">
                <v-list-item>
                  <template v-slot:prepend>
                    <v-icon color="primary">mdi-clock</v-icon>
                  </template>
                  <v-list-item-title>{{ chatDuration }}</v-list-item-title>
                  <v-list-item-subtitle>Длительность</v-list-item-subtitle>
                </v-list-item>
                
                <v-list-item>
                  <template v-slot:prepend>
                    <v-icon color="primary">mdi-message-text</v-icon>
                  </template>
                  <v-list-item-title>{{ messages.length }}</v-list-item-title>
                  <v-list-item-subtitle>Сообщений</v-list-item-subtitle>
                </v-list-item>
              </v-list>
            </div>
          </v-card-text>
        </v-card>
      </v-navigation-drawer>
    </v-row>
    
    <!-- Уведомления -->
    <v-snackbar
      v-model="snackbarVisible"
      :color="snackbarColor"
      :timeout="3000"
    >
      {{ snackbarText }}
      <template v-slot:actions>
        <v-btn variant="text" @click="snackbarVisible = false">Закрыть</v-btn>
      </template>
    </v-snackbar>
  </v-container>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, computed, nextTick, watch, inject } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { chatApi } from '@/api'

// Получаем доступ к snackbar для показа уведомлений
const snackbar = inject('snackbar') || ((msg, color) => {
  snackbarText.value = msg
  snackbarColor.value = color || 'success'
  snackbarVisible.value = true
})

const router = useRouter()
const route = useRoute()

// Проверяем, является ли пользователь оператором
const isOperator = computed(() => {
  return route.path.includes('/operator') || localStorage.getItem('userRole') === 'employee'
})

// Состояние чата
const selectedClient = ref({})
const operatorInfo = ref({})
const messages = ref([])
const newMessage = ref('')
const showInfo = ref(false)
const connectionStatus = ref('connecting')
const chatStartTime = ref(new Date())
const chatEnded = ref(false)
const chatRating = ref(0)
const feedbackText = ref('')
const submittingFeedback = ref(false)
const clientId = ref(null)
const operatorId = ref(null)
const websocket = ref(null)
const commId = ref(null)

// Уведомления
const snackbarText = ref('')
const snackbarColor = ref('success')
const snackbarVisible = ref(false)

// Список клиентов (для операторов)
const clients = ref([])

// Ссылка на DOM-элемент с сообщениями
const messagesContainer = ref(null)

// Подключение WebSocket и загрузка активных чатов
const connectWebSocket = async () => {
  try {
    if (isOperator.value) {
      // Получаем ID оператора
      operatorId.value = localStorage.getItem('employeeId')
      
      if (!operatorId.value) {
        snackbar('Не удалось получить ID оператора. Войдите в систему снова.', 'error')
        return
      }
      
      // Загружаем активные чаты
      await fetchActiveChats()
      
      // Подключаемся как оператор
      const wsUrl = `${window.location.protocol === 'https:' ? 'wss:' : 'ws:'}//${window.location.host}/api/chat/ws/support/${operatorId.value}`
      websocket.value = new WebSocket(wsUrl)
    } else {
      // Получаем ID клиента
      clientId.value = localStorage.getItem('clientId')
      
      if (!clientId.value) {
        snackbar('Не удалось получить ID клиента. Войдите в систему снова.', 'error')
        return
      }
      
      // Подключаемся как клиент
      const wsUrl = `${window.location.protocol === 'https:' ? 'wss:' : 'ws:'}//${window.location.host}/api/chat/ws/client/${clientId.value}`
      websocket.value = new WebSocket(wsUrl)
    }
    
    // Общие обработчики WebSocket
    websocket.value.onopen = () => {
      connectionStatus.value = 'connected'
      snackbar('Подключено к чату', 'success')
    }
    
    websocket.value.onclose = () => {
      connectionStatus.value = 'disconnected'
      snackbar('Соединение с чатом закрыто', 'warning')
    }
    
    websocket.value.onerror = (error) => {
      console.error('WebSocket ошибка:', error)
      snackbar('Ошибка соединения с чатом', 'error')
    }
    
    // Обработчик сообщений
    websocket.value.onmessage = handleWebSocketMessage
    
  } catch (error) {
    console.error('Ошибка при подключении к WebSocket:', error)
    snackbar('Ошибка при подключении к чату', 'error')
  }
}

// Обработка сообщений WebSocket
const handleWebSocketMessage = (event) => {
  try {
    const data = JSON.parse(event.data)
    console.log('Получено сообщение:', data)
    
    if (data.type === 'message') {
      // Получено новое сообщение
      const newMsg = {
        id: messages.value.length + 1,
        text: data.message,
        timestamp: new Date(),
        isUser: false
      }
      
      messages.value.push(newMsg)
      scrollToBottom()
      
      // Обновляем информацию о клиенте в списке (для операторов)
      if (isOperator.value && data.client_id) {
        const clientIndex = clients.value.findIndex(c => c.id === data.client_id)
        if (clientIndex !== -1) {
          clients.value[clientIndex].lastMessage = data.message
          clients.value[clientIndex].lastTime = new Date()
          
          // Если это не текущий выбранный клиент, увеличиваем счетчик непрочитанных
          if (!selectedClient.value || selectedClient.value.id !== data.client_id) {
            clients.value[clientIndex].unread = (clients.value[clientIndex].unread || 0) + 1
          }
        }
      }
    } 
    
    else if (data.type === 'operator_assigned') {
      // Оператор назначен клиенту
      operatorInfo.value = {
        id: data.operator_id,
        name: data.operator_name
      }
      
      // Сохраняем ID коммуникации
      commId.value = data.communication_id
      
      // Добавляем приветственное сообщение
      messages.value.push({
        id: messages.value.length + 1,
        text: `Здравствуйте! Меня зовут ${data.operator_name}. Чем я могу вам помочь?`,
        timestamp: new Date(),
        isUser: false
      })
      
      scrollToBottom()
    }
    
    else if (data.type === 'new_client') {
      // Новый клиент подключился (для операторов)
      if (isOperator.value) {
        // Обновляем список клиентов
        fetchActiveChats()
        snackbar(`Новый клиент: ${data.client_name}`, 'info')
      }
    }
    
    else if (data.type === 'client_disconnect' || data.type === 'operator_disconnect') {
      // Клиент или оператор отключился
      if (data.type === 'operator_disconnect') {
        chatEnded.value = true
      } else if (isOperator.value && data.client_id) {
        const clientIndex = clients.value.findIndex(c => c.id === data.client_id)
        if (clientIndex !== -1) {
          clients.value[clientIndex].online = false
          
          // Если это текущий выбранный клиент, добавляем сообщение
          if (selectedClient.value && selectedClient.value.id === data.client_id) {
            messages.value.push({
              id: messages.value.length + 1,
              text: 'Клиент отключился от чата',
              timestamp: new Date(),
              isUser: false,
              isSystem: true
            })
            scrollToBottom()
          }
        }
      }
    }
    
    else if (data.type === 'feedback_received') {
      snackbar('Отзыв успешно отправлен. Спасибо!', 'success')
      chatEnded.value = false
    }
    
    else if (data.type === 'error') {
      snackbar(data.message, 'error')
    }
    
  } catch (error) {
    console.error('Ошибка при обработке сообщения:', error)
  }
}

// Получение активных чатов (для операторов)
const fetchActiveChats = async () => {
  if (!isOperator.value) return
  
  try {
    const response = await chatApi.getActiveChats()
    
    if (response.data) {
      clients.value = response.data.map(client => ({
        id: client.client_id,
        name: client.client_name || `Клиент #${client.client_id}`,
        lastMessage: client.last_message || 'Новый чат',
        lastTime: client.last_message_time ? new Date(client.last_message_time) : new Date(),
        unread: client.unread_count || 0,
        online: client.status === 'online',
        email: client.email || '',
        phone: client.phone || '',
        communicationId: client.communication_id
      }))
    }
  } catch (error) {
    console.error('Ошибка при получении активных чатов:', error)
    snackbar('Не удалось загрузить список активных чатов', 'error')
  }
}

// Выбор клиента (для операторов)
const selectClient = async (client) => {
  selectedClient.value = client
  messages.value = []
  commId.value = client.communicationId
  
  // Получаем историю сообщений
  try {
    const history = await chatApi.getHistory(client.id)
    
    if (history.data && history.data.length > 0) {
      messages.value = history.data.map(msg => ({
        id: messages.value.length + 1,
        text: msg.message || msg.text,
        timestamp: new Date(msg.timestamp),
        isUser: msg.sender === 'operator'
      }))
      
      scrollToBottom()
    }
    
    // Сбрасываем счетчик непрочитанных
    const index = clients.value.findIndex(c => c.id === client.id)
    if (index !== -1) {
      clients.value[index].unread = 0
    }
  } catch (error) {
    console.error('Ошибка при получении истории сообщений:', error)
    snackbar('Не удалось загрузить историю сообщений', 'error')
  }
}

// Отправка сообщения
const sendMessage = () => {
  if (!newMessage.value.trim() || connectionStatus.value !== 'connected') return
  
  try {
    let message
    
    if (isOperator.value) {
      // Оператор отправляет сообщение клиенту
      message = {
        client_id: selectedClient.value.id,
        message: newMessage.value.trim()
      }
    } else {
      // Клиент отправляет сообщение оператору
      message = {
        message: newMessage.value.trim()
      }
    }
    
    // Отправка через WebSocket
    websocket.value.send(JSON.stringify(message))
    
    // Добавляем сообщение в список
    messages.value.push({
      id: messages.value.length + 1,
      text: newMessage.value.trim(),
      timestamp: new Date(),
      isUser: true
    })
    
    // Очищаем поле ввода
    newMessage.value = ''
    
    // Прокручиваем чат вниз
    scrollToBottom()
  } catch (error) {
    console.error('Ошибка при отправке сообщения:', error)
    snackbar('Не удалось отправить сообщение', 'error')
  }
}

// Завершение чата (для операторов)
const endChat = () => {
  if (!isOperator.value || !selectedClient.value.id) return
  
  try {
    // Отключаем клиента
    websocket.value.send(JSON.stringify({
      type: 'end_chat',
      client_id: selectedClient.value.id
    }))
    
    // Обновляем список клиентов
    const index = clients.value.findIndex(c => c.id === selectedClient.value.id)
    if (index !== -1) {
      clients.value.splice(index, 1)
    }
    
    // Сбрасываем выбранного клиента
    selectedClient.value = {}
    messages.value = []
    
    snackbar('Чат завершен', 'success')
  } catch (error) {
    console.error('Ошибка при завершении чата:', error)
    snackbar('Не удалось завершить чат', 'error')
  }
}

// Отправка отзыва
const submitFeedback = async () => {
  if (!commId.value) {
    snackbar('Не удалось отправить отзыв: ID коммуникации не найден', 'error')
    return
  }
  
  submittingFeedback.value = true
  
  try {
    const feedback = {
      rating: chatRating.value,
      comment: feedbackText.value,
      tags: []
    }
    
    // Отправляем отзыв через WebSocket если соединение активно
    if (websocket.value && websocket.value.readyState === WebSocket.OPEN) {
      websocket.value.send(JSON.stringify({ feedback }))
    } else {
      // Иначе через REST API
      await chatApi.submitFeedback(commId.value, feedback)
      chatEnded.value = false
      snackbar('Отзыв успешно отправлен. Спасибо!', 'success')
    }
  } catch (error) {
    console.error('Ошибка при отправке отзыва:', error)
    snackbar('Не удалось отправить отзыв', 'error')
  } finally {
    submittingFeedback.value = false
  }
}

// Прокрутка чата вниз
const scrollToBottom = () => {
  nextTick(() => {
    if (messagesContainer.value) {
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
    }
  })
}

// Форматирование времени
const formatTime = (timestamp) => {
  const date = new Date(timestamp)
  
  return date.toLocaleTimeString('ru-RU', {
    hour: '2-digit',
    minute: '2-digit'
  })
}

// Вычисляемые свойства
const onlineClients = computed(() => {
  return clients.value.filter(client => client.online).length
})

const filteredClients = computed(() => {
  return clients.value
})

const chatDuration = computed(() => {
  const now = new Date()
  const diff = Math.floor((now - chatStartTime.value) / 1000)
  
  const minutes = Math.floor(diff / 60)
  const seconds = diff % 60
  
  return `${minutes}:${seconds.toString().padStart(2, '0')}`
})

// Жизненный цикл компонента
onMounted(() => {
  connectWebSocket()
  
  // Для операторов обновляем список активных чатов каждые 30 секунд
  let interval
  if (isOperator.value) {
    interval = setInterval(() => {
      if (connectionStatus.value === 'connected') {
        fetchActiveChats()
      }
    }, 30000)
  }
  
  onBeforeUnmount(() => {
    if (interval) {
      clearInterval(interval)
    }
    
    if (websocket.value) {
      websocket.value.close()
    }
  })
})

// Наблюдатели
watch(messages, () => {
  scrollToBottom()
}, { deep: true })
</script>

<style scoped>
.h-100 {
  height: 100%;
}

.border-end {
  border-right: 1px solid rgba(0, 0, 0, 0.12);
}

.border-top {
  border-top: 1px solid rgba(0, 0, 0, 0.12);
}

.border-bottom {
  border-bottom: 1px solid rgba(0, 0, 0, 0.12);
}

.chat-input {
  margin-bottom: 0;
}

.user-message {
  background-color: rgb(var(--v-theme-primary-lighten-5, 236, 239, 241));
}

.other-message {
  background-color: rgb(var(--v-theme-surface-variant, 241, 245, 249));
}
</style> 