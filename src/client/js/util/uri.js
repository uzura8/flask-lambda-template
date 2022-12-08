import config from '@/config/config'
import common from './common'

export default {
  convToPostParams: (values, requiredKeys = []) => {
    if (!common.isEmpty(requiredKeys)) {
      for (let i = 0, n = requiredKeys.length; i < n; i++) {
        let key = requiredKeys[i]
        if (common.isEmpty(values[key])) throw new Error(`No value '${key}'`)
      }
    }

    let params = new URLSearchParams()
    const keys = Object.keys(values)
    for (let i = 0, n = keys.length; i < n; i++) {
      let key = keys[i]
      params.append(key, values[key]);
    }
    return params
  },

  getReqOptions(params = null, token = null) {
    let options = {}
    if (params) {
      options.params = { ...params }
    }
    if (token) {
      options.headers = {}
      const reqToken =  config.adminAuthHeaderTokenPrefix
        ? `${config.adminAuthHeaderTokenPrefix} ${token}`
        : token
      options.headers[config.adminAuthHeader] = reqToken
    }
    return options
  },

  getParameterByName: (name) => {
    const match = RegExp('[?&]' + name + '=([^&]*)').exec(window.location.search)
    return match && decodeURIComponent(match[1].replace(/\+/g, ' '))
  },
}

