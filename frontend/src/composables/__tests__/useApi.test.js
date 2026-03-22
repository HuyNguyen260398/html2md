import { describe, it, expect, vi, beforeEach } from 'vitest'
import { useApi } from '../useApi'

vi.mock('axios', () => {
  const mockInstance = {
    post: vi.fn(),
  }
  return {
    default: {
      create: () => mockInstance,
    },
    __mockInstance: mockInstance,
  }
})

describe('useApi', () => {
  it('initialises with loading=false and no error', () => {
    const { loading, error } = useApi()
    expect(loading.value).toBe(false)
    expect(error.value).toBeNull()
  })

  it('exposes extractContent and convertToMarkdown functions', () => {
    const { extractContent, convertToMarkdown } = useApi()
    expect(typeof extractContent).toBe('function')
    expect(typeof convertToMarkdown).toBe('function')
  })
})
