from flask import jsonify, request
from flask_cognito import cognito_auth_required
from app.models.dynamodb import Service, ServiceConfig
from app.common.error import InvalidUsage
from app.common.request import validate_req_params
from app.validators import NormalizerUtils
from app.admin import bp, site_before_request, admin_role_admin_required,\
        check_acl_service_id, admin_role_editor_required


@bp.before_request
@site_before_request
def before_request():
    pass


@bp.route('/services', methods=['POST', 'GET'])
@cognito_auth_required
@admin_role_admin_required
def service_list():
    services = Service.scan()
    services = sorted(services, key=lambda x: x['serviceId'])
    if request.method == 'POST':
        vals = validate_req_params(validation_schema_services(), request.json)
        if next((x for x in services if x['serviceId'] == vals['serviceId']), None):
            raise InvalidUsage('ServiceId already used', 400)

        configs = None
        if 'configs' in vals:
            configs = vals.pop('configs')

        service = Service.create(vals)

        if configs is not None and any(configs):
            for name, val in configs.items():
                ServiceConfig.save(service.serviceId, name, val)

        service['configs'] = ServiceConfig.get_all_by_service(service.serviceId, True, True, True)
        return jsonify(service), 200

    return jsonify(services), 200


@bp.route('/services/<string:service_id>', methods=['POST', 'GET'])
@cognito_auth_required
@admin_role_editor_required
def service_detail(service_id):
    service = check_acl_service_id(service_id, True)

    if request.method == 'POST':
        alloweds = ['label', 'functions', 'configs']
        vals = validate_req_params(validation_schema_services(), request.json, alloweds)
        configs = None
        if 'configs' in vals:
            configs = vals.pop('configs')

        key = {'p': {'key':'serviceId', 'val':service_id}}
        service = Service.update(key, vals, True)

        if configs is not None and any(configs):
            for name, val in configs.items():
                ServiceConfig.save(service_id, name, val)

    service['configs'] = ServiceConfig.get_all_by_service(service_id, True, True, True)
    return jsonify(service), 200


def validation_schema_services():
    return {
        'serviceId': {
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
        'functions': {
            'type': 'list',
            'required': False,
            'empty': True,
            'default': [],
            'allowed': Service.allowed_functions
        },
        'body': {
            'type': 'string',
            'coerce': (NormalizerUtils.rtrim),
            'required': False,
            'nullable': True,
            'empty': True,
            'default': '',
        },
        'configs' : {
            'type': 'dict',
            'required': False,
            'empty': True,
            'nullable': True,
            'schema': {
                'outerSiteUrl': {
                    'type': 'string',
                    'coerce': (NormalizerUtils.trim),
                    'valid_url': True,
                    'required': False,
                    'nullable': True,
                    'empty': True,
                    'default': '',
                },
                'frontendPostDetailUrlPrefix': {
                    'type': 'string',
                    'coerce': (NormalizerUtils.trim),
                    'valid_url': True,
                    'required': False,
                    'nullable': True,
                    'empty': True,
                    'default': '',
                },
                'mediaUploadAcceptMimetypesImage': {
                    'type': 'list',
                    'coerce': (NormalizerUtils.split),
                    'required': False,
                    'empty': True,
                    'default': [],
                    'schema': {
                        'type': 'string',
                        'required': False,
                        'empty': True,
                        'regex': r'^[0-9a-z_\-]+/[0-9a-z_\-]+$',
                    }
                },
                'mediaUploadImageSizes': {
                    'type': 'list',
                    'coerce': (NormalizerUtils.split),
                    'required': False,
                    'empty': True,
                    'default': [],
                    'schema': {
                        'type': 'string',
                        'required': False,
                        'empty': True,
                        'regex': r'^[0-9]+x[0-9]+(x[a-z]{1})?$',
                    }
                },
                'mediaUploadSizeLimitMBImage': {
                    'type': 'integer',
                    'coerce': int,
                    'required': False,
                    'empty': True,
                    'min': 1,
                    'max': 50,
                    'default': 5,
                },
                'mediaUploadAcceptMimetypesFile': {
                    'type': 'list',
                    'coerce': (NormalizerUtils.split),
                    'required': False,
                    'empty': True,
                    'default': [],
                    'schema': {
                        'type': 'string',
                        'required': False,
                        'empty': True,
                        'regex': r'^[0-9a-z_\-]+/[0-9a-z_\-]+$',
                    }
                },
                'mediaUploadSizeLimitMBFile': {
                    'type': 'integer',
                    'coerce': int,
                    'required': False,
                    'empty': True,
                    'min': 1,
                    'max': 50,
                    'default': 5,
                },
                'jumpPageUrl': {
                    'type': 'string',
                    'coerce': (NormalizerUtils.trim),
                    'valid_url': True,
                    'required': False,
                    'empty': True,
                    'nullable': True,
                },
                'jumpPageParamKey': {
                    'type': 'string',
                    'coerce': (NormalizerUtils.trim),
                    'required': False,
                    'empty': True,
                    'nullable': True,
                },
                'analysisParamKeyDefault': {
                    'type': 'string',
                    'coerce': (NormalizerUtils.trim),
                    'required': False,
                    'empty': True,
                    'nullable': True,
                },
            }
        },
    }
