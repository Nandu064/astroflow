<template>
  <v-app theme="astroTheme">
    <AppShell />
  </v-app>
</template>

<script setup>
import AppShell from '@/components/layout/AppShell.vue'
import { useRealtimeStore } from '@/stores/realtime'
import { onMounted, onUnmounted } from 'vue'

const rt = useRealtimeStore()
onMounted(() => rt.connect())
onUnmounted(() => rt.disconnect())
</script>

<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Space+Mono:wght@400;700&family=Inter:wght@300;400;500;600&display=swap');

:root {
  --font-display: 'Orbitron', sans-serif;
  --font-mono:    'Space Mono', monospace;
  --font-body:    'Inter', sans-serif;
}

* { box-sizing: border-box; }

body {
  background: #03030e !important;
  font-family: var(--font-body);
}

/* Neon glow utilities */
.glow-cyan   { text-shadow: 0 0 16px rgba(0,229,255,.6); }
.glow-purple { text-shadow: 0 0 16px rgba(191,95,255,.6); }
.glow-green  { text-shadow: 0 0 16px rgba(0,255,179,.6); }
.glow-gold   { text-shadow: 0 0 16px rgba(255,200,50,.6); }
.glow-red    { text-shadow: 0 0 16px rgba(255,63,110,.6); }

/* Scrollbar */
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(80,140,240,.2); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: rgba(80,140,240,.4); }

/* Number font */
.font-orbitron { font-family: var(--font-display) !important; }
.font-mono     { font-family: var(--font-mono) !important; }

/* Card top-border accent */
.card-accent-cyan   { border-top: 2px solid #00e5ff !important; }
.card-accent-purple { border-top: 2px solid #bf5fff !important; }
.card-accent-green  { border-top: 2px solid #00ffb3 !important; }
.card-accent-gold   { border-top: 2px solid #ffc832 !important; }
.card-accent-red    { border-top: 2px solid #ff3f6e !important; }

/* Pulse dot */
@keyframes pulse-dot {
  0%,100% { opacity:1; transform:scale(1); }
  50%      { opacity:.4; transform:scale(.75); }
}
.pulse-dot { animation: pulse-dot 1.6s ease-in-out infinite; }
</style>
