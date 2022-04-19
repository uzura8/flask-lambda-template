#!/bin/bash

if test $IS_LOCAL -eq 1 ; then
  URL="http://127.0.0.1:5000/api"
else
  URL=$BASE_URL
fi

SERVICE_ID="shop-info"

curl -H "Content-Type: application/json" -H "Authorization: Bearer ${AUTH_TOKEN}" -X POST "${URL}/admin/categories/${SERVICE_ID}" -d '{"label":"ショップからのお知らせ", "slug":"shop", "parentId":1}'
sleep 1;
curl -H "Content-Type: application/json" -H "Authorization: Bearer ${AUTH_TOKEN}" -X POST "${URL}/admin/categories/${SERVICE_ID}" -d '{"label":"注文・配達", "slug":"order", "parentId":2}'
sleep 1;
curl -H "Content-Type: application/json" -H "Authorization: Bearer ${AUTH_TOKEN}" -X POST "${URL}/admin/categories/${SERVICE_ID}" -d '{"label":"組合員活動", "slug":"kumikatsu", "parentId":2}'
sleep 1;
curl -H "Content-Type: application/json" -H "Authorization: Bearer ${AUTH_TOKEN}" -X POST "${URL}/admin/categories/${SERVICE_ID}" -d '{"label":"参加", "slug":"join", "parentId":2}'
sleep 1;
curl -H "Content-Type: application/json" -H "Authorization: Bearer ${AUTH_TOKEN}" -X POST "${URL}/admin/categories/${SERVICE_ID}" -d '{"label":"その他", "slug":"others", "parentId":2}'
sleep 1;

STATUS="publish"
curl -H "Content-Type: application/json" -H "Authorization: Bearer ${AUTH_TOKEN}" -X POST "${URL}/admin/posts/${SERVICE_ID}" -d '{"title":"お知らせ01", "body":"お知らせ01です。", "category":"order", "slug":"shop-info01", "status":"'${STATUS}'"}'
sleep 1;
curl -H "Content-Type: application/json" -H "Authorization: Bearer ${AUTH_TOKEN}" -X POST "${URL}/admin/posts/${SERVICE_ID}" -d '{"title":"お知らせ02", "body":"お知らせ02です。", "category":"order", "slug":"shop-info02", "status":"'${STATUS}'"}'
sleep 1;
curl -H "Content-Type: application/json" -H "Authorization: Bearer ${AUTH_TOKEN}" -X POST "${URL}/admin/posts/${SERVICE_ID}" -d '{"title":"お知らせ03", "body":"お知らせ03です。", "category":"order", "slug":"shop-info03", "status":"'${STATUS}'"}'
sleep 1;
curl -H "Content-Type: application/json" -H "Authorization: Bearer ${AUTH_TOKEN}" -X POST "${URL}/admin/posts/${SERVICE_ID}" -d '{"title":"お知らせ04", "body":"お知らせ04です。", "category":"order", "slug":"shop-info04", "status":"'${STATUS}'"}'
sleep 1;
curl -H "Content-Type: application/json" -H "Authorization: Bearer ${AUTH_TOKEN}" -X POST "${URL}/admin/posts/${SERVICE_ID}" -d '{"title":"お知らせ05", "body":"お知らせ05です。", "category":"order", "slug":"shop-info05", "status":"'${STATUS}'"}'
sleep 1;
curl -H "Content-Type: application/json" -H "Authorization: Bearer ${AUTH_TOKEN}" -X POST "${URL}/admin/posts/${SERVICE_ID}" -d '{"title":"お知らせ06", "body":"お知らせ06です。", "category":"order", "slug":"shop-info06", "status":"'${STATUS}'"}'
sleep 1;
curl -H "Content-Type: application/json" -H "Authorization: Bearer ${AUTH_TOKEN}" -X POST "${URL}/admin/posts/${SERVICE_ID}" -d '{"title":"お知らせ07", "body":"お知らせ07です。", "category":"order", "slug":"shop-info07", "status":"'${STATUS}'"}'
sleep 1;
curl -H "Content-Type: application/json" -H "Authorization: Bearer ${AUTH_TOKEN}" -X POST "${URL}/admin/posts/${SERVICE_ID}" -d '{"title":"お知らせ08", "body":"お知らせ08です。", "category":"order", "slug":"shop-info08", "status":"'${STATUS}'"}'
sleep 1;
curl -H "Content-Type: application/json" -H "Authorization: Bearer ${AUTH_TOKEN}" -X POST "${URL}/admin/posts/${SERVICE_ID}" -d '{"title":"お知らせ09", "body":"お知らせ09です。", "category":"order", "slug":"shop-info09", "status":"'${STATUS}'"}'
sleep 1;
