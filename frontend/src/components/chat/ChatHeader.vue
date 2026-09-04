<script setup>
defineProps({
  sessionId: {
    type: String,
    default: null,
  },
  mode: {
    type: String,
    default: 'standard',
  },
})

const emit = defineEmits(['clear', 'update:mode'])
</script>

<template>
  <div class="chat-header">
    <h1>AI Intelligent Dialogue System</h1>
    <div class="header-actions">
      <div class="mode-toggle">
        <button
          :class="{ active: mode === 'standard' }"
          @click="emit('update:mode', 'standard')"
        >
          Standard
        </button>
        <button
          :class="{ active: mode === 'agent' }"
          @click="emit('update:mode', 'agent')"
        >
          Agent
        </button>
      </div>
      <button class="btn-clear" @click="emit('clear')">Clear</button>
    </div>
  </div>
</template>

<style scoped>
</style>