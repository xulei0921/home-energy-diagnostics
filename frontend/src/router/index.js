import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '@/stores'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      redirect: '/index/dashboard',
    },
    {
      path: '/index',
      component: () => import('@/views/HomeView.vue'),
      meta: { title: '首页', requiresAuth: true },
      children: [
        {
          path: '/index/dashboard',
          component: () => import('@/views/Dashboard.vue'),
          meta: { title: '仪表盘', requiresAuth: true }
        },
        {
          path: '/index/electricity',
          component: () => import('@/views/Electricity.vue'),
          meta: { title: '电力分析', requiresAuth: true }
        },
        {
          path: '/index/gas',
          component: () => import('@/views/Gas.vue'),
          meta: { title: '燃气分析', requiresAuth: true }
        },
        {
          path: '/index/water',
          component: () => import('@/views/Water.vue'),
          meta: { title: '水资源分析', requiresAuth: true }
        },
        {
          path: '/index/devices',
          component: () => import('@/views/Devices.vue'),
          meta: { title: '设备管理', requiresAuth: true }
        },
        {
          path: '/index/bills',
          component: () => import('@/views/Bills.vue'),
          meta: { title: '账单管理', requiresAuth: true }
        },
        {
          path: '/index/settings',
          component: () => import('@/views/Settings.vue'),
          meta: { title: '个人设置', requiresAuth: true }
        }
      ]
    },
    {
      path: '/login',
      component: () => import('@/views/LoginPage.vue'),
      meta: { title: '用户登录与注册', requiresAuth: false }
    }
  ],
})


// 路由守卫 - 验证登录状态
router.beforeEach((to, from, next) => {
  const userStore = useUserStore()

  document.title = to.meta.title || '家庭能耗体检与节能建议系统'

  console.log(`是否有效登录:${userStore.isLogin()}`)

  if (to.meta.requiresAuth && !userStore.isLogin()) {
    next('/login')
  } else {
    next()
  }
})

export default router
