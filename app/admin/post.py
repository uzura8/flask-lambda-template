import json
from flask import jsonify, request
from app.models.dynamodb import Post, Category, Tag, PostTag
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
def post_list(service_id):
    if service_id not in ACCEPT_SERVICE_IDS:
        raise InvalidUsage('ServiceId does not exist', 404)

    post = None
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
        post = Post.create(vals)

        tags = []
        if vals.get('tags', []):
            res = update_post_tags(service_id, post, vals['tags'])
            if res.get('current_ids'):
                keys = []
                for tag_id in res['current_ids']:
                    keys.append({'tagId':tag_id})
                tags = Tag.batch_get_items(keys)
        post['tags'] = tags

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
        post = Post.query_pager(hkey, vals, True)

    return jsonify(post), 200


@bp.route('/posts/<string:service_id>/<string:post_id>', methods=['POST', 'GET', 'HEAD', 'DELETE'])
def post_detail(service_id, post_id):
    if service_id not in ACCEPT_SERVICE_IDS:
        raise InvalidUsage('ServiceId does not exist', 404)

    post = Post.get_one_by_id(post_id, True)
    if not post:
        raise InvalidUsage('Not Found', 404)

    if post['serviceId'] != service_id:
        raise InvalidUsage('serviceId is invalid', 400)

    saved = None
    if request.method == 'POST':
        schema = validation_schema_posts_post()
        vals = validate_req_params(schema, request.json)
        saved = Post.update(service_id, post_id, vals)

        is_upd_status_publish_at = False
        if not saved:
            saved = post
        else:
            if saved['publishAt'] != post['publishAt']\
                    or saved['postStatus'] != post['postStatus']:
                is_upd_status_publish_at = True

        tags = []
        if vals.get('tags', []):
            res = update_post_tags(service_id, saved, vals['tags'], is_upd_status_publish_at)
            if res.get('current_ids'):
                keys = []
                for tag_id in res['current_ids']:
                    keys.append({'tagId':tag_id})
                tags = Tag.batch_get_items(keys)
        saved['tags'] = tags

    elif request.method == 'DELETE':
        if post.get('tags'):
            del_tags = [ {'tagId':tag['tagId'],'postId':post['postId']} for tag in post['tags'] ]
            PostTag.batch_delete(del_tags)

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

    saved = Post.get_one_by_id(post_id, True)
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
    update_post_tags_status_publish_at(saved['postId'], saved['statusPublishAt'])
    return jsonify(saved), 200


def update_post_tags_status_publish_at(post_id, status_publish_at):
    post_tags = PostTag.get_all_by_pkey({'key':'postId', 'val':post_id})
    if not post_tags:
        return

    vals = []
    for post_tag in post_tags:
        vals.append({
            'postId': post_id,
            'tagId': post_tag['tagId'],
            'statusPublishAt': status_publish_at,
        })
    PostTag.batch_save(vals, ['postId', 'tagId'], True)
    return {
        'current_ids': [ val['tagId'] for val in vals ]
    }


def update_post_tags(service_id, post, req_tags, is_update_status_publish_at=False):
    new_tag_labels = []
    upd_tag_ids = []
    for req_tag in req_tags:
        if req_tag.get('tagId'):
            upd_tag_ids.append(req_tag['tagId'])
        elif req_tag.get('label'):
            new_tag_labels.append(req_tag['label'])

    if new_tag_labels:
        exist_tags = Tag.get_all_by_service_id(service_id)
        exist_tag_labels = [ d.get('label') for d in exist_tags ]
        for ntl in new_tag_labels:
            if ntl in exist_tag_labels:
                tag_id = [ d['tagId'] for d in exist_tags if d['label'] == ntl ][0]
                upd_tag_ids.append(tag_id)
            else:
                tag_vals ={
                    'serviceId': service_id,
                    'label': ntl,
                }
                new_tag = Tag.create(tag_vals, 'tagId')
                upd_tag_ids.append(new_tag['tagId'])

    del_tag_ids = []
    add_tag_ids = []
    saved_post_tags = PostTag.get_all_by_pkey({'key':'postId', 'val':post['postId']})
    if saved_post_tags:
        saved_tag_ids = [ d['tagId'] for d in saved_post_tags ]
        if not is_update_status_publish_at and set(upd_tag_ids) == set(saved_tag_ids):
            return {'current_ids':upd_tag_ids}

        del_tag_ids = set(saved_tag_ids) - set(upd_tag_ids)
        add_tag_ids = set(upd_tag_ids) - set(saved_tag_ids)
    else:
        add_tag_ids = upd_tag_ids

    if del_tag_ids:
        del_tags = [ {'tagId':tid,'postId':post['postId']} for tid in del_tag_ids ]
        PostTag.batch_delete(del_tags)

    if not upd_tag_ids:
        return {'del_ids':del_tag_ids, 'current_ids':upd_tag_ids}

    if is_update_status_publish_at:
        save_tag_ids = upd_tag_ids
        pkeys = ['postId', 'tagId']
    else:
        save_tag_ids = add_tag_ids
        pkeys = []

    save_tags = []
    for save_tag_id in save_tag_ids:
        save_tags.append({
            'postId': post['postId'],
            'tagId': save_tag_id,
            'statusPublishAt': post['statusPublishAt'],
        })
    PostTag.batch_save(save_tags, pkeys, is_update_status_publish_at)
    return {
        'del_tag_ids':del_tag_ids,
        'save_tag_ids':save_tag_ids,
        'current_ids':upd_tag_ids
    }



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
        'tags' : {
            'type': 'list',
             'schema': {
                 'type': 'dict',
                 'maxlength': 30,
                 'schema':{
                     'label': {
                         'type':'string',
                         'required':False
                     },
                     'tagId': {
                         'type':'string',
                         'required':False
                     }
                 }
            }
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
