import http from 'k6/http'
import { check, sleep } from 'k6'

const endpoint = 'https://example.com/api'

const req = function (urlPath, method = 'get', data = {}) {
  let url = `${endpoint}${urlPath}`
  const params = {
    headers: {
      'Content-Type': 'application/json;charset=UTF-8',
    }
  }

  let response
  if (method == 'post') {
    const payload = JSON.stringify(data)
    response = http.post(url, payload, params)
  } else {
    response = http.get(url, params)
  }
  return response
}


export function setup() {
  console.log('setup')
}

export default function() {
  req('/posts/pal-gunma', 'get', { id:'slug-01' })
}

export function teardown(data) {
    console.log('teardown')
}

