#!/bin/bash

if [ $IS_LOCAL = "True" ]; then
  URL="http://localhost:5000/api"
else
  URL=$BASE_URL
fi

SERVICE_ID="hoge"

#curl -H "Content-Type: application/json" -X GET "${URL}/posts/${SERVICE_ID}"
#curl -H "Content-Type: application/json" -X GET "${URL}/posts/${SERVICE_ID}?category=cate01"
#curl -H "Content-Type: application/json" -I "${URL}/posts/${SERVICE_ID}/info04"
#curl -H "Content-Type: application/json" -X GET "${URL}/posts/${SERVICE_ID}/info04"

#curl -H "Content-Type: application/json" -X GET "${URL}/posts/${SERVICE_ID}?fuga=momo"
#  params = {
#      'publish': True,
#      'limit': 5,
#      'order': 'desc',
#      'sinceTime': '2021-09-12T00:41:48Z',
#      'categories': ['cate01', 'cate03'],
#  }
curl -H "Content-Type: application/json" -X GET "${URL}/posts/${SERVICE_ID}?limit=3&order=asc&sinceTime=2021-09-12T00:41:35Z"

