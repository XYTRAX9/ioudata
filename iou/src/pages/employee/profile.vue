<template>
  <v-container>
    <h1 class="text-h4 mb-4">Профиль сотрудника</h1>
    
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
            <div class="text-h5 mb-2">{{ employee.name }}</div>
            <div class="text-subtitle-1 mb-1">ID: {{ employee.id }}</div>
            <div class="text-body-1 mb-1">Email: {{ employee.email }}</div>
            <div class="text-body-1 mb-1">Группа: {{ employee.group }}</div>
            <div class="text-body-1 mb-1">
              Уровень стресса: 
              <v-progress-linear
                v-model="employee.stressLevel"
                color="error"
                height="20"
                striped
              >
                <template v-slot:default="{ value }">
                  <strong>{{ Math.ceil(value) }}%</strong>
                </template>
              </v-progress-linear>
            </div>
          </v-col>
        </v-row>
      </v-card-text>
    </v-card>

    <v-card class="mb-4">
      <v-card-title>История коммуникаций</v-card-title>
      <v-card-text>
        <v-data-table
          :headers="communicationHeaders"
          :items="communicationHistory"
          :items-per-page="5"
          class="elevation-1"
        ></v-data-table>
      </v-card-text>
    </v-card>

    <v-card>
      <v-card-title>Результаты тестов</v-card-title>
      <v-card-text>
        <v-data-table
          :headers="testHeaders"
          :items="testResults"
          :items-per-page="5"
          class="elevation-1"
        ></v-data-table>
      </v-card-text>
    </v-card>
  </v-container>
</template>

<script setup>
import { ref } from 'vue';

// В реальном приложении эти данные будут получены с сервера
const employee = ref({
  id: '1234',
  name: 'Иванов Иван Иванович',
  email: 'ivanov@example.com',
  group: 'Поддержка клиентов',
  stressLevel: 45,
});

const communicationHeaders = ref([
  { title: 'Дата', key: 'date' },
  { title: 'Клиент', key: 'client' },
  { title: 'Тип', key: 'type' },
  { title: 'Продолжительность', key: 'duration' },
  { title: 'Оценка', key: 'rating' },
]);

const communicationHistory = ref([
  {
    date: '2023-10-15',
    client: 'Петров А.С.',
    type: 'Чат',
    duration: '15 мин',
    rating: '5/5',
  },
  {
    date: '2023-10-14',
    client: 'Сидоров В.А.',
    type: 'Чат',
    duration: '8 мин',
    rating: '4/5',
  },
  {
    date: '2023-10-13',
    client: 'Козлов М.И.',
    type: 'Чат',
    duration: '22 мин',
    rating: '3/5',
  },
]);

const testHeaders = ref([
  { title: 'Дата', key: 'date' },
  { title: 'Название теста', key: 'name' },
  { title: 'Результат', key: 'result' },
  { title: 'Оценка', key: 'score' },
]);

const testResults = ref([
  {
    date: '2023-09-20',
    name: 'Тест на стрессоустойчивость',
    result: 'Пройден',
    score: '87/100',
  },
  {
    date: '2023-08-15',
    name: 'Тест на знание продукта',
    result: 'Пройден',
    score: '92/100',
  },
  {
    date: '2023-07-10',
    name: 'Тест на коммуникативные навыки',
    result: 'Пройден',
    score: '78/100',
  },
]);

// Здесь будет логика для получения данных с сервера
// Например:
// onMounted(async () => {
//   try {
//     const response = await fetch('/employees/me');
//     const data = await response.json();
//     employee.value = data;
//   } catch (error) {
//     console.error('Ошибка при получении данных сотрудника:', error);
//   }
// });
</script> 