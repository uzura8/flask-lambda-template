import json
import traceback
from flask import jsonify, request
from flask_cognito import cognito_auth_required, current_cognito_jwt
from app.models.dynamodb import Post, Tag, Category, PostTag, File, PostGroup, ModelInvalidParamsException
from app.common.site import media_accept_mimetypes
from app.common.error import InvalidUsage
from app.common.request import validate_req_params
from app.common.string import validate_uuid
from app.validators import NormalizerUtils
from app.admin import bp, site_before_request, check_acl_service_id, admin_role_editor_required


@bp.before_request
@site_before_request
def before_request():
    pass


@bp.route('/posts/<string:service_id>', methods=['POST', 'GET'])
@cognito_auth_required
@admin_role_editor_required
def post_list(service_id):
    service = check_acl_service_id(service_id, True)

    post = None
    if request.method == 'POST':
        schema = validation_schema_posts_post(service['configs'])
        vals = validate_req_params(schema, request.json)
        vals['serviceId'] = service_id
        created_by = current_cognito_jwt.get('cognito:username', '')
        if created_by:
            vals['createdBy'] = created_by

        try:
            post = Post.create(vals)

        except ModelInvalidParamsException as e:
            raise InvalidUsage(e.message, 400)

        except Exception as e:
            print(traceback.format_exc())
            raise InvalidUsage('Server Error', 500)

        tags = []
        if vals.get('tags', []):
            try:
                res = update_post_tags(post, vals['tags'])
                if res.get('current_ids'):
                    keys = []
                    for tag_id in res['current_ids']:
                        keys.append({'tagId':tag_id})
                    tags = Tag.batch_get_items(keys)

            except ModelInvalidParamsException as e:
                raise InvalidUsage(e.message, 400)

            except Exception as e:
                print(traceback.format_exc())
                raise InvalidUsage('Server Error', 500)
        post['tags'] = tags

    else:
        params = {}
        for key in ['count', 'sort', 'order', 'filters', 'category', 'pagerKey']:
            params[key] = request.args.get(key)
        vals = validate_req_params(validation_schema_posts_get(), params)

        filter_conds = {}
        if vals.get('filters'):
            filter_conds['filters'] = vals['filters']

        cate_slug = vals.get('category')
        cate = None
        if cate_slug:
            cate = Category.get_one_by_slug(service_id, cate_slug, False, True, False, False)
            if not cate:
                raise InvalidUsage('Category does not exist', 404)

        if cate:
            cate_slugs = [cate['slug']]
            if cate['children']:
                for c in cate['children']:
                    cate_slugs.append(c['slug'])
            filter_conds['cate_slugs'] = cate_slugs

        if vals['sort'] == 'publishAt':
            index = 'publishAtGsi'
            index_skey = 'publishAt'
        else:
            index = 'createdAtGsi'
            index_skey = 'createdAt'

        if vals.get('pagerKey'):
            vals['ExclusiveStartKey'] = vals['pagerKey']

        pkeys = {'key':'serviceId', 'val':service_id}
        pager_keys = {'pkey':'postId', 'index_pkey':'serviceId', 'index_skey':index_skey}
        post = Post.query_pager_admin(pkeys, vals, pager_keys, index, filter_conds)

    return jsonify(post), 200


@bp.route('/posts/<string:service_id>/slug', methods=['GET'])
@cognito_auth_required
@admin_role_editor_required
def slug_util(service_id):
    check_acl_service_id(service_id)
    params = {'slug':request.args.get('slug')}
    vals = validate_req_params(validation_schema_posts_get(), params)
    post = Post.get_one_by_slug(service_id, vals['slug'])
    is_not_exists = not post
    return jsonify(is_not_exists), 200


@bp.route('/posts/<string:service_id>/<string:identifer>', methods=['POST', 'GET', 'HEAD', 'DELETE'])
@cognito_auth_required
@admin_role_editor_required
def post_detail(service_id, identifer):
    service = check_acl_service_id(service_id, True)
    post = get_post_by_identifer(service_id, identifer)
    post_id = post['postId']

    saved = None
    if request.method == 'POST':
        schema = validation_schema_posts_post(service['configs'])
        vals = validate_req_params(schema, request.json)
        vals['serviceId'] = service_id
        vals['updatedBy'] = current_cognito_jwt.get('cognito:username', '')

        try:
            res = Post.update(post_id, vals)
            saved = res['item']
            is_upd_status_publish_at = res['is_updated_index']

        except ModelInvalidParamsException as e:
            raise InvalidUsage(e.message, 400)

        except Exception as e:
            print(traceback.format_exc())
            raise InvalidUsage('Server Error', 500)

        if not saved:
            saved = post

        tags = []
        if vals.get('tags', []):
            try:
                res = update_post_tags(saved, vals['tags'], is_upd_status_publish_at)
                if res.get('current_ids'):
                    keys = []
                    for tag_id in res['current_ids']:
                        keys.append({'tagId':tag_id})
                    tags = Tag.batch_get_items(keys)

            except ModelInvalidParamsException as e:
                raise InvalidUsage(e.message, 400)

            except Exception as e:
                print(traceback.format_exc())
                raise InvalidUsage('Server Error', 500)

        else:
            try:
                post_tags = PostTag.get_all_by_post_id(post['postId'], False, False)
                if post_tags:
                    del_tags = [ {'tagId':pt['tagId'],'postId':pt['postId']} for pt in post_tags ]
                    PostTag.batch_delete(del_tags)

            except ModelInvalidParamsException as e:
                raise InvalidUsage(e.message, 400)

            except Exception as e:
                print(traceback.format_exc())
                raise InvalidUsage('Server Error', 500)

        saved['tags'] = tags

    elif request.method == 'DELETE':
        if post.get('tags'):
            try:
                del_tags = [ {'tagId':tag['tagId'],'postId':post['postId']} for tag in post['tags'] ]
                PostTag.batch_delete(del_tags)

            except ModelInvalidParamsException as e:
                raise InvalidUsage(e.message, 400)

            except Exception as e:
                print(traceback.format_exc())
                raise InvalidUsage('Server Error', 500)

        if post.get('images'):
            try:
                del_img_fids = [ i['fileId'] for i in post['images'] ]
                File.bulk_update_status(del_img_fids, 'removed')

            except ModelInvalidParamsException as e:
                raise InvalidUsage(e.message, 400)

            except Exception as e:
                print(traceback.format_exc())
                raise InvalidUsage('Server Error', 500)


        if post.get('files'):
            try:
                del_file_fids = [ i['fileId'] for i in post['files'] ]
                File.bulk_update_status(del_file_fids, 'removed')

            except ModelInvalidParamsException as e:
                raise InvalidUsage(e.message, 400)

            except Exception as e:
                print(traceback.format_exc())
                raise InvalidUsage('Server Error', 500)

        try:
            PostGroup.delete_post_id_for_all_items(service_id, post['postId'])
            Post.delete({'postId':post_id})
            return jsonify(), 200

        except ModelInvalidParamsException as e:
            raise InvalidUsage(e.message, 400)

        except Exception as e:
            print(traceback.format_exc())
            raise InvalidUsage('Server Error', 500)

    if request.method == 'HEAD':
        return jsonify(), 200

    res = saved if saved else post
    res['service'] = service

    return jsonify(res), 200


@bp.route('/posts/<string:service_id>/<string:identifer>/status', methods=['POST'])
@cognito_auth_required
@admin_role_editor_required
def post_status(service_id, identifer):
    service = check_acl_service_id(service_id)
    saved = get_post_by_identifer(service_id, identifer)
    post_id = saved['postId']
    tags = saved['tags']

    if not saved:
        raise InvalidUsage('Not Found', 404)

    if saved['serviceId'] != service_id:
        raise InvalidUsage('serviceId is invalid', 400)

    schema = validation_schema_posts_post_status()
    vals = validate_req_params(schema, request.json)
    vals['serviceId'] = service_id

    if vals['status'] == saved['postStatus']:
        raise InvalidUsage('Status is same value', 400)

    try:
        res = Post.update(post_id, vals)
        saved = res['item']
        #is_upd_status_publish_at = res['is_updated_index']

    except ModelInvalidParamsException as e:
        raise InvalidUsage(e.message, 400)

    except Exception as e:
        print(traceback.format_exc())
        raise InvalidUsage('Server Error', 500)

    saved['service'] = service
    saved['tags'] = tags
    update_post_tags_status_publish_at(saved['postId'], saved['statusPublishAt'],
                                        saved['publishAt'])
    return jsonify(saved), 200


def get_post_by_identifer(service_id, identifer):
    is_uuid = validate_uuid(identifer)
    if is_uuid:
        post = Post.get_one_by_id(identifer, True, False)
    else:
        post = Post.get_one_by_slug(service_id, identifer, True, False)

    if not post:
        raise InvalidUsage('Not Found', 404)

    if is_uuid and post['serviceId'] != service_id:
        raise InvalidUsage('PostId is invalid', 400)

    return post


def update_post_tags_status_publish_at(post_id, status_publish_at, publish_at):
    post_tags = PostTag.get_all_by_pkey({'key':'postId', 'val':post_id})
    if not post_tags:
        return None

    vals = []
    for post_tag in post_tags:
        vals.append({
            'postId': post_id,
            'tagId': post_tag['tagId'],
            'statusPublishAt': status_publish_at,
            'publishAt': publish_at,
        })
    PostTag.batch_save(vals, ['postId', 'tagId'], True)
    return {
        'current_ids': [ val['tagId'] for val in vals ]
    }


def update_post_tags(post, req_tags, is_update_status_publish_at=False):
    # If set is_update_status_publish_at, only for update PostTag records
    service_id = post['serviceId']
    upd_tag_ids = [] # For PostTag table to update
    del_tag_ids = [] # For PostTag table to delete
    add_tag_ids = [] # For PostTag table to add

    new_tag_labels = []
    for req_tag in req_tags:
        # If saved already, requested as tagId
        if req_tag.get('tagId'):
            upd_tag_ids.append(req_tag['tagId'])

        # If not saved, requested as tagLabel
        elif req_tag.get('label'):
            new_tag_labels.append(req_tag['label'])

    # If exists new requested tags, create new records in Tag table at first
    if new_tag_labels:
        exist_tags = Tag.get_all_by_service_id(service_id)
        exist_tag_labels = [ d.get('label') for d in exist_tags ]
        for ntl in new_tag_labels:
            # If already saved, not create record of Tag table
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
        return {'del_ids':del_tag_ids, 'current_ids':[]}

    # Following is only for update PostTag records
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
            'publishAt': post['publishAt'],
        })
    PostTag.batch_save(save_tags, pkeys, is_update_status_publish_at)
    return {
        'del_tag_ids':del_tag_ids,
        'save_tag_ids':save_tag_ids,
        'current_ids':upd_tag_ids
    }


schema_slug = {
    'type': 'string',
    'coerce': (str, NormalizerUtils.trim),
    'required': True,
    'empty': False,
    'maxlength': 128,
    'regex': r'^[0-9a-z\-]+$',
    'valid_ulid': False,
}
schema_status = {
    'type': 'string',
    'required': False,
    'allowed': ['publish', 'unpublish'],
    'nullable': True,
    'empty': True,
    'default': 'unpublish',
}


def validation_schema_posts_post(service_configs=None):
    return {
        'slug': schema_slug,
        'title': {
            'type': 'string',
            'coerce': (NormalizerUtils.trim),
            'required': True,
            'empty': False,
        },
        'bodyFormat': {
            'type': 'string',
            'coerce': (NormalizerUtils.trim),
            'required': True,
            'empty': False,
            'allowed': ['html', 'text', 'markdown'],
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
        'status': schema_status,
        'publishAt': {
            'type': 'string',
            'coerce': (NormalizerUtils.trim),
            'required': False,
            'empty': True,
            'regex': r'\d{4}\-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}([\+\-]\d{2}:\d{2}|Z)$',
        },
        'isHiddenInList': {
            'type': 'boolean',
            'coerce': (str, NormalizerUtils.to_bool),
            'required': False,
            'empty': False,
            'default': False,
        },
        'images' : {
            'type': 'list',
            'schema': {
                'type': 'dict',
                'maxlength': 5,
                'schema': {
                    'fileId': {
                        'type':'string',
                        'coerce': (NormalizerUtils.trim),
                        'required': True,
                        'empty': False,
                        'regex': r'^[0-9a-z\-]{26}$',
                    },
                    'mimeType': {
                        'type':'string',
                        'coerce': (NormalizerUtils.trim),
                        'required': True,
                        'empty': False,
                        'allowed': media_accept_mimetypes('image', service_configs),
                    },
                    'caption': {
                        'type':'string',
                        'coerce': (NormalizerUtils.trim),
                        'required': False,
                        'empty': True,
                    },
                }
            }
        },
        'files' : {
            'type': 'list',
            'schema': {
                'type': 'dict',
                'maxlength': 5,
                'schema': {
                    'fileId': {
                        'type':'string',
                        'coerce': (NormalizerUtils.trim),
                        'required': True,
                        'empty': False,
                        'regex': r'^[0-9a-z\-]{26}$',
                    },
                    'mimeType': {
                        'type':'string',
                        'coerce': (NormalizerUtils.trim),
                        'required': True,
                        'empty': False,
                        'allowed': media_accept_mimetypes('file', service_configs),
                    },
                    'caption': {
                        'type':'string',
                        'coerce': (NormalizerUtils.trim),
                        'required': False,
                        'empty': True,
                    },
                }
            }
        },
        'links' : {
            'type': 'list',
            'schema': {
                'type': 'dict',
                'maxlength': 10,
                'schema': {
                    'url': {
                        'type':'string',
                        'coerce': (NormalizerUtils.trim),
                        'required': True,
                        'empty': False,
                        'valid_url': True,
                    },
                    'label': {
                        'type':'string',
                        'coerce': (NormalizerUtils.trim),
                        'required': False,
                        'empty': True,
                    },
                    'id': {
                        'type': 'integer',
                        'coerce': int,
                        'required': True,
                        'min': 1,
                    },
                }
            }
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
        }
    }


def validation_schema_posts_get():
    return {
        'slug': schema_slug,
        'count': {
            'type': 'integer',
            'coerce': int,
            'required': False,
            'min': 1,
            'max': 50,
            'default': 20,
        },
        'sort': {
            'type': 'string',
            'required': False,
            'allowed': ['createdAt', 'publishAt'],
            'default': 'createdAt',
        },
        'order': {
            'type': 'string',
            'required': False,
            'allowed': ['asc', 'desc'],
            'default': 'desc',
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
        'withCategory': {
            'type': 'boolean',
            'coerce': (str, NormalizerUtils.to_bool),
            'required': False,
            'empty': True,
            'default': True,
        },
        'category': {
            'type': 'string',
            'coerce': (NormalizerUtils.trim),
            'nullable': True,
            'required': False,
            'empty': True,
        },
        'filters' : {
            'type': 'dict',
            'required': False,
            'empty': True,
            'nullable': True,
            'coerce': (NormalizerUtils.json2dict),
            'schema': {
                'attribute': {
                    'type': 'string',
                    'allowed': ['slug', 'title', 'body'],
                    'required': True,
                    'empty': False,
                },
                'compare': {
                    'type': 'string',
                    'allowed': ['eq', 'contains'],
                    'required': True,
                    'empty': False,
                },
                'value': {
                    'type': 'string',
                    'required': False,
                    'empty': True,
                    'default': '',
                },
            }
        },
        'pagerKey' : {
            'type': 'dict',
            'required': False,
            'empty': True,
            'nullable': True,
            'coerce': (NormalizerUtils.json2dict),
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
                    'required': False,
                    'empty': True,
                    'regex': r'\d{4}\-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}([\+\-]\d{2}:\d{2}|Z)$',
                },
                'publishAt': {
                    'type': 'string',
                    'required': False,
                    'empty': True,
                    'regex': r'((\d{4}\-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}([\+\-]\d{2}:\d{2}|Z))|None)$',
                },
            }
        },
    }


def validation_schema_posts_post_status():
    return {
        'status': schema_status,
    }
