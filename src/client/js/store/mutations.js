import * as types from './mutation-types'
import arr from '@/util/arr'

export default {
  [types.SET_COMMON_LOADING] (state, payload) {
    const item = payload.key
    if (payload.status === true) {
      state.common.loadingItems.push(item)
    } else {
      let idx = state.common.loadingItems.indexOf(item)
      if (idx !== -1) state.common.loadingItems.splice(idx, 1)
    }
  },

  [types.RESET_COMMON_LOADING] (state) {
    if (state.common.loadingItems.length === 0) return
    state.common.loadingItems.splice(0, state.common.loadingItems.length)
  },

  [types.SET_COMMON_LOADING_TIMER_ID] (state, timerId) {
    state.common.loadingTimerId = timerId
  },

  [types.RESET_COMMON_LOADING_TIMER_ID] (state) {
    clearTimeout(state.common.loadingTimerId)
    state.common.loadingTimerId = null
  },

  [types.SET_ADMIN_USER] (state, payload) {
    state.adminUser = payload
  },

  [types.SET_ADMIN_USER_TOKENS] (state, payload) {
    state.adminUser.token = payload.idToken
    state.adminUser.accessToken = payload.accessToken
    state.adminUser.refreshToken = payload.refreshToken
  },

  [types.SET_CATEGORY_ITEMS] (state, payload) {
    state.categoryItems = []
    payload.map((item) => {
      state.categoryItems.push({
        slug: item.slug,
        label: item.label,
      })
    })
  },

  [types.SET_ADMIN_POST_LIST] (state, posts) {
    state.adminPostList = []
    posts.map((post) => {
      state.adminPostList.push(post)
    })
  },

  [types.PUSH_ITEM_TO_ADMIN_POSTS_PAGER_KEYS] (state, payload) {
    const index = payload.index
    if (state.adminPostsPager.keys.find(item => item.index === index)) return
    state.adminPostsPager.keys.push(payload)
  },

  [types.RESET_ADMIN_POSTS_PAGER] (state, isResetKeys) {
    if (isResetKeys) state.adminPostsPager.keys = []
    state.adminPostsPager.lastIndex = 0
    state.adminPostsPager.filters = {
      attribute: '',
      compare: '',
      value: '',
    }
  },

  [types.SET_ADMIN_POSTS_PAGER_LAST_INDEX] (state, payload) {
    state.adminPostsPager.lastIndex = payload
  },

  [types.SET_ADMIN_POSTS_PAGER_PARAMS] (state, payload) {
    state.adminPostsPager.lastIndex = payload.index
    state.adminPostsPager.sort = payload.sort
    state.adminPostsPager.order = payload.order
    state.adminPostsPager.filters = payload.filters
    state.adminPostsPager.category = payload.category
  },

  [types.PUSH_ITEM_TO_ADMIN_SHORTEN_URLS_PAGER_KEYS] (state, payload) {
    const index = payload.index
    if (state.adminShortenUrlsPager.keys.find(item => item.index === index)) return
    state.adminShortenUrlsPager.keys.push(payload)
  },

  [types.RESET_ADMIN_SHORTEN_URLS_PAGER] (state, isResetKeys) {
    if (isResetKeys) state.adminShortenUrlsPager.keys = []
    state.adminShortenUrlsPager.lastIndex = 0
  },

  [types.SET_ADMIN_SHORTEN_URLS_PAGER_LAST_INDEX] (state, payload) {
    state.adminShortenUrlsPager.lastIndex = payload
  },

  //[types.AUTH_SET_USER] (state, payload) {
  //  state.auth.user = payload
  //},

  //[types.AUTH_UPDATE_USER_INFO] (state, payload) {
  //  const acceptKeys = ['uid', 'name', 'email', 'emailVerified', 'isAdmin', 'isAnonymous']
  //  if (!arr.inArray(payload.key, acceptKeys)) new Error('Invalid  argument')
  //  state.auth.user[payload.key] = payload.value
  //},

  //[types.AUTH_SET_TOKEN] (state, payload) {
  //  state.auth.token = payload
  //},

  //[types.AUTH_UPDATE_STATE] (state, payload) {
  //  state.auth.state = payload
  //},

  [types.SET_COMMON_HEADER_MENU_OPEN] (state, isOpen) {
    state.common.isHeaderMenuOpen = isOpen
  },
}

