import Layout from '@/layout/index.vue'
import Router from 'vue-router'
import Vue from 'vue'

Vue.use(Router)

export default new Router({
  mode: 'history', // Enable this if you need.
  scrollBehavior: (to, from, savedPosition) => {
    if (savedPosition) {
      return savedPosition
    } else {
      return { x: 0, y: 0 }
    }
  },
  base: process.env.BASE_URL,
  routes: [
    {
      path: '/login',
      component: () => import(/* webpackChunkName: "login" */ '@/views/login/index.vue')
    },
    {
      path: '/404',
      component: () => import(/* webpackChunkName: "404" */ '@/views/404.vue')
    },
    {
      path: '/',
      component: Layout,
      redirect: '/bill',
      children: [
        {
          name: 'Bill',
          path: 'bill',
          component: () => import(/* webpackChunkName: "bill" */ '@/views/bill/index.vue')
        }
      ]
    },
    {
      path: '*',
      redirect: '/404'
    }
  ]
})
