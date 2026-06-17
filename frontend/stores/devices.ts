import { defineStore } from 'pinia'
import type { DeviceOut } from '~/types'

export const useDevicesStore = defineStore('devices', () => {
  const config  = useRuntimeConfig()
  const devices = ref<DeviceOut[]>([])
  const loading = ref(false)
  const error   = ref<string | null>(null)

  async function fetchDevices() {
    loading.value = true
    error.value   = null
    try {
      devices.value = await $fetch<DeviceOut[]>(`${config.public.apiBase}/devices`)
    } catch {
      error.value = 'Failed to load devices'
    } finally {
      loading.value = false
    }
  }

  return { devices, loading, error, fetchDevices }
})
