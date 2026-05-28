import 'vuetify/styles'
import '@mdi/font/css/materialdesignicons.css'
import { createVuetify } from 'vuetify'
import { aliases, mdi } from 'vuetify/iconsets/mdi'

const astroTheme = {
  dark: true,
  colors: {
    background:       '#03030e',
    surface:          '#060612',
    'surface-bright': '#0a0f28',
    'surface-light':  '#0d1435',
    primary:          '#00e5ff',
    'primary-darken-1': '#00b4cc',
    secondary:        '#bf5fff',
    'secondary-darken-1': '#9b3fe0',
    success:          '#00ffb3',
    warning:          '#ffc832',
    error:            '#ff3f6e',
    info:             '#00e5ff',
    'on-background':  '#e8f0ff',
    'on-surface':     '#e8f0ff',
    'on-primary':     '#03030e',
    'on-secondary':   '#ffffff',
    'on-success':     '#03030e',
    'on-warning':     '#03030e',
    'on-error':       '#ffffff',
  },
}

export default createVuetify({
  icons: { defaultSet: 'mdi', aliases, sets: { mdi } },
  theme: {
    defaultTheme: 'astroTheme',
    themes: { astroTheme },
  },
  defaults: {
    VCard: {
      rounded: 'lg',
      elevation: 0,
    },
    VBtn: {
      rounded: 'lg',
      elevation: 0,
    },
    VChip: {
      rounded: 'lg',
    },
    VDataTable: {
      density: 'comfortable',
    },
  },
})
