import { ref, provide, inject } from 'vue'

const snackbarSymbol = Symbol('snackbar')

// Создаем глобальное состояние снэкбара
const globalSnackbar = ref({
  show: false,
  text: '',
  color: 'primary', // primary, success, error, warning
  timeout: 5000,
})

export function provideSnackbar() {
  const showSnackbar = (options) => {
    globalSnackbar.value = {
      show: true,
      text: options.text || '',
      color: options.color || 'primary',
      timeout: options.timeout || 5000,
    }
  }

  const hideSnackbar = () => {
    globalSnackbar.value.show = false
  }

  provide(snackbarSymbol, {
    snackbar: globalSnackbar,
    showSnackbar,
    hideSnackbar,
  })

  return {
    snackbar: globalSnackbar,
    showSnackbar,
    hideSnackbar,
  }
}

export function useSnackbar() {
  const snackbar = inject(snackbarSymbol)
  
  if (!snackbar) {
    throw new Error('useSnackbar() must be used after provideSnackbar()')
  }
  
  return snackbar
} 