<template>
  <v-container fluid class="pa-0 fill-height">
    <v-row no-gutters class="fill-height">
      <!-- Окно чата -->
      <v-col cols="12">
        <v-card flat height="100%" class="d-flex flex-column">
          <v-card-title class="border-bottom d-flex align-center">
            <v-avatar color="primary" size="36" class="mr-3">
              <v-icon color="white">mdi-headset</v-icon>
            </v-avatar>
            <div>
              <div class="text-body-1">Оператор поддержки</div>
              <div v-if="operatorTyping" class="text-caption">печатает...</div>
              <div v-else-if="operator" class="text-caption">{{ operator.status }}</div>
              <div v-else class="text-caption">
                <v-progress-circular
                  indeterminate
                  size="16"
                  width="2"
                  color="primary"
                  class="mr-2"
                ></v-progress-circular>
                Ожидание подключения оператора...
              </div>
            </div>
            <v-spacer></v-spacer>
            <v-chip
              v-if="isConnected"
              color="success"
              size="small"
            >
              Подключено
            </v-chip>
            <v-chip
              v-else
              color="error"
              size="small"
            >
              Отключено
            </v-chip>
            <v-btn icon class="ml-2">
              <v-icon>mdi-dots-vertical</v-icon>
            </v-btn>
          </v-card-title>

          <!-- Сообщения -->
          <v-card-text class="flex-grow-1 overflow-auto pa-4" ref="chatMessages">
            <div v-if="!operator && messages.length === 0" class="text-center my-8">
              <v-icon size="60" color="grey lighten-1">mdi-account-voice</v-icon>
              <div class="text-h6 mt-4">Ожидание подключения оператора</div>
              <div class="text-body-2 text-grey mt-2">Пожалуйста, подождите. Мы подключим вас к первому доступному оператору.</div>
            </div>

            <div 
              v-for="(message, index) in messages" 
              :key="index"
              class="mb-4"
              :class="{ 
                'd-flex justify-end': message.sender === 'client',
                'd-flex justify-start': message.sender === 'operator'
              }"
            >
              <div 
                class="message-bubble pa-3 rounded"
                :class="{ 
                  'primary': message.sender === 'client',
                  'bg-grey-lighten-3': message.sender === 'operator'
                }"
                style="max-width: 80%;"
              >
                <div :class="{ 'text-white': message.sender === 'client' }">
                  {{ message.text }}
                </div>
                <div 
                  class="text-caption mt-1 text-right"
                  :class="{ 'text-white': message.sender === 'client' }"
                >
                  {{ formatTime(message.time) }}
                </div>
              </div>
            </div>

            <div v-if="sessionEnded" class="text-center my-6 py-3 rounded bg-grey-lighten-4">
              <div class="text-body-1">Сессия завершена</div>
              <div class="text-body-2 text-grey mt-1">Оцените качество общения</div>
              <div class="my-2">
                <v-rating
                  v-model="rating"
                  color="amber"
                  active-color="amber"
                  hover
                  length="5"
                ></v-rating>
              </div>
              <v-textarea
                v-model="feedback"
                label="Ваши комментарии (необязательно)"
                rows="2"
                variant="outlined"
                density="compact"
                hide-details
                class="mx-auto mt-3"
                style="max-width: 400px;"
              ></v-textarea>
              <v-btn
                color="primary"
                class="mt-3"
                @click="submitFeedback"
              >
                Отправить отзыв
              </v-btn>
            </div>
          </v-card-text>

          <!-- Поле ввода сообщения -->
          <div class="pa-3 border-top" v-if="!sessionEnded">
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
                <v-btn icon class="ml-2" color="primary" @click="sendMessage" :disabled="!newMessage.trim() || !operator">
                  <v-icon>mdi-send</v-icon>
                </v-btn>
              </div>
            </v-form>
          </div>

          <!-- Кнопки после завершения сессии -->
          <div class="pa-3 border-top d-flex justify-center" v-if="sessionEnded && feedbackSubmitted">
            <v-btn color="primary" class="mx-2" @click="startNewChat">
              Новый чат
            </v-btn>
            <v-btn color="secondary" class="mx-2" to="/client/profile">
              Вернуться в профиль
            </v-btn>
          </div>
        </v-card>
      </v-col>
    </v-row>

    <!-- Диалог предпочтений -->
    <v-dialog v-model="preferencesDialog" max-width="500">
      <v-card>
        <v-card-title>Предпочтения общения</v-card-title>
        <v-card-text>
          <p class="mb-3">Вы можете указать предпочтительных операторов или тех, с кем бы не хотели общаться.</p>
          
          <v-select
            v-model="preferredOperators"
            :items="availableOperators"
            item-title="name"
            item-value="id"
            label="Предпочтительные операторы"
            multiple
            chips
          ></v-select>
          
          <v-select
            v-model="unwantedOperators"
            :items="availableOperators.filter(op => !preferredOperators.includes(op.id))"
            item-title="name"
            item-value="id"
            label="Нежелательные операторы"
            multiple
            chips
          ></v-select>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="primary" @click="savePreferences">Сохранить</v-btn>
          <v-btn color="secondary" @click="preferencesDialog = false">Отмена</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script setup>
import { ref, onMounted, onUnmounted, nextTick, inject } from 'vue';
import { useRouter } from 'vue-router';
import { chatApi } from '@/api';

// Инициализация
const router = useRouter();
const snackbar = inject('snackbar') || ((msg) => console.log(msg));

// Состояние чата
const operator = ref(null);
const messages = ref([]);
const newMessage = ref('');
const isConnected = ref(false);
const chatMessages = ref(null);
const operatorTyping = ref(false);
const clientId = ref(null);
const websocket = ref(null);
const commId = ref(null);
const sessionEnded = ref(false);
const rating = ref(3);
const feedback = ref('');
const feedbackSubmitted = ref(false);
const preferencesDialog = ref(false);
const preferredOperators = ref([]);
const unwantedOperators = ref([]);
const availableOperators = ref([]);

// Подключение к WebSocket
const connectToChat = async () => {
  try {
    // Получить ID клиента из localStorage или API
    clientId.value = localStorage.getItem('clientId');
    
    if (!clientId.value) {
      snackbar('Ошибка: Не удалось получить ID клиента', 'error');
      return;
    }
    
    // Получить историю сообщений, если есть
    const history = await chatApi.getHistory(clientId.value);
    if (history.data && history.data.length > 0) {
      messages.value = history.data.map(msg => ({
        sender: msg.sender,
        text: msg.message || msg.text,
        time: new Date(msg.timestamp),
      }));
      
      // Прокрутить к последнему сообщению
      await nextTick();
      scrollToBottom();
    }
    
    // Установка WebSocket соединения
    const wsUrl = `${window.location.protocol === 'https:' ? 'wss:' : 'ws:'}//${window.location.host}/api/chat/ws/client/${clientId.value}`;
    websocket.value = new WebSocket(wsUrl);
    
    websocket.value.onopen = () => {
      isConnected.value = true;
      console.log('WebSocket соединение установлено');
    };
    
    websocket.value.onmessage = (event) => {
      const data = JSON.parse(event.data);
      console.log('Получено сообщение:', data);
      
      if (data.type === 'message') {
        messages.value.push({
          sender: 'operator',
          text: data.message,
          time: new Date(),
        });
        
        // Прокрутить к новому сообщению
        nextTick(scrollToBottom);
      } 
      else if (data.type === 'operator_assigned') {
        operator.value = {
          name: data.operator_name,
          status: 'Онлайн',
        };
        commId.value = data.communication_id;
        console.log('Назначен оператор:', operator.value);
      }
      else if (data.type === 'operator_typing') {
        operatorTyping.value = true;
        setTimeout(() => { operatorTyping.value = false; }, 3000);
      }
      else if (data.type === 'operator_disconnect') {
        sessionEnded.value = true;
        isConnected.value = false;
        snackbar('Оператор отключился от чата', 'info');
      }
      else if (data.type === 'feedback_received') {
        feedbackSubmitted.value = true;
        snackbar('Спасибо за ваш отзыв!', 'success');
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
    console.error('Ошибка при подключении к чату:', error);
    snackbar('Ошибка при подключении к чату', 'error');
  }
};

// Отправка сообщения
const sendMessage = () => {
  if (!newMessage.value.trim() || !isConnected.value) return;
  
  const message = {
    message: newMessage.value.trim()
  };
  
  try {
    websocket.value.send(JSON.stringify(message));
    
    // Добавляем сообщение в чат
    messages.value.push({
      sender: 'client',
      text: newMessage.value.trim(),
      time: new Date(),
    });
    
    // Очищаем поле ввода
    newMessage.value = '';
    
    // Прокрутка вниз
    nextTick(scrollToBottom);
  } catch (error) {
    console.error('Ошибка при отправке сообщения:', error);
    snackbar('Ошибка при отправке сообщения', 'error');
  }
};

// Отправка отзыва
const submitFeedback = async () => {
  if (!commId.value) {
    snackbar('Невозможно отправить отзыв: ID коммуникации не найден', 'error');
    return;
  }
  
  try {
    const feedbackData = {
      rating: rating.value,
      comment: feedback.value,
      tags: []
    };
    
    if (websocket.value && websocket.value.readyState === WebSocket.OPEN) {
      // Отправляем через WebSocket
      websocket.value.send(JSON.stringify({ feedback: feedbackData }));
    } else {
      // Отправляем через REST API
      await chatApi.submitFeedback(commId.value, feedbackData);
      feedbackSubmitted.value = true;
      snackbar('Спасибо за ваш отзыв!', 'success');
    }
  } catch (error) {
    console.error('Ошибка при отправке отзыва:', error);
    snackbar('Ошибка при отправке отзыва', 'error');
  }
};

// Начать новый чат
const startNewChat = () => {
  // Сбрасываем состояние
  messages.value = [];
  operator.value = null;
  sessionEnded.value = false;
  feedbackSubmitted.value = false;
  rating.value = 3;
  feedback.value = '';
  
  // Переподключаемся
  connectToChat();
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
  return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
};

// Жизненный цикл компонента
onMounted(() => {
  connectToChat();
});

onUnmounted(() => {
  if (websocket.value) {
    websocket.value.close();
  }
});
</script>

<style scoped>
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