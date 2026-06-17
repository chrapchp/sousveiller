import { defineStore } from 'pinia'
import type { FingerprintDetailOut, FingerprintOut } from '~/types'

export const useFingerprintsStore = defineStore('fingerprints', () => {
  const config             = useRuntimeConfig()
  const fingerprints       = ref<FingerprintOut[]>([])
  const currentFingerprint = ref<FingerprintDetailOut | null>(null)
  const loading            = ref(false)
  const error              = ref<string | null>(null)

  async function fetchFingerprints() {
    loading.value = true
    error.value   = null
    try {
      fingerprints.value = await $fetch<FingerprintOut[]>(`${config.public.apiBase}/fingerprints`)
    } catch {
      error.value = 'Failed to load fingerprint groups'
    } finally {
      loading.value = false
    }
  }

  async function fetchFingerprint(hash: string) {
    loading.value            = true
    error.value              = null
    currentFingerprint.value = null
    try {
      currentFingerprint.value = await $fetch<FingerprintDetailOut>(
        `${config.public.apiBase}/fingerprints/${hash}`,
      )
    } catch {
      error.value = 'Failed to load fingerprint group'
    } finally {
      loading.value = false
    }
  }

  return { fingerprints, currentFingerprint, loading, error, fetchFingerprints, fetchFingerprint }
})
