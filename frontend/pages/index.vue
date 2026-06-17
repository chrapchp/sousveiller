<script setup lang="ts">
const sightingsStore = useSightingsStore()
const { stats, sightings, loading } = storeToRefs(sightingsStore)

onMounted(() => {
  sightingsStore.fetchStats()
  sightingsStore.fetchSightings({ limit: 10 })
})
</script>

<template>
  <div>
    <h1 class="text-2xl font-bold text-white mb-6">Dashboard</h1>

    <div class="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
      <StatCard label="Total Devices"   :value="stats?.total_devices   ?? '—'" />
      <StatCard label="Total Sightings" :value="stats?.total_sightings ?? '—'" />
      <StatCard label="Active Scanners" :value="stats?.active_scanners ?? '—'" />
      <StatCard
        label="Last Scan"
        :value="stats?.last_scan ? new Date(stats.last_scan).toLocaleTimeString() : '—'"
        :sub="stats?.last_scan   ? new Date(stats.last_scan).toLocaleDateString()  : undefined"
      />
    </div>

    <h2 class="text-base font-semibold text-gray-300 mb-3">Recent Sightings</h2>

    <div v-if="loading" class="text-gray-500 text-sm">Loading…</div>
    <ul v-else class="space-y-2">
      <li
        v-for="s in sightings"
        :key="s.id"
        class="bg-gray-900 border border-gray-800 rounded-lg px-4 py-3 flex items-center gap-4 text-sm"
      >
        <span class="font-mono text-green-400 text-xs shrink-0">{{ s.mac }}</span>
        <span class="text-gray-400 truncate">{{ s.name ?? '—' }}</span>
        <span class="text-gray-400 text-xs ml-auto shrink-0">{{ s.rssi }} dBm</span>
        <span class="text-gray-500 text-xs shrink-0">{{ new Date(s.seen_at).toLocaleString() }}</span>
      </li>
      <li v-if="sightings.length === 0" class="text-gray-500 text-sm">No sightings yet</li>
    </ul>
  </div>
</template>
