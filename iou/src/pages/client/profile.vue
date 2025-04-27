<template>
  <v-container>
    <h1 class="text-h4 mb-4">Профиль клиента</h1>
    
    <v-card class="mb-4">
      <v-card-title>Личная информация</v-card-title>
      <v-card-text>
        <v-row>
          <v-col cols="4">
            <v-avatar size="150" color="grey lighten-2">
              <v-icon size="80" color="grey">mdi-account</v-icon>
            </v-avatar>
          </v-col>
          <v-col cols="8">
            <div class="text-h5 mb-2">{{ client.name }}</div>
            <div class="text-subtitle-1 mb-1">ID: {{ client.id }}</div>
            <div class="text-body-1 mb-1">Email: {{ client.email }}</div>
            <div class="text-body-1 mb-1">Телефон: {{ client.phone }}</div>
            <div class="text-body-1 mb-1">Дата регистрации: {{ formatDate(client.registrationDate) }}</div>
          </v-col>
        </v-row>
      </v-card-text>
      <v-card-actions>
        <v-spacer></v-spacer>
        <v-btn color="primary" @click="showEditDialog">
          Редактировать профиль
        </v-btn>
      </v-card-actions>
    </v-card>

    <v-card class="mb-4">
      <v-card-title class="d-flex align-center">
        История коммуникаций
        <v-spacer></v-spacer>
        <v-btn variant="text" color="primary" to="/chat/client">
          Начать новый чат
        </v-btn>
      </v-card-title>
      <v-card-text>
        <v-data-table
          :headers="communicationHeaders"
          :items="communicationHistory"
          :items-per-page="5"
          class="elevation-1"
        >
          <template v-slot:item.actions="{ item }">
            <v-btn
              icon
              size="small"
              @click="viewChatHistory(item.raw)"
            >
              <v-icon>mdi-eye</v-icon>
            </v-btn>
          </template>
          
          <template v-slot:item.rating="{ item }">
            <v-rating
              :model-value="item.raw.rating"
              color="amber"
              density="compact"
              size="small"
              readonly
            ></v-rating>
          </template>
        </v-data-table>
      </v-card-text>
    </v-card>

    <v-card>
      <v-card-title>Настройки уведомлений</v-card-title>
      <v-card-text>
        <v-switch
          v-model="notifications.email"
          label="Получать уведомления по email"
        ></v-switch>
        <v-switch
          v-model="notifications.sms"
          label="Получать SMS-уведомления"
        ></v-switch>
        <v-switch
          v-model="notifications.push"
          label="Получать push-уведомления"
        ></v-switch>
      </v-card-text>
      <v-card-actions>
        <v-spacer></v-spacer>
        <v-btn color="primary" @click="saveNotificationSettings">
          Сохранить настройки
        </v-btn>
      </v-card-actions>
    </v-card>

    <!-- Диалог редактирования профиля -->
    <v-dialog v-model="editDialog" max-width="600">
      <v-card>
        <v-card-title>Редактирование профиля</v-card-title>
        <v-card-text>
          <v-form ref="form">
            <v-text-field
              v-model="editedClient.name"
              label="Имя"
              required
            ></v-text-field>
            <v-text-field
              v-model="editedClient.email"
              label="Email"
              type="email"
              required
            ></v-text-field>
            <v-text-field
              v-model="editedClient.phone"
              label="Телефон"
              required
            ></v-text-field>
          </v-form>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="secondary" @click="editDialog = false">Отмена</v-btn>
          <v-btn color="primary" @click="saveProfile">Сохранить</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Диалог просмотра истории чата -->
    <v-dialog v-model="chatHistoryDialog" max-width="800">
      <v-card>
        <v-card-title class="d-flex align-center">
          <span>Диалог с оператором</span>
          <v-spacer></v-spacer>
          <span class="text-subtitle-2">{{ selectedChat ? formatDate(selectedChat.date) : '' }}</span>
        </v-card-title>
        <v-card-text>
          <div class="chat-history-container pa-4">
            <div 
              v-for="(message, index) in selectedChatMessages"
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
          </div>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="primary" @click="chatHistoryDialog = false">Закрыть</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script setup>
import { ref, computed } from 'vue';

// Данные клиента
const client = ref({
  id: 'CL12345',
  name: 'Сергей Петров',
  email: 'petrov@example.com',
  phone: '+7 (999) 123-45-67',
  registrationDate: new Date('2023-01-15'),
});

// Настройки уведомлений
const notifications = ref({
  email: true,
  sms: false,
  push: true,
});

// История коммуникаций
const communicationHeaders = ref([
  { title: 'Дата', key: 'date' },
  { title: 'Оператор', key: 'operator' },
  { title: 'Тип', key: 'type' },
  { title: 'Продолжительность', key: 'duration' },
  { title: 'Оценка', key: 'rating' },
  { title: 'Действия', key: 'actions' },
]);

const communicationHistory = ref([
  {
    id: 1,
    date: new Date('2023-10-12'),
    operator: 'Иванов Иван',
    type: 'Чат',
    duration: '15 мин',
    rating: 5,
  },
  {
    id: 2,
    date: new Date('2023-09-28'),
    operator: 'Петрова Мария',
    type: 'Чат',
    duration: '8 мин',
    rating: 4,
  },
  {
    id: 3,
    date: new Date('2023-09-15'),
    operator: 'Сидоров Алексей',
    type: 'Чат',
    duration: '22 мин',
    rating: 3,
  },
]);

// Данные для диалога редактирования
const editDialog = ref(false);
const editedClient = ref({...client.value});

// Данные для диалога истории чата
const chatHistoryDialog = ref(false);
const selectedChat = ref(null);
const selectedChatMessages = ref([]);

// Функции форматирования
function formatDate(date) {
  if (!date) return '';
  return new Date(date).toLocaleDateString();
}

function formatTime(date) {
  if (!date) return '';
  
  const messageDate = new Date(date);
  return messageDate.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}

// Показать диалог редактирования профиля
function showEditDialog() {
  editedClient.value = {...client.value};
  editDialog.value = true;
}

// Сохранить изменения профиля
function saveProfile() {
  // В реальном приложении здесь будет запрос к API
  client.value = {...editedClient.value};
  editDialog.value = false;
  
  // Показываем уведомление
  alert('Профиль успешно обновлен');
}

// Сохранить настройки уведомлений
function saveNotificationSettings() {
  // В реальном приложении здесь будет запрос к API
  
  // Показываем уведомление
  alert('Настройки уведомлений сохранены');
}

// Просмотр истории чата
function viewChatHistory(chat) {
  selectedChat.value = chat;
  
  // Загрузка сообщений из истории (имитация)
  if (chat.id === 1) {
    selectedChatMessages.value = [
      {
        sender: 'client',
        text: 'Здравствуйте! У меня проблема с заказом №12345',
        time: new Date('2023-10-12T14:30:00'),
      },
      {
        sender: 'operator',
        text: 'Добрый день! Я посмотрю информацию по вашему заказу. Минутку, пожалуйста.',
        time: new Date('2023-10-12T14:31:00'),
      },
      {
        sender: 'operator',
        text: 'Я проверил ваш заказ. Он находится на стадии комплектации и будет отправлен завтра.',
        time: new Date('2023-10-12T14:33:00'),
      },
      {
        sender: 'client',
        text: 'Спасибо за информацию! А можно уточнить, каким способом будет доставка?',
        time: new Date('2023-10-12T14:34:00'),
      },
      {
        sender: 'operator',
        text: 'Ваш заказ будет доставлен курьером. Ожидаемая дата доставки - 15 октября.',
        time: new Date('2023-10-12T14:36:00'),
      },
      {
        sender: 'client',
        text: 'Отлично, спасибо за помощь!',
        time: new Date('2023-10-12T14:37:00'),
      },
      {
        sender: 'operator',
        text: 'Всегда рад помочь! Если возникнут еще вопросы, обращайтесь.',
        time: new Date('2023-10-12T14:38:00'),
      },
    ];
  } else if (chat.id === 2) {
    selectedChatMessages.value = [
      {
        sender: 'client',
        text: 'Добрый день! Хочу уточнить статус моего заказа №67890',
        time: new Date('2023-09-28T10:15:00'),
      },
      {
        sender: 'operator',
        text: 'Здравствуйте! Сейчас проверю информацию по вашему заказу.',
        time: new Date('2023-09-28T10:16:00'),
      },
      {
        sender: 'operator',
        text: 'Ваш заказ уже доставлен в пункт выдачи. Вы можете забрать его в любое удобное время.',
        time: new Date('2023-09-28T10:18:00'),
      },
      {
        sender: 'client',
        text: 'Спасибо! Подскажите, до какого числа я могу его забрать?',
        time: new Date('2023-09-28T10:19:00'),
      },
      {
        sender: 'operator',
        text: 'Ваш заказ будет храниться в пункте выдачи до 5 октября включительно.',
        time: new Date('2023-09-28T10:20:00'),
      },
      {
        sender: 'client',
        text: 'Понятно, спасибо за информацию!',
        time: new Date('2023-09-28T10:21:00'),
      },
    ];
  } else {
    selectedChatMessages.value = [
      {
        sender: 'client',
        text: 'Здравствуйте, у меня не работает приложение после обновления',
        time: new Date('2023-09-15T16:45:00'),
      },
      {
        sender: 'operator',
        text: 'Добрый день! Давайте разберемся с проблемой. Какое устройство вы используете?',
        time: new Date('2023-09-15T16:46:00'),
      },
      {
        sender: 'client',
        text: 'У меня iPhone 12, iOS 16.5',
        time: new Date('2023-09-15T16:47:00'),
      },
      {
        sender: 'operator',
        text: 'Спасибо за информацию. Пожалуйста, попробуйте следующие шаги: закройте приложение, перезагрузите устройство и запустите приложение снова.',
        time: new Date('2023-09-15T16:49:00'),
      },
      {
        sender: 'client',
        text: 'Я уже пробовал, не помогает',
        time: new Date('2023-09-15T16:51:00'),
      },
      {
        sender: 'operator',
        text: 'В таком случае, попробуйте удалить приложение и установить его заново. Ваши данные сохранятся, так как они привязаны к вашей учетной записи.',
        time: new Date('2023-09-15T16:53:00'),
      },
      {
        sender: 'client',
        text: 'Хорошо, попробую и сообщу о результате',
        time: new Date('2023-09-15T16:54:00'),
      },
      {
        sender: 'operator',
        text: 'Буду ждать вашего ответа. Если проблема не решится, мы можем попробовать другие варианты.',
        time: new Date('2023-09-15T16:55:00'),
      },
      {
        sender: 'client',
        text: 'Помогло! Спасибо за помощь',
        time: new Date('2023-09-15T17:05:00'),
      },
      {
        sender: 'operator',
        text: 'Отлично! Рад, что проблема решена. Если возникнут вопросы, обращайтесь снова.',
        time: new Date('2023-09-15T17:06:00'),
      },
    ];
  }
  
  chatHistoryDialog.value = true;
}
</script>

<style scoped>
.chat-history-container {
  max-height: 400px;
  overflow-y: auto;
}

.message-bubble {
  display: inline-block;
  border-radius: 12px;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
}
</style> 