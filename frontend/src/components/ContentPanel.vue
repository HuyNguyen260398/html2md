<script setup>
defineProps({
  label: {
    type: String,
    required: true,
  },
  content: {
    type: String,
    default: '',
  },
  language: {
    type: String,
    default: 'plaintext',
  },
  placeholder: {
    type: String,
    default: 'Content will appear here…',
  },
})
</script>

<template>
  <div class="flex flex-col h-full">
    <!-- Panel label -->
    <div
      class="flex items-center justify-between px-3 py-2 border-b rounded-t-md shrink-0"
      style="
        background-color: var(--color-canvas-subtle);
        border-color: var(--color-border-default);
      "
    >
      <span
        class="text-xs font-semibold font-mono uppercase tracking-wider"
        style="color: var(--color-fg-muted)"
      >{{ label }}</span>
      <span
        v-if="content"
        class="text-xs font-mono"
        style="color: var(--color-fg-muted)"
      >{{ content.length.toLocaleString() }} chars</span>
    </div>

    <!-- Scrollable content area -->
    <div
      class="gh-scrollbar relative rounded-b-md border border-t-0 overflow-y-auto"
      style="
        background-color: var(--color-canvas-subtle);
        border-color: var(--color-border-default);
        min-height: 300px;
        max-height: 60vh;
      "
    >
      <!-- Empty state -->
      <div
        v-if="!content"
        class="absolute inset-0 flex flex-col items-center justify-center gap-2 select-none pointer-events-none"
        aria-hidden="true"
      >
        <svg
          width="36"
          height="36"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="1.5"
          stroke-linecap="round"
          stroke-linejoin="round"
          style="color: var(--color-fg-muted); opacity: 0.4"
        >
          <rect x="3" y="3" width="18" height="18" rx="2" ry="2" />
          <line x1="3" y1="9" x2="21" y2="9" />
          <line x1="9" y1="21" x2="9" y2="3" />
        </svg>
        <p class="text-sm" style="color: var(--color-fg-muted); opacity: 0.6">
          {{ placeholder }}
        </p>
      </div>

      <!-- Content -->
      <pre
        v-if="content"
        class="m-0 p-4 text-xs leading-relaxed overflow-x-auto whitespace-pre-wrap break-words"
        style="color: var(--color-fg-default); font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, 'Courier New', monospace;"
      ><code>{{ content }}</code></pre>
    </div>
  </div>
</template>
