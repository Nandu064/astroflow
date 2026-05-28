import { defineStore } from 'pinia'
import { ref, shallowRef, computed } from 'vue'

const WS_URL = import.meta.env.VITE_WS_URL || `ws://${window.location.host}/ws`
const MAX_CHART_POINTS = 60
const RECONNECT_DELAY_MS = 4000

export const useRealtimeStore = defineStore('realtime', () => {
  // Connection state
  const connected = ref(false)
  const mode = ref('connecting') // 'connecting' | 'live' | 'reconnecting' | 'demo'

  // Latest payload
  const metrics   = ref(null)
  const neo       = ref(null)
  const etlJobs   = ref([])
  const events    = ref([])

  // Chart history — shallowRef so Chart.js internal mutations don't trigger Vue's deep proxy
  const cpuHistory    = shallowRef(Array(MAX_CHART_POINTS).fill(null))
  const memHistory    = shallowRef(Array(MAX_CHART_POINTS).fill(null))
  const chartLabels   = shallowRef(Array(MAX_CHART_POINTS).fill(''))

  // Computed helpers
  const etlRunning  = computed(() => etlJobs.value.filter(j => j.status === 'running').length)
  const etlHealthy  = computed(() => etlJobs.value.filter(j => j.status !== 'failed').length)
  const isHazardous = computed(() => neo.value?.hazardous ?? false)

  let _ws = null
  let _demoInterval = null
  let _demoTick = 0
  let _demoCpu = 38
  let _demoPrev = {}

  // ── WebSocket ────────────────────────────────────────────────────────────

  function connect() {
    mode.value = 'connecting'
    try {
      _ws = new WebSocket(WS_URL)
    } catch {
      _startDemo()
      return
    }

    const timeout = setTimeout(() => {
      _ws?.close()
      _startDemo()
    }, 3500)

    _ws.onopen = () => {
      clearTimeout(timeout)
      connected.value = true
      mode.value = 'live'
      _stopDemo()
    }

    _ws.onmessage = (e) => {
      try { _applyPayload(JSON.parse(e.data)) } catch { /* ignore */ }
    }

    _ws.onclose = () => {
      connected.value = false
      mode.value = 'reconnecting'
      _startDemo()
      setTimeout(connect, RECONNECT_DELAY_MS)
    }

    _ws.onerror = () => {
      clearTimeout(timeout)
    }
  }

  function disconnect() {
    _ws?.close()
    _stopDemo()
  }

  // ── Payload application ─────────────────────────────────────────────────

  function _applyPayload(data) {
    if (data.metrics) {
      metrics.value = data.metrics
      _pushChart(data.metrics.cpu, data.metrics.mem)
    }
    if (data.neo !== undefined) neo.value = data.neo
    if (Array.isArray(data.etl)) etlJobs.value = data.etl
    if (data.alert) _addEvent(data.alert)
  }

  function _pushChart(cpu, mem) {
    cpuHistory.value = [...cpuHistory.value.slice(1), cpu ?? null]
    memHistory.value = [...memHistory.value.slice(1), mem ?? null]
  }

  function _addEvent(alert) {
    events.value.unshift({
      id: Date.now(),
      type: alert.type,
      message: alert.message,
      ts: new Date().toLocaleTimeString(),
    })
    if (events.value.length > 50) events.value.pop()
  }

  // ── Demo / simulation mode ──────────────────────────────────────────────

  const DEMO_ASTEROIDS = ['2024 XK1', 'Apophis', 'Bennu', '1994 PC1', 'Florence', '2023 BU']
  const DEMO_ALERTS = [
    { type: 'info',     message: 'NEO approach detected within 0.12 AU' },
    { type: 'warning',  message: 'Solar Flare X1.4 detected by GOES-16' },
    { type: 'success',  message: "ETL 'NASA NEO Feed' completed in 3.8s" },
    { type: 'critical', message: 'Geomagnetic storm G3 incoming — 18h warning' },
    { type: 'info',     message: 'New exoplanet candidate confirmed in sector 42' },
  ]
  const DEMO_JOBS = ['NASA NEO Feed', 'NOAA Space Weather', 'Exoplanet Archive', 'Solar Flare Events']

  function _demoStep() {
    _demoTick++
    _demoCpu = Math.max(8, Math.min(96, _demoCpu + (Math.random() - 0.48) * 2.2))
    const mem = Math.max(28, Math.min(90, (_demoPrev.mem ?? 61) + (Math.random() - 0.5) * 1.1))

    const payload = {
      metrics: {
        cpu: +_demoCpu.toFixed(1),
        mem: +mem.toFixed(1),
        connections: Math.floor(Math.random() * 40 + 5),
        uptime_s: _demoTick,
      },
      neo: {
        name: DEMO_ASTEROIDS[_demoTick % DEMO_ASTEROIDS.length],
        dist_au: +(Math.random() * 1.8 + 0.05).toFixed(4),
        vel_km_s: +(Math.random() * 33 + 5).toFixed(1),
        diam_min_m: Math.floor(Math.random() * 800 + 50),
        diam_max_m: Math.floor(Math.random() * 1200 + 200),
        hazardous: Math.random() < 0.15,
      },
      etl: DEMO_JOBS.map(name => ({
        name,
        status: Math.random() < 0.1 ? 'running' : 'idle',
        last_run_at: new Date(Date.now() - Math.random() * 3600000).toISOString(),
        duration_s: +(Math.random() * 18 + 1).toFixed(1),
        records: Math.floor(Math.random() * 49000 + 500),
        success_rate: +(Math.random() * 5 + 95).toFixed(1),
        error: null,
      })),
      alert: Math.random() < 0.06 ? DEMO_ALERTS[Math.floor(Math.random() * DEMO_ALERTS.length)] : null,
    }

    _demoPrev.mem = mem
    _applyPayload(payload)
  }

  function _startDemo() {
    if (_demoInterval) return
    mode.value = 'demo'
    _demoInterval = setInterval(_demoStep, 1000)
  }

  function _stopDemo() {
    if (_demoInterval) {
      clearInterval(_demoInterval)
      _demoInterval = null
    }
  }

  return {
    connected, mode, metrics, neo, etlJobs, events,
    cpuHistory, memHistory, chartLabels,
    etlRunning, etlHealthy, isHazardous,
    connect, disconnect,
  }
})
