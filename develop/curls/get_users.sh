#!/bin/bash

if test $IS_LOCAL -eq 1 ; then
  URL="http://127.0.0.1:5000/api"
else
  URL=$BASE_URL
fi

curl -H "Content-Type: application/json" -H "Authorization: Bearer ${AUTH_TOKEN}" -X GET "${URL}/admin/users"

