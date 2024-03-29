from flask import Blueprint, jsonify, request
from app.models.dynamodb import Post, Category, Tag, Service, PostGroup
from app.common.error import InvalidUsage
from app.common.request import validate_req_params
from app.common.date import is_future
from app.validators import NormalizerUtils

bp = Blueprint('post', __name__, url_prefix='/posts')


@bp.route('/<string:service_id>', methods=['GET'])
def posts(service_id):
    if not Service.check_exists(service_id):
        raise InvalidUsage('ServiceId does not exist', 404)

    params = {}
    for key in ['count', 'order', 'category', 'tag', 'withCategory', 'pagerKey']:
        params[key] = request.args.get(key)
    schema = validation_schema_posts_get()
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
        body = Post.query_all_by_tag_id(tag_id, vals, True, service_id)

    else:
        pkeys = {'key':'serviceId', 'val':service_id}
        pager_keys = {'pkey':'postId', 'index_pkey':'serviceId', 'index_skey':'statusPublishAt'}
        cate_slugs = vals.get('categories', [])
        filter_conds = {'cate_slugs': cate_slugs}
        body = Post.query_pager_published(pkeys, vals, pager_keys, 'statusPublishAtGsi', filter_conds)

        if vals.get('withCategory', True):
            body['items'] = Post.set_category_to_list(body['items'], service_id)

    return jsonify(body), 200


@bp.route('/<string:service_id>/groups', methods=['GET'])
def post_groups(service_id):
    if not Service.check_exists(service_id):
        raise InvalidUsage('ServiceId does not exist', 404)

    pkeys = {'key':'serviceId', 'val':service_id}
    body = PostGroup.get_all_by_pkey(pkeys, None, 'PostGroupsByServiceIdGsi', False)
    return jsonify(body), 200


@bp.route('/<string:service_id>/groups/<string:slug>', methods=['GET'])
def post_group(service_id, slug):
    if not Service.check_exists(service_id):
        raise InvalidUsage('ServiceId does not exist', 404)

    query_key = '#'.join([service_id, slug])
    group = PostGroup.get_one_by_pkey('serviceIdSlug', query_key)
    if not group:
        raise InvalidUsage('Not Found', 404)

    vals = validate_req_params(validation_schema_group_get(), request.args)
    order = vals.get('order')
    count = vals.get('count')

    posts = []
    post_ids = group.get('postIds', [])
    if post_ids:
        if order == 'desc':
            post_ids.reverse()
        if count:
            post_ids = post_ids[:count]

        keys = [ {'postId':pid} for pid in post_ids ]
        batch_res = Post.batch_get_items(keys)
        for pid in post_ids:
            p = next((p for p in batch_res if p.get('postId') == pid), None)
            posts.append(Post.to_response(p))

    group['posts'] = posts
    group['postIds'] = post_ids

    return jsonify(PostGroup.to_response(group)), 200


@bp.route('/<string:service_id>/<string:slug>', methods=['GET', 'HEAD'])
def post(service_id, slug):
    if not Service.check_exists(service_id):
        raise InvalidUsage('ServiceId does not exist', 404)

    params = {'token':request.args.get('token'), 'slug':slug}
    vals = validate_req_params(validation_schema_post_get(), params)

    item = Post.get_one_by_slug(service_id, slug, True)
    if not item:
        raise InvalidUsage('Not Found', 404)

    is_published = (item['postStatus'] == 'publish')\
            and (item['publishAt'] and not is_future(item['publishAt']))

    if not is_published:
        if not vals['token'] or vals['token'] != item['previewToken']:
            raise InvalidUsage('Not Found', 404)

    if request.method == 'HEAD':
        return jsonify(), 200

    return jsonify(Post.to_response(item)), 200


validation_schema_slug = {
    'type': 'string',
    'coerce': (str, NormalizerUtils.trim),
    'required': True,
    'empty': False,
    'maxlength': 128,
    'regex': r'^[0-9a-zA-Z_\-]+$',
}


def validation_schema_post_get():
    return {
        'slug': validation_schema_slug,
        'token': {
            'type': 'string',
            'coerce': (NormalizerUtils.trim),
            'required': False,
            'nullable': True,
            'empty': True,
            'regex': r'^[0-9a-fA-F]+$',
        },
    }


def validation_schema_posts_get():
    return {
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
        'withCategory': {
            'type': 'boolean',
            'coerce': (str, NormalizerUtils.to_bool),
            'required': False,
            'empty': True,
            'default': True,
        },
        #'sinceTime': {
        #    'type': 'string',
        #    'coerce': (NormalizerUtils.trim),
        #    'required': False,
        #    'nullable': True,
        #    'empty': True,
        #    'regex': r'\d{4}\-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}([\+\-]\d{2}:\d{2}|Z)$',
        #},
        #'untilTime': {
        #    'type': 'string',
        #    'coerce': (NormalizerUtils.trim),
        #    'required': False,
        #    'nullable': True,
        #    'empty': True,
        #    'regex': r'\d{4}\-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}([\+\-]\d{2}:\d{2}|Z)$',
        #},
        'pagerKey' : {
            'type': 'dict',
            'coerce': (NormalizerUtils.json2dict),
            'required': False,
            'nullable': True,
            'empty': True,
            'schema': {
                'serviceId': {
                    'type': 'string',
                    #'required': True,
                    #'empty': False,
                },
                'postId': {
                    'type': 'string',
                    #'required': True,
                    #'empty': False,
                },
                'tagId': {
                    'type': 'string',
                    #'required': True,
                    #'empty': False,
                },
                'statusPublishAt': {
                    'type': 'string',
                    'required': True,
                    'empty': False,
                    'regex': r'publish#\d{4}\-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}([\+\-]\d{2}:\d{2}|Z)$',
                },
            }
        },
    }


def validation_schema_group_get():
    return {
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
            'default': 'asc',
        },
    }
