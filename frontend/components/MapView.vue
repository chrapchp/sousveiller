<script setup lang="ts">
import type { SightingOut } from '~/types'

const props = defineProps<{
  sightings: SightingOut[]
}>()

const center = computed<[number, number]>(() => {
  if (props.sightings.length === 0) return [37.7749, -122.4194]
  const last = props.sightings[0]
  return [last.lat, last.lng]
})
const zoom = ref(15)
</script>

<template>
  <ClientOnly>
    <LMap
      :center="center"
      :zoom="zoom"
      class="w-full h-full"
      :use-global-leaflet="false"
    >
      <LTileLayer
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        layer-type="base"
        name="OpenStreetMap"
      />
      <LCircleMarker
        v-for="s in sightings"
        :key="s.id"
        :lat-lng="[s.lat, s.lng]"
        :radius="6"
        color="#4ade80"
        fill-color="#4ade80"
        :fill-opacity="0.7"
        :weight="1"
      >
        <LPopup>
          <div class="text-xs font-mono space-y-0.5 min-w-40">
            <p><span class="text-gray-500">MAC</span>  {{ s.mac }}</p>
            <p><span class="text-gray-500">Name</span> {{ s.name ?? '—' }}</p>
            <p><span class="text-gray-500">RSSI</span> {{ s.rssi }} dBm</p>
            <p><span class="text-gray-500">Time</span> {{ new Date(s.seen_at).toLocaleString() }}</p>
          </div>
        </LPopup>
      </LCircleMarker>
    </LMap>
    <template #fallback>
      <div class="w-full h-full bg-gray-900 flex items-center justify-center text-gray-500 text-sm">
        Loading map…
      </div>
    </template>
  </ClientOnly>
</template>
