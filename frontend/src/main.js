import { createApp } from 'vue'
// import { createPinia } from 'pinia'
import pinia from './stores'

import App from './App.vue'
import router from './router'
import '@/assets/css/iconfont/iconfont.css'

// 引入 Element Plus 的国际化相关文件
import ElementPlus from 'element-plus'  // 虽然是自动导入，但配置 i18n 仍需引入核心
import zhCn from 'element-plus/dist/locale/zh-cn.mjs'

// 引入 dayjs 和中文语言包
import dayjs from 'dayjs'
import 'dayjs/locale/zh-cn'

// 配置 dayjs 全局使用中文
dayjs.locale('zh-cn')

const app = createApp(App)

app.use(pinia)
app.use(router)

// 全局注册 ElementPlus 并配置国际化
app.use(ElementPlus, {
    locale: zhCn
})

app.mount('#app')
