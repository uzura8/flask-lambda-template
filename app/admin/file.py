import json
import os
import boto3
from botocore.client import Config
from flask import jsonify, request
from flask_cognito import cognito_auth_required, current_cognito_jwt
from app.models.dynamodb import File, ModelInvalidParamsException
from app.common.error import InvalidUsage
from app.common.request import validate_req_params
from app.common.media import get_ext_by_mimetype
from app.validators import NormalizerUtils
from app.admin import bp, site_before_request, check_acl_service_id

MEDIA_S3_BUCKET_NAME = os.environ.get('MEDIA_S3_BUCKET_NAME', '')
MEDIA_ACCEPT_MIMETYPES = json.loads(os.environ.get('MEDIA_ACCEPT_MIMETYPES', ''))
s3_clident = boto3.client('s3', config=Config(signature_version='s3v4'))


@bp.before_request
@site_before_request
def before_request():
    pass


@bp.route('/files/<string:service_id>', methods=['POST'])
@cognito_auth_required
def create_pre_signed_url(service_id):
    check_acl_service_id(service_id)

    file_type = request.json.get('fileType')
    if not file_type or file_type not in ['image', 'file']:
        raise InvalidUsage('fileType is invalid', 400)

    schema = validation_schema_files()
    allowed_mimetype = MEDIA_ACCEPT_MIMETYPES.get(file_type, [])
    if allowed_mimetype:
        schema['mimeType']['allowed'] = allowed_mimetype

    vals = validate_req_params(schema, request.json)
    vals['serviceId'] = service_id
    vals['fileStatus'] = 'reserved'
    vals['createdBy'] = current_cognito_jwt.get('cognito:username', '')
    try:
        file = File.create(vals)

    except ModelInvalidParamsException as e:
        raise InvalidUsage(e.message, 400)

    except Exception as e:
        raise InvalidUsage('Server Error', 500)

    bucket_key = generate_s3_key(file)
    pre_signed_url = s3_clident.generate_presigned_url(
        ClientMethod = 'put_object',
        Params = {'Bucket':MEDIA_S3_BUCKET_NAME, 'Key':bucket_key},
        ExpiresIn = 30,
        HttpMethod = 'PUT'
    )
    res = File.to_response(file)
    res['url'] = pre_signed_url
    return jsonify(res), 200


@bp.route('/files/<string:service_id>/<string:file_id>', methods=['GET', 'DELETE'])
@cognito_auth_required
def file_detail(service_id, file_id):
    check_acl_service_id(service_id)
    query_keys = {'p': {'key':'fileId', 'val':file_id}}
    file = File.get_one(query_keys)
    if not file:
        raise InvalidUsage('Not Found', 404)

    if request.method == 'DELETE':
        query_keys = {'p': {'key':'fileId', 'val':file_id}}
        upd_vals = {'fileStatus':'removed'}
        file = File.update(query_keys, upd_vals, True)

    return jsonify(File.to_response(file)), 200


def generate_s3_key(vals, size='raw'):
    ext = get_ext_by_mimetype(vals['mimeType'])
    if vals['fileType'] == 'image':
        params = (vals['serviceId'], vals['fileId'], size, ext)
        key = '%s/images/%s/%s.%s' % params
    else:
        params = (vals['serviceId'], vals['fileId'], ext)
        key = '%s/docs/%s.%s' % params
    return key


def validation_schema_files():
    return {
        'fileId': {
            'type':'string',
            'coerce': (NormalizerUtils.trim),
            'required': False,
            'empty': True,
            'regex': r'^[0-9a-z\-]{26}$',
        },
        'fileType': {
            'type': 'string',
            'coerce': (NormalizerUtils.trim),
            'required': True,
            'empty': False,
            'allowed': ['image', 'file'],
        },
        'fileStatus': {
            'type': 'string',
            'coerce': (NormalizerUtils.trim),
            'required': True,
            'empty': False,
            'allowed': ['reserved', 'removed', 'published'],
        },
        'mimeType': {
            'type': 'string',
            'coerce': (NormalizerUtils.trim),
            'required': True,
            'nullable': False,
            'empty': False,
        },
        'name': {
            'type': 'string',
            'coerce': (NormalizerUtils.trim),
            'required': True,
            'empty': False,
            'maxlength': 128,
        },
        'size': {
            'type': 'integer',
            'coerce': int,
        },
    }
