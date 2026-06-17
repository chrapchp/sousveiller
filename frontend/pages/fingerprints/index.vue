<script setup lang="ts">
const store = useFingerprintsStore()
const { fingerprints, loading, error } = storeToRefs(store)

onMounted(() => store.fetchFingerprints())

function shortHash(h: string) {
  return h.slice(0, 8)
}

function fmt(iso: string) {
  return new Date(iso).toLocaleString()
}
</script>

<template>
  <div>
    <h1 class="text-2xl font-bold text-white mb-2">Fingerprint Groups</h1>
    <p class="text-gray-500 text-sm mb-6">
      Devices grouped by stable BLE advertising features. Groups with multiple MACs indicate a re-identified device.
    </p>

    <p v-if="error" class="text-red-400 text-sm mb-4">{{ error }}</p>
    <div v-if="loading" class="text-gray-500 text-sm">Loading…</div>
    <div v-else class="overflow-x-auto">
      <table class="w-full text-sm">
        <thead>
          <tr class="text-left text-xs text-gray-500 uppercase tracking-wide border-b border-gray-800">
            <th class="pb-2 pr-4 font-medium">Hash</th>
            <th class="pb-2 pr-4 font-medium">Strategy</th>
            <th class="pb-2 pr-4 font-medium">Service UUIDs</th>
            <th class="pb-2 pr-4 font-medium">Mfr Prefix</th>
            <th class="pb-2 pr-4 font-medium">MACs</th>
            <th class="pb-2 pr-4 font-medium">Sightings</th>
            <th class="pb-2 font-medium">Last Seen</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="fp in fingerprints"
            :key="fp.fingerprint_hash"
            class="border-b border-gray-800/50 hover:bg-gray-800/50 cursor-pointer transition-colors"
            @click="$router.push(`/fingerprints/${fp.fingerprint_hash}`)"
          >
            <td class="py-3 pr-4 font-mono text-purple-400 text-xs">{{ shortHash(fp.fingerprint_hash) }}</td>
            <td class="py-3 pr-4">
              <span class="text-xs bg-gray-800 text-gray-400 rounded px-2 py-0.5">{{ fp.strategy }}</span>
            </td>
            <td class="py-3 pr-4 font-mono text-xs text-gray-400 max-w-48 truncate" :title="fp.service_uuids_key ?? ''">
              {{ fp.service_uuids_key || '—' }}
            </td>
            <td class="py-3 pr-4 font-mono text-xs text-gray-400">{{ fp.mfr_prefix || '—' }}</td>
            <td class="py-3 pr-4">
              <span
                class="tabular-nums font-semibold text-xs"
                :class="fp.mac_count > 1 ? 'text-amber-400' : 'text-gray-300'"
              >{{ fp.mac_count }}</span>
            </td>
            <td class="py-3 pr-4 text-gray-300 tabular-nums text-xs">{{ fp.sighting_count }}</td>
            <td class="py-3 text-gray-400 text-xs">{{ fmt(fp.last_seen) }}</td>
          </tr>
          <tr v-if="fingerprints.length === 0">
            <td colspan="7" class="py-10 text-center text-gray-500">No fingerprints yet — send some scan batches first</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>
