<script setup>
import { useTheme } from '../composables/useTheme.js'

const { isDark, toggleTheme } = useTheme()
</script>

<template>
  <header
    class="sticky top-0 z-40 border-b backdrop-blur-sm"
    style="
      background-color: color-mix(in srgb, var(--color-canvas-default) 85%, transparent);
      border-color: var(--color-border-default);
    "
  >
    <div class="mx-auto max-w-5xl px-4 sm:px-6 h-14 flex items-center justify-between gap-4">
      <!-- Logo + title -->
      <div class="flex items-center gap-2 min-w-0">
        <svg
          aria-hidden="true"
          class="shrink-0 text-accent-fg"
          style="color: var(--color-accent-fg)"
          width="22"
          height="22"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
          stroke-linecap="round"
          stroke-linejoin="round"
        >
          <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
          <polyline points="14 2 14 8 20 8" />
          <line x1="16" y1="13" x2="8" y2="13" />
          <line x1="16" y1="17" x2="8" y2="17" />
          <polyline points="10 9 9 9 8 9" />
        </svg>
        <span
          class="font-mono text-base font-semibold tracking-tight truncate"
          style="color: var(--color-fg-default)"
        >html2md</span>
        <span
          class="hidden sm:inline text-sm"
          style="color: var(--color-fg-muted)"
        >— URL to Markdown</span>
      </div>

      <!-- Theme toggle -->
      <button
        type="button"
        :aria-label="isDark ? 'Switch to light theme' : 'Switch to dark theme'"
        :title="isDark ? 'Switch to light theme' : 'Switch to dark theme'"
        class="gh-btn-secondary inline-flex items-center justify-center w-9 h-9 rounded-md border transition-colors duration-150"
        style="
          background-color: var(--color-btn-bg);
          border-color: var(--color-btn-border);
          color: var(--color-fg-muted);
        "
        @click="toggleTheme"
      >
        <!-- Sun icon (shown in dark mode) -->
        <svg
          v-if="isDark"
          aria-hidden="true"
          width="16"
          height="16"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
          stroke-linecap="round"
          stroke-linejoin="round"
        >
          <circle cx="12" cy="12" r="5" />
          <line x1="12" y1="1" x2="12" y2="3" />
          <line x1="12" y1="21" x2="12" y2="23" />
          <line x1="4.22" y1="4.22" x2="5.64" y2="5.64" />
          <line x1="18.36" y1="18.36" x2="19.78" y2="19.78" />
          <line x1="1" y1="12" x2="3" y2="12" />
          <line x1="21" y1="12" x2="23" y2="12" />
          <line x1="4.22" y1="19.78" x2="5.64" y2="18.36" />
          <line x1="18.36" y1="5.64" x2="19.78" y2="4.22" />
        </svg>
        <!-- Moon icon (shown in light mode) -->
        <svg
          v-else
          aria-hidden="true"
          width="16"
          height="16"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
          stroke-linecap="round"
          stroke-linejoin="round"
        >
          <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z" />
        </svg>
      </button>
    </div>
  </header>
</template>
