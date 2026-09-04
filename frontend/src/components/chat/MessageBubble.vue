<script setup>
defineProps({
  message: {
    type: Object,
    required: true,
  },
})

import { ref } from 'vue'

const showSources = ref(false)
</script>

<template>
  <div
    class="message-bubble"
    :class="[message.role]"
  >
    <div class="bubble-role">
      <template v-if="message.role === 'user'">You</template>
      <template v-else-if="message.role === 'assistant'">AI</template>
      <template v-else-if="message.role === 'tool'">Tool</template>
      <template v-else-if="message.role === 'system'">System</template>
    </div>
    <div
      class="bubble-content"
      :class="{ 'streaming-cursor': message.isStreaming }"
    >
      {{ message.content }}
    </div>
    <div
      v-if="message.sources && message.sources.length > 0"
      class="sources-section"
    >
      <button class="sources-toggle" @click="showSources = !showSources">
        {{ showSources ? 'Hide' : 'Show' }} {{ message.sources.length }} source(s)
      </button>
      <div v-if="showSources" class="sources-list">
        <div
          v-for="(src, idx) in message.sources"
          :key="idx"
          class="source-item"
        >
          {{ src }}
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
</style>