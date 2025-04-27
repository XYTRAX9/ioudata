/**
 * plugins/index.js
 *
 * Автоматически импортирует и регистрирует компоненты Vue
 * Это файл с точкой входа для ваших плагинов, включая настройку компонентов.
 */

// Plugins
import vuetify from './vuetify'
import router from '../router'
import { createPinia } from 'pinia'
import api, * as apiServices from '../api'

export function registerPlugins(app) {
  app
    .use(vuetify)
    .use(router)
    .use(createPinia())
  
  // Глобальный доступ к API
  app.config.globalProperties.$api = api
  app.config.globalProperties.$auth = apiServices.authApi
  app.config.globalProperties.$employees = apiServices.employeesApi
  app.config.globalProperties.$clients = apiServices.clientsApi
  app.config.globalProperties.$communications = apiServices.communicationsApi
  app.config.globalProperties.$tests = apiServices.testsApi
  
  // Также предоставляем API через provide/inject
  app.provide('api', api)
  app.provide('auth', apiServices.authApi)
  app.provide('employees', apiServices.employeesApi)
  app.provide('clients', apiServices.clientsApi)
  app.provide('communications', apiServices.communicationsApi)
  app.provide('tests', apiServices.testsApi)
}
