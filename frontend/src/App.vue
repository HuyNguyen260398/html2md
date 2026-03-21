<script setup>
import { ref, onMounted } from 'vue'
import AppHeader from './components/AppHeader.vue'
import UrlInput from './components/UrlInput.vue'
import ContentPanel from './components/ContentPanel.vue'
import ActionBar from './components/ActionBar.vue'
import { useApi } from './composables/useApi.js'

const { loading, error: apiError, extractContent, convertToMarkdown } = useApi()

onMounted(() => {
  const loader = document.getElementById('page-loader')
  if (!loader) return
  // Snap the indeterminate bar to full width, then fade the overlay out
  const bar = loader.querySelector('.loader-bar')
  if (bar) {
    bar.style.animation = 'none'
    bar.style.transition = 'left 0.18s ease-out, width 0.18s ease-out'
    bar.style.left = '0'
    bar.style.width = '100%'
  }
  setTimeout(() => {
    loader.classList.add('fade-out')
    setTimeout(() => loader.remove(), 320)
  }, 180)
})

const rawHtml = ref('')
const markdownText = ref('')
const converting = ref(false)
const convertError = ref('')

async function handleExtract(url) {
  rawHtml.value = ''
  markdownText.value = ''
  convertError.value = ''
  const result = await extractContent(url)
  if (result?.html) {
    rawHtml.value = result.html
  } else if (result?.content) {
    rawHtml.value = result.content
  }
}

async function handleConvert() {
  if (!rawHtml.value) return
  converting.value = true
  convertError.value = ''
  try {
    const result = await convertToMarkdown(rawHtml.value)
    if (result?.markdown) {
      markdownText.value = result.markdown
    } else if (typeof result === 'string') {
      markdownText.value = result
    }
  } finally {
    converting.value = false
  }
}

function handleDownload() {
  if (!markdownText.value) return
  const blob = new Blob([markdownText.value], { type: 'text/markdown;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = 'output.md'
  document.body.appendChild(a)
  a.click()
  a.remove()
  URL.revokeObjectURL(url)
}
</script>

<template>
  <div class="min-h-dvh flex flex-col" style="background-color: var(--color-canvas-default)">
    <AppHeader />

    <main class="flex-1 mx-auto w-full max-w-5xl px-4 sm:px-6 py-8 flex flex-col gap-6">
      <!-- Hero tagline -->
      <div>
        <h1
          class="text-xl font-semibold font-mono mb-1"
          style="color: var(--color-fg-default)"
        >
          Extract &amp; convert any webpage to Markdown
        </h1>
        <p class="text-sm" style="color: var(--color-fg-muted)">
          Paste a URL, extract its raw content, then convert it to clean Markdown ready for humans and AI.
        </p>
      </div>

      <!-- URL input -->
      <UrlInput :loading="loading" @extract="handleExtract" />

      <!-- API error banner -->
      <div
        v-if="apiError"
        role="alert"
        class="rounded-md border px-4 py-3 text-sm"
        style="
          background-color: color-mix(in srgb, var(--color-danger-fg) 8%, var(--color-canvas-subtle));
          border-color: color-mix(in srgb, var(--color-danger-fg) 30%, transparent);
          color: var(--color-danger-fg);
        "
      >
        <strong>Error:</strong> {{ apiError }}
      </div>

      <!-- Two-panel grid -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 items-start">
        <!-- Panel 1: Raw HTML -->
        <ContentPanel
          label="Raw HTML"
          language="html"
          :content="rawHtml"
          placeholder="Extracted HTML will appear here after clicking Extract."
        />

        <!-- Panel 2: Markdown -->
        <ContentPanel
          label="Markdown"
          language="markdown"
          :content="markdownText"
          placeholder="Converted Markdown will appear here after clicking Convert."
        />
      </div>

      <!-- Action bar -->
      <div class="flex flex-col gap-3">
        <ActionBar
          :has-raw-content="!!rawHtml"
          :has-markdown-content="!!markdownText"
          :converting="converting"
          @convert="handleConvert"
          @download="handleDownload"
        />

        <!-- Convert error -->
        <p
          v-if="convertError"
          role="alert"
          class="text-sm"
          style="color: var(--color-danger-fg)"
        >
          {{ convertError }}
        </p>
      </div>
    </main>

    <!-- Footer -->
    <footer
      class="border-t mt-auto py-4 px-4 sm:px-6 text-center text-xs"
      style="
        border-color: var(--color-border-default);
        color: var(--color-fg-muted);
      "
    >
      html2md &mdash; built with Vue 3 &amp; FastAPI
    </footer>
  </div>
</template>
