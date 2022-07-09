#!/bin/bash

if test $IS_LOCAL -eq 1 ; then
  URL="http://localhost:5000/api"
else
  URL=$BASE_URL
fi

SERVICE_ID="hoge"

curl -H "Content-Type: application/json" -X GET "${URL}/comments/${SERVICE_ID}/post-001/?limit=3&order=desc&category=cate01&sinceTime=2022-05-25T05:55:40Z&untilTime=2022-05-25T05:55:50Z"

