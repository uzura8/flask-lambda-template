#!/bin/bash

if test $IS_LOCAL -eq 1 ; then
  URL="http://127.0.0.1:5000/api"
else
  URL=$BASE_URL
fi

SERVICE_ID="hoge"

#curl -H "Content-Type: application/json" -X POST "${URL}/comments/${SERVICE_ID}/post-001" -d '{"body":"お知らせ01のコメント01です。", "category":"cate01"}'
#curl -H "Content-Type: application/json" -X POST "${URL}/posts/${SERVICE_ID}" -d '{"title":"お知らせ44", "body":"お知らせ44です。", "category":"cate01", "slug":"info44", "publishAt":"2021-09-09T15:46:00+09:00"}'

CNT=1;
while [ $CNT -lt 10 ];
  do
    #echo 'Number is '$CNT;
    CATE_NO=$(( $CNT % 3 + 1))
    PUBLISH=$(( $CNT % 2))

    #CONT_ID="post-00${CATE_NO}"
    CONT_ID=""

    #if test $PUBLISH -eq 1 ; then
    #  STATUS='publish';
    #else
    #  STATUS='unpublish';
    #fi

    curl -H "Content-Type: application/json" -X POST "${URL}/comments/${SERVICE_ID}/${CONT_ID}" -d '{"body":"お知らせコメント'${CNT}'です。", "category":"cate'0${CATE_NO}'"}'
    #curl -H "Content-Type: application/json" -X POST "${URL}/comments/${SERVICE_ID}/${CONT_ID}" -d '{"body":"お知らせコメント'${CNT}'です。", "category":"cate'0${CATE_NO}'", "slug":"info'${CNT}'", "status":"'${STATUS}'","bodyFormat":"text"}'
    CNT=$(( CNT + 1 ));
    sleep 1;
done
