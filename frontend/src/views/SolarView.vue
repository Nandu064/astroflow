<template>
  <div>
    <div class="d-flex align-center justify-space-between mb-6">
      <div>
        <h1 class="font-orbitron text-warning glow-gold" style="font-size:1.4rem;letter-spacing:4px;font-weight:900;">
          SOLAR EVENTS
        </h1>
        <p class="font-mono text-medium-emphasis mt-1" style="font-size:.7rem;letter-spacing:2px;">
          NASA DONKI · NOAA SPACE WEATHER · LIVE FEED
        </p>
      </div>
      <v-btn icon="mdi-refresh" variant="text" color="warning" size="small" :loading="loading" @click="refetch()" />
    </div>

    <!-- Event type filter -->
    <div class="d-flex ga-2 mb-5 flex-wrap">
      <v-chip
        v-for="t in eventTypes" :key="t.value"
        :color="selectedType === t.value ? t.color : 'default'"
        :variant="selectedType === t.value ? 'tonal' : 'outlined'"
        size="small" class="font-mono cursor-pointer" style="font-size:.65rem;letter-spacing:1px;"
        @click="selectedType = selectedType === t.value ? null : t.value"
      >
        {{ t.label }}
      </v-chip>
    </div>

    <v-card style="background:rgba(6,6,18,.9);border:1px solid rgba(80,140,240,.1);" class="card-accent-gold">
      <v-card-text class="pa-0">
        <v-data-table
          :headers="headers"
          :items="items"
          :loading="loading"
          style="background:transparent;"
          density="comfortable"
        >
          <template #item.eventType="{ item }">
            <v-chip
              :color="typeColor(item.eventType)"
              size="x-small" variant="tonal"
              class="font-mono" style="font-size:.6rem;letter-spacing:1px;"
            >{{ item.eventType }}</v-chip>
          </template>
          <template #item.classType="{ item }">
            <span class="font-mono text-warning" style="font-size:.75rem;font-weight:700;">{{ item.classType ?? '—' }}</span>
          </template>
          <template #item.kpIndex="{ item }">
            <span class="font-mono" :style="`font-size:.72rem;color:${kpColor(item.kpIndex)}`">
              {{ item.kpIndex?.toFixed(1) ?? '—' }}
            </span>
          </template>
          <template #item.startTime="{ item }">
            <span class="font-mono text-medium-emphasis" style="font-size:.7rem;">{{ formatDt(item.startTime) }}</span>
          </template>
          <template #item.sourceLocation="{ item }">
            <span class="font-mono text-disabled" style="font-size:.7rem;">{{ item.sourceLocation ?? '—' }}</span>
          </template>
          <template #no-data>
            <div class="text-center py-8">
              <v-icon color="warning" size="40" class="mb-3">mdi-white-balance-sunny</v-icon>
              <p class="font-mono text-disabled" style="font-size:.72rem;">Solar event data will populate once ETL runs</p>
            </div>
          </template>
        </v-data-table>
      </v-card-text>
    </v-card>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useQuery } from '@vue/apollo-composable'
import gql from 'graphql-tag'

const SOLAR_QUERY = gql`
  query SolarEvents($eventType: String, $limit: Int) {
    solarEvents(eventType: $eventType, limit: $limit) {
      id eventType classType kpIndex startTime peakTime sourceLocation instruments
    }
  }
`

const selectedType = ref(null)
const eventTypes = [
  { value: 'FLARE',    label: 'FLARES',    color: 'warning' },
  { value: 'KP_INDEX', label: 'KP INDEX',  color: 'primary' },
  { value: 'CME',      label: 'CME',       color: 'secondary' },
  { value: 'GST',      label: 'STORMS',    color: 'error' },
]

const { result, loading, refetch } = useQuery(SOLAR_QUERY, () => ({
  eventType: selectedType.value,
  limit: 100,
}))

const items = computed(() => result.value?.solarEvents ?? [])
watch(selectedType, () => refetch())

const headers = [
  { title: 'Type',       key: 'eventType',      sortable: true  },
  { title: 'Class',      key: 'classType',      sortable: true  },
  { title: 'Kp Index',   key: 'kpIndex',        sortable: true  },
  { title: 'Start Time', key: 'startTime',      sortable: true  },
  { title: 'Source',     key: 'sourceLocation', sortable: false },
]

const typeColor  = (t) => ({ FLARE: 'warning', KP_INDEX: 'primary', CME: 'secondary', GST: 'error' }[t] ?? 'default')
const kpColor    = (v) => !v ? '#7a8fb8' : v >= 7 ? '#ff3f6e' : v >= 5 ? '#ffc832' : '#00e5ff'
function formatDt(d) {
  if (!d) return '—'
  return new Date(d).toLocaleString('en-GB', { dateStyle: 'medium', timeStyle: 'short' })
}
</script>
