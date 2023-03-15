import os
from flask import Blueprint, jsonify, request
from app.models.dynamodb import Category, Service
from app.common.error import InvalidUsage
from app.common.request import validate_req_params
from app.validators import NormalizerUtils

bp = Blueprint('category', __name__, url_prefix='/categories')


@bp.route('/<string:service_id>', methods=['GET'])
def handle_list(service_id):
    if not Service.check_exists(service_id):
        raise InvalidUsage('ServiceId does not exist', 404)

    vals = validate_req_params(validation_schema_list_get(), request.args)
    is_nested = not vals.get('isList')
    body = Category.get_all_by_service_id(service_id, True, is_nested)
    return jsonify(body), 200


@bp.route('/<string:service_id>/<string:slug>', methods=['GET', 'HEAD'])
def handle_detail(service_id, slug):
    if not Service.check_exists(service_id):
        raise InvalidUsage('ServiceId does not exist', 404)

    params = {'slug':slug}
    if request.method == 'GET':
        for key in ['withParents', 'withChildren']:
            params[key] = request.args.get(key)

    vals = validate_req_params(validation_schema_detail_get(), params)
    item = Category.get_one_by_slug(service_id, vals['slug'],
                                vals['withParents'], vals['withChildren'], True)
    if not item:
        item = []
        #raise InvalidUsage('Not Found', 404)

    if request.method == 'HEAD':
        return jsonify(), 200

    return jsonify(item), 200


@bp.route('/<string:service_id>/<string:slug>/children', methods=['GET'])
def handle_detail_childlen(service_id, slug):
    if not Service.check_exists(service_id):
        raise InvalidUsage('ServiceId does not exist', 404)

    parent = Category.get_one_by_slug(service_id, slug, False, False, True, False)
    if not parent:
        raise InvalidUsage('Not Found', 404)

    parent_path = '#'.join([parent['parentPath'], str(parent['id'])])
    items = Category.get_children_by_parent_path(service_id, parent_path, False, True, False)
    if not items:
        items = []

    return jsonify(items), 200


def validation_schema_detail_get():
    return {
        'slug': {
            'type': 'string',
            'coerce': (str, NormalizerUtils.trim),
            'required': True,
            'empty': False,
            'maxlength': 128,
            'regex': r'^[0-9a-z\-]+$',
        },
        'label': {
            'type': 'string',
            'coerce': (NormalizerUtils.trim),
            'required': True,
            'empty': False,
        },
        'parentId': {
            'type': 'integer',
            'coerce': int,
            'required': True,
            'nullable': False,
            'empty': False,
        },
        'withParents': {
            'type': 'boolean',
            'coerce': (str, NormalizerUtils.to_bool),
            'required': False,
            'empty': True,
            'default': False,
        },
        'withChildren': {
            'type': 'boolean',
            'coerce': (str, NormalizerUtils.to_bool),
            'required': False,
            'empty': True,
            'default': False,
        },
    }


def validation_schema_list_get():
    return {
        'isList': {
            'type': 'boolean',
            'coerce': (str, NormalizerUtils.to_bool),
            'required': False,
            'empty': True,
            'default': False,
        },
    }
