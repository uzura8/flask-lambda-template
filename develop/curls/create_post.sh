#!/bin/bash

if test $IS_LOCAL -eq 1 ; then
  URL="http://localhost:5000/api"
else
  URL=$BASE_URL
fi

SERVICE_ID="hoge"

#curl -H "Content-Type: application/json" -X POST "${URL}/posts/${SERVICE_ID}" -d '{"title":"お知らせ01", "body":"お知らせ01です。", "category":"cate01", "slug":"info01"}'
#curl -H "Content-Type: application/json" -X POST "${URL}/posts/${SERVICE_ID}" -d '{"title":"お知らせ02", "body":"お知らせ02です。", "category":"cate02", "slug":"info02"}'
#curl -H "Content-Type: application/json" -X POST "${URL}/posts/${SERVICE_ID}" -d '{"title":"お知らせ03", "body":"お知らせ03です。", "category":"cate01", "slug":"info03"}'
#curl -H "Content-Type: application/json" -X POST "${URL}/posts/${SERVICE_ID}" -d '{"title":"お知らせ04", "body":"お知らせ04です。", "category":"cate02", "slug":"info04"}'
#curl -H "Content-Type: application/json" -X POST "${URL}/posts/${SERVICE_ID}" -d '{"title":"お知らせ05", "body":"お知らせ05です。", "category":"cate03", "slug":"info05"}'
#curl -H "Content-Type: application/json" -X POST "${URL}/posts/${SERVICE_ID}" -d '{"title":"お知らせ06", "body":"お知らせ06です。", "category":"cate01", "slug":"info06"}'
#curl -H "Content-Type: application/json" -X POST "${URL}/posts/${SERVICE_ID}" -d '{"title":"お知らせ07", "body":"お知らせ07です。", "category":"cate02", "slug":"info07"}'
#curl -H "Content-Type: application/json" -X POST "${URL}/posts/${SERVICE_ID}" -d '{"title":"お知らせ08", "body":"お知らせ08です。", "category":"cate03", "slug":"info08"}'
#curl -H "Content-Type: application/json" -X POST "${URL}/posts/${SERVICE_ID}" -d '{"title":"お知らせ09", "body":"お知らせ09です。", "category":"cate01", "slug":"info09"}'
#curl -H "Content-Type: application/json" -X POST "${URL}/posts/${SERVICE_ID}" -d '{"title":"お知らせ44", "body":"お知らせ44です。", "category":"cate01", "slug":"info44", "publishAt":"2021-09-09T15:46:00+09:00"}'

CNT=1;
while [ $CNT -lt 30 ];
  do
    #echo 'Number is '$CNT;
    CATE_NO=$(( $CNT % 3 + 1))
    PUBLISH=$(( $CNT % 2))
    #data='{"title":"お知らせ'${CNT}'", "body":"お知らせ'${CNT}'です。", "category":"cate'0${CATE_NO}'", "slug":"info'${CNT}'"}'
    #echo $data
    curl -H "Content-Type: application/json" -X POST "${URL}/posts/${SERVICE_ID}" -d '{"title":"お知らせ'${CNT}'", "body":"お知らせ'${CNT}'です。", "category":"cate'0${CATE_NO}'", "slug":"info'${CNT}'", "publish":'$PUBLISH'}'
    CNT=$(( CNT + 1 ));
done
