<script setup>
import { ref, watch, onMounted, nextTick } from 'vue'
import MessageBubble from './MessageBubble.vue'

const props = defineProps({
  messages: {
    type: Array,
    default: () => [],
  },
})

const listRef = ref(null)

function scrollToBottom() {
  nextTick(() => {
    if (listRef.value) {
      listRef.value.scrollTop = listRef.value.scrollHeight
    }
  })
}

watch(
  () => props.messages.length,
  () => scrollToBottom(),
)

watch(
  () => {
    const last = props.messages[props.messages.length - 1]
    return last ? last.content : ''
  },
  () => scrollToBottom(),
)

onMounted(() => scrollToBottom())
</script>

<template>
  <div class="message-list" ref="listRef">
    <div v-if="messages.length === 0" class="empty-state">
      Start a conversation — type a message below.
    </div>
    <MessageBubble
      v-for="msg in messages"
      :key="msg.id"
      :message="msg"
    />
  </div>
</template>

<style scoped>
</style>