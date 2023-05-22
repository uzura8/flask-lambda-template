#!/bin/bash

if [ $IS_LOCAL = "True" ]; then
  URL="http://127.0.0.1:5000/api"
else
  URL=$BASE_URL
fi

curl -H "Content-Type: application/json" -H "Authorization: Bearer ${AUTH_TOKEN}" -X GET "${URL}/admin/users"

