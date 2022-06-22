import os
from flask import Blueprint, jsonify, request
from app.models.dynamodb import VoteCount, VoteLog, Service
from app.common.error import InvalidUsage
from app.validators import NormalizerUtils
from app.common.request import validate_req_params

bp = Blueprint('vote', __name__, url_prefix='/votes')

ACCEPT_TYPES = os.environ.get('ACCEPT_TYPES', '').split(',')


@bp.route('/<string:service_id>', methods=['GET'])
def get_vote_by_service(service_id):
    if not Service.check_exists(service_id):
        raise InvalidUsage('ServiceId does not exist', 404)

    params = {}
    for key in ['contentIds']:
        params[key] = request.args.get(key)
    vals = validate_req_params(validation_schema_vote(), params)

    if vals.get('contentIds'):
        body = VoteCount.query_all_by_contentIds(service_id, vals['contentIds'])
    else:
        keys = {'p': {'key':'serviceId', 'val':service_id}}
        items = VoteCount.get_all(keys)
        body = conv_res_obj_for_all_votes(items)
    return jsonify(body), 200


@bp.route('/<string:service_id>/<string:content_id>', methods=['POST', 'GET'])
def vote_by_service_and_content(service_id, content_id):
    if not Service.check_exists(service_id):
        raise InvalidUsage('ServiceId does not exist', 404)

    params = {'contentId':content_id}
    vals = validate_req_params(validation_schema_vote(), params)

    if request.method == 'POST':
        vote_type = request.json.get('type', 'like').strip()
        if vote_type not in ACCEPT_TYPES:
            raise InvalidUsage('Type is invalid', 400)

        item = {
            'serviceId': service_id,
            'contentId': vals['contentId'],
            'voteType': vote_type,
            'ip': request.remote_addr,
            'ua': request.headers.get('User-Agent', ''),
        }
        VoteLog.create(item)
        VoteCount.update_count(service_id, vals['contentId'], vote_type)

    keys = {
        'p': {'key':'serviceId', 'val':service_id},
        's': {'key':'contentId', 'val':vals['contentId']},
    }
    proj_exps = 'serviceId, contentId, voteType, voteCount, updatedAt'
    items = VoteCount.get_all(keys, False, 'ServiceIdContentIdLsi', 0, proj_exps)

    return jsonify(items), 200


def conv_res_obj_for_all_votes(items):
    res_body = {
        'items': [],
        'totalCount': 0,
    }

    if items:
        res_body['items'] = items
        count = 0
        for item in items:
            count += item['voteCount']
        res_body['totalCount'] = count

    return res_body


def validation_schema_vote():
    return {
        'contentId': {
            'type': 'string',
            'coerce': (str, NormalizerUtils.trim),
            'required': True,
            'empty': False,
            'minlength': 4,
            'maxlength': 36,
            'regex': r'^[0-9a-z_]+$',
        },
        'contentIds': {
            'type': 'list',
            'coerce': (NormalizerUtils.split),
            'required': False,
            'empty': True,
            'default': [],
            'schema': {
                'type': 'string',
                'minlength': 4,
                'maxlength': 36,
                'regex': r'^[0-9a-z_]+$',
            }
        },
    }
