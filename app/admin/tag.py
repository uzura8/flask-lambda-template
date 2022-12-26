from flask import jsonify, request
from flask_cognito import cognito_auth_required
from app.models.dynamodb import Tag, Service
from app.common.error import InvalidUsage
from app.common.request import validate_req_params
from app.validators import NormalizerUtils
from app.admin import bp, site_before_request, admin_role_editor_required


@bp.before_request
@site_before_request
def before_request():
    pass


@bp.route('/tags/<string:service_id>', methods=['POST', 'GET'])
@cognito_auth_required
@admin_role_editor_required
def handle_tags(service_id):
    if not Service.check_exists(service_id):
        raise InvalidUsage('ServiceId does not exist', 404)

    if request.method == 'POST':
        vals = validate_req_params(validation_schema(), request.json)
        item = Tag.get_one({
            'p': {'key':'serviceId', 'val':service_id},
            's': {'key':'label', 'val':vals['label']},
        }, False, 'TagsByServiceIdGsi')
        if item:
            raise InvalidUsage('Label already used', 400)

        vals['serviceId'] = service_id
        body = Tag.create(vals, 'tagId')

    else:
        body = Tag.get_all_by_service_id(service_id)

    return jsonify(body), 200


def validation_schema():
    return {
        'label': {
            'type': 'string',
            'coerce': (NormalizerUtils.trim),
            'required': True,
            'empty': False,
            'maxlength': 128,
        },
    }
