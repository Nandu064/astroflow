<template>
  <div>
    <div class="d-flex align-center justify-space-between mb-6">
      <div>
        <h1 class="font-orbitron text-success glow-green" style="font-size:1.4rem;letter-spacing:4px;font-weight:900;">
          ETL WATCHTOWER
        </h1>
        <p class="font-mono text-medium-emphasis mt-1" style="font-size:.7rem;letter-spacing:2px;">
          PIPELINE HEALTH · INGESTION STATUS · SCHEDULE
        </p>
      </div>
      <div class="d-flex ga-2">
        <v-chip :color="summaryColor" variant="tonal" size="small" class="font-mono" style="letter-spacing:2px;font-size:.62rem;">
          {{ summary?.healthy ?? '—' }}/{{ summary?.total ?? '—' }} HEALTHY
        </v-chip>
        <v-btn icon="mdi-refresh" variant="text" color="success" size="small" :loading="health.loading" @click="health.refresh()" />
      </div>
    </div>

    <!-- Summary cards -->
    <v-row class="mb-4">
      <v-col v-for="c in summaryCards" :key="c.label" cols="6" md="3">
        <MetricCard v-bind="c" />
      </v-col>
    </v-row>

    <!-- Job table -->
    <v-card style="background:rgba(6,6,18,.9);border:1px solid rgba(80,140,240,.1);" class="card-accent-green mb-4">
      <v-card-text class="pa-4">
        <p class="font-mono text-medium-emphasis mb-4" style="font-size:.7rem;letter-spacing:2px;">PIPELINE JOBS</p>

        <v-data-table
          :headers="headers"
          :items="jobRows"
          :items-per-page="-1"
          hide-default-footer
          density="comfortable"
          style="background:transparent;"
        >
          <template #item.name="{ item }">
            <div class="d-flex align-center ga-2">
              <span class="pulse-dot" :style="`width:8px;height:8px;border-radius:50%;background:${statusDot(item.status)};box-shadow:${item.status === 'running' ? '0 0 8px #00ffb3' : 'none'};`" />
              <span class="font-mono" style="font-size:.72rem;">{{ item.name }}</span>
            </div>
          </template>

          <template #item.status="{ item }">
            <v-chip
              :color="statusColor(item.status)"
              size="x-small" variant="tonal"
              class="font-mono" style="font-size:.6rem;letter-spacing:1px;"
            >
              {{ item.status?.toUpperCase() }}
            </v-chip>
          </template>

          <template #item.last_run_ago="{ item }">
            <span class="font-mono text-medium-emphasis" style="font-size:.7rem;">{{ item.last_run_ago }}</span>
          </template>

          <template #item.records="{ item }">
            <span class="font-mono text-primary" style="font-size:.7rem;">{{ item.records }}</span>
          </template>

          <template #item.duration="{ item }">
            <span class="font-mono text-medium-emphasis" style="font-size:.7rem;">{{ item.duration }}</span>
          </template>

          <template #item.success_rate="{ item }">
            <div class="d-flex align-center ga-2" style="min-width:100px;">
              <v-progress-linear
                :model-value="item.success_rate"
                :color="item.success_rate >= 98 ? 'success' : item.success_rate >= 90 ? 'warning' : 'error'"
                bg-color="rgba(255,255,255,.06)"
                rounded height="4"
                style="min-width:60px;"
              />
              <span class="font-mono" style="font-size:.68rem;" :class="item.success_rate >= 98 ? 'text-success' : 'text-warning'">{{ item.success_rate }}%</span>
            </div>
          </template>

          <template #item.healthy="{ item }">
            <v-icon :color="item.healthy ? 'success' : 'error'" size="16">
              {{ item.healthy ? 'mdi-check-circle' : 'mdi-alert-circle' }}
            </v-icon>
          </template>
        </v-data-table>
      </v-card-text>
    </v-card>

    <!-- Error log -->
    <v-card v-if="errorJobs.length" style="background:rgba(6,6,18,.9);border:1px solid rgba(255,63,110,.2);" class="card-accent-red">
      <v-card-text class="pa-4">
        <p class="font-mono text-error mb-3" style="font-size:.7rem;letter-spacing:2px;">⚠ PIPELINE ERRORS</p>
        <div v-for="j in errorJobs" :key="j.name" class="pa-3 rounded-lg mb-2" style="background:rgba(255,63,110,.05);border:1px solid rgba(255,63,110,.2);">
          <div class="font-mono text-error mb-1" style="font-size:.72rem;font-weight:700;">{{ j.name }}</div>
          <div class="font-mono text-disabled" style="font-size:.68rem;line-height:1.6;">{{ j.error }}</div>
        </div>
      </v-card-text>
    </v-card>
  </div>
</template>

<script setup>
import { computed, onMounted, onUnmounted } from 'vue'
import { useHealthStore } from '@/stores/health'
import MetricCard from '@/components/common/MetricCard.vue'

const health = useHealthStore()
onMounted(() => health.startPolling(5000))
onUnmounted(() => health.stopPolling())

const summary = computed(() => health.etl?.summary)
const jobs    = computed(() => health.etl?.jobs ?? [])
const summaryColor = computed(() => (summary.value?.failed ?? 0) > 0 ? 'warning' : 'success')

const summaryCards = computed(() => [
  { label: 'Total Jobs',   value: summary.value?.total   ?? '—', sub: 'registered pipelines', icon: 'mdi-pipe',         color: 'primary' },
  { label: 'Healthy',      value: summary.value?.healthy ?? '—', sub: 'no failures',          icon: 'mdi-check-circle', color: 'success' },
  { label: 'Running Now',  value: summary.value?.running ?? '—', sub: 'currently ingesting',  icon: 'mdi-play-circle',  color: 'warning' },
  { label: 'Failed',       value: summary.value?.failed  ?? '—', sub: 'needs attention',      icon: 'mdi-alert-circle', color: 'error' },
])

const headers = [
  { title: 'Pipeline',     key: 'name',         sortable: false },
  { title: 'Status',       key: 'status',       sortable: true  },
  { title: 'Last Run',     key: 'last_run_ago', sortable: false },
  { title: 'Records',      key: 'records',      sortable: true  },
  { title: 'Duration',     key: 'duration',     sortable: false },
  { title: 'Success Rate', key: 'success_rate', sortable: true  },
  { title: 'Health',       key: 'healthy',      sortable: false },
]

const jobRows = computed(() => jobs.value.map(j => ({
  name: j.name,
  status: j.status,
  last_run_ago: j.last_run_ago_s != null
    ? j.last_run_ago_s < 60
      ? `${j.last_run_ago_s}s ago`
      : `${Math.floor(j.last_run_ago_s / 60)}m ago`
    : 'Never',
  records: j.records_processed?.toLocaleString() ?? '—',
  duration: j.duration_s ? `${j.duration_s.toFixed(1)}s` : '—',
  success_rate: j.success_rate ?? 100,
  healthy: j.healthy,
  error: j.error,
})))

const errorJobs = computed(() => jobs.value.filter(j => j.status === 'failed' && j.error))

const statusColor = (s) => ({ running: 'success', idle: 'default', failed: 'error' }[s] ?? 'default')
const statusDot   = (s) => ({ running: '#00ffb3', idle: '#3a4a6e', failed: '#ff3f6e' }[s] ?? '#3a4a6e')
</script>
