import json
import os
from datetime import datetime
import boto3
from flask import jsonify, request
from flask_cognito import cognito_auth_required
from app.validators import NormalizerUtils
from app.common.request import validate_req_params
from app.common.error import InvalidUsage
from app.admin import bp, site_before_request, admin_role_admin_required

COGNITO_REGION = os.environ.get('COGNITO_REGION', '')
COGNITO_USERPOOL_ID = os.environ.get('COGNITO_USERPOOL_ID', '')

cognito = boto3.client('cognito-idp', COGNITO_REGION)


@bp.before_request
@site_before_request
def before_request():
    pass


@bp.route('/users', methods=['GET'])
@cognito_auth_required
@admin_role_admin_required
def user_list():
    res = cognito.list_users(
        UserPoolId = COGNITO_USERPOOL_ID
    )
    users = [ user_to_dict_for_response(u) for u in res.get('Users', []) ]
    return json.dumps(users, default=support_datetime_default), 200


@bp.route('/users/<string:username>', methods=['GET', 'POST'])
@cognito_auth_required
@admin_role_admin_required
def user_detail(username):
    if request.method == 'POST':
        schema = validation_schema_users_post()
        vals = validate_req_params(schema, request.json)
        attr = {'Name':'custom:acceptServiceIds', 'Value':','.join(vals['serviceIds'])}
        try:
            res = cognito.admin_update_user_attributes(
                UserPoolId = COGNITO_USERPOOL_ID,
                Username=username,
                UserAttributes=[attr]
            )
        except cognito.exceptions.UserNotFoundException:
            raise InvalidUsage('User does not exist', 404)

        if res['ResponseMetadata']['HTTPStatusCode'] != 200:
            raise InvalidUsage('Failed update user', 500)

        return jsonify({'message': 'Update success'}), 200

    try:
        res = cognito.admin_get_user(
            UserPoolId = COGNITO_USERPOOL_ID,
            Username=username
        )
    except cognito.exceptions.UserNotFoundException:
        raise InvalidUsage('User does not exist', 404)

    user = user_to_dict_for_response(res)
    return json.dumps(user, default=support_datetime_default), 200


def user_to_dict_for_response(coguser):
    cog_attrs = coguser['Attributes'] if 'Attributes' in coguser else coguser['UserAttributes']
    attrs = { i['Name']:i['Value'] for i in cog_attrs }
    sids_str = attrs.get('custom:acceptServiceIds', '')
    sids = sids_str.split(',') if sids_str else []
    res = {
        'username': coguser.get('Username', ''),
        'email': attrs.get('email', ''),
        'emailVerified': attrs.get('email_verified') == 'true',
        'role': attrs.get('custom:role', 'normal'),
        'acceptServiceIds': sids,
        'enabled': coguser.get('Enabled', False),
        'status': coguser.get('UserStatus', ''),
        'createdAt': coguser.get('UserCreateDate'),
        'updatedAt': coguser.get('UserLastModifiedDate'),
    }
    return res


def support_datetime_default(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(repr(obj) + " is not JSON serializable")


def validation_schema_users_post():
    return {
        'username': {
            'type': 'string',
            'coerce': (NormalizerUtils.trim),
            'required': True,
            'empty': False,
            'maxlength': 128,
            'regex': r'^[0-9a-zA-Z_\-]+$',
        },
        'serviceIds' : {
            'type': 'list',
            'schema': {
                'type': 'string',
                'coerce': (str, NormalizerUtils.trim),
                'maxlength': 128,
                'regex': r'^[0-9a-z\-]+$',
            }
        },
    }
