import './assets/main.css'

import { createApp } from 'vue'
import App from './App.vue'
import 'vfonts/Lato.css'
// 等宽字体
import 'vfonts/FiraCode.css'
import naive from 'naive-ui'

const app = createApp(App)
app.use(naive)
app.mount('#app')
