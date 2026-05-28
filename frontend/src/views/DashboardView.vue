<template>
  <div>
    <!-- Page header -->
    <div class="d-flex align-center justify-space-between mb-6">
      <div>
        <h1 class="font-orbitron text-primary glow-cyan" style="font-size:1.4rem;letter-spacing:4px;font-weight:900;">
          MISSION CONTROL
        </h1>
        <p class="font-mono text-medium-emphasis mt-1" style="font-size:.7rem;letter-spacing:2px;">
          REAL-TIME SPACE INTELLIGENCE · LIVE DATA STREAM
        </p>
      </div>
      <v-chip :color="modeColor" variant="tonal" size="small" class="font-mono" style="letter-spacing:2px;font-size:.62rem;">
        <span class="pulse-dot mr-1">●</span> {{ rt.mode.toUpperCase() }}
      </v-chip>
    </div>

    <!-- Metric cards row -->
    <v-row class="mb-4">
      <v-col cols="12" sm="6" md="3" v-for="m in metricCards" :key="m.label">
        <MetricCard v-bind="m" />
      </v-col>
    </v-row>

    <!-- Chart + NEO panel -->
    <v-row class="mb-4">
      <v-col cols="12" md="8">
        <v-card style="background:rgba(6,6,18,.9);border:1px solid rgba(80,140,240,.1);" class="card-accent-cyan h-100">
          <v-card-text class="pa-4">
            <div class="d-flex justify-space-between align-center mb-3">
              <span class="font-mono text-medium-emphasis" style="font-size:.7rem;letter-spacing:2px;">
                CPU &amp; MEMORY · LAST 60 SECONDS
              </span>
              <div class="d-flex ga-3">
                <span class="font-mono" style="font-size:.65rem;color:#00e5ff;">● CPU</span>
                <span class="font-mono" style="font-size:.65rem;color:#bf5fff;">● MEM</span>
              </div>
            </div>
            <div style="height:220px;">
              <LiveStreamChart
                :dataset1="rt.cpuHistory"
                :dataset2="rt.memHistory"
                label1="CPU %"
                label2="Memory %"
                color1="#00e5ff"
                color2="#bf5fff"
              />
            </div>
          </v-card-text>
        </v-card>
      </v-col>

      <!-- Nearest NEO -->
      <v-col cols="12" md="4">
        <v-card
          :style="`background:rgba(6,6,18,.9);border:1px solid ${rt.isHazardous ? 'rgba(255,63,110,.3)' : 'rgba(80,140,240,.1)'};`"
          :class="rt.isHazardous ? 'card-accent-red' : 'card-accent-cyan'"
          height="100%"
        >
          <v-card-text class="pa-4">
            <div class="d-flex justify-space-between align-center mb-3">
              <span class="font-mono text-medium-emphasis" style="font-size:.7rem;letter-spacing:2px;">NEAREST APPROACH</span>
              <v-chip
                :color="rt.isHazardous ? 'error' : 'success'"
                size="x-small"
                variant="tonal"
                class="font-mono"
                style="letter-spacing:1px;font-size:.6rem;"
              >
                {{ rt.isHazardous ? '⚠ HAZARDOUS' : '✓ SAFE' }}
              </v-chip>
            </div>

            <div class="font-orbitron text-primary glow-cyan mb-4" style="font-size:1rem;font-weight:700;">
              {{ rt.neo?.name ?? '—' }}
            </div>

            <v-row dense>
              <v-col v-for="stat in neoStats" :key="stat.label" cols="4">
                <div style="background:rgba(255,255,255,.03);border:1px solid rgba(80,140,240,.1);border-radius:10px;padding:10px;text-align:center;">
                  <div class="font-mono text-disabled mb-1" style="font-size:.58rem;letter-spacing:1px;">{{ stat.label }}</div>
                  <div class="font-orbitron" :class="`text-${stat.color}`" style="font-size:.9rem;font-weight:700;">{{ stat.value }}</div>
                  <div class="font-mono text-disabled" style="font-size:.56rem;">{{ stat.unit }}</div>
                </div>
              </v-col>
            </v-row>

            <!-- Orbit canvas -->
            <div class="d-flex justify-center mt-4">
              <canvas ref="orbitCanvas" width="160" height="160" style="border-radius:50%;" />
            </div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- ETL status + Event stream -->
    <v-row>
      <v-col cols="12" md="6">
        <v-card style="background:rgba(6,6,18,.9);border:1px solid rgba(80,140,240,.1);" class="card-accent-green">
          <v-card-text class="pa-4">
            <div class="d-flex justify-space-between align-center mb-3">
              <span class="font-mono text-medium-emphasis" style="font-size:.7rem;letter-spacing:2px;">ETL PIPELINE STATUS</span>
              <v-chip
                :color="rt.etlRunning > 0 ? 'success' : 'grey'"
                size="x-small" variant="tonal"
                class="font-mono" style="font-size:.6rem;letter-spacing:1px;"
              >
                {{ rt.etlRunning }} RUNNING
              </v-chip>
            </div>

            <div class="d-flex flex-column ga-2">
              <div
                v-for="job in rt.etlJobs" :key="job.name"
                class="etl-row d-flex align-center ga-3 pa-2 rounded-lg"
                :style="`background:rgba(255,255,255,.025);border:1px solid ${job.status === 'running' ? 'rgba(0,255,179,.2)' : 'rgba(80,140,240,.08)'};`"
              >
                <div
                  class="pulse-dot"
                  :style="`width:8px;height:8px;border-radius:50%;flex-shrink:0;background:${job.status === 'running' ? '#00ffb3' : job.status === 'failed' ? '#ff3f6e' : '#3a4a6e'};box-shadow:${job.status === 'running' ? '0 0 8px #00ffb3' : 'none'};`"
                />
                <span class="font-mono text-on-surface flex-grow-1" style="font-size:.7rem;">{{ job.name }}</span>
                <span class="font-mono" style="font-size:.62rem;color:#00ffb3;">{{ job.records?.toLocaleString() ?? 0 }} rec</span>
                <v-chip
                  :color="job.status === 'running' ? 'success' : job.status === 'failed' ? 'error' : 'default'"
                  size="x-small" variant="tonal"
                  class="font-mono" style="font-size:.58rem;letter-spacing:1px;"
                >
                  {{ job.status?.toUpperCase() }}
                </v-chip>
              </div>
            </div>
          </v-card-text>
        </v-card>
      </v-col>

      <!-- Event feed -->
      <v-col cols="12" md="6">
        <v-card style="background:rgba(6,6,18,.9);border:1px solid rgba(80,140,240,.1);" class="card-accent-purple" height="100%">
          <v-card-text class="pa-4">
            <div class="d-flex justify-space-between align-center mb-3">
              <span class="font-mono text-medium-emphasis" style="font-size:.7rem;letter-spacing:2px;">LIVE EVENT STREAM</span>
              <span class="font-mono text-disabled" style="font-size:.62rem;">{{ rt.events.length }} events</span>
            </div>

            <div style="max-height:220px;overflow-y:auto;" class="d-flex flex-column ga-2">
              <transition-group name="event-slide">
                <div
                  v-for="ev in rt.events.slice(0, 20)"
                  :key="ev.id"
                  class="event-row pa-2 rounded"
                  :style="`border-left:3px solid ${eventColor(ev.type)};background:${eventBg(ev.type)};`"
                >
                  <div class="d-flex align-center ga-2">
                    <v-chip
                      :color="eventChipColor(ev.type)"
                      size="x-small" variant="tonal"
                      class="font-mono flex-shrink-0" style="font-size:.58rem;letter-spacing:1px;"
                    >
                      {{ ev.type.toUpperCase() }}
                    </v-chip>
                    <span class="font-mono text-on-surface" style="font-size:.68rem;flex:1;">{{ ev.message }}</span>
                    <span class="font-mono text-disabled" style="font-size:.58rem;white-space:nowrap;">{{ ev.ts }}</span>
                  </div>
                </div>
              </transition-group>
              <div v-if="rt.events.length === 0" class="text-center py-6">
                <span class="font-mono text-disabled" style="font-size:.72rem;">Waiting for events…</span>
              </div>
            </div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </div>
</template>

<script setup>
import { computed, ref, watch, onMounted, onUnmounted } from 'vue'
import { useRealtimeStore } from '@/stores/realtime'
import MetricCard from '@/components/common/MetricCard.vue'
import LiveStreamChart from '@/components/charts/LiveStreamChart.vue'

const rt = useRealtimeStore()

const modeColor = computed(() => ({
  live: 'success', demo: 'secondary', connecting: 'warning', reconnecting: 'warning',
}[rt.mode] ?? 'grey'))

const metricCards = computed(() => [
  {
    label: 'Near-Earth Objects',
    value: rt.neo ? '4' : '—',
    sub: 'active approaches',
    icon: 'mdi-meteor',
    color: 'primary',
    valueSize: '1.8rem',
  },
  {
    label: 'CPU Usage',
    value: rt.metrics ? rt.metrics.cpu + '%' : '—',
    sub: 'server load',
    icon: 'mdi-lightning-bolt',
    color: 'secondary',
    showBar: true,
    barValue: rt.metrics?.cpu ?? 0,
    valueSize: '1.8rem',
  },
  {
    label: 'Memory',
    value: rt.metrics ? rt.metrics.mem + '%' : '—',
    sub: 'RAM utilisation',
    icon: 'mdi-memory',
    color: 'success',
    showBar: true,
    barValue: rt.metrics?.mem ?? 0,
    valueSize: '1.8rem',
  },
  {
    label: 'WS Connections',
    value: rt.metrics?.connections ?? '—',
    sub: 'active clients',
    icon: 'mdi-wifi',
    color: 'warning',
    valueSize: '1.8rem',
  },
])

const neoStats = computed(() => [
  { label: 'Distance', value: rt.neo?.dist_au?.toFixed(3) ?? '—', unit: 'AU',   color: 'primary' },
  { label: 'Velocity', value: rt.neo?.vel_km_s != null ? (+rt.neo.vel_km_s).toFixed(2) : '—', unit: 'km/s', color: 'warning' },
  { label: 'Diameter', value: rt.neo?.diam_min_m != null ? Math.round(rt.neo.diam_min_m).toLocaleString() : '—', unit: 'm', color: 'secondary' },
])

// Orbit canvas animation
const orbitCanvas = ref(null)
let _orbitFrame = null
let _orbitAngle = 0

function drawOrbit() {
  const canvas = orbitCanvas.value
  if (!canvas) return
  const ctx = canvas.getContext('2d')
  const W = 160, H = 160, cx = 80, cy = 80

  ctx.clearRect(0, 0, W, H)

  // Background
  const bg = ctx.createRadialGradient(cx, cy, 0, cx, cy, 80)
  bg.addColorStop(0, 'rgba(10,15,50,.95)')
  bg.addColorStop(1, 'rgba(3,3,14,.98)')
  ctx.fillStyle = bg
  ctx.beginPath(); ctx.arc(cx, cy, 79, 0, Math.PI * 2); ctx.fill()

  // Grid rings
  ;[20, 38, 56].forEach(r => {
    ctx.beginPath(); ctx.arc(cx, cy, r, 0, Math.PI * 2)
    ctx.strokeStyle = 'rgba(80,130,220,.08)'; ctx.lineWidth = 1; ctx.stroke()
  })

  // Earth orbit
  ctx.beginPath(); ctx.arc(cx, cy, 20, 0, Math.PI * 2)
  ctx.strokeStyle = 'rgba(0,100,255,.2)'; ctx.lineWidth = 1.5; ctx.stroke()

  // Earth
  ctx.beginPath(); ctx.arc(cx, cy, 5, 0, Math.PI * 2)
  const eg = ctx.createRadialGradient(cx - 1, cy - 1, 0, cx, cy, 5)
  eg.addColorStop(0, '#64b5f6'); eg.addColorStop(1, '#1565c0')
  ctx.fillStyle = eg; ctx.fill()

  // Asteroid orbit (elliptical)
  const dist = rt.neo?.dist_au ?? 0.5
  const a = Math.min(52 + dist * 6, 70), b = Math.min(36 + dist * 4, 54)
  const hazardous = rt.neo?.hazardous ?? false
  const orbitColor = hazardous ? 'rgba(255,63,110,.35)' : 'rgba(0,229,255,.2)'
  ctx.beginPath(); ctx.ellipse(cx, cy, a, b, Math.PI * 0.15, 0, Math.PI * 2)
  ctx.strokeStyle = orbitColor; ctx.lineWidth = 1; ctx.setLineDash([4, 4]); ctx.stroke(); ctx.setLineDash([])

  // Asteroid position
  const ax = cx + a * Math.cos(_orbitAngle) * Math.cos(Math.PI * .15) - b * Math.sin(_orbitAngle) * Math.sin(Math.PI * .15)
  const ay = cy + a * Math.cos(_orbitAngle) * Math.sin(Math.PI * .15) + b * Math.sin(_orbitAngle) * Math.cos(Math.PI * .15)
  const dotColor = hazardous ? '#ff3f6e' : '#00e5ff'
  ctx.beginPath(); ctx.arc(ax, ay, 4, 0, Math.PI * 2); ctx.fillStyle = dotColor; ctx.fill()
  ctx.beginPath(); ctx.arc(ax, ay, 9, 0, Math.PI * 2)
  ctx.fillStyle = hazardous ? 'rgba(255,63,110,.15)' : 'rgba(0,229,255,.12)'; ctx.fill()

  _orbitAngle += 0.014
  _orbitFrame = requestAnimationFrame(drawOrbit)
}

onMounted(() => { _orbitFrame = requestAnimationFrame(drawOrbit) })
onUnmounted(() => { if (_orbitFrame) cancelAnimationFrame(_orbitFrame) })

// Event helpers
const eventColor = (type) => ({ info: '#00e5ff', warning: '#ffc832', critical: '#ff3f6e', success: '#00ffb3' }[type] ?? '#8899cc')
const eventBg    = (type) => ({ info: 'rgba(0,229,255,.04)', warning: 'rgba(255,200,50,.04)', critical: 'rgba(255,63,110,.04)', success: 'rgba(0,255,179,.04)' }[type] ?? 'transparent')
const eventChipColor = (type) => ({ info: 'primary', warning: 'warning', critical: 'error', success: 'success' }[type] ?? 'default')
</script>

<style scoped>
.event-slide-enter-active { transition: all .25s ease-out; }
.event-slide-enter-from   { opacity:0; transform:translateX(12px); }
</style>
