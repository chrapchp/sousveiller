<script setup lang="ts">
const devicesStore = useDevicesStore()
const { devices, loading, error } = storeToRefs(devicesStore)

onMounted(() => devicesStore.fetchDevices())
</script>

<template>
  <div>
    <h1 class="text-2xl font-bold text-white mb-6">Devices</h1>
    <p v-if="error" class="text-red-400 text-sm mb-4">{{ error }}</p>
    <DeviceTable :devices="devices" :loading="loading" />
  </div>
</template>
