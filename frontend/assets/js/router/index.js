import Vue from 'vue'
import Router from 'vue-router'
import SearchMainComponent from '../components/SearchMainComponent'

const _base = process.env.SCRIPT_NAME || '';

Vue.use(Router)

export default new Router({
  mode: 'history',
  scrollBehavior: (to, from, savedPosition) => ({ y: 0 }),
  base: _base,
  routes: [
    {
      path: '/',
      name: 'SearchMainComponent',
      component: SearchMainComponent
    }
  ]
})
