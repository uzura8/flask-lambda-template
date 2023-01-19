import utilArr from '@/util/arr'
import utilCommon from '@/util/common'

export default {
  //checkUserType: state => (type) => {
  //  if (!state.auth.state) return false
  //  if (state.auth.user == null) return false
  //  return state.auth.user.type == type
  //},

  isAdminUser: state => () => {
    return Boolean(state.adminUser)
  },

  adminRole: state => () => {
    if (state.adminUser == null) return
    if (utilCommon.checkObjHasProp(state.adminUser, 'attributes') === false) return
    if (utilCommon.checkObjHasProp(state.adminUser.attributes, 'role') === false) return
    return state.adminUser.attributes.role
  },

  checkAdminRole: state => (role) => {
    if (state.adminUser == null) return false
    if (utilCommon.checkObjHasProp(state.adminUser, 'attributes') === false) return false
    if (utilCommon.checkObjHasProp(state.adminUser.attributes, 'role') === false) return false
    return state.adminUser.attributes.role === role
  },

  hasAdminRole: state => () => {
    if (state.adminUser == null) return false
    if (utilCommon.checkObjHasProp(state.adminUser, 'attributes') === false) return false
    if (utilCommon.checkObjHasProp(state.adminUser.attributes, 'role') === false) return false
    return state.adminUser.attributes.role === 'admin'
  },

  hasEditorRole: state => () => {
    if (state.adminUser == null) return false
    if (utilCommon.checkObjHasProp(state.adminUser, 'attributes') === false) return false
    if (utilCommon.checkObjHasProp(state.adminUser.attributes, 'role') === false) return false
    const editorRoles = ['admin', 'editor']
    return editorRoles.includes(state.adminUser.attributes.role)
  },

  adminUserAcceptServiceIds: state => () => {
    if (state.adminUser == null) return []
    if ('attributes' in state.adminUser === false) return []
    if ('acceptServiceIds' in state.adminUser.attributes === false) return []
    if (! state.adminUser.attributes.acceptServiceIds) return []
    return state.adminUser.attributes.acceptServiceIds.split(',')
  },

  checkServiceIdAccepted: state => (serviceId) => {
    if (state.adminUser == null) return false
    if ('attributes' in state.adminUser === false) return false
    if ('acceptServiceIds' in state.adminUser.attributes === false) return false
    if (! state.adminUser.attributes.acceptServiceIds) return false
    const acceptServiceIds = state.adminUser.attributes.acceptServiceIds.split(',')
    return acceptServiceIds.includes(serviceId)
  },

  adminPostsPagerQueryCurrent: state => () => {
    let params = {
      sort: state.adminPostsPager.sort,
      order: state.adminPostsPager.order,
    }
    if (state.adminPostsPager.lastIndex != null) {
      params.index = state.adminPostsPager.lastIndex
    }
    return params
  },

  adminPostsPagerIndexCount: state => () => {
    return state.adminPostsPager.keys.length
  },

  adminShortenUrlsPagerIndexCount: state => () => {
    return state.adminShortenUrlsPager.keys.length
  },

  //userInfo: state => (key) => {
  //  const acceptKey = [
  //    'uid', 'name', 'email', 'photoURL'
  //  ]
  //  if (!state.auth.state) return
  //  if (state.auth.user == null) return
  //  if (!utilArr.inArray(key, acceptKey)) return
  //  if (utilCommon.isEmpty(state.auth.user[key])) return
  //  return state.auth.user[key]
  //},

  //isEmailVerified: state => () => {
  //  if (!state.auth.state) return false
  //  if (state.auth.user == null) return false
  //  return state.auth.user.emailVerified === true
  //},
}
