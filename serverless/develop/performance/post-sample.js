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
  req('/posts/hgoe/groups/top-slides', 'get', { order:'desc', count:5 })
  req('/posts/hgoe', 'get', { count:4 })
  req('/hgoe-page-content/top-middle')
  req('/hgoe-page-content/top-bottom')
  req('/posts/hgoe/groups/top-pickups', 'get', { order:'desc', count:4 })
  sleep(5)
  req('/posts/hgoe', 'get', { id:'slug-02' })
  sleep(5)
  req('/posts/', 'get', { withCategory:0, count:20, category:'info-all'})
  sleep(3)
  req('/posts/', 'get', {
    category:'info-all',
    withCategory:0,
    count:20,
    pagerKey: '{"postId":"xxxxxxxxxxxxxxxxxxx","serviceId":"hgoe","statusPublishAt":"publish#2022-11-16T00:44:04Z"}',
  })
  sleep(3)
  req('/posts/hgoe', 'get', { id:'slug-01' })
  sleep(5)
  req('/posts/', 'get', { withCategory:0, count:20, category:'info'})
  sleep(3)
  req('/posts/hgoe', 'get', { id:'slug-02' })
  sleep(5)
  req('/posts/', 'get', { withCategory:0, count:20, category:'cate02'})
  sleep(3)
  req('/posts/hgoe', 'get', { id:'slug-01' })
  sleep(5)
  req('/posts/', 'get', { withCategory:0, count:20, tag:'tag01'})
  sleep(3)
  req('/posts/hgoe', 'get', { id:'slug-02' })
  sleep(5)
  req('/posts/', 'get', { withCategory:0, count:20, category:'info-all'})
  sleep(3)
  req('/posts/hgoe', 'get', { id:'slug-01' })
  sleep(5)
  req('/posts/', 'get', { withCategory:0, count:20, category:'cate03'})
  sleep(3)
  req('/posts/hgoe', 'get', { id:'slug-02' })
  sleep(5)
  req('/posts/', 'get', { withCategory:0, count:20, category:'cate04'})
  sleep(3)
  req('/posts/hgoe', 'get', { id:'slug-02' })
  sleep(5)
  req('/posts/', 'get', { withCategory:0, count:20, category:'cate05'})
  sleep(3)
  req('/posts/hgoe', 'get', { id:'slug-02' })
}

export function teardown(data) {
    console.log('teardown')
}

