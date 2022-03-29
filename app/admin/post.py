import json
from flask import jsonify, request
from app.models.dynamodb import Post, Category
from app.common.error import InvalidUsage
from app.common.request import validate_req_params
from app.validators import NormalizerUtils
from app.admin import bp, site_before_request, ACCEPT_SERVICE_IDS
from flask_cognito import cognito_auth_required, current_user, current_cognito_jwt


@bp.before_request
@site_before_request
def before_request():
    pass


@bp.route('/posts/<string:service_id>', methods=['POST', 'GET'])
@cognito_auth_required
def posts(service_id):
    if service_id not in ACCEPT_SERVICE_IDS:
        raise InvalidUsage('ServiceId does not exist', 404)

    if request.method == 'POST':
        schema = validation_schema_posts_post()
        vals = validate_req_params(schema, request.json)
        item = Post.get_one_by_slug(service_id, vals['slug'])
        if item:
            raise InvalidUsage('Slug already used', 400)

        if vals.get('category'):
            cate = Category.get_one_by_slug(service_id, vals['category'])
            if not cate:
                raise InvalidUsage('Category not exists', 400)

        vals['serviceId'] = service_id
        body = Post.create(vals)

    else:
        params = {}
        for key in ['count', 'order']:
            params[key] = request.args.get(key)
        vals = validate_req_params(validation_schema_posts_post(), params)
        key_name =  'lastKeyCreatedAt'
        vals['index'] = 'createdAtGsi'
        last_key = request.args.get('lastKey')
        if last_key:
            params = {key_name:json.loads(last_key)}
            vals_last_key = validate_req_params(validation_schema_posts_post(), params)
            vals['ExclusiveStartKey'] = vals_last_key[key_name]

        hkey = {'name':'serviceId', 'value': service_id}
        body = Post.query_pager(hkey, vals, True)

    return jsonify(body), 200


@bp.route('/posts/<string:service_id>/<string:post_id>', methods=['POST', 'GET', 'HEAD', 'DELETE'])
def post(service_id, post_id):
    if service_id not in ACCEPT_SERVICE_IDS:
        raise InvalidUsage('ServiceId does not exist', 404)

    #with_cate = True if request.method in ['GET', 'POST'] else False
    post = Post.get_one_by_id(post_id, True, service_id)
    if not post:
        raise InvalidUsage('Not Found', 404)

    if post['serviceId'] != service_id:
        raise InvalidUsage('serviceId is invalid', 400)

    saved = None
    if request.method == 'POST':
        schema = validation_schema_posts_post()
        vals = validate_req_params(schema, request.json)
        saved = Post.update(service_id, post_id, vals)

    elif request.method == 'DELETE':
        Post.delete({'postId':post_id})
        return jsonify(), 200

    if request.method == 'HEAD':
        return jsonify(), 200

    res = saved if saved else post
    return jsonify(res), 200


@bp.route('/posts/<string:service_id>/<string:post_id>/status', methods=['POST'])
def post_status(service_id, post_id):
    if service_id not in ACCEPT_SERVICE_IDS:
        raise InvalidUsage('ServiceId does not exist', 404)

    saved = Post.get_one_by_id(post_id, True, service_id)
    if not saved:
        raise InvalidUsage('Not Found', 404)

    if saved['serviceId'] != service_id:
        raise InvalidUsage('serviceId is invalid', 400)

    schema_all = validation_schema_posts_post()
    schema = dict(filter(lambda item: item[0] == 'status', schema_all.items()))
    vals = validate_req_params(schema, request.json)
    if vals['status'] == saved['postStatus']:
        raise InvalidUsage('', 400)
    saved = Post.update(service_id, post_id, vals)

    return jsonify(saved), 200


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
        'status': {
            'type': 'string',
            'required': False,
            'allowed': ['publish', 'unpublish'],
            'nullable': True,
            'empty': True,
            'default': 'unpublish',
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
            'default': 20,
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
        'lastKeyCreatedAt' : {
            'type': 'dict',
            'schema': {
                'serviceId': {
                    'type': 'string',
                    'required': True,
                    'empty': False,
                },
                'postId': {
                    'type': 'string',
                    'required': True,
                    'empty': False,
                },
                'createdAt': {
                    'type': 'string',
                    'required': True,
                    'empty': False,
                    'regex': r'\d{4}\-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}([\+\-]\d{2}:\d{2}|Z)$',
                },
            }
        },
    }
