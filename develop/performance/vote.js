import http from 'k6/http'
import { check, sleep } from 'k6'

const endpoint = 'https://example.com/api'
//const endpoint = 'http://localhost:5000/api'

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
  req('/votes/fuga')
  sleep(5)
  req('/votes/fuga/0008', 'post', { type: 'like' })
  sleep(1)
  req('/votes/fuga/0009', 'post', { type: 'like' })
  sleep(1)
  req('/votes/fuga/0010', 'post', { type: 'like' })
  sleep(1)
}

export function teardown(data) {
    console.log('teardown')
}

