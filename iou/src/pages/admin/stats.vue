<template>
  <v-container fluid>
    <v-row>
      <v-col cols="12">
        <h1 class="text-h4 mb-4">Статистика системы</h1>
      </v-col>
    </v-row>

    <v-row>
      <!-- Статистика по сотрудникам -->
      <v-col cols="12" md="6">
        <v-card>
          <v-card-title class="d-flex align-center">
            <v-icon color="primary" class="me-2">mdi-account-group</v-icon>
            Сотрудники
          </v-card-title>
          
          <v-card-text v-if="loading.employees">
            <v-skeleton-loader type="card"></v-skeleton-loader>
          </v-card-text>
          
          <v-card-text v-else-if="stats.employees">
            <v-row>
              <v-col cols="12" md="6">
                <v-list>
                  <v-list-item>
                    <v-list-item-title>{{ stats.employees.total }}</v-list-item-title>
                    <v-list-item-subtitle>Всего сотрудников</v-list-item-subtitle>
                  </v-list-item>
                  <v-list-item>
                    <v-list-item-title>{{ stats.employees.active }}</v-list-item-title>
                    <v-list-item-subtitle>Активных сотрудников</v-list-item-subtitle>
                  </v-list-item>
                  <v-list-item>
                    <v-list-item-title>{{ stats.employees.superusers }}</v-list-item-title>
                    <v-list-item-subtitle>Администраторов</v-list-item-subtitle>
                  </v-list-item>
                </v-list>
              </v-col>
              
              <v-col cols="12" md="6">
                <h3 class="text-subtitle-1 mb-2">По группам:</h3>
                <v-list density="compact">
                  <v-list-item>
                    <v-list-item-title>{{ stats.employees.by_group.normal }}</v-list-item-title>
                    <v-list-item-subtitle>Нормальная группа</v-list-item-subtitle>
                  </v-list-item>
                  <v-list-item>
                    <v-list-item-title>{{ stats.employees.by_group.slightly_below }}</v-list-item-title>
                    <v-list-item-subtitle>Ниже нормы</v-list-item-subtitle>
                  </v-list-item>
                  <v-list-item>
                    <v-list-item-title>{{ stats.employees.by_group.significantly_below }}</v-list-item-title>
                    <v-list-item-subtitle>Значительно ниже нормы</v-list-item-subtitle>
                  </v-list-item>
                </v-list>
              </v-col>
            </v-row>
            
            <v-divider class="my-3"></v-divider>
            
            <h3 class="text-subtitle-1 mb-2">По уровню стресса:</h3>
            <v-row>
              <v-col cols="12">
                <v-progress-linear
                  v-for="(value, key) in stats.employees.by_stress"
                  :key="key"
                  :model-value="(value / stats.employees.total) * 100"
                  :color="getStressColor(key)"
                  height="20"
                  class="mb-2"
                >
                  <template v-slot:default>
                    <strong>{{ key }}: {{ value }} ({{ Math.round((value / stats.employees.total) * 100) }}%)</strong>
                  </template>
                </v-progress-linear>
              </v-col>
            </v-row>
          </v-card-text>
        </v-card>
      </v-col>

      <!-- Статистика по клиентам -->
      <v-col cols="12" md="6">
        <v-card>
          <v-card-title class="d-flex align-center">
            <v-icon color="primary" class="me-2">mdi-account-multiple</v-icon>
            Клиенты
          </v-card-title>
          
          <v-card-text v-if="loading.clients">
            <v-skeleton-loader type="card"></v-skeleton-loader>
          </v-card-text>
          
          <v-card-text v-else-if="stats.clients">
            <v-row>
              <v-col cols="12">
                <v-list>
                  <v-list-item>
                    <v-list-item-title>{{ stats.clients.total }}</v-list-item-title>
                    <v-list-item-subtitle>Всего клиентов</v-list-item-subtitle>
                  </v-list-item>
                  <v-list-item>
                    <v-list-item-title>{{ stats.clients.with_preferences }}</v-list-item-title>
                    <v-list-item-subtitle>С предпочтениями</v-list-item-subtitle>
                  </v-list-item>
                  <v-list-item>
                    <v-list-item-title>{{ stats.clients.with_blacklist }}</v-list-item-title>
                    <v-list-item-subtitle>С черным списком</v-list-item-subtitle>
                  </v-list-item>
                </v-list>
              </v-col>
            </v-row>
            
            <v-divider class="my-3"></v-divider>
            
            <v-row>
              <v-col cols="12">
                <v-card variant="outlined">
                  <v-card-title class="text-subtitle-1">
                    Распределение клиентов
                  </v-card-title>
                  <v-card-text>
                    <v-chart class="chart" :option="clientChartOption" autoresize />
                  </v-card-text>
                </v-card>
              </v-col>
            </v-row>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <v-row class="mt-4">
      <!-- Статистика по коммуникациям -->
      <v-col cols="12" md="6">
        <v-card>
          <v-card-title class="d-flex align-center">
            <v-icon color="primary" class="me-2">mdi-message-text</v-icon>
            Коммуникации
          </v-card-title>
          
          <v-card-text v-if="loading.communications">
            <v-skeleton-loader type="card"></v-skeleton-loader>
          </v-card-text>
          
          <v-card-text v-else-if="stats.communications">
            <v-row>
              <v-col cols="12">
                <v-list>
                  <v-list-item>
                    <v-list-item-title>{{ stats.communications.total }}</v-list-item-title>
                    <v-list-item-subtitle>Всего коммуникаций</v-list-item-subtitle>
                  </v-list-item>
                  <v-list-item>
                    <v-list-item-title>{{ formatPercent(stats.communications.average_success_rate) }}</v-list-item-title>
                    <v-list-item-subtitle>Средний показатель успешности</v-list-item-subtitle>
                  </v-list-item>
                </v-list>
              </v-col>
            </v-row>
            
            <v-divider class="my-3"></v-divider>
            
            <h3 class="text-subtitle-1 mb-2">По типам звонков:</h3>
            <v-row>
              <v-col cols="12">
                <v-chart class="chart" :option="communicationTypeChartOption" autoresize />
              </v-col>
            </v-row>
            
            <v-divider class="my-3"></v-divider>
            
            <h3 class="text-subtitle-1 mb-2">По статусам:</h3>
            <v-row>
              <v-col cols="12">
                <v-chart class="chart" :option="communicationStatusChartOption" autoresize />
              </v-col>
            </v-row>
          </v-card-text>
        </v-card>
      </v-col>

      <!-- Статистика по тестам -->
      <v-col cols="12" md="6">
        <v-card>
          <v-card-title class="d-flex align-center">
            <v-icon color="primary" class="me-2">mdi-clipboard-text</v-icon>
            Тесты
          </v-card-title>
          
          <v-card-text v-if="loading.tests">
            <v-skeleton-loader type="card"></v-skeleton-loader>
          </v-card-text>
          
          <v-card-text v-else-if="stats.tests">
            <v-row>
              <v-col cols="12" md="6">
                <h3 class="text-subtitle-1 mb-2">Тесты:</h3>
                <v-list>
                  <v-list-item>
                    <v-list-item-title>{{ stats.tests.tests.total }}</v-list-item-title>
                    <v-list-item-subtitle>Всего тестов</v-list-item-subtitle>
                  </v-list-item>
                  <v-list-item>
                    <v-list-item-title>{{ stats.tests.tests.active }}</v-list-item-title>
                    <v-list-item-subtitle>Активных тестов</v-list-item-subtitle>
                  </v-list-item>
                </v-list>
              </v-col>
              
              <v-col cols="12" md="6">
                <h3 class="text-subtitle-1 mb-2">Результаты:</h3>
                <v-list>
                  <v-list-item>
                    <v-list-item-title>{{ stats.tests.results.total }}</v-list-item-title>
                    <v-list-item-subtitle>Всего результатов</v-list-item-subtitle>
                  </v-list-item>
                  <v-list-item>
                    <v-list-item-title>{{ formatPercent(stats.tests.results.average_score) }}</v-list-item-title>
                    <v-list-item-subtitle>Средний балл</v-list-item-subtitle>
                  </v-list-item>
                </v-list>
              </v-col>
            </v-row>
            
            <v-divider class="my-3"></v-divider>
            
            <h3 class="text-subtitle-1 mb-2">Распределение баллов:</h3>
            <v-row>
              <v-col cols="12">
                <v-chart class="chart" :option="testScoreChartOption" autoresize />
              </v-col>
            </v-row>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <v-row class="mt-4">
      <!-- Недавние события -->
      <v-col cols="12">
        <v-card>
          <v-card-title class="d-flex align-center">
            <v-icon color="primary" class="me-2">mdi-clock-outline</v-icon>
            Недавние события
          </v-card-title>
          
          <v-card-text v-if="loading.events">
            <v-skeleton-loader type="table"></v-skeleton-loader>
          </v-card-text>
          
          <v-card-text v-else>
            <v-data-table
              :headers="eventsHeaders"
              :items="events"
              class="elevation-1"
            >
              <template v-slot:item.type="{ item }">
                <v-chip
                  :color="getEventTypeColor(item.raw.type)"
                  size="small"
                >
                  {{ getEventTypeLabel(item.raw.type) }}
                </v-chip>
              </template>
              
              <template v-slot:item.timestamp="{ item }">
                {{ new Date(item.raw.timestamp).toLocaleString() }}
              </template>
              
              <template v-slot:item.details="{ item }">
                <v-btn
                  icon
                  size="small"
                  variant="text"
                  @click="showEventDetails(item.raw)"
                >
                  <v-icon>mdi-information-outline</v-icon>
                </v-btn>
              </template>
            </v-data-table>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- Диалог с деталями события -->
    <v-dialog v-model="eventDialog" max-width="600px">
      <v-card v-if="selectedEvent">
        <v-card-title>
          Детали события
          <v-spacer></v-spacer>
          <v-btn icon @click="eventDialog = false">
            <v-icon>mdi-close</v-icon>
          </v-btn>
        </v-card-title>
        <v-card-text>
          <v-list>
            <v-list-item>
              <v-list-item-title>Тип</v-list-item-title>
              <v-list-item-subtitle>{{ getEventTypeLabel(selectedEvent.type) }}</v-list-item-subtitle>
            </v-list-item>
            <v-list-item>
              <v-list-item-title>Время</v-list-item-title>
              <v-list-item-subtitle>{{ new Date(selectedEvent.timestamp).toLocaleString() }}</v-list-item-subtitle>
            </v-list-item>
          </v-list>
          
          <v-divider class="my-3"></v-divider>
          
          <v-list v-if="selectedEvent.data">
            <v-list-item v-for="(value, key) in selectedEvent.data" :key="key">
              <v-list-item-title>{{ key }}</v-list-item-title>
              <v-list-item-subtitle>{{ value }}</v-list-item-subtitle>
            </v-list-item>
          </v-list>
        </v-card-text>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script>
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { PieChart, BarChart } from 'echarts/charts'
import { TitleComponent, TooltipComponent, LegendComponent } from 'echarts/components'
import VChart from 'vue-echarts'
import axios from 'axios'
import { useSnackbar } from '@/composables/useSnackbar'

use([
  CanvasRenderer,
  PieChart,
  BarChart,
  TitleComponent,
  TooltipComponent,
  LegendComponent
])

export default {
  name: 'AdminStatsPage',
  
  components: {
    VChart
  },
  
  setup() {
    const { showSnackbar } = useSnackbar()
    return { showSnackbar }
  },
  
  data() {
    return {
      loading: {
        employees: true,
        clients: true,
        communications: true,
        tests: true,
        events: true
      },
      
      stats: {
        employees: null,
        clients: null,
        communications: null,
        tests: null
      },
      
      events: [],
      eventsHeaders: [
        { title: 'Тип', key: 'type', sortable: true },
        { title: 'Время', key: 'timestamp', sortable: true },
        { title: 'Детали', key: 'details', sortable: false, align: 'end' }
      ],
      
      eventDialog: false,
      selectedEvent: null
    }
  },
  
  computed: {
    clientChartOption() {
      if (!this.stats.clients) return {}
      
      const { total, with_preferences, with_blacklist } = this.stats.clients
      
      return {
        tooltip: {
          trigger: 'item',
          formatter: '{b}: {c} ({d}%)'
        },
        legend: {
          orient: 'vertical',
          left: 'left',
          data: ['С предпочтениями', 'С черным списком', 'Стандартные']
        },
        series: [
          {
            name: 'Клиенты',
            type: 'pie',
            radius: '70%',
            center: ['50%', '60%'],
            data: [
              { value: with_preferences, name: 'С предпочтениями' },
              { value: with_blacklist, name: 'С черным списком' },
              { value: total - with_preferences - with_blacklist, name: 'Стандартные' }
            ],
            emphasis: {
              itemStyle: {
                shadowBlur: 10,
                shadowOffsetX: 0,
                shadowColor: 'rgba(0, 0, 0, 0.5)'
              }
            }
          }
        ]
      }
    },
    
    communicationTypeChartOption() {
      if (!this.stats.communications || !this.stats.communications.by_type) return {}
      
      const data = Object.entries(this.stats.communications.by_type).map(([name, value]) => ({
        name,
        value
      }))
      
      return {
        tooltip: {
          trigger: 'item',
          formatter: '{b}: {c} ({d}%)'
        },
        legend: {
          orient: 'vertical',
          left: 'left',
          data: data.map(item => item.name)
        },
        series: [
          {
            name: 'Типы звонков',
            type: 'pie',
            radius: '70%',
            center: ['50%', '60%'],
            data,
            emphasis: {
              itemStyle: {
                shadowBlur: 10,
                shadowOffsetX: 0,
                shadowColor: 'rgba(0, 0, 0, 0.5)'
              }
            }
          }
        ]
      }
    },
    
    communicationStatusChartOption() {
      if (!this.stats.communications || !this.stats.communications.by_status) return {}
      
      const data = Object.entries(this.stats.communications.by_status).map(([name, value]) => ({
        name,
        value
      }))
      
      return {
        tooltip: {
          trigger: 'item',
          formatter: '{b}: {c} ({d}%)'
        },
        legend: {
          orient: 'vertical',
          left: 'left',
          data: data.map(item => item.name)
        },
        series: [
          {
            name: 'Статусы звонков',
            type: 'pie',
            radius: '70%',
            center: ['50%', '60%'],
            data,
            emphasis: {
              itemStyle: {
                shadowBlur: 10,
                shadowOffsetX: 0,
                shadowColor: 'rgba(0, 0, 0, 0.5)'
              }
            }
          }
        ]
      }
    },
    
    testScoreChartOption() {
      if (!this.stats.tests || !this.stats.tests.results.score_distribution) return {}
      
      const data = Object.entries(this.stats.tests.results.score_distribution).map(([name, value]) => ({
        name,
        value
      }))
      
      return {
        tooltip: {
          trigger: 'axis',
          axisPointer: {
            type: 'shadow'
          }
        },
        grid: {
          left: '3%',
          right: '4%',
          bottom: '3%',
          containLabel: true
        },
        xAxis: {
          type: 'value'
        },
        yAxis: {
          type: 'category',
          data: data.map(item => item.name)
        },
        series: [
          {
            name: 'Количество',
            type: 'bar',
            data: data.map(item => item.value)
          }
        ]
      }
    }
  },
  
  mounted() {
    this.fetchStats()
    this.fetchEvents()
  },
  
  methods: {
    async fetchStats() {
      await Promise.all([
        this.fetchEmployeeStats(),
        this.fetchClientStats(),
        this.fetchCommunicationStats(),
        this.fetchTestStats()
      ])
    },
    
    async fetchEmployeeStats() {
      this.loading.employees = true
      
      try {
        const response = await axios.get('/api/admin/stats/employees')
        this.stats.employees = response.data
      } catch (error) {
        console.error('Error fetching employee stats:', error)
        this.showSnackbar({
          text: 'Не удалось загрузить статистику по сотрудникам',
          color: 'error'
        })
      } finally {
        this.loading.employees = false
      }
    },
    
    async fetchClientStats() {
      this.loading.clients = true
      
      try {
        const response = await axios.get('/api/admin/stats/clients')
        this.stats.clients = response.data
      } catch (error) {
        console.error('Error fetching client stats:', error)
        this.showSnackbar({
          text: 'Не удалось загрузить статистику по клиентам',
          color: 'error'
        })
      } finally {
        this.loading.clients = false
      }
    },
    
    async fetchCommunicationStats() {
      this.loading.communications = true
      
      try {
        const response = await axios.get('/api/admin/stats/communications')
        this.stats.communications = response.data
      } catch (error) {
        console.error('Error fetching communication stats:', error)
        this.showSnackbar({
          text: 'Не удалось загрузить статистику по коммуникациям',
          color: 'error'
        })
      } finally {
        this.loading.communications = false
      }
    },
    
    async fetchTestStats() {
      this.loading.tests = true
      
      try {
        const response = await axios.get('/api/admin/stats/tests')
        this.stats.tests = response.data
      } catch (error) {
        console.error('Error fetching test stats:', error)
        this.showSnackbar({
          text: 'Не удалось загрузить статистику по тестам',
          color: 'error'
        })
      } finally {
        this.loading.tests = false
      }
    },
    
    async fetchEvents() {
      this.loading.events = true
      
      try {
        const response = await axios.get('/api/admin/events')
        this.events = response.data
      } catch (error) {
        console.error('Error fetching events:', error)
        this.showSnackbar({
          text: 'Не удалось загрузить недавние события',
          color: 'error'
        })
      } finally {
        this.loading.events = false
      }
    },
    
    getStressColor(level) {
      if (level.includes('low')) return 'success'
      if (level.includes('medium')) return 'warning'
      if (level.includes('high')) return 'error'
      return 'primary'
    },
    
    getEventTypeColor(type) {
      switch (type) {
        case 'communication':
          return 'primary'
        case 'test_result':
          return 'purple'
        default:
          return 'grey'
      }
    },
    
    getEventTypeLabel(type) {
      switch (type) {
        case 'communication':
          return 'Коммуникация'
        case 'test_result':
          return 'Результат теста'
        default:
          return type
      }
    },
    
    showEventDetails(event) {
      this.selectedEvent = event
      this.eventDialog = true
    },
    
    formatPercent(value) {
      if (value === null || value === undefined) return '0%'
      return `${Math.round(value * 100)}%`
    }
  }
}
</script>

<style scoped>
.chart {
  height: 300px;
}
</style> 