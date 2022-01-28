import os
from flask import Blueprint, jsonify, request
from app.models.dynamodb import Post, Category
from app.common.error import InvalidUsage
from app.common.request import validate_req_params
from app.validators import ValidatorExtended, NormalizerUtils
#import time

bp = Blueprint('post', __name__, url_prefix='/posts')
ACCEPT_SERVICE_IDS = os.environ.get('ACCEPT_SERVICE_IDS', '').split(',')


@bp.route('/<string:service_id>', methods=['POST', 'GET'])
def posts(service_id):
    if service_id not in ACCEPT_SERVICE_IDS:
        raise InvalidUsage('ServiceId does not exist', 404)

    if request.method == 'POST':
        schema = validation_schema_posts_post()
        vals = validate_req_params(schema, request.json)
        item = Post.get_one_by_slug(service_id, vals['slug'])
        if item:
            raise InvalidUsage('Slug already used', 400)

        #time.sleep(1)
        body = Post.create(service_id, vals)

    else:
        params = {'publish': True}
        for key in ['count', 'order', 'sinceTime', 'untilTime', 'category']:
            params[key] = request.args.get(key)
        schema = validation_schema_posts_post()
        vals = validate_req_params(schema, params)
        cate_slug = vals.get('category')
        if cate_slug:
            cate = Category.get_one_by_slug(service_id, cate_slug, False, True)
            if not cate:
                raise InvalidUsage('Category does not exist', 404)

            # For category filter
            vals['categories'] = [cate_slug]
            if cate['children']:
                for c in cate['children']:
                    vals['categories'].append(c['slug'])

        body = Post.query_all('gsi-list-all', service_id, vals)

    return jsonify(body), 200


@bp.route('/<string:service_id>/<string:slug>', methods=['POST', 'GET', 'HEAD'])
def post(service_id, slug):
    if service_id not in ACCEPT_SERVICE_IDS:
        raise InvalidUsage('ServiceId does not exist', 404)

    item = Post.get_one_by_slug(service_id, slug, True)
    if not item:
        raise InvalidUsage('Not Found', 404)

    if request.method == 'POST':
        pass

    if request.method == 'HEAD':
        return jsonify(), 200

    return jsonify(item), 200


def validation_schema_posts_post():
    return {
        'slug': {
            'type': 'string',
            'coerce': (str, NormalizerUtils.trim),
            'required': True,
            'empty': False,
            'maxlength': 128,
            'regex': r'^[0-9a-z\-]+$',
        },
        'title': {
            'type': 'string',
            'coerce': (NormalizerUtils.trim),
            'required': True,
            'empty': False,
        },
        'body': {
            'type': 'string',
            'coerce': (NormalizerUtils.rtrim),
            'required': False,
            'nullable': True,
            'empty': True,
            'default': '',
        },
        'category': {
            'type': 'string',
            'coerce': (NormalizerUtils.trim),
            'nullable': True,
            'required': False,
            'empty': True,
        },
        'publish': {
            'type': 'boolean',
            'coerce': (str, NormalizerUtils.to_bool),
            'required': False,
            'empty': True,
            'default': False,
        },
        'publishAt': {
            'type': 'string',
            'coerce': (NormalizerUtils.trim),
            'required': False,
            'empty': True,
            'regex': r'\d{4}\-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}([\+\-]\d{2}:\d{2}|Z)$',
        },
        'count': {
            'type': 'integer',
            'coerce': int,
            'required': False,
            'min': 1,
            'max': 50,
            'default': 5,
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
