#!/bin/bash

if test $IS_LOCAL -eq 1 ; then
  URL="http://127.0.0.1:5000/api"
else
  URL=$BASE_URL
fi

curl -H "Content-Type: application/json" -H "Authorization: Bearer ${AUTH_TOKEN}" -X POST "${URL}/admin/services" -d '{"serviceId":"hoge","label":"ほげ","frontendPostDetailUrlPrefix":"http://content-api-frontend-sample.loopback.jp/posts/hoge/"}'
curl -H "Content-Type: application/json" -H "Authorization: Bearer ${AUTH_TOKEN}" -X POST "${URL}/admin/services" -d '{"serviceId":"shop-content","label":"ショップコンテンツ"}'
curl -H "Content-Type: application/json" -H "Authorization: Bearer ${AUTH_TOKEN}" -X POST "${URL}/admin/services" -d '{"serviceId":"shop-info","label":"ショップのお知らせ"}'
