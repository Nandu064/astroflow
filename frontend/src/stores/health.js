import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

const BASE = import.meta.env.VITE_API_URL || ''

export const useHealthStore = defineStore('health', () => {
  const server = ref(null)
  const etl    = ref(null)
  const loading = ref(false)
  const error   = ref(null)
  let _interval = null

  const serverStatus = computed(() => server.value?.status ?? 'unknown')
  const etlStatus    = computed(() => etl.value?.status    ?? 'unknown')

  async function fetchServer() {
    try {
      const res = await fetch(`${BASE}/health`)
      server.value = await res.json()
      error.value = null
    } catch (e) {
      error.value = e.message
    }
  }

  async function fetchEtl() {
    try {
      const res = await fetch(`${BASE}/health/etl`)
      etl.value = await res.json()
    } catch (e) {
      error.value = e.message
    }
  }

  async function refresh() {
    loading.value = true
    await Promise.all([fetchServer(), fetchEtl()])
    loading.value = false
  }

  function startPolling(intervalMs = 5000) {
    refresh()
    _interval = setInterval(refresh, intervalMs)
  }

  function stopPolling() {
    if (_interval) { clearInterval(_interval); _interval = null }
  }

  return {
    server, etl, loading, error,
    serverStatus, etlStatus,
    refresh, startPolling, stopPolling,
  }
})
