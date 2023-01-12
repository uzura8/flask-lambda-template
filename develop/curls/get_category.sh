#!/bin/bash

if [ $IS_LOCAL = "True" ]; then
  URL="http://localhost:5000/api"
else
  URL=$BASE_URL
fi

SERVICE_ID="hoge"
SLUG="tama-shi"

curl -H "Content-Type: application/json" -X GET "${URL}/categories/${SERVICE_ID}/${SLUG}"
