<template>
  <div>
    <div class="d-flex align-center justify-space-between mb-6">
      <div>
        <h1 class="font-orbitron text-primary glow-cyan" style="font-size:1.4rem;letter-spacing:4px;font-weight:900;">
          NEAR-EARTH OBJECTS
        </h1>
        <p class="font-mono text-medium-emphasis mt-1" style="font-size:.7rem;letter-spacing:2px;">
          NASA NEOWS · CLOSE APPROACH DATABASE
        </p>
      </div>
      <div class="d-flex ga-2 align-center">
        <v-switch v-model="hazardousOnly" label="Hazardous only" color="error" hide-details density="compact" class="font-mono" />
        <v-btn icon="mdi-refresh" variant="text" color="primary" size="small" :loading="loading" @click="loadData" />
      </div>
    </div>

    <!-- Summary chips -->
    <div class="d-flex ga-3 mb-5 flex-wrap">
      <v-chip color="primary" variant="tonal" class="font-mono" style="font-size:.68rem;letter-spacing:1px;">
        <v-icon start size="14">mdi-meteor</v-icon> {{ data?.total ?? '—' }} TOTAL
      </v-chip>
      <v-chip color="error" variant="tonal" class="font-mono" style="font-size:.68rem;letter-spacing:1px;">
        <v-icon start size="14">mdi-alert</v-icon> {{ hazardousCount }} HAZARDOUS
      </v-chip>
    </div>

    <v-card style="background:rgba(6,6,18,.9);border:1px solid rgba(80,140,240,.1);" class="card-accent-cyan">
      <v-card-text class="pa-0">
        <v-data-table
          :headers="headers"
          :items="items"
          :loading="loading"
          style="background:transparent;"
          density="comfortable"
        >
          <template #item.name="{ item }">
            <span class="font-mono text-primary" style="font-size:.72rem;">{{ item.name }}</span>
          </template>
          <template #item.distAu="{ item }">
            <span class="font-mono" style="font-size:.72rem;">{{ item.distAu?.toFixed(4) }}</span>
          </template>
          <template #item.velKmS="{ item }">
            <span class="font-mono text-warning" style="font-size:.72rem;">{{ item.velKmS?.toFixed(1) }}</span>
          </template>
          <template #item.diam="{ item }">
            <span class="font-mono text-secondary" style="font-size:.72rem;">
              {{ item.diamMinM?.toFixed(0) }}–{{ item.diamMaxM?.toFixed(0) }} m
            </span>
          </template>
          <template #item.hazardous="{ item }">
            <v-chip
              :color="item.hazardous ? 'error' : 'success'"
              size="x-small" variant="tonal"
              class="font-mono" style="font-size:.6rem;letter-spacing:1px;"
            >
              {{ item.hazardous ? '⚠ YES' : '✓ NO' }}
            </v-chip>
          </template>
          <template #item.approachDate="{ item }">
            <span class="font-mono text-medium-emphasis" style="font-size:.7rem;">{{ formatDate(item.approachDate) }}</span>
          </template>
          <template #loading>
            <div class="text-center py-8">
              <v-progress-circular indeterminate color="primary" />
              <p class="font-mono text-disabled mt-3" style="font-size:.7rem;">FETCHING NEO DATA…</p>
            </div>
          </template>
          <template #no-data>
            <div class="text-center py-8">
              <v-icon color="primary" size="40" class="mb-3">mdi-meteor</v-icon>
              <p class="font-mono text-disabled" style="font-size:.72rem;">No asteroid data yet — ETL pipeline will populate this shortly</p>
            </div>
          </template>
        </v-data-table>
      </v-card-text>
    </v-card>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { useQuery } from '@vue/apollo-composable'
import gql from 'graphql-tag'

const ASTEROIDS_QUERY = gql`
  query Asteroids($hazardousOnly: Boolean, $page: Int, $perPage: Int) {
    asteroids(hazardousOnly: $hazardousOnly, page: $page, perPage: $perPage) {
      items {
        id name nasaId distAu velKmS diamMinM diamMaxM hazardous approachDate
      }
      total page perPage totalPages
    }
  }
`

const hazardousOnly = ref(false)
const page = ref(1)

const { result, loading, refetch } = useQuery(ASTEROIDS_QUERY, () => ({
  hazardousOnly: hazardousOnly.value,
  page: page.value,
  perPage: 50,
}))

const data = computed(() => result.value?.asteroids)
const items = computed(() => data.value?.items ?? [])
const hazardousCount = computed(() => items.value.filter(i => i.hazardous).length)

watch(hazardousOnly, () => { page.value = 1; refetch() })

function loadData() { refetch() }
function formatDate(d) {
  if (!d) return '—'
  return new Date(d).toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' })
}

const headers = [
  { title: 'Name',          key: 'name',          sortable: true  },
  { title: 'Distance (AU)', key: 'distAu',        sortable: true  },
  { title: 'Vel (km/s)',    key: 'velKmS',        sortable: true  },
  { title: 'Diameter',      key: 'diam',          sortable: false },
  { title: 'Hazardous',     key: 'hazardous',     sortable: true  },
  { title: 'Approach Date', key: 'approachDate',  sortable: true  },
]
</script>
