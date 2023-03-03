import os
from flask import Blueprint, jsonify, request
from app.models.dynamodb import Comment, CommentCount, Service, ModelInvalidParamsException
from app.common.error import InvalidUsage
from app.common.request import validate_req_params
from app.validators import NormalizerUtils

bp = Blueprint('comment', __name__, url_prefix='/comments')

COMMENT_DEFAULT_PUBLISH_STATUS = os.environ.get('COMMENT_DEFAULT_PUBLISH_STATUS', False)


@bp.route('/<string:service_id>/counts', methods=['GET'])
def comment_counts(service_id):
    if not Service.check_exists(service_id):
        raise InvalidUsage('ServiceId does not exist', 404)

    pkeys = {'key':'serviceId', 'val':service_id}
    items = CommentCount.get_all_by_pkey(pkeys, None, None, False)
    body = conv_res_obj_for_all_count(items)
    return jsonify(body), 200


@bp.route('/<string:service_id>/<string:content_id>', methods=['GET', 'POST'])
def comments(service_id, content_id):
    if not Service.check_exists(service_id):
        raise InvalidUsage('ServiceId does not exist', 404)

    res_body = None
    if request.method == 'POST':
        params = request.json
        params['contentId'] = content_id
        schema = validation_schema_comments()
        vals = validate_req_params(schema, request.json)
        vals['serviceId'] = service_id
        vals['publishStatus'] = COMMENT_DEFAULT_PUBLISH_STATUS
        vals['ip'] = request.remote_addr
        vals['ua'] = request.headers.get('User-Agent', '')

        try:
            res_body = Comment.create(vals)

        except ModelInvalidParamsException as e:
            raise InvalidUsage(e.message, 400)

        except Exception as e:
            import traceback
            print(traceback.format_exc())
            raise InvalidUsage('Server Error', 500)
    else:
        params = {}
        for key in ['count', 'order', 'sinceTime', 'untilTime']:
            params[key] = request.args.get(key)
        params['contentId'] = content_id
        schema = validation_schema_comments()
        vals = validate_req_params(schema, params)
        res_body = Comment.query_all_publish(service_id, content_id, vals)

    return jsonify(res_body), 200


def conv_res_obj_for_all_count(items):
    res_body = {
        'items': [],
        'totalCount': 0,
    }

    if items:
        res_body['items'] = items
        count = 0
        for item in items:
            count += item.get('commentCount', 0)
        res_body['totalCount'] = count

    return res_body


def validation_schema_comments():
    return {
        'contentId': {
            'type': 'string',
            'coerce': (NormalizerUtils.trim),
            'required': True,
            'nullable': False,
            'empty': False,
            'regex': r'^[0-9a-z_\-]{4,64}$',
        },
        'body': {
            'type': 'string',
            'coerce': (NormalizerUtils.rtrim),
            'required': False,
            'nullable': True,
            'empty': True,
            'default': '',
        },
        'count': {
            'type': 'integer',
            'coerce': int,
            'required': False,
            'min': 1,
            'max': 100,
            'default': 10,
        },
        'order': {
            'type': 'string',
            'required': False,
            'allowed': ['asc', 'desc'],
            'default': 'desc',
        },
        'sinceTime': {
            'type': 'string',
            'coerce': (NormalizerUtils.trim),
            'required': False,
            'nullable': True,
            'empty': True,
            'regex': r'\d{4}\-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}([\+\-]\d{2}:\d{2}|Z)$',
        },
        'untilTime': {
            'type': 'string',
            'coerce': (NormalizerUtils.trim),
            'required': False,
            'nullable': True,
            'empty': True,
            'regex': r'\d{4}\-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}([\+\-]\d{2}:\d{2}|Z)$',
        },
    }
