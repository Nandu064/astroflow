<template>
  <div>
    <div class="d-flex align-center justify-space-between mb-6">
      <div>
        <h1 class="font-orbitron text-secondary glow-purple" style="font-size:1.4rem;letter-spacing:4px;font-weight:900;">
          EXOPLANET CATALOG
        </h1>
        <p class="font-mono text-medium-emphasis mt-1" style="font-size:.7rem;letter-spacing:2px;">
          NASA EXOPLANET ARCHIVE · 5,500+ CONFIRMED WORLDS
        </p>
      </div>
      <v-btn icon="mdi-refresh" variant="text" color="secondary" size="small" :loading="loading" @click="refetch()" />
    </div>

    <!-- Filters -->
    <v-row class="mb-4">
      <v-col cols="12" sm="6" md="4">
        <v-select
          v-model="selectedMethod"
          :items="methods"
          label="Discovery Method"
          variant="outlined"
          density="compact"
          clearable
          class="font-mono"
          bg-color="rgba(6,6,18,.9)"
          @update:model-value="refetch()"
        />
      </v-col>
      <v-col cols="12" sm="6" md="4">
        <v-text-field
          v-model.number="minYearInput"
          label="Discovered after year"
          variant="outlined"
          density="compact"
          type="number"
          class="font-mono"
          bg-color="rgba(6,6,18,.9)"
        />
      </v-col>
    </v-row>

    <!-- Stats chips -->
    <div class="d-flex ga-3 mb-4 flex-wrap">
      <v-chip color="secondary" variant="tonal" class="font-mono" style="font-size:.68rem;letter-spacing:1px;">
        {{ data?.total?.toLocaleString() ?? '—' }} TOTAL
      </v-chip>
    </div>

    <v-card style="background:rgba(6,6,18,.9);border:1px solid rgba(80,140,240,.1);" class="card-accent-purple">
      <v-card-text class="pa-0">
        <v-data-table
          :headers="headers"
          :items="items"
          :loading="loading"
          style="background:transparent;"
          density="comfortable"
        >
          <template #item.name="{ item }">
            <span class="font-mono text-secondary" style="font-size:.72rem;">{{ item.name }}</span>
          </template>
          <template #item.hostStar="{ item }">
            <span class="font-mono text-warning" style="font-size:.7rem;">{{ item.hostStar ?? '—' }}</span>
          </template>
          <template #item.distLy="{ item }">
            <span class="font-mono" style="font-size:.7rem;">{{ item.distLy ? item.distLy.toLocaleString() : '—' }}</span>
          </template>
          <template #item.radiusEarth="{ item }">
            <span class="font-mono text-primary" style="font-size:.7rem;">{{ item.radiusEarth?.toFixed(2) ?? '—' }} R⊕</span>
          </template>
          <template #item.discoveryYear="{ item }">
            <span class="font-mono text-medium-emphasis" style="font-size:.7rem;">{{ item.discoveryYear ?? '—' }}</span>
          </template>
          <template #item.discoveryMethod="{ item }">
            <v-chip color="secondary" size="x-small" variant="tonal" class="font-mono" style="font-size:.6rem;">
              {{ item.discoveryMethod ?? '—' }}
            </v-chip>
          </template>
          <template #no-data>
            <div class="text-center py-8">
              <v-icon color="secondary" size="40" class="mb-3">mdi-earth</v-icon>
              <p class="font-mono text-disabled" style="font-size:.72rem;">Exoplanet catalog will load after daily ETL sync</p>
            </div>
          </template>
        </v-data-table>
      </v-card-text>
    </v-card>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useQuery } from '@vue/apollo-composable'
import gql from 'graphql-tag'
import { useDebouncedRef } from '@/composables/useDebounce.js'

const EXOPLANETS_QUERY = gql`
  query Exoplanets($discoveryMethod: String, $minYear: Int, $page: Int, $perPage: Int) {
    exoplanets(discoveryMethod: $discoveryMethod, minYear: $minYear, page: $page, perPage: $perPage) {
      items {
        id name hostStar distLy radiusEarth massEarth orbitalPeriodDays discoveryYear discoveryMethod
      }
      total page perPage totalPages
    }
  }
`

const selectedMethod = ref(null)
const methods = ['Transit', 'Radial Velocity', 'Direct Imaging', 'Gravitational Microlensing', 'Astrometry', 'Timing Variations']

// innerValue → bound to the text field (updates on every keystroke, UI stays responsive)
// debouncedValue → used as the GraphQL variable (fires only 400ms after the user stops typing)
const { innerValue: minYearInput, debouncedValue: minYear } = useDebouncedRef(null, 400)

const { result, loading, refetch } = useQuery(EXOPLANETS_QUERY, () => ({
  discoveryMethod: selectedMethod.value,
  minYear: minYear.value ? Number(minYear.value) : null,
  page: 1,
  perPage: 50,
}))

const data  = computed(() => result.value?.exoplanets)
const items = computed(() => data.value?.items ?? [])

const headers = [
  { title: 'Name',         key: 'name',            sortable: true  },
  { title: 'Host Star',    key: 'hostStar',        sortable: true  },
  { title: 'Distance (ly)',key: 'distLy',          sortable: true  },
  { title: 'Radius',       key: 'radiusEarth',     sortable: true  },
  { title: 'Discovered',   key: 'discoveryYear',   sortable: true  },
  { title: 'Method',       key: 'discoveryMethod', sortable: true  },
]
</script>
