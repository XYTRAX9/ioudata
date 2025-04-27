<template>
  <v-container class="fill-height">
    <v-row justify="center" align="center">
      <v-col cols="12" sm="8" md="6">
        <v-card class="mx-auto text-center">
          <v-card-title class="text-h4 mt-4">
            Страница не найдена
          </v-card-title>
          
          <v-card-text>
            <v-icon size="128" color="error">mdi-alert-circle-outline</v-icon>
            <p class="text-h6 mt-4">
              Запрашиваемый ресурс не существует или был перемещен.
            </p>
            <p class="text-body-1 mt-2">
              Код ошибки: 404 Not Found
            </p>
          </v-card-text>
          
          <v-card-actions class="justify-center mb-4">
            <v-btn 
              color="primary" 
              variant="flat" 
              @click="goBack"
            >
              Вернуться назад
            </v-btn>
            <v-btn 
              color="secondary" 
              variant="flat" 
              to="/"
            >
              На главную
            </v-btn>
          </v-card-actions>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup>
// Метод для возврата на предыдущую страницу
const goBack = () => {
  window.history.length > 1 
    ? window.history.back() 
    : window.location = '/'
}
</script> 