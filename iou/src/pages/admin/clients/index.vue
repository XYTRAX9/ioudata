<template>
  <v-container fluid>
    <v-row>
      <v-col cols="12">
        <v-card>
          <v-card-title class="d-flex align-center justify-space-between">
            <span>Управление клиентами</span>
            <v-btn
              color="primary"
              prepend-icon="mdi-account-plus"
              @click="openCreateDialog"
            >
              Добавить клиента
            </v-btn>
          </v-card-title>
          
          <v-card-text>
            <v-text-field
              v-model="search"
              label="Поиск"
              prepend-inner-icon="mdi-magnify"
              density="compact"
              single-line
              hide-details
              variant="outlined"
              class="mb-4"
            />
            
            <v-data-table
              :headers="headers"
              :items="clients"
              :search="search"
              :loading="loading"
              item-value="id"
              class="elevation-1"
            >
              <template v-slot:item.actions="{ item }">
                <v-btn
                  icon
                  size="small"
                  color="primary"
                  variant="text"
                  @click="openClientDetails(item.raw)"
                >
                  <v-icon>mdi-eye</v-icon>
                </v-btn>
                <v-btn
                  icon
                  size="small"
                  color="error"
                  variant="text"
                  @click="confirmDeleteClient(item.raw)"
                >
                  <v-icon>mdi-delete</v-icon>
                </v-btn>
              </template>
            </v-data-table>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- Диалог создания клиента -->
    <v-dialog v-model="createDialog" max-width="600px">
      <v-card>
        <v-card-title>Новый клиент</v-card-title>
        <v-card-text>
          <v-form ref="createForm" v-model="createFormValid">
            <v-row>
              <v-col cols="12">
                <v-text-field
                  v-model="newClient.name"
                  label="Имя"
                  :rules="[v => !!v || 'Имя обязательно']"
                  required
                ></v-text-field>
              </v-col>
              <v-col cols="12">
                <v-text-field
                  v-model="newClient.email"
                  label="Email"
                  :rules="[
                    v => !!v || 'Email обязателен',
                    v => /.+@.+\..+/.test(v) || 'Email должен быть валидным'
                  ]"
                  required
                ></v-text-field>
              </v-col>
              <v-col cols="12">
                <v-text-field
                  v-model="newClient.password"
                  label="Пароль"
                  type="password"
                  :rules="[v => !!v || 'Пароль обязателен']"
                  required
                ></v-text-field>
              </v-col>
              <v-col cols="12">
                <v-textarea
                  v-model="newClient.notes"
                  label="Заметки"
                  rows="3"
                ></v-textarea>
              </v-col>
            </v-row>
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
            @click="createClient" 
            :disabled="!createFormValid"
          >
            Создать
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Диалог подтверждения удаления -->
    <v-dialog v-model="deleteDialog" max-width="500px">
      <v-card>
        <v-card-title>Подтверждение удаления</v-card-title>
        <v-card-text>
          Вы уверены, что хотите удалить клиента {{ selectedClient?.name }}?
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
            @click="deleteClient"
          >
            Удалить
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Диалог деталей клиента -->
    <v-dialog v-model="detailsDialog" max-width="800px">
      <v-card v-if="selectedClient">
        <v-card-title>
          <span>Информация о клиенте</span>
          <v-spacer></v-spacer>
          <v-btn icon @click="detailsDialog = false">
            <v-icon>mdi-close</v-icon>
          </v-btn>
        </v-card-title>
        <v-card-text>
          <v-row>
            <v-col cols="12" md="6">
              <v-list>
                <v-list-item>
                  <template v-slot:prepend>
                    <v-icon color="primary">mdi-account</v-icon>
                  </template>
                  <v-list-item-title>{{ selectedClient.name }}</v-list-item-title>
                  <v-list-item-subtitle>Имя</v-list-item-subtitle>
                </v-list-item>
                <v-list-item>
                  <template v-slot:prepend>
                    <v-icon color="primary">mdi-email</v-icon>
                  </template>
                  <v-list-item-title>{{ selectedClient.email }}</v-list-item-title>
                  <v-list-item-subtitle>Email</v-list-item-subtitle>
                </v-list-item>
                <v-list-item v-if="selectedClient.notes">
                  <template v-slot:prepend>
                    <v-icon color="primary">mdi-note-text</v-icon>
                  </template>
                  <v-list-item-title>{{ selectedClient.notes }}</v-list-item-title>
                  <v-list-item-subtitle>Заметки</v-list-item-subtitle>
                </v-list-item>
              </v-list>
            </v-col>
            <v-col cols="12" md="6">
              <v-card>
                <v-card-title>Последние коммуникации</v-card-title>
                <v-list v-if="clientCommunications.length">
                  <v-list-item
                    v-for="comm in clientCommunications"
                    :key="comm.id"
                  >
                    <v-list-item-title>
                      {{ comm.call_type }} ({{ comm.status }})
                    </v-list-item-title>
                    <v-list-item-subtitle>
                      {{ new Date(comm.timestamp).toLocaleString() }}
                    </v-list-item-subtitle>
                  </v-list-item>
                </v-list>
                <v-card-text v-else>
                  Нет данных о коммуникациях с этим клиентом
                </v-card-text>
              </v-card>
            </v-col>
          </v-row>
        </v-card-text>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script>
import { clientsApi, communicationsApi } from '@/api'
import { useSnackbar } from '@/composables/useSnackbar'

export default {
  name: 'AdminClientsPage',
  
  setup() {
    const { showSnackbar } = useSnackbar()
    return { showSnackbar }
  },
  
  data() {
    return {
      clients: [],
      loading: false,
      search: '',
      
      headers: [
        { title: 'ID', key: 'id', sortable: true },
        { title: 'Имя', key: 'name', sortable: true },
        { title: 'Email', key: 'email', sortable: true },
        { title: 'Дата создания', key: 'created_at', sortable: true },
        { title: 'Действия', key: 'actions', sortable: false }
      ],
      
      createDialog: false,
      createFormValid: false,
      newClient: {
        name: '',
        email: '',
        password: '',
        notes: ''
      },
      
      deleteDialog: false,
      selectedClient: null,
      
      detailsDialog: false,
      clientCommunications: []
    }
  },
  
  mounted() {
    this.fetchClients()
  },
  
  methods: {
    async fetchClients() {
      this.loading = true
      
      try {
        const response = await clientsApi.getList()
        this.clients = response.data
      } catch (error) {
        console.error('Error fetching clients:', error)
        this.showSnackbar({
          text: 'Не удалось загрузить список клиентов',
          color: 'error'
        })
      } finally {
        this.loading = false
      }
    },
    
    openCreateDialog() {
      this.newClient = {
        name: '',
        email: '',
        password: '',
        notes: ''
      }
      this.createDialog = true
    },
    
    async createClient() {
      try {
        await clientsApi.create(this.newClient)
        this.showSnackbar({
          text: 'Клиент успешно создан',
          color: 'success'
        })
        this.createDialog = false
        this.fetchClients()
      } catch (error) {
        console.error('Error creating client:', error)
        this.showSnackbar({
          text: error.response?.data?.detail || 'Не удалось создать клиента',
          color: 'error'
        })
      }
    },
    
    confirmDeleteClient(client) {
      this.selectedClient = client
      this.deleteDialog = true
    },
    
    async deleteClient() {
      if (!this.selectedClient) return
      
      try {
        // Этот метод может отсутствовать в API, нужно проверить
        await clientsApi.delete(this.selectedClient.id)
        this.showSnackbar({
          text: 'Клиент успешно удален',
          color: 'success'
        })
        this.deleteDialog = false
        this.fetchClients()
      } catch (error) {
        console.error('Error deleting client:', error)
        this.showSnackbar({
          text: error.response?.data?.detail || 'Не удалось удалить клиента',
          color: 'error'
        })
      }
    },
    
    async openClientDetails(client) {
      this.selectedClient = client
      this.detailsDialog = true
      
      try {
        const response = await communicationsApi.getList({
          client_id: client.id,
          limit: 5
        })
        this.clientCommunications = response.data
      } catch (error) {
        console.error('Error fetching client communications:', error)
        this.clientCommunications = []
      }
    }
  }
}
</script> 