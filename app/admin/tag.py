from flask import jsonify, request
from app.models.dynamodb import Tag
from app.common.error import InvalidUsage
from app.common.request import validate_req_params
from app.validators import NormalizerUtils
from app.admin import bp, site_before_request, ACCEPT_SERVICE_IDS
from flask_cognito import cognito_auth_required, current_user, current_cognito_jwt


@bp.before_request
@site_before_request
def before_request():
    pass


@bp.route('/tags/<string:service_id>', methods=['POST', 'GET'])
@cognito_auth_required
def handle_tags(service_id):
    if service_id not in ACCEPT_SERVICE_IDS:
        raise InvalidUsage('ServiceId does not exist', 404)

    if request.method == 'POST':
        vals = validate_req_params(validation_schema(), request.json)
        item = Tag.get_one({
            'p': {'key':'serviceId', 'val':service_id},
            's': {'key':'slug', 'val':vals['slug']},
        })
        if item:
            raise InvalidUsage('Slug already used', 400)

        vals['serviceId'] = service_id
        body = Tag.create(vals)

    else:
        body = Tag.get_all_by_service_id(service_id)

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
    }
