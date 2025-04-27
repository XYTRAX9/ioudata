<template>
  <div :class="['message-container', isUser ? 'user-message' : 'other-message', isSystem ? 'system-message' : '']">
    <div class="message-content">
      <div class="message-text">
        {{ text }}
      </div>
      <div class="message-time">
        {{ formattedTime }}
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue';

const props = defineProps({
  text: {
    type: String,
    required: true
  },
  timestamp: {
    type: [Date, String],
    required: true
  },
  isUser: {
    type: Boolean,
    default: false
  },
  isSystem: {
    type: Boolean,
    default: false
  }
});

// Форматирование времени
const formattedTime = computed(() => {
  const date = props.timestamp instanceof Date ? props.timestamp : new Date(props.timestamp);
  
  return date.toLocaleTimeString('ru-RU', {
    hour: '2-digit',
    minute: '2-digit'
  });
});
</script>

<style scoped>
.message-container {
  display: flex;
  margin-bottom: 8px;
  max-width: 80%;
}

.user-message {
  margin-left: auto;
  justify-content: flex-end;
}

.other-message {
  margin-right: auto;
  justify-content: flex-start;
}

.message-content {
  padding: 8px 12px;
  border-radius: 12px;
  position: relative;
}

.user-message .message-content {
  background-color: #2196F3;
  color: white;
  border-bottom-right-radius: 4px;
}

.other-message .message-content {
  background-color: #F5F5F5;
  color: #333;
  border-bottom-left-radius: 4px;
}

.system-message .message-content {
  background-color: #FFF3E0;
  color: #DD2C00;
  font-style: italic;
  border-radius: 8px;
}

.message-text {
  word-break: break-word;
  white-space: pre-wrap;
}

.message-time {
  font-size: 0.75rem;
  color: rgba(255, 255, 255, 0.7);
  text-align: right;
  margin-top: 4px;
}

.other-message .message-time {
  color: rgba(0, 0, 0, 0.5);
}
</style> 