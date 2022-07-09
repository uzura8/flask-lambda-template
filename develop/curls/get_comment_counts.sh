#!/bin/bash

if test $IS_LOCAL -eq 1 ; then
  URL="http://localhost:5000/api"
else
  URL=$BASE_URL
fi

SERVICE_ID="hoge"

curl -H "Content-Type: application/json" -X GET "${URL}/comments/${SERVICE_ID}/counts"

