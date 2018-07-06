import Vue from 'vue'
import Router from 'vue-router'
import SearchMainComponent from '../components/SearchMainComponent'


Vue.use(Router)

export default new Router({
  mode: 'history',
  scrollBehavior: (to, from, savedPosition) => ({ y: 0 }),
  routes: [
    {
      path: '/',
      name: 'SearchMainComponent',
      component: SearchMainComponent
    }
  ]
})
