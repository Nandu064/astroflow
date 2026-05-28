<template>
  <div>
    <div class="d-flex align-center justify-space-between mb-6">
      <div>
        <h1 class="font-orbitron text-primary glow-cyan" style="font-size:1.4rem;letter-spacing:4px;font-weight:900;">
          SERVER HEALTH
        </h1>
        <p class="font-mono text-medium-emphasis mt-1" style="font-size:.7rem;letter-spacing:2px;">
          INFRASTRUCTURE MONITORING · LIVE METRICS
        </p>
      </div>
      <div class="d-flex ga-2 align-center">
        <v-chip :color="overallColor" variant="tonal" size="small" class="font-mono" style="letter-spacing:2px;font-size:.62rem;">
          <span class="pulse-dot mr-1">●</span> {{ overallStatus.toUpperCase() }}
        </v-chip>
        <v-btn icon="mdi-refresh" variant="text" color="primary" size="small" :loading="health.loading" @click="health.refresh()" />
      </div>
    </div>

    <!-- Top metric cards -->
    <v-row class="mb-4">
      <v-col v-for="c in topCards" :key="c.label" cols="6" md="3">
        <MetricCard v-bind="c" />
      </v-col>
    </v-row>

    <v-row>
      <!-- System gauges -->
      <v-col cols="12" md="6">
        <v-card style="background:rgba(6,6,18,.9);border:1px solid rgba(80,140,240,.1);" class="card-accent-cyan">
          <v-card-text class="pa-4">
            <p class="font-mono text-medium-emphasis mb-4" style="font-size:.7rem;letter-spacing:2px;">SYSTEM RESOURCES</p>
            <div class="d-flex flex-column ga-4">
              <div v-for="g in gauges" :key="g.label">
                <div class="d-flex justify-space-between mb-1">
                  <div class="d-flex align-center ga-2">
                    <v-icon :color="g.color" size="16">{{ g.icon }}</v-icon>
                    <span class="font-mono text-on-surface" style="font-size:.72rem;">{{ g.label }}</span>
                  </div>
                  <span class="font-orbitron" :class="`text-${g.color}`" style="font-size:.9rem;font-weight:700;">{{ g.value }}</span>
                </div>
                <v-progress-linear
                  :model-value="g.pct"
                  :color="g.color"
                  bg-color="rgba(255,255,255,.06)"
                  rounded height="6"
                />
              </div>
            </div>
          </v-card-text>
        </v-card>
      </v-col>

      <!-- Service checks -->
      <v-col cols="12" md="6">
        <v-card style="background:rgba(6,6,18,.9);border:1px solid rgba(80,140,240,.1);" class="card-accent-green" height="100%">
          <v-card-text class="pa-4">
            <p class="font-mono text-medium-emphasis mb-4" style="font-size:.7rem;letter-spacing:2px;">SERVICE CONNECTIVITY</p>
            <div class="d-flex flex-column ga-3">
              <div
                v-for="svc in services" :key="svc.label"
                class="d-flex align-center ga-3 pa-3 rounded-lg"
                style="background:rgba(255,255,255,.025);border:1px solid rgba(80,140,240,.08);"
              >
                <v-icon :color="svc.ok ? 'success' : 'error'" size="20">{{ svc.icon }}</v-icon>
                <div class="flex-grow-1">
                  <div class="font-mono text-on-surface" style="font-size:.72rem;">{{ svc.label }}</div>
                  <div class="font-mono text-disabled" style="font-size:.62rem;">{{ svc.detail }}</div>
                </div>
                <v-chip :color="svc.ok ? 'success' : 'error'" size="x-small" variant="tonal" class="font-mono" style="font-size:.6rem;letter-spacing:1px;">
                  {{ svc.ok ? 'ONLINE' : 'OFFLINE' }}
                </v-chip>
              </div>
            </div>

            <div class="mt-4 pa-3 rounded-lg" style="background:rgba(0,255,179,.04);border:1px solid rgba(0,255,179,.15);">
              <div class="d-flex justify-space-between">
                <span class="font-mono text-success" style="font-size:.68rem;">UPTIME</span>
                <span class="font-orbitron text-success" style="font-size:.88rem;font-weight:700;">{{ uptimeFormatted }}</span>
              </div>
            </div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- Raw JSON toggle -->
    <v-row class="mt-4">
      <v-col>
        <v-expansion-panels variant="accordion">
          <v-expansion-panel style="background:rgba(6,6,18,.9);border:1px solid rgba(80,140,240,.1);">
            <v-expansion-panel-title class="font-mono text-medium-emphasis" style="font-size:.7rem;letter-spacing:2px;">
              RAW HEALTH PAYLOAD
            </v-expansion-panel-title>
            <v-expansion-panel-text>
              <pre class="font-mono text-disabled" style="font-size:.68rem;line-height:1.8;overflow-x:auto;">{{ JSON.stringify(health.server, null, 2) }}</pre>
            </v-expansion-panel-text>
          </v-expansion-panel>
        </v-expansion-panels>
      </v-col>
    </v-row>
  </div>
</template>

<script setup>
import { computed, onMounted, onUnmounted } from 'vue'
import { useHealthStore } from '@/stores/health'
import MetricCard from '@/components/common/MetricCard.vue'

const health = useHealthStore()
onMounted(() => health.startPolling(5000))
onUnmounted(() => health.stopPolling())

const s = computed(() => health.server)
const overallStatus = computed(() => s.value?.status ?? 'unknown')
const overallColor  = computed(() => ({ ok: 'success', degraded: 'warning' }[overallStatus.value] ?? 'error'))

const topCards = computed(() => [
  { label: 'CPU Usage',    value: s.value ? s.value.cpu_percent + '%' : '—', sub: 'processor load',   icon: 'mdi-lightning-bolt',    color: 'secondary', showBar: true, barValue: s.value?.cpu_percent ?? 0 },
  { label: 'Memory',       value: s.value ? s.value.memory?.percent + '%' : '—', sub: `${s.value?.memory?.used_gb ?? '—'} GB used`, icon: 'mdi-memory', color: 'primary', showBar: true, barValue: s.value?.memory?.percent ?? 0 },
  { label: 'Disk',         value: s.value ? s.value.disk?.percent + '%' : '—', sub: `${s.value?.disk?.free_gb ?? '—'} GB free`,     icon: 'mdi-harddisk', color: 'warning', showBar: true, barValue: s.value?.disk?.percent ?? 0 },
  { label: 'WS Clients',   value: s.value?.websocket_connections ?? '—', sub: 'active connections', icon: 'mdi-wifi',              color: 'success' },
])

const gauges = computed(() => [
  { label: 'CPU',    value: s.value ? s.value.cpu_percent + '%' : '—',      pct: s.value?.cpu_percent ?? 0,      icon: 'mdi-lightning-bolt', color: gaugeColor(s.value?.cpu_percent) },
  { label: 'Memory', value: s.value ? s.value.memory?.percent + '%' : '—',  pct: s.value?.memory?.percent ?? 0,  icon: 'mdi-memory',         color: gaugeColor(s.value?.memory?.percent) },
  { label: 'Disk',   value: s.value ? s.value.disk?.percent + '%' : '—',    pct: s.value?.disk?.percent ?? 0,    icon: 'mdi-harddisk',       color: gaugeColor(s.value?.disk?.percent) },
])

const services = computed(() => [
  { label: 'PostgreSQL', icon: 'mdi-database', ok: s.value?.database?.ok ?? false, detail: `Latency: ${s.value?.database?.latency_ms ?? '—'} ms` },
  { label: 'Redis Cache', icon: 'mdi-server', ok: s.value?.redis?.ok ?? false, detail: `Latency: ${s.value?.redis?.latency_ms ?? '—'} ms` },
  { label: 'GraphQL API', icon: 'mdi-graphql', ok: !!s.value, detail: 'Strawberry + FastAPI' },
  { label: 'WebSocket',   icon: 'mdi-wifi', ok: (s.value?.websocket_connections ?? 0) >= 0, detail: `${s.value?.websocket_connections ?? 0} clients connected` },
])

const uptimeFormatted = computed(() => {
  const u = s.value?.uptime_seconds ?? 0
  const h = Math.floor(u / 3600)
  const m = Math.floor((u % 3600) / 60)
  const sec = Math.floor(u % 60)
  return `${h}h ${m}m ${sec}s`
})

function gaugeColor(pct) {
  if (!pct) return 'primary'
  if (pct >= 90) return 'error'
  if (pct >= 75) return 'warning'
  return 'success'
}
</script>
