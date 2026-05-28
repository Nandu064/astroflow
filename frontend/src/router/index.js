import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    redirect: '/dashboard',
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: () => import('@/views/DashboardView.vue'),
    meta: { title: 'Mission Control', icon: 'mdi-view-dashboard' },
  },
  {
    path: '/asteroids',
    name: 'Asteroids',
    component: () => import('@/views/AsteroidsView.vue'),
    meta: { title: 'Near-Earth Objects', icon: 'mdi-meteor' },
  },
  {
    path: '/solar',
    name: 'Solar',
    component: () => import('@/views/SolarView.vue'),
    meta: { title: 'Solar Events', icon: 'mdi-white-balance-sunny' },
  },
  {
    path: '/exoplanets',
    name: 'Exoplanets',
    component: () => import('@/views/ExoplanetsView.vue'),
    meta: { title: 'Exoplanets', icon: 'mdi-earth' },
  },
  {
    path: '/health/server',
    name: 'HealthServer',
    component: () => import('@/views/HealthServerView.vue'),
    meta: { title: 'Server Health', icon: 'mdi-server' },
  },
  {
    path: '/health/etl',
    name: 'HealthEtl',
    component: () => import('@/views/HealthEtlView.vue'),
    meta: { title: 'ETL Watchtower', icon: 'mdi-pipe' },
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.afterEach((to) => {
  document.title = to.meta.title ? `${to.meta.title} — AstroFlow` : 'AstroFlow'
})

export default router
