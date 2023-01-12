#!/bin/bash

if [ $IS_LOCAL = "True" ]; then
  URL="http://localhost:5000/api"
else
  URL=$BASE_URL
fi

SERVICE_ID="hoge"
CONTENT_ID="0001"

curl -H "Content-Type: application/json" -X GET "${URL}/votes/${SERVICE_ID}"

