<template>
  <v-container fluid>
    <v-row>
      <v-col cols="12">
        <div class="d-flex align-center">
          <v-btn
            icon
            variant="flat"
            size="small"
            to="/tests"
            class="me-3"
          >
            <v-icon>mdi-arrow-left</v-icon>
          </v-btn>
          <h1 class="text-h4">Результаты теста</h1>
        </div>
      </v-col>
    </v-row>
    
    <v-row v-if="loading">
      <v-col cols="12" class="text-center py-5">
        <v-progress-circular
          indeterminate
          color="primary"
          size="64"
        ></v-progress-circular>
        <div class="mt-4">Загрузка результатов...</div>
      </v-col>
    </v-row>
    
    <v-row v-else-if="error">
      <v-col cols="12">
        <v-alert
          type="error"
          title="Ошибка загрузки"
          text="Не удалось загрузить результаты теста"
        >
          <template v-slot:append>
            <v-btn color="error" @click="loadTestResults">
              Повторить
            </v-btn>
          </template>
        </v-alert>
      </v-col>
    </v-row>
    
    <template v-else>
      <v-row>
        <v-col cols="12">
          <v-card class="mb-4">
            <v-card-title class="pb-1">{{ testData.title }}</v-card-title>
            <v-card-subtitle>{{ testData.category }}</v-card-subtitle>
            
            <v-divider class="mx-4"></v-divider>
            
            <v-card-text>
              <v-row>
                <v-col cols="12" md="8">
                  <p class="text-body-1">{{ testData.description }}</p>
                </v-col>
                
                <v-col cols="12" md="4">
                  <v-list density="compact">
                    <v-list-item>
                      <template v-slot:prepend>
                        <v-icon color="info">mdi-calendar</v-icon>
                      </template>
                      <v-list-item-title>
                        {{ formatDate(testData.completedAt) }}
                      </v-list-item-title>
                      <v-list-item-subtitle>
                        Дата прохождения
                      </v-list-item-subtitle>
                    </v-list-item>
                    
                    <v-list-item>
                      <template v-slot:prepend>
                        <v-icon color="info">mdi-help-circle</v-icon>
                      </template>
                      <v-list-item-title>
                        {{ testData.questionCount }} вопросов
                      </v-list-item-title>
                      <v-list-item-subtitle>
                        Всего вопросов
                      </v-list-item-subtitle>
                    </v-list-item>
                    
                    <v-list-item>
                      <template v-slot:prepend>
                        <v-icon color="info">mdi-check</v-icon>
                      </template>
                      <v-list-item-title>
                        {{ testData.correctAnswers }} правильных
                      </v-list-item-title>
                      <v-list-item-subtitle>
                        Правильные ответы
                      </v-list-item-subtitle>
                    </v-list-item>
                    
                    <v-list-item>
                      <template v-slot:prepend>
                        <v-icon color="info">mdi-timer</v-icon>
                      </template>
                      <v-list-item-title>
                        {{ formatDuration(testData.duration) }}
                      </v-list-item-title>
                      <v-list-item-subtitle>
                        Время прохождения
                      </v-list-item-subtitle>
                    </v-list-item>
                  </v-list>
                </v-col>
              </v-row>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>
      
      <v-row>
        <v-col cols="12" md="6" class="mb-4">
          <v-card height="100%">
            <v-card-title>Общий результат</v-card-title>
            
            <v-card-text class="text-center py-5">
              <v-progress-circular
                :model-value="testData.score"
                :color="getScoreColor(testData.score)"
                size="180"
                width="18"
              >
                <div class="text-h3">{{ testData.score }}%</div>
              </v-progress-circular>
              
              <h3 class="text-h5 mt-6">{{ getScoreMessage(testData.score) }}</h3>
              <p class="text-body-1 mt-2">{{ getScoreDescription(testData.score) }}</p>
            </v-card-text>
          </v-card>
        </v-col>
        
        <v-col cols="12" md="6" class="mb-4">
          <v-card height="100%">
            <v-card-title>Детальная информация</v-card-title>
            
            <v-card-text>
              <v-list>
                <v-list-subheader>Распределение по категориям</v-list-subheader>
                
                <v-list-item
                  v-for="(category, index) in testData.categories"
                  :key="index"
                >
                  <template v-slot:prepend>
                    <v-icon :color="getScoreColor(category.score)">mdi-chart-bar</v-icon>
                  </template>
                  
                  <v-list-item-title>{{ category.name }}</v-list-item-title>
                  
                  <template v-slot:append>
                    <v-chip
                      :color="getScoreColor(category.score)"
                      size="small"
                    >
                      {{ category.score }}%
                    </v-chip>
                  </template>
                </v-list-item>
              </v-list>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>
      
      <v-row>
        <v-col cols="12">
          <v-card>
            <v-card-title class="d-flex align-center">
              <span>Ответы на вопросы</span>
              <v-spacer></v-spacer>
              <v-btn-toggle
                v-model="answersFilter"
                mandatory
                color="primary"
                density="comfortable"
              >
                <v-btn value="all">
                  Все
                </v-btn>
                <v-btn value="correct">
                  Правильные
                </v-btn>
                <v-btn value="incorrect">
                  Неправильные
                </v-btn>
              </v-btn-toggle>
            </v-card-title>
            
            <v-divider></v-divider>
            
            <v-expansion-panels
              v-model="openPanels"
              multiple
              variant="accordion"
            >
              <v-expansion-panel
                v-for="(question, index) in filteredQuestions"
                :key="index"
                :disabled="loading"
                :class="{'bg-success-lighten-5': question.isCorrect, 'bg-error-lighten-5': !question.isCorrect}"
              >
                <v-expansion-panel-title>
                  <div class="d-flex align-center">
                    <v-icon
                      :color="question.isCorrect ? 'success' : 'error'"
                      class="me-2"
                    >
                      {{ question.isCorrect ? 'mdi-check-circle' : 'mdi-close-circle' }}
                    </v-icon>
                    <div>Вопрос {{ index + 1 }}: {{ question.text }}</div>
                  </div>
                </v-expansion-panel-title>
                
                <v-expansion-panel-text>
                  <v-radio-group
                    :model-value="question.selectedAnswer"
                    disabled
                  >
                    <v-radio
                      v-for="(option, i) in question.options"
                      :key="i"
                      :label="option.text"
                      :value="i"
                      :color="getOptionColor(question, i)"
                    ></v-radio>
                  </v-radio-group>
                  
                  <v-alert
                    v-if="!question.isCorrect"
                    type="info"
                    variant="tonal"
                    class="mt-3"
                  >
                    <strong>Правильный ответ:</strong> {{ getCorrectAnswerText(question) }}
                    
                    <div class="mt-2">
                      <strong>Пояснение:</strong> {{ question.explanation }}
                    </div>
                  </v-alert>
                </v-expansion-panel-text>
              </v-expansion-panel>
            </v-expansion-panels>
          </v-card>
        </v-col>
      </v-row>
      
      <v-row class="mt-4">
        <v-col cols="12" class="text-center">
          <v-btn
            color="primary"
            size="large"
            class="me-2"
            to="/tests"
          >
            <v-icon start>mdi-format-list-bulleted</v-icon>
            К списку тестов
          </v-btn>
          
          <v-btn
            v-if="testData.canRetake"
            color="info"
            size="large"
            :to="`/tests/take/${testId}`"
          >
            <v-icon start>mdi-reload</v-icon>
            Пройти заново
          </v-btn>
        </v-col>
      </v-row>
    </template>
  </v-container>
</template>

<script setup>
import { ref, computed, onMounted, watch, inject } from 'vue'
import { useRoute } from 'vue-router'

// Инъекция API сервисов
const testsApi = inject('tests')
const route = useRoute()

// Получаем ID теста из URL
const testId = computed(() => route.params.id)

// Состояния
const loading = ref(true)
const error = ref(false)
const testData = ref({})
const answersFilter = ref('all')
const openPanels = ref([])

// Загрузка результатов теста
const loadTestResults = async () => {
  loading.value = true
  error.value = false
  
  try {
    // В реальном приложении здесь был бы запрос к API
    // await testsApi.getTestResults(testId.value)
    
    // Имитация загрузки данных
    await new Promise(resolve => setTimeout(resolve, 1200))
    
    // Тестовые данные
    testData.value = {
      id: Number(testId.value),
      title: 'Коммуникативные навыки',
      category: 'Soft Skills',
      description: 'Тест оценивает навыки общения, способность выстраивать диалог, слушать собеседника и эффективно доносить информацию.',
      completedAt: new Date() - 86400000 * 2,
      duration: 450, // секунды
      questionCount: 15,
      correctAnswers: 13,
      score: 85,
      canRetake: true,
      categories: [
        { name: 'Активное слушание', score: 90 },
        { name: 'Эмпатия', score: 75 },
        { name: 'Убедительность', score: 92 },
        { name: 'Решение конфликтов', score: 83 }
      ],
      questions: [
        {
          text: 'Какой из следующих способов является наиболее эффективным для начала разговора с незнакомым человеком?',
          options: [
            { text: 'Говорить о себе и своих достижениях' },
            { text: 'Задать открытый вопрос по теме, которая может быть интересна собеседнику' },
            { text: 'Критиковать что-то, что вас обоих касается' },
            { text: 'Поделиться негативными впечатлениями о ком-то известном вам обоим' }
          ],
          correctAnswer: 1,
          selectedAnswer: 1,
          isCorrect: true,
          explanation: 'Открытые вопросы побуждают к разговору и показывают ваш интерес к собеседнику.'
        },
        {
          text: 'Что означает термин "активное слушание"?',
          options: [
            { text: 'Слушать, периодически кивая головой' },
            { text: 'Перебивать собеседника, чтобы показать свою заинтересованность' },
            { text: 'Полностью сосредоточиться на словах собеседника, задавать уточняющие вопросы и перефразировать услышанное' },
            { text: 'Слушать только ту информацию, которая вам интересна' }
          ],
          correctAnswer: 2,
          selectedAnswer: 2,
          isCorrect: true,
          explanation: 'Активное слушание предполагает полное внимание к собеседнику и использование техник, подтверждающих понимание.'
        },
        {
          text: 'Какой из следующих способов не является эффективным для разрешения конфликта?',
          options: [
            { text: 'Поиск компромисса' },
            { text: 'Вызов посредника для разрешения спора' },
            { text: 'Игнорирование проблемы в надежде, что она разрешится сама собой' },
            { text: 'Открытое обсуждение причин конфликта' }
          ],
          correctAnswer: 2,
          selectedAnswer: 0,
          isCorrect: false,
          explanation: 'Игнорирование проблемы обычно приводит к ее усугублению, а не к разрешению.'
        },
        // Другие вопросы скрыты для краткости
      ]
    }
  } catch (e) {
    console.error('Ошибка загрузки результатов теста:', e)
    error.value = true
  } finally {
    loading.value = false
  }
}

// Фильтрация вопросов
const filteredQuestions = computed(() => {
  if (!testData.value.questions) return []
  
  switch (answersFilter.value) {
    case 'correct':
      return testData.value.questions.filter(q => q.isCorrect)
    case 'incorrect':
      return testData.value.questions.filter(q => !q.isCorrect)
    default:
      return testData.value.questions
  }
})

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
  const minutes = Math.floor(seconds / 60)
  const secs = seconds % 60
  return `${minutes} мин. ${secs} сек.`
}

function getScoreColor(score) {
  if (score >= 80) return 'success'
  if (score >= 60) return 'warning'
  return 'error'
}

function getScoreMessage(score) {
  if (score >= 90) return 'Отличный результат!'
  if (score >= 75) return 'Хороший результат'
  if (score >= 50) return 'Средний результат'
  return 'Требуется улучшение'
}

function getScoreDescription(score) {
  if (score >= 90) {
    return 'Вы продемонстрировали превосходные знания и навыки в данной области!'
  } else if (score >= 75) {
    return 'У вас хороший уровень знаний, но есть некоторые аспекты, которые можно улучшить.'
  } else if (score >= 50) {
    return 'Вы обладаете базовыми знаниями, но требуется дополнительное обучение.'
  } else {
    return 'Рекомендуется более тщательное изучение материала и дополнительная практика.'
  }
}

function getOptionColor(question, optionIndex) {
  if (optionIndex === question.correctAnswer) {
    return 'success'
  }
  if (optionIndex === question.selectedAnswer && !question.isCorrect) {
    return 'error'
  }
  return ''
}

function getCorrectAnswerText(question) {
  return question.options[question.correctAnswer].text
}

// Следим за изменением ID теста
watch(testId, () => {
  loadTestResults()
})

// Инициализация компонента
onMounted(() => {
  loadTestResults()
})
</script> 