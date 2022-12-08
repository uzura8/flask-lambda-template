import * as types from './mutation-types'
import arr from '@/util/arr'

export default {
  [types.SET_COMMON_LOADING] (state, isLoading) {
    state.common.isLoading = isLoading
  },

  [types.SET_ADMIN_USER] (state, payload) {
    state.adminUser = payload
  },

  [types.PUSH_ITEM_TO_ADMIN_POSTS_PAGER_KEYS] (state, payload) {
    const index = payload.index
    if (state.adminPostsPager.keys.find(item => item.index === index)) return
    state.adminPostsPager.keys.push(payload)
  },

  [types.RESET_ADMIN_POSTS_PAGER] (state, isResetKeys) {
    if (isResetKeys) state.adminPostsPager.keys = []
    state.adminPostsPager.lastIndex = 0
  },

  [types.SET_ADMIN_POSTS_PAGER_LAST_INDEX] (state, payload) {
    state.adminPostsPager.lastIndex = payload
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

