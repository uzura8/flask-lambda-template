import os
from flask import Blueprint, jsonify, request
from app.models.dynamodb import Post, Category, Tag, Service
from app.common.error import InvalidUsage
from app.common.request import validate_req_params
from app.validators import NormalizerUtils

bp = Blueprint('post', __name__, url_prefix='/posts')


@bp.route('/<string:service_id>', methods=['GET'])
def posts(service_id):
    if not Service.check_exists(service_id):
        raise InvalidUsage('ServiceId does not exist', 404)

    params = {}
    for key in ['count', 'order', 'sinceTime', 'untilTime', 'category', 'tag']:
        params[key] = request.args.get(key)
    schema = validation_schema_posts_post()
    vals = validate_req_params(schema, params)
    #vals['status'] = 'publish'

    cate_slug = vals.get('category')
    tag_label = vals.get('tag')
    tag_id = None
    if cate_slug:
        cate = Category.get_one_by_slug(service_id, cate_slug, False, True, False, False)
        if not cate:
            raise InvalidUsage('Category does not exist', 404)

        # For category filter
        vals['categories'] = [cate_slug]
        if cate['children']:
            for c in cate['children']:
                vals['categories'].append(c['slug'])
    elif tag_label:
        tag = Tag.get_one({
            'p': {'key':'serviceId' ,'val':service_id},
            's': {'key':'label' ,'val':tag_label},
        }, False, 'TagsByServiceIdGsi')
        if tag:
            tag_id = tag['tagId']

    if tag_id:
        body = Post.query_all_by_tag_id(tag_id, vals)
    else:
        body = Post.query_all('statusPublishAtGsi', service_id, vals)

    return jsonify(body), 200


@bp.route('/<string:service_id>/<string:slug>', methods=['GET', 'HEAD'])
def post(service_id, slug):
    if not Service.check_exists(service_id):
        raise InvalidUsage('ServiceId does not exist', 404)

    item = Post.get_one_by_slug(service_id, slug, True)
    if not item:
        raise InvalidUsage('Not Found', 404)

    if item['postStatus'] != 'publish':
        raise InvalidUsage('Not Found', 404)

    if request.method == 'HEAD':
        return jsonify(), 200

    return jsonify(Post.to_response(item)), 200


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
        'tag': {
            'type': 'string',
            'coerce': (NormalizerUtils.trim),
            'nullable': True,
            'required': False,
            'empty': True,
            'maxlength': 100,
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
