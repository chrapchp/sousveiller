<script setup lang="ts">
defineProps<{
  label: string
  value: string | number
  sub?: string
}>()
</script>

<template>
  <div class="bg-gray-900 border border-gray-800 rounded-lg p-4">
    <p class="text-xs text-gray-500 uppercase tracking-wider mb-1">{{ label }}</p>
    <p class="text-2xl font-bold text-white tabular-nums">{{ value }}</p>
    <p v-if="sub" class="text-xs text-gray-500 mt-1">{{ sub }}</p>
  </div>
</template>
