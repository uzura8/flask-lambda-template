#!/bin/bash

if test $IS_LOCAL -eq 1 ; then
  URL="http://localhost:5000/api"
else
  URL=$BASE_URL
fi

SERVICE_ID="fuga"
CONTENT_ID="0001"

curl -H "Content-Type: application/json" -X POST "${URL}/contacts/${SERVICE_ID}" -d '{"contact_type":"1","name":"test","name_phonetic":"tst","email":"user@example.com","tel":"08012345678","content":"This is test.This is test."}'

