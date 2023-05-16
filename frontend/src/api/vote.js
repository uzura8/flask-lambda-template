import utilUri from '@/util/uri'
import client from './client'

export default {
  get: (serviceId, contentId = null, params = {}, token = null) => {
    return new Promise((resolve, reject) => {
      let options = {}
      let params_cloned = { ...params }
      options.params = params_cloned
      if (token) options.headers = { Authorization: token }
      const uri = contentId
        ? `votes/${serviceId}/${contentId}`
        : `votes/${serviceId}`
      client.get(uri, options)
        .then((res) => {
          resolve(res.data)
        })
        .catch(err => {
          reject(err)
        })
    })
  },

  post: (serviceId, contentId, vals, token = null) => {
    return new Promise((resolve, reject) => {
      const options = utilUri.getReqOptions(null, token)
      const uri = `votes/${serviceId}/${contentId}`
      client.post(uri, vals, options)
        .then(res => resolve(res.data))
        .catch(err => reject(err))
    })
  },
}

