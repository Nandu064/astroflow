<template>
  <Line :data="chartData" :options="chartOptions" style="max-height:100%;" />
</template>

<script setup>
import { computed } from 'vue'
import { Line } from 'vue-chartjs'
import {
  Chart as ChartJS,
  LineElement, PointElement, LinearScale,
  CategoryScale, Filler, Tooltip, Legend,
} from 'chart.js'

ChartJS.register(LineElement, PointElement, LinearScale, CategoryScale, Filler, Tooltip, Legend)

const props = defineProps({
  dataset1:     { type: Array, default: () => [] },
  dataset2:     { type: Array, default: () => [] },
  label1:       { type: String, default: 'CPU %' },
  label2:       { type: String, default: 'Memory %' },
  color1:       { type: String, default: '#00e5ff' },
  color2:       { type: String, default: '#bf5fff' },
})

const labels = computed(() => props.dataset1.map((_, i) => ''))

const makeGradient = (ctx, color) => {
  if (!ctx?.chart?.ctx) return color
  const g = ctx.chart.ctx.createLinearGradient(0, 0, 0, ctx.chart.height)
  g.addColorStop(0, color.replace(')', ', 0.3)').replace('rgb', 'rgba').replace('#', 'rgba(') || color + '4d')
  g.addColorStop(1, 'transparent')
  return g
}

const chartData = computed(() => ({
  labels: labels.value,
  datasets: [
    {
      label: props.label1,
      data: props.dataset1,
      borderColor: props.color1,
      borderWidth: 2,
      pointRadius: 0,
      tension: 0.4,
      fill: true,
      backgroundColor: (ctx) => {
        const c = ctx.chart.ctx
        if (!c) return props.color1 + '22'
        const g = c.createLinearGradient(0, 0, 0, ctx.chart.height)
        g.addColorStop(0, props.color1 + '44')
        g.addColorStop(1, props.color1 + '00')
        return g
      },
    },
    {
      label: props.label2,
      data: props.dataset2,
      borderColor: props.color2,
      borderWidth: 2,
      pointRadius: 0,
      tension: 0.4,
      fill: true,
      backgroundColor: (ctx) => {
        const c = ctx.chart.ctx
        if (!c) return props.color2 + '22'
        const g = c.createLinearGradient(0, 0, 0, ctx.chart.height)
        g.addColorStop(0, props.color2 + '33')
        g.addColorStop(1, props.color2 + '00')
        return g
      },
    },
  ],
}))

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  animation: { duration: 200 },
  interaction: { mode: 'index', intersect: false },
  plugins: {
    legend: { display: false },
    tooltip: {
      backgroundColor: 'rgba(6,6,18,.95)',
      borderColor: 'rgba(80,140,240,.3)',
      borderWidth: 1,
      titleColor: '#7a8fb8',
      bodyColor: '#e8f0ff',
    },
  },
  scales: {
    x: { display: false },
    y: {
      min: 0, max: 100,
      grid: { color: 'rgba(80,140,240,.07)' },
      ticks: { color: '#3a4a6e', font: { family: 'Space Mono', size: 9 }, maxTicksLimit: 5 },
      border: { display: false },
    },
  },
}
</script>
