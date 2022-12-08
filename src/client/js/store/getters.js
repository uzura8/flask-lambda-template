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

  hasAdminRole: state => () => {
    if (state.adminUser == null) return false
    if ('attributes' in state.adminUser === false) return false
    if ('role' in state.adminUser.attributes === false) return false
    return state.adminUser.attributes.role === 'admin'
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

  adminPostsPagerIndexCount: state => () => {
    return state.adminPostsPager.keys.length
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
