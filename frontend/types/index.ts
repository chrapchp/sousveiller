export interface SightingOut {
  id: number
  mac: string
  rssi: number
  name: string | null
  manufacturer_data: string | null
  service_uuids: string[]
  tx_power: number | null
  fingerprint_hash: string | null
  lat: number
  lng: number
  simulated: boolean
  device_id: string
  seen_at: string
}

export interface DeviceOut {
  mac: string
  name: string | null
  manufacturer_data: string | null
  service_uuids: string[]
  fingerprint_hash: string | null
  first_seen: string
  last_seen: string
  sighting_count: number
  avg_rssi: number
  last_lat: number
  last_lng: number
}

export interface StatsOut {
  total_devices: number
  total_sightings: number
  active_scanners: number
  last_scan: string | null
}

export interface FingerprintOut {
  fingerprint_hash: string
  strategy: string
  service_uuids_key: string | null
  mfr_prefix: string | null
  first_seen: string
  last_seen: string
  mac_count: number
  sighting_count: number
}

export interface FingerprintDetailOut extends FingerprintOut {
  devices: DeviceOut[]
}
