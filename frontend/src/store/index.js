import Vue from 'vue'
import Vuex from 'vuex'
//import createPersistedState from 'vuex-persistedstate'
import actions from './actions'
import getters from './getters'
import mutations from './mutations'

Vue.use(Vuex)

const state = {
  common: {
    loadingItems: [],
    isHeaderMenuOpen: false,
    loadingTimerId: null,
  },
  auth: {
    state: null,
    user: null,
    token: null,// idToken
    accessToken: null,
    refreshToken: null,
  },
  categoryItems: [],
  adminUser: null,
  adminPostList: [],
  adminPostListServiceId: null,
  adminPostsPager: {
    keys: [],
    lastIndex: 0,
    sort: 'createdAt',
    order: 'desc',
    filters: {
      attribute: '',
      compare: '',
      value: '',
    },
    category: '',
  },
  adminShortenUrlsPager: {
    keys: [],
    lastIndex: 0,
  }
}

export default new Vuex.Store({
  state,
  getters,
  actions,
  mutations,
  plugins: [
    //createPersistedState({
    //  key: 'SampleSiteState',
    //  paths: ['auth'],
    //  //storage: window.sessionStorage
    //})
  ],
  strict: process.env.NODE_ENV !== 'production'
})
