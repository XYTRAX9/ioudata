<template>
  <v-container fluid>
    <v-row>
      <v-col cols="12">
        <v-card>
          <v-card-title class="d-flex align-center justify-space-between">
            <span>Управление тестами</span>
        <v-btn 
          color="primary" 
          prepend-icon="mdi-plus" 
              @click="openCreateDialog"
        >
          Создать тест
        </v-btn>
          </v-card-title>

      <v-card-text>
      <v-data-table
        :headers="headers"
              :items="tests"
        :loading="loading"
              item-value="id"
        class="elevation-1"
      >
              <template v-slot:item.is_active="{ item }">
          <v-chip
                  :color="item.raw.is_active ? 'success' : 'grey'"
            size="small"
          >
                  {{ item.raw.is_active ? 'Активен' : 'Неактивен' }}
          </v-chip>
        </template>

        <template v-slot:item.actions="{ item }">
          <v-btn
            icon
                  size="small"
                  color="primary"
            variant="text"
            @click="viewTest(item.raw)"
          >
            <v-icon>mdi-eye</v-icon>
          </v-btn>
                <v-btn
                  icon
                  size="small"
                  color="warning"
                  variant="text"
                  @click="toggleTestStatus(item.raw)"
                >
                  <v-icon>
                    {{ item.raw.is_active ? 'mdi-close-circle' : 'mdi-check-circle' }}
                  </v-icon>
                </v-btn>
                <v-btn
                  icon
                  size="small"
                  color="error"
                  variant="text"
                  @click="confirmDeleteTest(item.raw)"
                >
                  <v-icon>mdi-delete</v-icon>
                </v-btn>
              </template>
            </v-data-table>
        </v-card-text>
      </v-card>
      </v-col>
    </v-row>

    <!-- Диалог создания теста -->
    <v-dialog v-model="createDialog" max-width="800px" persistent>
      <v-card>
        <v-card-title>Создание нового теста</v-card-title>
        <v-card-text>
          <v-form ref="testForm" v-model="formValid">
            <v-row>
              <v-col cols="12">
            <v-text-field
                  v-model="newTest.title"
              label="Название теста"
              required
              :rules="[v => !!v || 'Название обязательно']"
            ></v-text-field>
              </v-col>
              
              <v-col cols="12">
                <v-textarea
                  v-model="newTest.description"
                  label="Описание теста"
                  rows="3"
              required
              :rules="[v => !!v || 'Описание обязательно']"
                ></v-textarea>
              </v-col>
            </v-row>

            <v-divider class="my-4"></v-divider>
            
            <h3 class="text-h6 mb-3">Вопросы</h3>

            <div v-for="(question, i) in newTest.questions" :key="i" class="mb-5">
              <v-card variant="outlined" class="pa-3">
                <div class="d-flex justify-space-between align-center mb-2">
                  <h4 class="text-subtitle-1">Вопрос {{ i + 1 }}</h4>
                <v-btn
                  icon
                  size="small"
                  color="error"
                  variant="text"
                    @click="removeQuestion(i)"
                    v-if="newTest.questions.length > 1"
                >
                    <v-icon>mdi-close</v-icon>
                </v-btn>
              </div>
              
              <v-text-field
                v-model="question.text"
                label="Текст вопроса"
                required
                :rules="[v => !!v || 'Текст вопроса обязателен']"
              ></v-text-field>

                <v-radio-group
                  v-model="question.correct_option"
                  label="Правильный ответ"
                  class="mt-3"
                >
                  <div v-for="(option, j) in question.options" :key="j" class="d-flex align-center">
                    <v-radio :value="j"></v-radio>
                    <v-text-field
                      v-model="question.options[j]"
                      :label="`Вариант ${j + 1}`"
                      class="ml-2"
                      required
                      :rules="[v => !!v || 'Вариант ответа обязателен']"
                    ></v-text-field>
                  </div>
                </v-radio-group>
              </v-card>
              </div>
              
            <div class="d-flex justify-center my-4">
              <v-btn
                color="primary"
                prepend-icon="mdi-plus"
                @click="addQuestion"
              >
                Добавить вопрос
              </v-btn>
            </div>
          </v-form>
        </v-card-text>
        
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn 
            color="grey-darken-1" 
            variant="text" 
            @click="createDialog = false"
          >
            Отмена
          </v-btn>
          <v-btn 
            color="primary" 
            variant="text"
            :disabled="!formValid"
            @click="createTest"
          >
            Создать
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Диалог просмотра теста -->
    <v-dialog v-model="viewDialog" max-width="700px">
      <v-card v-if="selectedTest">
        <v-card-title>
          {{ selectedTest.title }}
          <v-spacer></v-spacer>
          <v-btn icon @click="viewDialog = false">
            <v-icon>mdi-close</v-icon>
          </v-btn>
        </v-card-title>
        
        <v-card-text>
          <p class="text-body-1 mb-4">{{ selectedTest.description }}</p>

          <v-divider class="mb-4"></v-divider>

          <div v-for="(question, i) in selectedTest.questions" :key="i" class="mb-4">
            <h3 class="text-subtitle-1 font-weight-bold mb-2">
              Вопрос {{ i + 1 }}: {{ question.text }}
            </h3>
            
            <v-list dense>
              <v-list-item
                v-for="(option, j) in question.options"
                :key="j"
                :class="{ 'bg-light-green-lighten-5': j === question.correct_option }"
              >
                <template v-slot:prepend>
                  <v-icon
                    v-if="j === question.correct_option"
                    color="success"
                    size="small"
                  >
                    mdi-check-circle
                  </v-icon>
                  <v-icon v-else color="grey" size="small">mdi-circle-outline</v-icon>
                </template>
                <v-list-item-title>{{ option }}</v-list-item-title>
              </v-list-item>
            </v-list>
          </div>
        </v-card-text>
      </v-card>
    </v-dialog>

    <!-- Диалог подтверждения удаления -->
    <v-dialog v-model="deleteDialog" max-width="500px">
      <v-card>
        <v-card-title>Подтверждение удаления</v-card-title>
        <v-card-text>
          Вы уверены, что хотите удалить тест "{{ selectedTest?.title }}"?
          Это действие нельзя отменить.
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn 
            color="grey-darken-1" 
            variant="text" 
            @click="deleteDialog = false"
          >
            Отмена
          </v-btn>
          <v-btn 
            color="error" 
            variant="text" 
            @click="deleteTest"
          >
            Удалить
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script>
import axios from 'axios'
import { useSnackbar } from '@/composables/useSnackbar'

export default {
  name: 'AdminTestsPage',
  
  setup() {
    const { showSnackbar } = useSnackbar()
    return { showSnackbar }
  },
  
  data() {
    return {
      tests: [],
      loading: false,
      
      headers: [
        { title: 'ID', key: 'id', sortable: true },
        { title: 'Название', key: 'title', sortable: true },
        { title: 'Вопросов', key: 'question_count', sortable: true },
        { title: 'Статус', key: 'is_active', sortable: true },
        { title: 'Действия', key: 'actions', sortable: false, align: 'end' }
      ],
      
      createDialog: false,
      viewDialog: false,
      deleteDialog: false,
      
      formValid: false,
      selectedTest: null,
      
      newTest: {
        title: '',
        description: '',
    questions: [
      {
            text: '',
            options: ['', '', '', ''],
            correct_option: 0
          }
        ]
      }
    }
  },
  
  mounted() {
    this.fetchTests()
  },
  
  methods: {
    async fetchTests() {
      this.loading = true
      
      try {
        const response = await axios.get('/api/tests/multiple-choice')
        
        // Добавляем вычисляемое поле с количеством вопросов
        this.tests = response.data.map(test => ({
          ...test,
          question_count: test.questions ? test.questions.length : 0
        }))
      } catch (error) {
        console.error('Error fetching tests:', error)
        this.showSnackbar({
          text: 'Не удалось загрузить список тестов',
          color: 'error'
        })
      } finally {
        this.loading = false
      }
    },
    
    openCreateDialog() {
      this.newTest = {
  title: '',
  description: '',
        questions: [
          {
            text: '',
            options: ['', '', '', ''],
            correct_option: 0
          }
        ]
      }
      
      this.createDialog = true
      this.formValid = false
      
      // Сбрасываем валидацию формы, если она уже была инициализирована
      if (this.$refs.testForm) {
        this.$refs.testForm.resetValidation()
      }
    },
    
    addQuestion() {
      this.newTest.questions.push({
    text: '',
        options: ['', '', '', ''],
        correct_option: 0
      })
    },
    
    removeQuestion(index) {
      if (this.newTest.questions.length > 1) {
        this.newTest.questions.splice(index, 1)
      }
    },
    
    async createTest() {
      try {
        await axios.post('/api/tests/multiple-choice/', this.newTest)
        
        this.showSnackbar({
          text: 'Тест успешно создан',
          color: 'success'
        })
        
        this.createDialog = false
        this.fetchTests()
      } catch (error) {
        console.error('Error creating test:', error)
        this.showSnackbar({
          text: error.response?.data?.detail || 'Не удалось создать тест',
          color: 'error'
        })
      }
    },
    
    viewTest(test) {
      this.selectedTest = test
      this.viewDialog = true
    },
    
    async toggleTestStatus(test) {
      try {
        await axios.put(`/api/tests/multiple-choice/${test.id}/toggle-status`)
        
        this.showSnackbar({
          text: `Тест ${test.is_active ? 'деактивирован' : 'активирован'}`,
          color: 'success'
        })
        
        this.fetchTests()
      } catch (error) {
        console.error('Error toggling test status:', error)
        this.showSnackbar({
          text: error.response?.data?.detail || 'Не удалось изменить статус теста',
          color: 'error'
        })
      }
    },
    
    confirmDeleteTest(test) {
      this.selectedTest = test
      this.deleteDialog = true
    },
    
    async deleteTest() {
      if (!this.selectedTest) return
      
      try {
        await axios.delete(`/api/tests/multiple-choice/${this.selectedTest.id}`)
        
        this.showSnackbar({
          text: 'Тест успешно удален',
          color: 'success'
        })
        
        this.deleteDialog = false
        this.fetchTests()
      } catch (error) {
        console.error('Error deleting test:', error)
        this.showSnackbar({
          text: error.response?.data?.detail || 'Не удалось удалить тест',
          color: 'error'
        })
      }
    }
  }
}
</script> 