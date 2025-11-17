import { createApp } from 'vue'
// import { createPinia } from 'pinia'
import pinia from './stores'

import App from './App.vue'
import router from './router'
import '@/assets/css/iconfont/iconfont.css'

const app = createApp(App)

app.use(pinia)
app.use(router)

app.mount('#app')
