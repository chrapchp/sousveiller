<script setup lang="ts">
import type { DeviceOut } from '~/types'

const props = defineProps<{
  devices: DeviceOut[]
  loading?: boolean
}>()

const router = useRouter()
const search = ref('')

const filtered = computed(() =>
  props.devices.filter(d =>
    d.mac.toLowerCase().includes(search.value.toLowerCase()) ||
    (d.name ?? '').toLowerCase().includes(search.value.toLowerCase())
  )
)

function fmt(iso: string) {
  return new Date(iso).toLocaleString()
}

function shortHash(h: string) {
  return h.slice(0, 8)
}
</script>

<template>
  <div>
    <input
      v-model="search"
      type="text"
      placeholder="Filter by MAC or name…"
      class="mb-4 w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-sm text-white placeholder-gray-500 focus:outline-none focus:border-green-500"
    />
    <div class="overflow-x-auto">
      <table class="w-full text-sm">
        <thead>
          <tr class="text-left text-xs text-gray-500 uppercase tracking-wide border-b border-gray-800">
            <th class="pb-2 pr-4 font-medium">MAC</th>
            <th class="pb-2 pr-4 font-medium">Name</th>
            <th class="pb-2 pr-4 font-medium">Group</th>
            <th class="pb-2 pr-4 font-medium">First seen</th>
            <th class="pb-2 pr-4 font-medium">Last seen</th>
            <th class="pb-2 pr-4 font-medium">Sightings</th>
            <th class="pb-2 font-medium">Avg RSSI</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="loading">
            <td colspan="7" class="py-10 text-center text-gray-500">Loading…</td>
          </tr>
          <tr
            v-for="d in filtered"
            :key="d.mac"
            class="border-b border-gray-800/50 hover:bg-gray-800/50 cursor-pointer transition-colors"
            @click="router.push(`/devices/${encodeURIComponent(d.mac)}`)"
          >
            <td class="py-3 pr-4 font-mono text-green-400 text-xs">{{ d.mac }}</td>
            <td class="py-3 pr-4 text-gray-300">{{ d.name ?? '—' }}</td>
            <td class="py-3 pr-4">
              <NuxtLink
                v-if="d.fingerprint_hash"
                :to="`/fingerprints/${d.fingerprint_hash}`"
                class="font-mono text-xs text-purple-400 hover:text-purple-300 transition-colors"
                @click.stop
              >{{ shortHash(d.fingerprint_hash) }}</NuxtLink>
              <span v-else class="text-gray-600 text-xs">—</span>
            </td>
            <td class="py-3 pr-4 text-gray-400 text-xs">{{ fmt(d.first_seen) }}</td>
            <td class="py-3 pr-4 text-gray-400 text-xs">{{ fmt(d.last_seen) }}</td>
            <td class="py-3 pr-4 text-gray-300 tabular-nums">{{ d.sighting_count }}</td>
            <td class="py-3 text-gray-300 tabular-nums">{{ d.avg_rssi.toFixed(1) }} dBm</td>
          </tr>
          <tr v-if="!loading && filtered.length === 0">
            <td colspan="7" class="py-10 text-center text-gray-500">No devices found</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>
