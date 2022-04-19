#!/bin/bash

if test $IS_LOCAL -eq 1 ; then
  URL="http://127.0.0.1:5000/api"
else
  URL=$BASE_URL
fi

SERVICE_ID="hoge"

echo $AUTH_TOKEN

curl -H "Content-Type: application/json" -H "Authorization: Bearer ${AUTH_TOKEN}" -X POST "${URL}/admin/tags/${SERVICE_ID}" -d '{"label":"タグ01", "slug":"tag01"}'
curl -H "Content-Type: application/json" -H "Authorization: Bearer ${AUTH_TOKEN}" -X POST "${URL}/admin/tags/${SERVICE_ID}" -d '{"label":"タグ02", "slug":"tag02"}'
curl -H "Content-Type: application/json" -H "Authorization: Bearer ${AUTH_TOKEN}" -X POST "${URL}/admin/tags/${SERVICE_ID}" -d '{"label":"タグ03", "slug":"tag03"}'