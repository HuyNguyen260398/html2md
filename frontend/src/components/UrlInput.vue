<script setup>
import { ref } from 'vue'
import LoadingSpinner from './LoadingSpinner.vue'

const props = defineProps({
  loading: {
    type: Boolean,
    default: false,
  },
})

const emit = defineEmits(['extract'])

const url = ref('')
const urlError = ref('')

function isValidUrl(value) {
  if (!value.trim()) return false
  try {
    const parsed = new URL(value.trim())
    return parsed.protocol === 'http:' || parsed.protocol === 'https:'
  } catch {
    return false
  }
}

function validateUrl() {
  if (!url.value.trim()) {
    urlError.value = 'Please enter a URL.'
  } else if (!isValidUrl(url.value)) {
    urlError.value = 'Please enter a valid URL (e.g. https://example.com).'
  } else {
    urlError.value = ''
  }
}

function handleExtract() {
  validateUrl()
  if (urlError.value) return
  emit('extract', url.value.trim())
}
</script>

<template>
  <section aria-label="URL input" class="w-full">
    <div class="flex flex-col sm:flex-row gap-3 items-start">
      <div class="flex-1 w-full">
        <label
          for="url-input"
          class="block text-sm font-medium mb-1.5"
          style="color: var(--color-fg-default)"
        >
          URL to extract
        </label>
        <input
          id="url-input"
          v-model="url"
          type="url"
          autocomplete="url"
          spellcheck="false"
          placeholder="https://example.com/article"
          :disabled="loading"
          :aria-invalid="!!urlError"
          :aria-describedby="urlError ? 'url-error' : undefined"
          class="w-full h-11 px-3 rounded-md border font-mono text-sm transition-colors duration-150 disabled:opacity-50 disabled:cursor-not-allowed"
          style="
            background-color: var(--color-canvas-default);
            border-color: var(--color-border-default);
            color: var(--color-fg-default);
          "
          @blur="validateUrl"
          @keydown.enter="handleExtract"
        />
        <p
          v-if="urlError"
          id="url-error"
          role="alert"
          class="mt-1.5 text-xs"
          style="color: var(--color-danger-fg)"
        >
          {{ urlError }}
        </p>
      </div>

      <div class="sm:mt-7">
        <button
          type="button"
          :disabled="loading"
          class="gh-btn-primary h-11 px-5 rounded-md border font-medium text-sm inline-flex items-center gap-2 transition-colors duration-150 disabled:opacity-50 disabled:cursor-not-allowed whitespace-nowrap"
          style="
            background-color: var(--color-accent-emphasis);
            border-color: var(--color-accent-emphasis);
            color: #ffffff;
            min-width: 110px;
            justify-content: center;
          "
          @click="handleExtract"
        >
          <LoadingSpinner v-if="loading" size="sm" />
          <svg
            v-else
            aria-hidden="true"
            width="15"
            height="15"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2.5"
            stroke-linecap="round"
            stroke-linejoin="round"
          >
            <polyline points="4 17 10 11 4 5" />
            <line x1="12" y1="19" x2="20" y2="19" />
          </svg>
          {{ loading ? 'Extracting…' : 'Extract' }}
        </button>
      </div>
    </div>
  </section>
</template>
