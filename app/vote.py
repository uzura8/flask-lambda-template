import re
import os
from flask import Blueprint, jsonify, request
from boto3.dynamodb.conditions import Key
from dynamodb import dynamodb
from app.common.date import utc_iso
from app.common.error import InvalidUsage

bp = Blueprint('vote', __name__, url_prefix='/votes')

PRJ_PREFIX = os.environ['PRJ_PREFIX']
VOTE_LOG_TABLE = '-'.join([PRJ_PREFIX, 'vote-log'])
VOTE_COUNT_TABLE = '-'.join([PRJ_PREFIX, 'vote-count'])
ACCEPT_SERVICE_IDS = os.environ.get('ACCEPT_SERVICE_IDS', '').split(',')
ACCEPT_TYPES = os.environ.get('ACCEPT_TYPES', '').split(',')
cors_accept_origins_str = os.environ.get('CORS_ACCEPT_ORIGINS', '')
CORS_ACCEPT_ORIGINS = cors_accept_origins_str.split(',') if cors_accept_origins_str else []


@bp.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


@bp.after_request
def add_cors_headers(response):
    response.headers.add('X-Content-Type-Options', 'nosniff')

    r = request.referrer[:-1] if request.referrer else None
    if not CORS_ACCEPT_ORIGINS:
        response.headers.add('Access-Control-Allow-Origin', '*')

    elif r is not None and r in CORS_ACCEPT_ORIGINS:
        response.headers.add('Access-Control-Allow-Origin', r)

    if not CORS_ACCEPT_ORIGINS or r is not None and r in CORS_ACCEPT_ORIGINS:
        response.headers.add('Access-Control-Allow-Credentials', 'true')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        response.headers.add('Access-Control-Allow-Headers', 'Cache-Control')
        response.headers.add('Access-Control-Allow-Headers', 'X-Requested-With')
        response.headers.add('Access-Control-Allow-Headers', 'Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET, POST, OPTIONS, PUT, DELETE')

    return response


@bp.route('/<string:service_id>', methods=['GET'])
def get_vote_by_service(service_id):
    if service_id not in ACCEPT_SERVICE_IDS:
        raise InvalidUsage('ServiceId does not exist', 404)

    table = dynamodb.Table(VOTE_COUNT_TABLE)
    res = table.query(
        ProjectionExpression='serviceId, contentId, voteType, voteCount, updatedAt',
        KeyConditionExpression=Key('serviceId').eq(service_id)
    )
    body = conv_res_obj_for_all_votes(res)
    return jsonify(body), 200


@bp.route('/<string:service_id>/<string:content_id>', methods=['POST', 'GET'])
def vote_by_service_and_content(service_id, content_id):
    if service_id not in ACCEPT_SERVICE_IDS:
        raise InvalidUsage('ServiceId does not exist', 404)

    if not validate_content_id(content_id):
        raise InvalidUsage('ContentId is invalid', 404)

    if request.method == 'POST':
        vote_type = request.json.get('type', 'like').strip()
        if vote_type not in ACCEPT_TYPES:
            raise InvalidUsage('Type is invalid', 400)

        time = utc_iso(True, True)
        content_id_type = '-'.join([content_id, vote_type])

        table = dynamodb.Table(VOTE_LOG_TABLE)
        item = {
            'serviceId': service_id,
            'contentId': content_id,
            'voteType': vote_type,
            'createdAt': time,
            'ip': request.remote_addr,
            'ua': request.headers.get('User-Agent', ''),
        }
        table.put_item(Item=item)

        table = dynamodb.Table(VOTE_COUNT_TABLE)
        table.update_item(
            Key={
                'serviceId': service_id,
                'contentIdType': content_id_type,
            },
            UpdateExpression="""
                ADD voteCount :incr
                SET updatedAt = :time, contentId = :contId, voteType = :voteType
            """,
            ExpressionAttributeValues={
                ':incr': 1,
                ':time': time,
                ':contId': content_id,
                ':voteType': vote_type,
            }
        )

    table = dynamodb.Table(VOTE_COUNT_TABLE)
    res = table.query(
        IndexName=VOTE_COUNT_TABLE + '-lsi',
        ProjectionExpression='serviceId, contentId, voteType, voteCount, updatedAt',
        KeyConditionExpression=Key('serviceId').eq(service_id) & Key('contentId').eq(content_id)
    )
    items = res['Items'] if 'Items' in res and res['Items'] else []
    return jsonify(items), 200


def validate_content_id(target):
    target = target.strip()
    ptn = r'^[0-9a-z_]{4,36}$'
    res = re.match(ptn, target)
    return res is not None


def conv_res_obj_for_all_votes(ddb_res):
    res_body = {
        'items': [],
        'totalCount': 0,
    }

    if 'Items' in ddb_res and ddb_res['Items']:
        res_body['items'] = ddb_res['Items']
        count = 0
        for item in ddb_res['Items']:
            count += item['voteCount']
        res_body['totalCount'] = count

    return res_body
