/**
 * plugins/vuetify.js
 *
 * Настройка Vuetify
 */

// Styles
import '@mdi/font/css/materialdesignicons.css'
import 'vuetify/styles'

// Composables
import { createVuetify } from 'vuetify'
import { VBtn } from 'vuetify/components'

// Тема приложения
const darkTheme = {
  dark: true,
  colors: {
    primary: '#1976D2',
    secondary: '#424242',
    accent: '#82B1FF',
    error: '#FF5252',
    info: '#2196F3',
    success: '#4CAF50',
    warning: '#FB8C00',
    surface: '#121212',
    background: '#1E1E1E',
  },
}

// Создание инстанса Vuetify
export default createVuetify({
  theme: {
    defaultTheme: 'darkTheme',
    themes: {
      darkTheme,
    },
  },
  defaults: {
    VBtn: {
      color: 'primary',
      variant: 'flat',
    },
  },
})