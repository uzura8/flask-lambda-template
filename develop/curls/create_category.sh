#!/bin/bash

if test $IS_LOCAL -eq 1 ; then
  URL="http://127.0.0.1:5000/api"
else
  URL=$BASE_URL
fi

SERVICE_ID="hoge"

curl -H "Content-Type: application/json" -H "Authorization: Bearer ${AUTH_TOKEN}" -X POST "${URL}/admin/categories/${SERVICE_ID}" -d '{"label":"ルート01", "slug":"root", "parentId":"0"}'
curl -H "Content-Type: application/json" -H "Authorization: Bearer ${AUTH_TOKEN}" -X POST "${URL}/admin/categories/${SERVICE_ID}" -d '{"label":"東北", "slug":"tohoku", "parentId":1}'
curl -H "Content-Type: application/json" -H "Authorization: Bearer ${AUTH_TOKEN}" -X POST "${URL}/admin/categories/${SERVICE_ID}" -d '{"label":"関東", "slug":"kanto", "parentId":1}'
curl -H "Content-Type: application/json" -H "Authorization: Bearer ${AUTH_TOKEN}" -X POST "${URL}/admin/categories/${SERVICE_ID}" -d '{"label":"東京", "slug":"tokyo", "parentId":3}'
curl -H "Content-Type: application/json" -H "Authorization: Bearer ${AUTH_TOKEN}" -X POST "${URL}/admin/categories/${SERVICE_ID}" -d '{"label":"神奈川", "slug":"kanagawa", "parentId":3}'
curl -H "Content-Type: application/json" -H "Authorization: Bearer ${AUTH_TOKEN}" -X POST "${URL}/admin/categories/${SERVICE_ID}" -d '{"label":"多摩市", "slug":"tama-shi", "parentId":4}'

curl -H "Content-Type: application/json" -H "Authorization: Bearer ${AUTH_TOKEN}" -X POST "${URL}/admin/categories/${SERVICE_ID}" -d '{"label":"カテゴリ01", "slug":"cate01", "parentId":1}'
curl -H "Content-Type: application/json" -H "Authorization: Bearer ${AUTH_TOKEN}" -X POST "${URL}/admin/categories/${SERVICE_ID}" -d '{"label":"カテゴリ02", "slug":"cate02", "parentId":1}'
curl -H "Content-Type: application/json" -H "Authorization: Bearer ${AUTH_TOKEN}" -X POST "${URL}/admin/categories/${SERVICE_ID}" -d '{"label":"カテゴリ03", "slug":"cate03", "parentId":7}'
