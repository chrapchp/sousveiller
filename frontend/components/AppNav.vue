<script setup lang="ts">
const links = [
  { to: '/',             label: 'Dashboard', icon: '▣' },
  { to: '/map',          label: 'Map',       icon: '◈' },
  { to: '/devices',      label: 'Devices',   icon: '◉' },
  { to: '/fingerprints', label: 'Groups',    icon: '◎' },
]
</script>

<template>
  <!-- Sidebar — desktop -->
  <nav class="hidden lg:flex lg:flex-col lg:fixed lg:inset-y-0 lg:w-64 bg-gray-900 border-r border-gray-800 z-40">
    <div class="p-6 border-b border-gray-800">
      <h1 class="text-lg font-bold text-green-400 tracking-widest uppercase">Sousveiller</h1>
      <p class="text-xs text-gray-500 mt-0.5">BT Device Scanner</p>
    </div>
    <ul class="flex-1 px-3 py-4 space-y-1">
      <li v-for="link in links" :key="link.to">
        <NuxtLink
          :to="link.to"
          class="flex items-center gap-3 px-3 py-2 rounded-lg text-gray-400 hover:text-white hover:bg-gray-800 transition-colors text-sm"
          active-class="text-white bg-gray-800 font-medium"
          :exact="link.to === '/'"
        >
          <span class="text-base">{{ link.icon }}</span>
          <span>{{ link.label }}</span>
        </NuxtLink>
      </li>
    </ul>
  </nav>

  <!-- Bottom tab bar — mobile -->
  <nav class="lg:hidden fixed bottom-0 inset-x-0 bg-gray-900 border-t border-gray-800 z-50 safe-area-pb">
    <ul class="flex">
      <li v-for="link in links" :key="link.to" class="flex-1">
        <NuxtLink
          :to="link.to"
          class="flex flex-col items-center gap-0.5 py-3 text-gray-400 hover:text-white text-xs transition-colors"
          active-class="text-green-400"
          :exact="link.to === '/'"
        >
          <span class="text-xl leading-none">{{ link.icon }}</span>
          <span>{{ link.label }}</span>
        </NuxtLink>
      </li>
    </ul>
  </nav>
</template>
