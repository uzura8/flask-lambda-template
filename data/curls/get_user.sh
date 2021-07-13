#!/bin/bash

if test $IS_LOCAL -eq 1 ; then
  URL="http://localhost:5000"
else
  URL=$BASE_URL
fi

curl -H "Content-Type: application/json" -X GET "${URL}/users/taroyamada"

