<script setup lang="ts">
const route = useRoute()
const mac   = decodeURIComponent(route.params.mac as string)

const sightingsStore = useSightingsStore()
const { sightings, loading } = storeToRefs(sightingsStore)

onMounted(() => sightingsStore.fetchSightings({ mac }))

const fingerprintHash = computed(() =>
  sightings.value.find(s => s.fingerprint_hash)?.fingerprint_hash ?? null
)
</script>

<template>
  <div>
    <NuxtLink
      to="/devices"
      class="inline-flex items-center gap-1 text-gray-500 hover:text-white text-sm mb-4 transition-colors"
    >
      ← Devices
    </NuxtLink>

    <div class="flex flex-wrap items-center gap-3 mb-1">
      <h1 class="text-xl font-bold text-white font-mono">{{ mac }}</h1>
      <NuxtLink
        v-if="fingerprintHash"
        :to="`/fingerprints/${fingerprintHash}`"
        class="text-xs font-mono text-purple-400 hover:text-purple-300 bg-purple-900/20 border border-purple-800/40 rounded px-2 py-0.5 transition-colors"
        title="View fingerprint group"
      >◎ {{ fingerprintHash.slice(0, 8) }}</NuxtLink>
    </div>
    <p class="text-gray-400 text-sm mb-6">{{ sightings.length }} sightings</p>

    <div class="h-64 rounded-lg overflow-hidden border border-gray-800 mb-8">
      <MapView :sightings="sightings" />
    </div>

    <h2 class="text-base font-semibold text-gray-300 mb-3">Sighting History</h2>
    <div v-if="loading" class="text-gray-500 text-sm">Loading…</div>
    <div v-else class="overflow-x-auto">
      <table class="w-full text-sm">
        <thead>
          <tr class="text-left text-xs text-gray-500 uppercase tracking-wide border-b border-gray-800">
            <th class="pb-2 pr-4 font-medium">Time</th>
            <th class="pb-2 pr-4 font-medium">Location</th>
            <th class="pb-2 font-medium">RSSI</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="s in sightings"
            :key="s.id"
            class="border-b border-gray-800/50 text-gray-300"
          >
            <td class="py-2 pr-4 text-xs">{{ new Date(s.seen_at).toLocaleString() }}</td>
            <td class="py-2 pr-4 font-mono text-xs text-gray-400">
              {{ s.lat.toFixed(6) }}, {{ s.lng.toFixed(6) }}
            </td>
            <td class="py-2 tabular-nums text-xs">{{ s.rssi }} dBm</td>
          </tr>
          <tr v-if="sightings.length === 0">
            <td colspan="3" class="py-10 text-center text-gray-500">No sightings</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>
