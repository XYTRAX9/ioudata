<template>
  <v-container fluid>
    <v-row>
      <v-col cols="12" class="mb-3">
        <h1 class="text-h4">Доступные тесты</h1>
        <p class="text-subtitle-1 mt-2">
          Проходите тесты для оценки уровня стресса и профессиональных навыков
        </p>
      </v-col>
    </v-row>
    
    <v-row v-if="loading">
      <v-col cols="12" class="text-center py-5">
        <v-progress-circular
          indeterminate
          color="primary"
          size="64"
        ></v-progress-circular>
        <div class="mt-4">Загрузка тестов...</div>
      </v-col>
    </v-row>
    
    <template v-else>
      <v-row v-if="tests.length === 0">
        <v-col cols="12" class="text-center py-5">
          <v-icon size="64" color="grey">mdi-clipboard-text-outline</v-icon>
          <h3 class="text-h5 mt-4">Нет доступных тестов</h3>
          <p class="text-body-1 mt-2">В данный момент нет тестов, доступных для прохождения</p>
        </v-col>
      </v-row>
      
      <v-row v-else>
        <v-col
          v-for="(test, index) in tests"
          :key="index"
          cols="12"
          sm="6"
          md="4"
        >
          <v-card
            class="h-100"
            :class="{ 'border-success': test.completed }"
            hover
          >
            <v-card-title class="d-flex align-center">
              <div>{{ test.title }}</div>
              <v-spacer></v-spacer>
              <v-chip
                :color="test.completed ? 'success' : 'primary'"
                size="small"
              >
                {{ test.completed ? 'Пройден' : 'Новый' }}
              </v-chip>
            </v-card-title>
            
            <v-card-subtitle>
              <v-icon size="small" class="me-1">mdi-folder</v-icon> 
              {{ test.category }}
            </v-card-subtitle>
            
            <v-card-text>
              <p class="text-body-1">{{ test.description }}</p>
              
              <v-list density="compact" class="bg-transparent">
                <v-list-item>
                  <template v-slot:prepend>
                    <v-icon color="info">mdi-help-circle</v-icon>
                  </template>
                  <v-list-item-subtitle>
                    Вопросов: {{ test.questionCount }}
                  </v-list-item-subtitle>
                </v-list-item>
                
                <v-list-item>
                  <template v-slot:prepend>
                    <v-icon color="warning">mdi-clock</v-icon>
                  </template>
                  <v-list-item-subtitle>
                    Время: {{ test.timeLimit }} минут
                  </v-list-item-subtitle>
                </v-list-item>
                
                <v-list-item v-if="test.completed">
                  <template v-slot:prepend>
                    <v-icon color="success">mdi-check-decagram</v-icon>
                  </template>
                  <v-list-item-subtitle>
                    Результат: {{ test.score }}%
                  </v-list-item-subtitle>
                </v-list-item>
              </v-list>
            </v-card-text>
            
            <v-divider></v-divider>
            
            <v-card-actions>
              <v-btn
                v-if="!test.completed"
                color="primary"
                variant="flat"
                :to="`/tests/take/${test.id}`"
              >
                Пройти тест
              </v-btn>
              
              <v-btn
                v-else
                color="info"
                variant="flat"
                :to="`/tests/results/${test.id}`"
              >
                Просмотреть результаты
              </v-btn>
              
              <v-spacer></v-spacer>
              
              <v-btn
                icon
                variant="text"
                @click="test.showDetails = !test.showDetails"
              >
                <v-icon>
                  {{ test.showDetails ? 'mdi-chevron-up' : 'mdi-chevron-down' }}
                </v-icon>
              </v-btn>
            </v-card-actions>
            
            <v-expand-transition>
              <div v-if="test.showDetails">
                <v-divider></v-divider>
                <v-card-text>
                  <h3 class="text-subtitle-1 font-weight-bold mb-2">Детали теста</h3>
                  <p>{{ test.detailedDescription }}</p>
                  
                  <h3 class="text-subtitle-1 font-weight-bold mt-3 mb-2">Кому рекомендуется</h3>
                  <v-chip-group>
                    <v-chip
                      v-for="(tag, i) in test.tags"
                      :key="i"
                      size="small"
                      color="secondary"
                      class="me-1"
                    >
                      {{ tag }}
                    </v-chip>
                  </v-chip-group>
                </v-card-text>
              </div>
            </v-expand-transition>
          </v-card>
        </v-col>
      </v-row>
    </template>
  </v-container>
</template>

<script setup>
import { ref, onMounted, inject } from 'vue'

// API сервисы
const testsApi = inject('tests')

// Состояния
const tests = ref([])
const loading = ref(true)

// Загрузка тестов
const loadTests = async () => {
  loading.value = true
  
  try {
    // Здесь был бы запрос к API для получения списка тестов
    // Используем тестовые данные
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    tests.value = [
      {
        id: 1,
        title: 'Стрессоустойчивость',
        category: 'Психология',
        description: 'Оценка уровня стрессоустойчивости и психологического состояния',
        detailedDescription: 'Тест позволяет определить ваш текущий уровень стресса и способность справляться с различными стрессовыми ситуациями. Основан на методиках оценки психологического состояния.',
        questionCount: 20,
        timeLimit: 15,
        completed: false,
        score: null,
        tags: ['Все сотрудники', 'Новички', 'Обязательный'],
        showDetails: false
      },
      {
        id: 2,
        title: 'Коммуникативные навыки',
        category: 'Soft Skills',
        description: 'Оценка навыков общения и коммуникаций с клиентами',
        detailedDescription: 'Тест оценивает ваши навыки общения, способность выстраивать диалог, слушать собеседника и эффективно доносить информацию.',
        questionCount: 15,
        timeLimit: 10,
        completed: true,
        score: 85,
        tags: ['Операторы', 'Менеджеры', 'Soft skills'],
        showDetails: false
      },
      {
        id: 3,
        title: 'Профессиональные знания',
        category: 'Hard Skills',
        description: 'Проверка знаний в профессиональной области',
        detailedDescription: 'Тест проверяет уровень профессиональных знаний, необходимых для выполнения ваших рабочих обязанностей.',
        questionCount: 30,
        timeLimit: 25,
        completed: false,
        score: null,
        tags: ['Специалисты', 'Профессиональный рост'],
        showDetails: false
      },
      {
        id: 4,
        title: 'Эмоциональный интеллект',
        category: 'Психология',
        description: 'Оценка способности понимать эмоции и управлять ими',
        detailedDescription: 'Тест направлен на определение уровня эмоционального интеллекта: способности распознавать эмоции, понимать намерения и мотивацию других людей и свои собственные, а также управлять своими эмоциями и влиять на эмоции других людей.',
        questionCount: 25,
        timeLimit: 20,
        completed: true,
        score: 92,
        tags: ['Все сотрудники', 'Личностный рост'],
        showDetails: false
      }
    ]
  } catch (error) {
    console.error('Ошибка загрузки тестов:', error)
  } finally {
    loading.value = false
  }
}

// Инициализация страницы
onMounted(() => {
  loadTests()
})
</script>

<style scoped>
.border-success {
  border: 2px solid rgb(var(--v-theme-success));
}
</style> 