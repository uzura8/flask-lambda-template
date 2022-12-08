import Vue from 'vue'
import Router from 'vue-router'
import cognito from '@/cognito'
import store from '@/store'
import routes from './routes'
import arr from '@/util/arr'

Vue.use(Router)

const adminSignOut = (to, from, next) => {
  cognito.signOut()
  next('/admin/signin')
}

routes.push({
  path: '/admin/signout',
  beforeEnter: adminSignOut,
})

const router = new Router({
  mode: 'history',
  saveScrollPosition: true,
  routes,
  scrollBehavior (to, from, savedPosition) {
    if (to.hash) {
      return { selector: to.hash };
    } else if (savedPosition) {
      return savedPosition;
    } else {
      return { x: 0, y: 0 };
    }
  }
})

router.beforeEach(async(to, from, next) => {
  const isAdminPath = to.path.startsWith('/admin')
  let session
  try {
    session = await cognito.isAuthenticated()
  } catch (err) {
    //console.log(err)
    store.dispatch('setAdminUser', null)
  }
  if (!session) {
    if (to.matched.some(record => record.meta.requiresAuth)) {
      const signInPath = isAdminPath ? '/admin/signin' : '/signin'
      let nextRoute = { path: signInPath }
      if (to.name !== 'AdminTop') {
        nextRoute.query = { redirect: to.fullPath }
      }
      next(nextRoute)
    } else {
      next()
    }
  } else {
    try {
      const token = session.idToken.jwtToken
      const res = await cognito.getAttribute()
      let attrs = {}
      for(let v of res) {
        let key = v.getName().replace(/^custom\:/g, '')
        attrs[key] = v.getValue()
      }
      const user = {
        username: cognito.currentUser.username,
        token: token,
        attributes: attrs,
      }
      store.dispatch('setAdminUser', user)
      if (to.matched.some(record => record.meta.requiresRoleAdmin)) {
        if (store.getters.hasAdminRole() === false) {
          next({ path: '/error/forbidden' })
        }
      }
      if (to.matched.some(record => record.meta.requiresAcceptService)) {
        if (store.getters.checkServiceIdAccepted(to.params.serviceId) === false) {
          next({ path: '/error/forbidden' })
        }
      }
    } catch (err) {
      //console.log(err)
      store.dispatch('setAdminUser', null)
      adminSignOut(to, from, next)
    }
    next()
  }
  store.dispatch('setHeaderMenuOpen', false)
})

export default router
