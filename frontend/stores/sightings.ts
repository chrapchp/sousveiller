import { defineStore } from 'pinia'
import type { SightingOut, StatsOut } from '~/types'

const REFRESH_MS = 30_000

export const useSightingsStore = defineStore('sightings', () => {
  const config   = useRuntimeConfig()
  const sightings = ref<SightingOut[]>([])
  const stats    = ref<StatsOut | null>(null)
  const loading  = ref(false)
  const error    = ref<string | null>(null)
  let   timer: ReturnType<typeof setInterval> | null = null

  async function fetchSightings(params?: { mac?: string; since?: string; limit?: number }) {
    loading.value = true
    error.value   = null
    try {
      const q = new URLSearchParams()
      if (params?.mac)   q.set('mac',   params.mac)
      if (params?.since) q.set('since', params.since)
      if (params?.limit) q.set('limit', String(params.limit))
      const qs = q.toString()
      sightings.value = await $fetch<SightingOut[]>(
        `${config.public.apiBase}/sightings${qs ? '?' + qs : ''}`,
      )
    } catch {
      error.value = 'Failed to load sightings'
    } finally {
      loading.value = false
    }
  }

  async function fetchStats() {
    try {
      stats.value = await $fetch<StatsOut>(`${config.public.apiBase}/stats`)
    } catch { /* non-fatal */ }
  }

  function startAutoRefresh(params?: Parameters<typeof fetchSightings>[0]) {
    stopAutoRefresh()
    timer = setInterval(() => fetchSightings(params), REFRESH_MS)
  }

  function stopAutoRefresh() {
    if (timer) { clearInterval(timer); timer = null }
  }

  return { sightings, stats, loading, error, fetchSightings, fetchStats, startAutoRefresh, stopAutoRefresh }
})
