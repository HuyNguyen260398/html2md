<script setup>
defineProps({
  size: {
    type: String,
    default: 'sm',
    validator: (v) => ['sm', 'md', 'lg'].includes(v),
  },
})

const sizes = {
  sm: 14,
  md: 20,
  lg: 28,
}
</script>

<template>
  <svg
    :width="sizes[size]"
    :height="sizes[size]"
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    stroke-width="2.5"
    stroke-linecap="round"
    stroke-linejoin="round"
    class="animate-spin"
    aria-hidden="true"
    role="status"
    style="flex-shrink: 0"
  >
    <path d="M12 2v4M12 18v4M4.93 4.93l2.83 2.83M16.24 16.24l2.83 2.83M2 12h4M18 12h4M4.93 19.07l2.83-2.83M16.24 7.76l2.83-2.83"
      opacity="0.4"
    />
    <path d="M12 2v4" />
  </svg>
</template>
