<template>
  <v-navigation-drawer
    v-model="drawer"
    :rail="rail"
    permanent
    color="surface"
    border="0"
    style="border-right: 1px solid rgba(80,140,240,.1) !important;"
  >
    <!-- Logo -->
    <div
      class="d-flex align-center"
      :class="rail ? 'justify-center pa-3' : 'pa-4'"
      style="height:64px; border-bottom:1px solid rgba(80,140,240,.1); overflow:hidden;"
    >
      <!-- Icon — always visible -->
      <svg width="28" height="28" viewBox="0 0 28 28" fill="none" xmlns="http://www.w3.org/2000/svg" style="flex-shrink:0;">
        <polygon points="14,2 24,8 24,20 14,26 4,20 4,8"
          fill="none" stroke="#00e5ff" stroke-width="1.6" stroke-linejoin="round" stroke-opacity="0.8"/>
        <ellipse cx="14" cy="14" rx="6" ry="2.5" fill="none"
          stroke="#7c3aed" stroke-width="0.9" stroke-opacity="0.7" transform="rotate(-20 14 14)"/>
        <circle cx="14" cy="14" r="3" fill="url(#fl)"/>
        <circle cx="20" cy="10.5" r="1.4" fill="#00e5ff"/>
        <defs>
          <radialGradient id="fl" cx="35%" cy="35%">
            <stop offset="0%" stop-color="#3b82f6"/>
            <stop offset="100%" stop-color="#1e3a8a"/>
          </radialGradient>
        </defs>
      </svg>

      <!-- Text — only shown when sidebar is expanded -->
      <span
        v-if="!rail"
        class="font-orbitron text-primary ml-2"
        style="font-size:.9rem;letter-spacing:3px;font-weight:900;white-space:nowrap;"
      >
        ASTRO<span class="text-secondary">FLOW</span>
      </span>
    </div>

    <!-- Nav items -->
    <v-list density="compact" nav class="mt-2">
      <v-list-item
        v-for="item in navItems"
        :key="item.to"
        :to="item.to"
        :prepend-icon="item.icon"
        :title="item.title"
        rounded="lg"
        active-color="primary"
        class="mb-1 font-mono"
        style="font-size:.72rem; letter-spacing:1px;"
      />
    </v-list>

    <template #append>
      <!-- Mode badge -->
      <div class="pa-3">
        <v-chip
          :color="modeColor"
          size="small"
          variant="tonal"
          class="font-mono w-100 d-flex justify-center"
          style="letter-spacing:2px; font-size:.62rem;"
        >
          <span class="pulse-dot mr-2" :style="`color:${modeColor}`">●</span>
          {{ rt.mode.toUpperCase() }}
        </v-chip>
      </div>
    </template>
  </v-navigation-drawer>

  <!-- Top app bar -->
  <v-app-bar
    color="surface"
    elevation="0"
    border="b"
    style="border-color: rgba(80,140,240,.1) !important;"
  >
    <v-app-bar-nav-icon @click="rail = !rail" color="primary" />

    <v-app-bar-title>
      <span class="font-mono text-medium-emphasis" style="font-size:.75rem;letter-spacing:2px;">
        {{ currentTitle }}
      </span>
    </v-app-bar-title>

    <template #append>
      <div class="d-flex align-center ga-3 pr-4">
        <!-- ETL running chips -->
        <v-chip
          v-if="rt.etlRunning > 0"
          color="success"
          size="small"
          variant="tonal"
          class="font-mono"
          style="font-size:.62rem;letter-spacing:1px;"
        >
          <span class="pulse-dot mr-1">●</span>
          {{ rt.etlRunning }} ETL RUNNING
        </v-chip>

        <!-- Local clock -->
        <span class="font-mono text-medium-emphasis" style="font-size:.72rem;letter-spacing:1px;">
          {{ utcClock }}
        </span>
      </div>
    </template>
  </v-app-bar>

  <!-- Main content -->
  <v-main style="background:#03030e; min-height:100vh;">
    <div class="pa-4">
      <router-view v-slot="{ Component }">
        <transition name="fade" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </div>
  </v-main>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'
import { useRealtimeStore } from '@/stores/realtime'

const rt = useRealtimeStore()
const route = useRoute()

const drawer = ref(true)
const rail   = ref(false)

const navItems = [
  { to: '/dashboard',    title: 'MISSION CONTROL', icon: 'mdi-view-dashboard-outline' },
  { to: '/asteroids',    title: 'NEAR-EARTH OBJECTS', icon: 'mdi-meteor' },
  { to: '/solar',        title: 'SOLAR EVENTS',    icon: 'mdi-white-balance-sunny' },
  { to: '/exoplanets',   title: 'EXOPLANETS',      icon: 'mdi-earth' },
  { to: '/health/server',title: 'SERVER HEALTH',   icon: 'mdi-server-outline' },
  { to: '/health/etl',   title: 'ETL WATCHTOWER',  icon: 'mdi-pipe' },
]

const currentTitle = computed(() => route.meta.title ?? 'AstroFlow')

const modeColor = computed(() => ({
  live:         'success',
  demo:         'secondary',
  connecting:   'warning',
  reconnecting: 'warning',
}[rt.mode] ?? 'grey'))

// Local clock — shows HH:MM:SS + browser timezone abbreviation (e.g. "03:09:34 IST")
const utcClock = ref('--:--:--')
let _clockInterval = null
function tickClock() {
  const now = new Date()
  const time = now.toLocaleTimeString('en-GB', {
    hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: false,
  })
  // Extract short TZ name: "03:09:34 GMT+5:30" → "GMT+5:30"
  const tzShort = now.toLocaleTimeString('en-GB', { timeZoneName: 'short' }).split(' ').slice(1).join(' ')
  utcClock.value = `${time} ${tzShort}`
}
onMounted(() => { tickClock(); _clockInterval = setInterval(tickClock, 1000) })
onUnmounted(() => clearInterval(_clockInterval))
</script>

<style scoped>
.fade-enter-active, .fade-leave-active { transition: opacity .18s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
</style>
