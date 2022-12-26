from flask import jsonify, request
from flask_cognito import cognito_auth_required
from app.models.dynamodb import Category, Service
from app.common.error import InvalidUsage
from app.common.request import validate_req_params
from app.validators import NormalizerUtils
from app.admin import bp, site_before_request, admin_role_editor_required


@bp.before_request
@site_before_request
def before_request():
    pass


@bp.route('/categories/<string:service_id>', methods=['POST', 'GET'])
@cognito_auth_required
@admin_role_editor_required
def handle_categories(service_id):
    if not Service.check_exists(service_id):
        raise InvalidUsage('ServiceId does not exist', 404)

    if request.method == 'POST':
        vals = validate_req_params(validation_schema(), request.json)
        item = Category.get_one_by_slug(service_id, vals['slug'])
        if item:
            raise InvalidUsage('Slug already used', 400)

        vals['serviceId'] = service_id
        body = Category.create(vals)

    else:
        body = Category.get_all_by_service_id(service_id)

    return jsonify(body), 200


def validation_schema():
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
    }
