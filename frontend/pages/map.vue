<script setup lang="ts">
const sightingsStore = useSightingsStore()
const { sightings, loading } = storeToRefs(sightingsStore)

const macFilter = ref('')

const filtered = computed(() =>
  macFilter.value
    ? sightings.value.filter(s => s.mac.includes(macFilter.value))
    : sightings.value
)

onMounted(async () => {
  await sightingsStore.fetchSightings({ limit: 500 })
  sightingsStore.startAutoRefresh({ limit: 500 })
})

onUnmounted(() => sightingsStore.stopAutoRefresh())
</script>

<template>
  <div class="flex flex-col" style="height: calc(100vh - 6rem)">
    <div class="flex items-center gap-3 mb-4 flex-wrap">
      <h1 class="text-2xl font-bold text-white">Map</h1>
      <input
        v-model="macFilter"
        type="text"
        placeholder="Filter by MAC…"
        class="bg-gray-800 border border-gray-700 rounded-lg px-3 py-1.5 text-sm text-white placeholder-gray-500 focus:outline-none focus:border-green-500"
      />
      <span class="text-gray-500 text-xs">{{ filtered.length }} sightings</span>
      <span v-if="loading" class="text-gray-500 text-xs ml-auto">Refreshing…</span>
    </div>
    <div class="flex-1 rounded-lg overflow-hidden border border-gray-800">
      <MapView :sightings="filtered" />
    </div>
  </div>
</template>
