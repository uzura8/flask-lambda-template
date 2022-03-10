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

        cate = Category.get_one_by_slug(service_id, vals['category'])
        if not cate:
            raise InvalidUsage('Category not exists', 400)

        body = Post.create(service_id, vals)

    else:
        params = {}
        for key in ['count', 'order', 'sinceTime', 'untilTime', 'category']:
            params[key] = request.args.get(key)
        schema = validation_schema_posts_post()
        vals = validate_req_params(schema, params)
        cate_slug = vals.get('category')
        if cate_slug:
            cate = Category.get_one_by_slug(service_id, cate_slug, False, True, False, False)
            if not cate:
                raise InvalidUsage('Category does not exist', 404)

            # For category filter
            vals['categories'] = [cate_slug]
            if cate['children']:
                for c in cate['children']:
                    vals['categories'].append(c['slug'])

        body = Post.query_all('createdAtGsi', service_id, vals, True)

    return jsonify(body), 200


@bp.route('/posts/<string:service_id>/<string:slug>', methods=['POST', 'GET', 'HEAD', 'DELETE'])
def post(service_id, slug):
    if service_id not in ACCEPT_SERVICE_IDS:
        raise InvalidUsage('ServiceId does not exist', 404)

    with_cate = True if request.method in ['GET', 'POST'] else False
    saved = Post.get_one_by_slug(service_id, slug, with_cate)
    if not saved:
        raise InvalidUsage('Not Found', 404)

    if request.method == 'POST':
        schema = validation_schema_posts_post()
        vals = validate_req_params(schema, request.json)
        saved = Post.update(service_id, slug, vals)

    elif request.method == 'DELETE':
        Post.delete({'serviceIdSlug': '#'.join([service_id, slug])})
        return jsonify(), 200

    if request.method == 'HEAD':
        return jsonify(), 200

    return jsonify(saved), 200


@bp.route('/posts/<string:service_id>/<string:slug>/status', methods=['POST'])
def post_status(service_id, slug):
    if service_id not in ACCEPT_SERVICE_IDS:
        raise InvalidUsage('ServiceId does not exist', 404)

    saved = Post.get_one_by_slug(service_id, slug, True)
    if not saved:
        raise InvalidUsage('Not Found', 404)

    schema_all = validation_schema_posts_post()
    schema = dict(filter(lambda item: item[0] == 'status', schema_all.items()))
    vals = validate_req_params(schema, request.json)
    if vals['status'] == saved['postStatus']:
        raise InvalidUsage('', 400)
    saved = Post.update(service_id, slug, vals)

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
