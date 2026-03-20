import axios from 'axios'
import { ref } from 'vue'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000',
  headers: { 'Content-Type': 'application/json' },
})

export function useApi() {
  const loading = ref(false)
  const error = ref(null)

  async function extractContent(url) {
    loading.value = true
    error.value = null
    try {
      const { data } = await api.post('/extract', { url })
      return data
    } catch (err) {
      error.value = err.response?.data?.detail ?? err.message ?? 'Failed to extract content.'
      return null
    } finally {
      loading.value = false
    }
  }

  async function convertToMarkdown(html) {
    loading.value = true
    error.value = null
    try {
      const { data } = await api.post('/convert', { html })
      return data
    } catch (err) {
      error.value = err.response?.data?.detail ?? err.message ?? 'Failed to convert to Markdown.'
      return null
    } finally {
      loading.value = false
    }
  }

  return { loading, error, extractContent, convertToMarkdown }
}
