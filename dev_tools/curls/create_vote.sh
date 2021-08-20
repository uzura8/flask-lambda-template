#!/bin/bash

if test $IS_LOCAL -eq 1 ; then
  URL="http://localhost:5000/api"
else
  URL=$BASE_URL
fi

SERVICE_ID="hoge"
CONTENT_ID="0001"

curl -H "Content-Type: application/json" -X POST "${URL}/votes/${SERVICE_ID}/${CONTENT_ID}" -d '{"type": "like"}'

