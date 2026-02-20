<template>
  <div style="padding: 24px; max-width: 900px; margin: 0 auto;">
    <h2>Dashboard</h2>

    <textarea
      v-model="notes"
      rows="10"
      style="width: 100%; margin-top: 12px; padding: 10px;"
      placeholder="Paste standup / meeting notes here..."/>

    <div style="margin-top: 12px; display: flex; gap: 10px;">
      <button @click="analyze" :disabled="loading || !notes.trim()">
        {{ loading ? "Analyzing..." : "Analyze" }}
      </button>

      <button @click="clear" :disabled="loading">
        Clear
      </button>
    </div>

    <pre
      v-if="result"
      style="margin-top: 16px; background: #111; color: #0f0; padding: 12px; border-radius: 8px; overflow: auto;"
    >{{ JSON.stringify(result, null, 2) }}</pre>
  </div>
</template>

<script setup>
import { ref } from "vue"
import { analyzeNotes } from "../services/api"

const notes = ref("")
const loading = ref(false)
const result = ref(null)

async function analyze() {
  loading.value = true
  result.value = null

  try {
    result.value = await analyzeNotes(notes.value)
  } catch (e) {
    result.value = { error: String(e) }
  } finally {
    loading.value = false
  }
}

function clear() {
  notes.value = ""
  result.value = null
}
</script>
