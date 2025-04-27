<template>
  <v-container fluid class="pa-0 fill-height">
    <v-row no-gutters class="fill-height">
      <!-- Список клиентов -->
      <v-col cols="3" class="border-right">
        <v-card flat height="100%">
          <v-card-title class="d-flex align-center">
            <span>Клиенты</span>
            <v-spacer></v-spacer>
            <v-chip 
              v-if="isConnected" 
              color="success" 
              size="small"
            >
              Онлайн
            </v-chip>
            <v-chip 
              v-else 
              color="error" 
              size="small"
            >
              Офлайн
            </v-chip>
          </v-card-title>
          <v-card-text class="pa-0">
            <v-list>
              <v-list-item
                v-for="client in clients"
                :key="client.id"
                :active="selectedClient?.id === client.id"
                @click="selectClient(client)"
              >
                <template v-slot:prepend>
                  <v-avatar color="grey lighten-1" size="36">
                    <span class="text-caption">{{ client.name.charAt(0) }}</span>
                  </v-avatar>
                </template>
                <v-list-item-title>{{ client.name }}</v-list-item-title>
                <v-list-item-subtitle>{{ client.lastMessage }}</v-list-item-subtitle>
                <template v-slot:append>
                  <div class="d-flex flex-column align-center">
                    <span class="text-caption">{{ formatTime(client.lastMessageTime) }}</span>
                    <v-badge
                      v-if="client.unreadCount > 0"
                      :content="client.unreadCount"
                      color="error"
                      floating
                    ></v-badge>
                  </div>
                </template>
              </v-list-item>
            </v-list>
          </v-card-text>
        </v-card>
      </v-col>

      <!-- Окно чата -->
      <v-col cols="9">
        <v-card flat height="100%" class="d-flex flex-column">
          <v-card-title v-if="selectedClient" class="border-bottom d-flex align-center">
            <v-avatar color="grey lighten-1" size="36" class="mr-3">
              <span class="text-caption">{{ selectedClient.name.charAt(0) }}</span>
            </v-avatar>
            <div>
              <div class="text-body-1">{{ selectedClient.name }}</div>
              <div class="text-caption">{{ selectedClient.status }}</div>
            </div>
            <v-spacer></v-spacer>
            <v-btn icon>
              <v-icon>mdi-phone</v-icon>
            </v-btn>
            <v-btn icon>
              <v-icon>mdi-video</v-icon>
            </v-btn>
            <v-btn icon>
              <v-icon>mdi-information-outline</v-icon>
            </v-btn>
            <v-btn icon>
              <v-icon>mdi-dots-vertical</v-icon>
            </v-btn>
          </v-card-title>

          <v-card-title v-else class="border-bottom d-flex align-center">
            <div>Выберите клиента для начала общения</div>
          </v-card-title>

          <!-- Сообщения -->
          <v-card-text v-if="selectedClient" class="flex-grow-1 overflow-auto pa-4" ref="chatMessages">
            <div 
              v-for="(message, index) in messages" 
              :key="index"
              class="mb-4"
              :class="{ 
                'd-flex justify-end': message.sender === 'operator',
                'd-flex justify-start': message.sender === 'client'
              }"
            >
              <div 
                class="message-bubble pa-3 rounded"
                :class="{ 
                  'primary': message.sender === 'operator',
                  'bg-grey-lighten-3': message.sender === 'client'
                }"
                style="max-width: 80%;"
              >
                <div :class="{ 'text-white': message.sender === 'operator' }">
                  {{ message.text }}
                </div>
                <div 
                  class="text-caption mt-1 text-right"
                  :class="{ 'text-white': message.sender === 'operator' }"
                >
                  {{ formatTime(message.time) }}
                </div>
              </div>
            </div>
          </v-card-text>

          <v-card-text v-else class="flex-grow-1 d-flex align-center justify-center">
            <div class="text-h6 text-grey-darken-1">
              Выберите клиента из списка слева для начала общения
            </div>
          </v-card-text>

          <!-- Поле ввода сообщения -->
          <div v-if="selectedClient" class="pa-3 border-top">
            <v-form @submit.prevent="sendMessage">
              <div class="d-flex align-center">
                <v-btn icon class="mr-2">
                  <v-icon>mdi-emoticon-outline</v-icon>
                </v-btn>
                <v-btn icon class="mr-2">
                  <v-icon>mdi-paperclip</v-icon>
                </v-btn>
                <v-textarea
                  v-model="newMessage"
                  placeholder="Введите сообщение..."
                  rows="1"
                  auto-grow
                  hide-details
                  density="compact"
                  class="flex-grow-1"
                  @keydown.enter.prevent="sendMessage"
                ></v-textarea>
                <v-btn icon class="ml-2" color="primary" @click="sendMessage" :disabled="!newMessage.trim()">
                  <v-icon>mdi-send</v-icon>
                </v-btn>
              </div>
            </v-form>
          </div>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch, nextTick, inject } from 'vue';
import { chatApi } from '@/api';

// Инициализация
const snackbar = inject('snackbar') || ((msg) => console.log(msg));

// Состояние чата
const clients = ref([]);
const selectedClient = ref(null);
const messages = ref([]);
const newMessage = ref('');
const isConnected = ref(false);
const chatMessages = ref(null);
const operatorId = ref(null);
const websocket = ref(null);
const clientTyping = ref(false);
const currentCommunicationId = ref(null);

// Получение активных чатов
const fetchActiveChats = async () => {
  try {
    const response = await chatApi.getActiveChats();
    if (response.data) {
      clients.value = response.data.map(client => ({
        id: client.client_id,
        name: client.client_name || `Клиент #${client.client_id}`,
        lastMessage: client.last_message || 'Новый чат',
        lastMessageTime: client.last_message_time ? new Date(client.last_message_time) : new Date(),
        unreadCount: client.unread_count || 0,
        status: client.status || 'online',
        communicationId: client.communication_id
      }));
    }
  } catch (error) {
    console.error('Ошибка при получении активных чатов:', error);
    snackbar('Ошибка при получении списка активных чатов', 'error');
  }
};

// Выбор клиента
const selectClient = async (client) => {
  selectedClient.value = client;
  messages.value = [];
  currentCommunicationId.value = client.communicationId;
  
  // Получаем историю сообщений для выбранного клиента
  try {
    const history = await chatApi.getHistory(client.id);
    if (history.data && history.data.length > 0) {
      messages.value = history.data.map(msg => ({
        sender: msg.sender === 'operator' ? 'operator' : 'client',
        text: msg.message || msg.text,
        time: new Date(msg.timestamp),
      }));
      
      // Прокрутить к последнему сообщению
      await nextTick();
      scrollToBottom();
    }
    
    // Сбрасываем счетчик непрочитанных сообщений для выбранного клиента
    const index = clients.value.findIndex(c => c.id === client.id);
    if (index !== -1) {
      clients.value[index].unreadCount = 0;
    }
  } catch (error) {
    console.error('Ошибка при получении истории сообщений:', error);
    snackbar('Ошибка при загрузке истории сообщений', 'error');
  }
};

// Подключение WebSocket
const connectToWebSocket = async () => {
  try {
    // Получаем ID оператора из localStorage или другого источника
    operatorId.value = localStorage.getItem('operatorId') || localStorage.getItem('employeeId');
    
    if (!operatorId.value) {
      snackbar('Ошибка: Не удалось получить ID оператора', 'error');
      return;
    }
    
    // Устанавливаем WebSocket соединение
    const wsUrl = `${window.location.protocol === 'https:' ? 'wss:' : 'ws:'}//${window.location.host}/api/chat/ws/support/${operatorId.value}`;
    websocket.value = new WebSocket(wsUrl);
    
    websocket.value.onopen = () => {
      isConnected.value = true;
      console.log('WebSocket соединение установлено');
      
      // Загружаем список активных чатов после подключения
      fetchActiveChats();
    };
    
    websocket.value.onmessage = (event) => {
      const data = JSON.parse(event.data);
      console.log('Получено сообщение:', data);
      
      if (data.type === 'message') {
        // Если сообщение от текущего выбранного клиента
        if (selectedClient.value && data.client_id === selectedClient.value.id) {
          messages.value.push({
            sender: 'client',
            text: data.message,
            time: new Date(),
          });
          
          // Прокрутить к новому сообщению
          nextTick(scrollToBottom);
        } 
        
        // Обновляем информацию о последнем сообщении в списке чатов
        const clientIndex = clients.value.findIndex(c => c.id === data.client_id);
        if (clientIndex !== -1) {
          clients.value[clientIndex].lastMessage = data.message;
          clients.value[clientIndex].lastMessageTime = new Date();
          
          // Если это не текущий выбранный клиент, увеличиваем счетчик непрочитанных
          if (!selectedClient.value || selectedClient.value.id !== data.client_id) {
            clients.value[clientIndex].unreadCount += 1;
          }
        } else {
          // Если клиента нет в списке, добавляем его
          fetchActiveChats();
        }
      }
      else if (data.type === 'client_typing') {
        if (selectedClient.value && data.client_id === selectedClient.value.id) {
          clientTyping.value = true;
          setTimeout(() => { clientTyping.value = false; }, 3000);
        }
      }
      else if (data.type === 'client_disconnect') {
        snackbar(`Клиент #${data.client_id} отключился`, 'info');
        
        // Обновляем статус клиента в списке
        const clientIndex = clients.value.findIndex(c => c.id === data.client_id);
        if (clientIndex !== -1) {
          clients.value[clientIndex].status = 'offline';
        }
      }
      else if (data.type === 'new_client') {
        // Добавляем нового клиента в список
        fetchActiveChats();
        snackbar('Новый клиент подключился к чату', 'info');
      }
      else if (data.type === 'feedback') {
        snackbar(`Получен отзыв от клиента #${data.client_id}`, 'info');
      }
      else if (data.type === 'error') {
        snackbar(data.message, 'error');
      }
    };
    
    websocket.value.onclose = () => {
      isConnected.value = false;
      console.log('WebSocket соединение закрыто');
    };
    
    websocket.value.onerror = (error) => {
      console.error('WebSocket ошибка:', error);
      snackbar('Ошибка подключения к чату', 'error');
    };
  } catch (error) {
    console.error('Ошибка при подключении к WebSocket:', error);
    snackbar('Ошибка при подключении к чату', 'error');
  }
};

// Отправка сообщения
const sendMessage = () => {
  if (!newMessage.value.trim() || !selectedClient.value || !isConnected.value) return;
  
  const message = {
    client_id: selectedClient.value.id,
    message: newMessage.value.trim(),
  };
  
  try {
    websocket.value.send(JSON.stringify(message));
    
    // Добавляем сообщение в чат
    messages.value.push({
      sender: 'operator',
      text: newMessage.value.trim(),
      time: new Date(),
    });
    
    // Обновляем информацию о последнем сообщении
    const clientIndex = clients.value.findIndex(c => c.id === selectedClient.value.id);
    if (clientIndex !== -1) {
      clients.value[clientIndex].lastMessage = newMessage.value.trim();
      clients.value[clientIndex].lastMessageTime = new Date();
    }
    
    // Очищаем поле ввода
    newMessage.value = '';
    
    // Прокрутка вниз
    nextTick(scrollToBottom);
  } catch (error) {
    console.error('Ошибка при отправке сообщения:', error);
    snackbar('Ошибка при отправке сообщения', 'error');
  }
};

// Функция для прокрутки чата вниз
const scrollToBottom = () => {
  if (chatMessages.value) {
    chatMessages.value.scrollTop = chatMessages.value.scrollHeight;
  }
};

// Форматирование времени
const formatTime = (time) => {
  if (!time) return '';
  
  const date = time instanceof Date ? time : new Date(time);
  const now = new Date();
  
  if (now.toDateString() === date.toDateString()) {
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  } else {
    return date.toLocaleDateString();
  }
};

// Жизненный цикл компонента
onMounted(() => {
  connectToWebSocket();
  
  // Обновляем список активных чатов каждые 30 секунд
  const interval = setInterval(() => {
    if (isConnected.value) {
      fetchActiveChats();
    }
  }, 30000);
  
  // Очистка интервала при размонтировании
  onUnmounted(() => {
    clearInterval(interval);
    if (websocket.value) {
      websocket.value.close();
    }
  });
});
</script>

<style scoped>
.border-right {
  border-right: 1px solid rgba(0, 0, 0, 0.12);
}

.border-bottom {
  border-bottom: 1px solid rgba(0, 0, 0, 0.12);
}

.border-top {
  border-top: 1px solid rgba(0, 0, 0, 0.12);
}

.message-bubble {
  display: inline-block;
  border-radius: 12px;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
}
</style> 