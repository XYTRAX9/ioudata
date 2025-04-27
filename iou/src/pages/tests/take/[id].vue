<template>
  <v-container>
    <div v-if="loading" class="d-flex justify-center align-center" style="height: 300px;">
      <v-progress-circular
        indeterminate
        color="primary"
        size="64"
      ></v-progress-circular>
    </div>

    <div v-else>
      <v-card class="mb-4">
        <v-card-title>{{ test.title }}</v-card-title>
        <v-card-subtitle>{{ test.category }}</v-card-subtitle>
        <v-card-text>
          <p>{{ test.description }}</p>
          <div class="mt-2 d-flex align-center">
            <v-icon color="info" class="mr-2">mdi-clock-outline</v-icon>
            <span>Ограничение по времени: {{ test.timeLimit }} минут</span>
            <v-spacer></v-spacer>
            <span>Вопрос {{ currentQuestionIndex + 1 }} из {{ test.questions.length }}</span>
          </div>
          <v-progress-linear
            v-model="progressPercent"
            color="primary"
            height="10"
            class="mt-2"
          ></v-progress-linear>
        </v-card-text>
      </v-card>

      <v-card>
        <v-card-title>
          {{ currentQuestion.text }}
        </v-card-title>
        <v-card-text>
          <v-radio-group v-model="selectedAnswer">
            <v-radio
              v-for="(option, index) in currentQuestion.options"
              :key="index"
              :label="option.text"
              :value="index"
              color="primary"
            ></v-radio>
          </v-radio-group>
        </v-card-text>
        <v-card-actions>
          <v-btn
            v-if="currentQuestionIndex > 0"
            color="secondary"
            @click="prevQuestion"
          >
            Назад
          </v-btn>
          <v-spacer></v-spacer>
          <v-btn
            v-if="currentQuestionIndex < test.questions.length - 1"
            color="primary"
            @click="nextQuestion"
            :disabled="selectedAnswer === null"
          >
            Далее
          </v-btn>
          <v-btn
            v-else
            color="success"
            @click="submitTest"
            :disabled="selectedAnswer === null"
          >
            Завершить тест
          </v-btn>
        </v-card-actions>
      </v-card>

      <v-dialog v-model="resultDialog" max-width="600">
        <v-card>
          <v-card-title>Результаты теста</v-card-title>
          <v-card-text>
            <h3 class="text-h5 mb-3">{{ test.title }}</h3>
            <p class="text-h6">Правильных ответов: {{ correctAnswers }} из {{ test.questions.length }}</p>
            <v-progress-linear
              :model-value="(correctAnswers / test.questions.length) * 100"
              color="success"
              height="20"
              striped
            >
              <template v-slot:default="{ value }">
                <strong>{{ Math.ceil(value) }}%</strong>
              </template>
            </v-progress-linear>
          </v-card-text>
          <v-card-actions>
            <v-spacer></v-spacer>
            <v-btn color="primary" to="/tests">К списку тестов</v-btn>
          </v-card-actions>
        </v-card>
      </v-dialog>
    </div>
  </v-container>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';

const route = useRoute();
const router = useRouter();
const testId = route.params.id;

const loading = ref(true);
const test = ref({});
const currentQuestionIndex = ref(0);
const selectedAnswer = ref(null);
const answers = ref([]);
const resultDialog = ref(false);
const correctAnswers = ref(0);

const currentQuestion = computed(() => {
  if (test.value.questions && test.value.questions.length > 0) {
    return test.value.questions[currentQuestionIndex.value];
  }
  return { text: '', options: [] };
});

const progressPercent = computed(() => {
  return (currentQuestionIndex.value / (test.value.questions?.length - 1)) * 100;
});

function nextQuestion() {
  answers.value[currentQuestionIndex.value] = selectedAnswer.value;
  if (currentQuestionIndex.value < test.value.questions.length - 1) {
    currentQuestionIndex.value++;
    selectedAnswer.value = answers.value[currentQuestionIndex.value] !== undefined 
      ? answers.value[currentQuestionIndex.value] 
      : null;
  }
}

function prevQuestion() {
  answers.value[currentQuestionIndex.value] = selectedAnswer.value;
  if (currentQuestionIndex.value > 0) {
    currentQuestionIndex.value--;
    selectedAnswer.value = answers.value[currentQuestionIndex.value];
  }
}

function submitTest() {
  answers.value[currentQuestionIndex.value] = selectedAnswer.value;
  
  // Вычисляем количество правильных ответов
  correctAnswers.value = 0;
  answers.value.forEach((answer, index) => {
    const question = test.value.questions[index];
    if (answer !== null && question.options[answer].correct) {
      correctAnswers.value++;
    }
  });

  // Показываем результаты
  resultDialog.value = true;

  // В реальном приложении здесь будет отправка результатов на сервер
  // submitTestResults();
}

// Функция для отправки результатов на сервер
async function submitTestResults() {
  try {
    const response = await fetch(`/tests/multiple-choice/${testId}/submit`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        answers: answers.value,
      }),
    });
    
    if (response.ok) {
      const result = await response.json();
      correctAnswers.value = result.correctAnswers;
      resultDialog.value = true;
    } else {
      console.error('Ошибка при отправке результатов');
    }
  } catch (error) {
    console.error('Ошибка:', error);
  }
}

// Загрузка теста
onMounted(async () => {
  // В реальном приложении данные будут загружены с сервера
  // Имитация загрузки данных
  setTimeout(() => {
    test.value = {
      id: testId,
      title: 'Тест на знание продукта',
      category: 'Профессиональные навыки',
      description: 'Проверка знаний о продуктах и услугах компании',
      timeLimit: 30,
      questions: [
        {
          text: 'Какой основной продукт компании?',
          options: [
            { text: 'Программное обеспечение', correct: true },
            { text: 'Аппаратные средства', correct: false },
            { text: 'Консультационные услуги', correct: false },
            { text: 'Облачные сервисы', correct: false },
          ],
        },
        {
          text: 'Какой срок гарантии на продукты компании?',
          options: [
            { text: '1 год', correct: false },
            { text: '2 года', correct: true },
            { text: '3 года', correct: false },
            { text: 'Без гарантии', correct: false },
          ],
        },
        {
          text: 'Какой канал поддержки клиентов наиболее предпочтителен?',
          options: [
            { text: 'Телефон', correct: false },
            { text: 'Электронная почта', correct: false },
            { text: 'Онлайн-чат', correct: true },
            { text: 'Социальные сети', correct: false },
          ],
        },
      ],
    };
    
    // Инициализация массива ответов
    answers.value = Array(test.value.questions.length).fill(null);
    
    loading.value = false;
  }, 1000);

  // В реальном приложении данные будут загружены с сервера
  // try {
  //   const response = await fetch(`/tests/multiple-choice/${testId}`);
  //   if (response.ok) {
  //     test.value = await response.json();
  //     answers.value = Array(test.value.questions.length).fill(null);
  //     loading.value = false;
  //   } else {
  //     console.error('Ошибка при загрузке теста');
  //   }
  // } catch (error) {
  //   console.error('Ошибка:', error);
  // }
});
</script> 