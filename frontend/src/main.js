import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import vuetify from './plugins/vuetify'
import { apolloClient } from './plugins/apollo'
import { DefaultApolloClient } from '@vue/apollo-composable'

const app = createApp(App)

app.use(createPinia())
app.use(router)
app.use(vuetify)
app.provide(DefaultApolloClient, apolloClient)

app.mount('#app')
