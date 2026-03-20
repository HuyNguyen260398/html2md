<script setup>
import LoadingSpinner from './LoadingSpinner.vue'

defineProps({
  hasRawContent: {
    type: Boolean,
    default: false,
  },
  hasMarkdownContent: {
    type: Boolean,
    default: false,
  },
  converting: {
    type: Boolean,
    default: false,
  },
})

const emit = defineEmits(['convert', 'download'])
</script>

<template>
  <div class="flex flex-wrap items-center gap-3" role="group" aria-label="Actions">
    <!-- Convert button -->
    <button
      type="button"
      :disabled="!hasRawContent || converting"
      class="h-11 px-5 rounded-md border font-medium text-sm inline-flex items-center gap-2 transition-colors duration-150 disabled:opacity-40 disabled:cursor-not-allowed"
      style="
        background-color: var(--color-btn-bg);
        border-color: var(--color-btn-border);
        color: var(--color-fg-default);
        min-width: 120px;
        justify-content: center;
      "
      @click="emit('convert')"
    >
      <LoadingSpinner v-if="converting" size="sm" />
      <svg
        v-else
        aria-hidden="true"
        width="15"
        height="15"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        stroke-width="2"
        stroke-linecap="round"
        stroke-linejoin="round"
      >
        <polyline points="17 1 21 5 17 9" />
        <path d="M3 11V9a4 4 0 0 1 4-4h14" />
        <polyline points="7 23 3 19 7 15" />
        <path d="M21 13v2a4 4 0 0 1-4 4H3" />
      </svg>
      {{ converting ? 'Converting…' : 'Convert to Markdown' }}
    </button>

    <!-- Download button -->
    <button
      type="button"
      :disabled="!hasMarkdownContent"
      class="h-11 px-5 rounded-md border font-medium text-sm inline-flex items-center gap-2 transition-colors duration-150 disabled:opacity-40 disabled:cursor-not-allowed"
      style="
        background-color: var(--color-btn-bg);
        border-color: var(--color-btn-border);
        color: var(--color-fg-default);
        min-width: 120px;
        justify-content: center;
      "
      @click="emit('download')"
    >
      <svg
        aria-hidden="true"
        width="15"
        height="15"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        stroke-width="2"
        stroke-linecap="round"
        stroke-linejoin="round"
      >
        <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
        <polyline points="7 10 12 15 17 10" />
        <line x1="12" y1="15" x2="12" y2="3" />
      </svg>
      Download .md
    </button>
  </div>
</template>
