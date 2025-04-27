<template>
  <v-container>
    <v-row class="mb-4">
      <v-col>
        <h1 class="text-h4">Управление сотрудниками</h1>
      </v-col>
      <v-col cols="auto">
        <v-btn 
          color="primary" 
          prepend-icon="mdi-account-plus" 
          @click="showAddEmployeeDialog"
        >
          Добавить сотрудника
        </v-btn>
      </v-col>
    </v-row>

    <v-card>
      <v-card-text>
        <v-row>
          <v-col cols="12" md="4">
            <v-text-field
              v-model="search"
              label="Поиск"
              prepend-inner-icon="mdi-magnify"
              single-line
              hide-details
              clearable
            ></v-text-field>
          </v-col>
          <v-col cols="12" md="4">
            <v-select
              v-model="groupFilter"
              :items="groups"
              label="Фильтр по группе"
              prepend-inner-icon="mdi-filter"
              clearable
              hide-details
            ></v-select>
          </v-col>
          <v-col cols="12" md="4">
            <v-select
              v-model="statusFilter"
              :items="['Активен', 'Неактивен']"
              label="Фильтр по статусу"
              prepend-inner-icon="mdi-filter"
              clearable
              hide-details
            ></v-select>
          </v-col>
        </v-row>
      </v-card-text>

      <v-data-table
        :headers="headers"
        :items="filteredEmployees"
        :items-per-page="10"
        :loading="loading"
        class="elevation-1"
      >
        <template v-slot:item.avatar="{ item }">
          <v-avatar color="grey lighten-1" size="36">
            <span class="text-caption">{{ item.raw.name.charAt(0) }}</span>
          </v-avatar>
        </template>

        <template v-slot:item.status="{ item }">
          <v-chip
            :color="item.raw.isActive ? 'success' : 'error'"
            size="small"
          >
            {{ item.raw.isActive ? 'Активен' : 'Неактивен' }}
          </v-chip>
        </template>

        <template v-slot:item.stressLevel="{ item }">
          <v-progress-linear
            :model-value="item.raw.stressLevel"
            :color="getStressLevelColor(item.raw.stressLevel)"
            height="10"
            rounded
          ></v-progress-linear>
          <span class="text-caption">{{ item.raw.stressLevel }}%</span>
        </template>

        <template v-slot:item.actions="{ item }">
          <v-btn
            icon
            variant="text"
            size="small"
            @click="viewEmployee(item.raw)"
          >
            <v-icon>mdi-eye</v-icon>
          </v-btn>
          <v-btn
            icon
            variant="text"
            size="small"
            @click="editEmployee(item.raw)"
          >
            <v-icon>mdi-pencil</v-icon>
          </v-btn>
          <v-btn
            icon
            variant="text"
            size="small"
            color="error"
            @click="confirmDeleteEmployee(item.raw)"
          >
            <v-icon>mdi-delete</v-icon>
          </v-btn>
        </template>
      </v-data-table>
    </v-card>

    <!-- Диалог добавления сотрудника -->
    <v-dialog v-model="addEmployeeDialog" max-width="600">
      <v-card>
        <v-card-title>Добавить сотрудника</v-card-title>
        <v-card-text>
          <v-form ref="addForm" v-model="isAddFormValid">
            <v-text-field
              v-model="newEmployee.name"
              label="ФИО"
              required
              :rules="[v => !!v || 'ФИО обязательно']"
            ></v-text-field>
            <v-text-field
              v-model="newEmployee.email"
              label="Email"
              type="email"
              required
              :rules="[
                v => !!v || 'Email обязателен',
                v => /.+@.+\..+/.test(v) || 'Email должен быть действительным'
              ]"
            ></v-text-field>
            <v-text-field
              v-model="newEmployee.password"
              label="Пароль"
              type="password"
              required
              :rules="[v => !!v || 'Пароль обязателен', v => v.length >= 8 || 'Пароль должен быть не менее 8 символов']"
            ></v-text-field>
            <v-select
              v-model="newEmployee.group"
              :items="groups"
              label="Группа"
              required
              :rules="[v => !!v || 'Группа обязательна']"
            ></v-select>
            <v-checkbox
              v-model="newEmployee.isAdmin"
              label="Администратор"
            ></v-checkbox>
          </v-form>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="secondary" @click="addEmployeeDialog = false">Отмена</v-btn>
          <v-btn color="primary" @click="addEmployee" :disabled="!isAddFormValid">Добавить</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Диалог редактирования сотрудника -->
    <v-dialog v-model="editEmployeeDialog" max-width="600">
      <v-card>
        <v-card-title>Редактировать сотрудника</v-card-title>
        <v-card-text>
          <v-form ref="editForm" v-model="isEditFormValid">
            <v-text-field
              v-model="editedEmployee.name"
              label="ФИО"
              required
              :rules="[v => !!v || 'ФИО обязательно']"
            ></v-text-field>
            <v-text-field
              v-model="editedEmployee.email"
              label="Email"
              type="email"
              required
              :rules="[
                v => !!v || 'Email обязателен',
                v => /.+@.+\..+/.test(v) || 'Email должен быть действительным'
              ]"
            ></v-text-field>
            <v-select
              v-model="editedEmployee.group"
              :items="groups"
              label="Группа"
              required
              :rules="[v => !!v || 'Группа обязательна']"
            ></v-select>
            <v-checkbox
              v-model="editedEmployee.isAdmin"
              label="Администратор"
            ></v-checkbox>
            <v-checkbox
              v-model="editedEmployee.isActive"
              label="Активен"
            ></v-checkbox>
          </v-form>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="secondary" @click="editEmployeeDialog = false">Отмена</v-btn>
          <v-btn color="primary" @click="updateEmployee" :disabled="!isEditFormValid">Сохранить</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Диалог просмотра сотрудника -->
    <v-dialog v-model="viewEmployeeDialog" max-width="800">
      <v-card>
        <v-card-title>Информация о сотруднике</v-card-title>
        <v-card-text v-if="selectedEmployee">
          <v-row>
            <v-col cols="12" md="4" class="text-center">
              <v-avatar color="grey lighten-1" size="100">
                <span class="text-h4">{{ selectedEmployee.name.charAt(0) }}</span>
              </v-avatar>
              <div class="mt-4">
                <v-chip
                  :color="selectedEmployee.isActive ? 'success' : 'error'"
                  class="mt-2"
                >
                  {{ selectedEmployee.isActive ? 'Активен' : 'Неактивен' }}
                </v-chip>
                <v-chip
                  color="primary"
                  class="mt-2 ml-2"
                  v-if="selectedEmployee.isAdmin"
                >
                  Администратор
                </v-chip>
              </div>
            </v-col>
            <v-col cols="12" md="8">
              <v-list>
                <v-list-item>
                  <template v-slot:prepend>
                    <v-icon color="primary">mdi-account</v-icon>
                  </template>
                  <v-list-item-title>{{ selectedEmployee.name }}</v-list-item-title>
                </v-list-item>
                <v-list-item>
                  <template v-slot:prepend>
                    <v-icon color="primary">mdi-email</v-icon>
                  </template>
                  <v-list-item-title>{{ selectedEmployee.email }}</v-list-item-title>
                </v-list-item>
                <v-list-item>
                  <template v-slot:prepend>
                    <v-icon color="primary">mdi-account-group</v-icon>
                  </template>
                  <v-list-item-title>{{ selectedEmployee.group }}</v-list-item-title>
                </v-list-item>
                <v-list-item>
                  <template v-slot:prepend>
                    <v-icon color="primary">mdi-calendar</v-icon>
                  </template>
                  <v-list-item-title>Дата регистрации: {{ formatDate(selectedEmployee.createdAt) }}</v-list-item-title>
                </v-list-item>
                <v-list-item>
                  <template v-slot:prepend>
                    <v-icon :color="getStressLevelColor(selectedEmployee.stressLevel)">mdi-emoticon</v-icon>
                  </template>
                  <v-list-item-title>Уровень стресса:</v-list-item-title>
                  <v-list-item-subtitle>
                    <v-progress-linear
                      :model-value="selectedEmployee.stressLevel"
                      :color="getStressLevelColor(selectedEmployee.stressLevel)"
                      height="20"
                      striped
                      class="mt-2"
                    >
                      <template v-slot:default="{ value }">
                        <strong>{{ Math.ceil(value) }}%</strong>
                      </template>
                    </v-progress-linear>
                  </v-list-item-subtitle>
                </v-list-item>
              </v-list>
            </v-col>
          </v-row>

          <v-divider class="my-4"></v-divider>

          <v-tabs v-model="activeTab">
            <v-tab value="stats">Статистика</v-tab>
            <v-tab value="tests">Тесты</v-tab>
          </v-tabs>

          <v-window v-model="activeTab">
            <v-window-item value="stats">
              <v-card flat>
                <v-card-text>
                  <h3 class="text-h6 mb-2">Статистика работы</h3>
                  <v-row>
                    <v-col cols="12" md="4">
                      <v-card outlined>
                        <v-card-text class="text-center">
                          <div class="text-h4">{{ selectedEmployee.stats.totalChats }}</div>
                          <div class="text-caption">Всего чатов</div>
                        </v-card-text>
                      </v-card>
                    </v-col>
                    <v-col cols="12" md="4">
                      <v-card outlined>
                        <v-card-text class="text-center">
                          <div class="text-h4">{{ selectedEmployee.stats.averageRating.toFixed(1) }}</div>
                          <div class="text-caption">Средняя оценка</div>
                        </v-card-text>
                      </v-card>
                    </v-col>
                    <v-col cols="12" md="4">
                      <v-card outlined>
                        <v-card-text class="text-center">
                          <div class="text-h4">{{ selectedEmployee.stats.resolvedIssues }}</div>
                          <div class="text-caption">Решенных проблем</div>
                        </v-card-text>
                      </v-card>
                    </v-col>
                  </v-row>
                </v-card-text>
              </v-card>
            </v-window-item>

            <v-window-item value="tests">
              <v-card flat>
                <v-card-text>
                  <h3 class="text-h6 mb-2">Результаты тестов</h3>
                  <v-data-table
                    :headers="testHeaders"
                    :items="selectedEmployee.tests"
                    :items-per-page="5"
                  ></v-data-table>
                </v-card-text>
              </v-card>
            </v-window-item>
          </v-window>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="primary" @click="viewEmployeeDialog = false">Закрыть</v-btn>
          <v-btn color="secondary" @click="editEmployee(selectedEmployee)">Редактировать</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Диалог подтверждения удаления -->
    <v-dialog v-model="deleteConfirmDialog" max-width="400">
      <v-card>
        <v-card-title>Подтверждение удаления</v-card-title>
        <v-card-text>
          Вы действительно хотите удалить сотрудника {{ selectedEmployee?.name }}?
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="secondary" @click="deleteConfirmDialog = false">Отмена</v-btn>
          <v-btn color="error" @click="deleteEmployee">Удалить</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';

// Состояние загрузки
const loading = ref(false);

// Фильтры
const search = ref('');
const groupFilter = ref(null);
const statusFilter = ref(null);

// Группы для фильтра и форм
const groups = ref([
  'Поддержка клиентов',
  'Техническая поддержка',
  'Продажи',
  'Консультанты',
]);

// Заголовки таблицы
const headers = ref([
  { title: '', key: 'avatar', width: '60px' },
  { title: 'ФИО', key: 'name' },
  { title: 'Email', key: 'email' },
  { title: 'Группа', key: 'group' },
  { title: 'Статус', key: 'status', width: '100px' },
  { title: 'Уровень стресса', key: 'stressLevel', width: '150px' },
  { title: 'Действия', key: 'actions', width: '120px', sortable: false },
]);

// Данные сотрудников
const employees = ref([
  {
    id: 1,
    name: 'Иванов Иван Иванович',
    email: 'ivanov@example.com',
    group: 'Поддержка клиентов',
    isActive: true,
    isAdmin: false,
    stressLevel: 45,
    createdAt: new Date('2023-01-15'),
    stats: {
      totalChats: 156,
      averageRating: 4.8,
      resolvedIssues: 142,
    },
    tests: [
      {
        id: 1,
        name: 'Тест на знание продукта',
        date: new Date('2023-09-10'),
        score: '92/100',
        result: 'Пройден',
      },
      {
        id: 2,
        name: 'Тест на стрессоустойчивость',
        date: new Date('2023-08-15'),
        score: '87/100',
        result: 'Пройден',
      },
    ],
  },
  {
    id: 2,
    name: 'Петрова Мария Сергеевна',
    email: 'petrova@example.com',
    group: 'Техническая поддержка',
    isActive: true,
    isAdmin: true,
    stressLevel: 32,
    createdAt: new Date('2023-02-20'),
    stats: {
      totalChats: 203,
      averageRating: 4.9,
      resolvedIssues: 198,
    },
    tests: [
      {
        id: 1,
        name: 'Тест на знание продукта',
        date: new Date('2023-09-05'),
        score: '95/100',
        result: 'Пройден',
      },
      {
        id: 2,
        name: 'Тест на стрессоустойчивость',
        date: new Date('2023-08-10'),
        score: '90/100',
        result: 'Пройден',
      },
    ],
  },
  {
    id: 3,
    name: 'Сидоров Алексей Петрович',
    email: 'sidorov@example.com',
    group: 'Продажи',
    isActive: false,
    isAdmin: false,
    stressLevel: 78,
    createdAt: new Date('2023-03-05'),
    stats: {
      totalChats: 98,
      averageRating: 4.2,
      resolvedIssues: 85,
    },
    tests: [
      {
        id: 1,
        name: 'Тест на знание продукта',
        date: new Date('2023-09-01'),
        score: '82/100',
        result: 'Пройден',
      },
      {
        id: 2,
        name: 'Тест на стрессоустойчивость',
        date: new Date('2023-08-05'),
        score: '75/100',
        result: 'Пройден условно',
      },
    ],
  },
]);

// Отфильтрованные сотрудники
const filteredEmployees = computed(() => {
  return employees.value.filter(employee => {
    const matchesSearch = !search.value || 
      employee.name.toLowerCase().includes(search.value.toLowerCase()) ||
      employee.email.toLowerCase().includes(search.value.toLowerCase());
    
    const matchesGroup = !groupFilter.value || employee.group === groupFilter.value;
    
    const matchesStatus = !statusFilter.value || 
      (statusFilter.value === 'Активен' && employee.isActive) ||
      (statusFilter.value === 'Неактивен' && !employee.isActive);
    
    return matchesSearch && matchesGroup && matchesStatus;
  });
});

// Диалоги
const addEmployeeDialog = ref(false);
const editEmployeeDialog = ref(false);
const viewEmployeeDialog = ref(false);
const deleteConfirmDialog = ref(false);

// Валидация форм
const isAddFormValid = ref(false);
const isEditFormValid = ref(false);

// Новый сотрудник
const newEmployee = ref({
  name: '',
  email: '',
  password: '',
  group: '',
  isAdmin: false,
});

// Редактируемый сотрудник
const editedEmployee = ref({});

// Выбранный сотрудник
const selectedEmployee = ref(null);

// Активная вкладка при просмотре сотрудника
const activeTab = ref('stats');

// Заголовки для таблицы тестов
const testHeaders = ref([
  { title: 'Название теста', key: 'name' },
  { title: 'Дата', key: 'date' },
  { title: 'Результат', key: 'result' },
  { title: 'Оценка', key: 'score' },
]);

// Функции управления сотрудниками

// Добавление сотрудника
function showAddEmployeeDialog() {
  newEmployee.value = {
    name: '',
    email: '',
    password: '',
    group: '',
    isAdmin: false,
  };
  addEmployeeDialog.value = true;
}

function addEmployee() {
  // В реальном приложении здесь будет запрос к API
  const id = Math.max(...employees.value.map(e => e.id)) + 1;
  
  employees.value.push({
    id,
    ...newEmployee.value,
    isActive: true,
    stressLevel: 0,
    createdAt: new Date(),
    stats: {
      totalChats: 0,
      averageRating: 0,
      resolvedIssues: 0,
    },
    tests: [],
  });
  
  addEmployeeDialog.value = false;
  
  // Показываем уведомление
  alert('Сотрудник успешно добавлен');
}

// Редактирование сотрудника
function editEmployee(employee) {
  editedEmployee.value = {...employee};
  viewEmployeeDialog.value = false;
  editEmployeeDialog.value = true;
}

function updateEmployee() {
  // В реальном приложении здесь будет запрос к API
  const index = employees.value.findIndex(e => e.id === editedEmployee.value.id);
  if (index !== -1) {
    employees.value[index] = {...employees.value[index], ...editedEmployee.value};
  }
  
  editEmployeeDialog.value = false;
  
  // Показываем уведомление
  alert('Информация о сотруднике обновлена');
}

// Просмотр сотрудника
function viewEmployee(employee) {
  selectedEmployee.value = employee;
  viewEmployeeDialog.value = true;
  activeTab.value = 'stats';
}

// Удаление сотрудника
function confirmDeleteEmployee(employee) {
  selectedEmployee.value = employee;
  deleteConfirmDialog.value = true;
}

function deleteEmployee() {
  // В реальном приложении здесь будет запрос к API
  const index = employees.value.findIndex(e => e.id === selectedEmployee.value.id);
  if (index !== -1) {
    employees.value.splice(index, 1);
  }
  
  deleteConfirmDialog.value = false;
  
  // Показываем уведомление
  alert('Сотрудник успешно удален');
}

// Вспомогательные функции
function formatDate(date) {
  if (!date) return '';
  return new Date(date).toLocaleDateString();
}

function getStressLevelColor(level) {
  if (level < 30) return 'success';
  if (level < 70) return 'warning';
  return 'error';
}

// Загрузка данных
onMounted(async () => {
  loading.value = true;
  
  // В реальном приложении здесь будет запрос к API
  // Имитация загрузки
  setTimeout(() => {
    loading.value = false;
  }, 1000);
});
</script> 