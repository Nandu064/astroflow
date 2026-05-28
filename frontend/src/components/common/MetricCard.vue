<template>
  <v-card
    :class="['metric-card', `card-accent-${color}`]"
    style="background:rgba(6,6,18,.9); border:1px solid rgba(80,140,240,.1);"
    height="100%"
  >
    <v-card-text class="pa-4">
      <div class="d-flex justify-space-between align-start mb-3">
        <span class="font-mono text-medium-emphasis" style="font-size:.62rem;letter-spacing:2px;text-transform:uppercase;">
          {{ label }}
        </span>
        <v-icon :color="color" size="18">{{ icon }}</v-icon>
      </div>

      <div
        class="font-orbitron mb-1"
        :class="`text-${color} glow-${color}`"
        :style="`font-size:${valueSize};font-weight:700;line-height:1;`"
      >
        {{ displayValue }}
      </div>

      <div class="font-mono text-disabled" style="font-size:.62rem;letter-spacing:1px;margin-top:6px;">
        {{ sub }}
      </div>

      <v-progress-linear
        v-if="showBar"
        :model-value="barValue"
        :color="color"
        bg-color="rgba(255,255,255,.06)"
        rounded
        height="3"
        class="mt-3"
      />
    </v-card-text>
  </v-card>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  label:     { type: String, required: true },
  value:     { type: [String, Number], default: '—' },
  sub:       { type: String, default: '' },
  icon:      { type: String, default: 'mdi-circle' },
  color:     { type: String, default: 'primary' },
  showBar:   { type: Boolean, default: false },
  barValue:  { type: Number, default: 0 },
  valueSize: { type: String, default: '1.6rem' },
})

const displayValue = computed(() => props.value ?? '—')
</script>

<style scoped>
.metric-card { transition: transform .25s, box-shadow .25s; }
.metric-card:hover { transform: translateY(-3px); }
</style>
