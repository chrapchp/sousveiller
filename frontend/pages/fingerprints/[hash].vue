<script setup lang="ts">
const route = useRoute()
const hash  = route.params.hash as string

const store = useFingerprintsStore()
const { currentFingerprint, loading, error } = storeToRefs(store)

onMounted(() => store.fetchFingerprint(hash))

function fmt(iso: string) {
  return new Date(iso).toLocaleString()
}
</script>

<template>
  <div>
    <NuxtLink
      to="/fingerprints"
      class="inline-flex items-center gap-1 text-gray-500 hover:text-white text-sm mb-4 transition-colors"
    >
      ← Groups
    </NuxtLink>

    <div v-if="loading" class="text-gray-500 text-sm mt-8">Loading…</div>
    <div v-else-if="error" class="text-red-400 text-sm mt-8">{{ error }}</div>
    <div v-else-if="currentFingerprint">

      <!-- Header -->
      <div class="mb-6">
        <div class="flex flex-wrap items-center gap-3 mb-2">
          <h1 class="text-xl font-bold text-white font-mono">
            {{ currentFingerprint.fingerprint_hash.slice(0, 8) }}
          </h1>
          <span class="text-xs bg-gray-800 text-gray-400 rounded px-2 py-0.5">
            {{ currentFingerprint.strategy }}
          </span>
          <span
            v-if="currentFingerprint.mac_count > 1"
            class="text-xs bg-amber-900/40 text-amber-400 border border-amber-800/50 rounded px-2 py-0.5"
          >
            {{ currentFingerprint.mac_count }} MACs — re-identified
          </span>
        </div>
        <p class="font-mono text-xs text-gray-700 break-all select-all">
          {{ currentFingerprint.fingerprint_hash }}
        </p>
      </div>

      <!-- Key components -->
      <div class="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-6">
        <div class="bg-gray-900 border border-gray-800 rounded-lg p-4">
          <p class="text-xs text-gray-500 uppercase tracking-wide mb-2">Service UUIDs Key</p>
          <p class="font-mono text-xs text-gray-300 break-all">
            {{ currentFingerprint.service_uuids_key || '—' }}
          </p>
        </div>
        <div class="bg-gray-900 border border-gray-800 rounded-lg p-4">
          <p class="text-xs text-gray-500 uppercase tracking-wide mb-2">Mfr Data Prefix</p>
          <p class="font-mono text-xs text-gray-300">
            {{ currentFingerprint.mfr_prefix || '—' }}
          </p>
        </div>
      </div>

      <!-- Stats -->
      <div class="grid grid-cols-2 sm:grid-cols-4 gap-4 mb-8">
        <StatCard label="Linked MACs" :value="currentFingerprint.mac_count" />
        <StatCard label="Sightings"   :value="currentFingerprint.sighting_count" />
        <StatCard label="First Seen"  :value="new Date(currentFingerprint.first_seen).toLocaleDateString()" />
        <StatCard label="Last Seen"   :value="new Date(currentFingerprint.last_seen).toLocaleDateString()" />
      </div>

      <!-- Linked devices -->
      <h2 class="text-base font-semibold text-gray-300 mb-3">Linked Devices</h2>
      <p v-if="currentFingerprint.mac_count > 1" class="text-amber-400/80 text-xs mb-3">
        These MACs share the same BLE fingerprint and are likely the same physical device.
      </p>
      <DeviceTable :devices="currentFingerprint.devices" />
    </div>
  </div>
</template>
