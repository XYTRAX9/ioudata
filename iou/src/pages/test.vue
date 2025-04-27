<template>
    <v-container class="mx-auto" width="800">
      <h1 class="text-h4 mb-6">Управление тестами</h1>
      
      <!-- Создание нового теста -->
      <v-card class="mb-6 pa-4">
        <v-text-field v-model="newTestTitle" label="Название теста" outlined></v-text-field>
        <v-btn color="primary" @click="addTest">Создать тест</v-btn>
      </v-card>
      
      <!-- Список тестов -->
      <v-card v-for="(test, index) in tests" :key="test.id" class="mb-4">
        <v-card-title>
          <v-text-field v-model="test.title" outlined hide-details></v-text-field>
        </v-card-title>
        
        <v-card-text>
          <!-- Вопросы теста -->
          <div v-for="(question, qIndex) in test.questions" :key="qIndex" class="mb-4">
            <v-text-field v-model="question.text" label="Вопрос" outlined class="mb-2"></v-text-field>
            
            <!-- Варианты ответов (фиксированные 4 варианта) -->
            <div v-for="(answer, aIndex) in question.answers" :key="aIndex" class="d-flex align-center mb-2">
              <v-checkbox v-model="answer.isCorrect" hide-details class="mr-2"></v-checkbox>
              <v-text-field v-model="answer.text" :label="'Ответ ' + (aIndex + 1)" outlined hide-details></v-text-field>
            </div>
            
            <v-btn color="error" @click="removeQuestion(test.id, qIndex)">Удалить вопрос</v-btn>
          </div>
          
          <v-btn color="primary" @click="addQuestion(test.id)" class="mr-2">+ Вопрос</v-btn>
        </v-card-text>
        
        <v-card-actions>
          <v-btn color="success" @click="saveTest(test)">Сохранить</v-btn>
          <v-btn color="error" @click="removeTest(index)">Удалить тест</v-btn>
          <v-spacer></v-spacer>
          <v-btn color="info" @click="viewResults(test)">Результаты</v-btn>
        </v-card-actions>
      </v-card>
      
      <!-- Диалог результатов -->
      <v-dialog v-model="resultsDialog" max-width="600">
        <v-card>
          <v-card-title>Результаты теста: {{ currentTest?.title }}</v-card-title>
          <v-card-text>
            <v-simple-table>
              <template v-slot:default>
                <thead>
                  <tr>
                    <th>Пользователь</th>
                    <th>Дата</th>
                    <th>Результат</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="(result, index) in testResults" :key="index">
                    <td>{{ result.user }}</td>
                    <td>{{ result.date }}</td>
                    <td>{{ result.score }}%</td>
                  </tr>
                </tbody>
              </template>
            </v-simple-table>
          </v-card-text>
          <v-card-actions>
            <v-spacer></v-spacer>
            <v-btn color="primary" @click="resultsDialog = false">Закрыть</v-btn>
          </v-card-actions>
        </v-card>
      </v-dialog>
    </v-container>
  </template>
  
  <script setup>
  import { ref } from 'vue';
  
  const newTestTitle = ref('');
  const tests = ref([
    {
      id: 1,
      title: 'Пример теста',
      questions: [
        {
          text: 'Какой язык программирования вы изучаете?',
          answers: [
            { text: 'JavaScript', isCorrect: true },
            { text: 'Python', isCorrect: false },
            { text: 'Java', isCorrect: false },
            { text: 'C++', isCorrect: false }
          ]
        }
      ]
    }
  ]);
  
  const resultsDialog = ref(false);
  const currentTest = ref(null);
  const testResults = ref([
    { user: 'Иван Иванов', date: '2023-05-15', score: 85 },
    { user: 'Петр Петров', date: '2023-05-16', score: 92 }
  ]);
  
  function addTest() {
    if (!newTestTitle.value) return;
    
    tests.value.push({
      id: Date.now(),
      title: newTestTitle.value,
      questions: []
    });
    
    newTestTitle.value = '';
  }
  
  function removeTest(index) {
    tests.value.splice(index, 1);
  }
  
  function addQuestion(testId) {
    const test = tests.value.find(t => t.id === testId);
    if (test) {
      test.questions.push({
        text: '',
        answers: [
          { text: '', isCorrect: false },
          { text: '', isCorrect: false },
          { text: '', isCorrect: false },
          { text: '', isCorrect: false }
        ]
      });
    }
  }
  
  function removeQuestion(testId, questionIndex) {
    const test = tests.value.find(t => t.id === testId);
    if (test) {
      test.questions.splice(questionIndex, 1);
    }
  }
  
  function saveTest(test) {
    console.log('Сохранен тест:', test);
    // Здесь должна быть логика сохранения на сервер
  }
  
  function viewResults(test) {
    currentTest.value = test;
    resultsDialog.value = true;
  }
  </script>
  
  <style scoped>
  .v-card {
    transition: all 0.3s ease;
  }
  </style>