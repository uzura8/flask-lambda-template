import json
import traceback
from urllib.parse import quote, urlparse
from flask import jsonify, request
from flask_cognito import cognito_auth_required, current_cognito_jwt
from app.models.dynamodb import ShortenUrl, ShortenUrlDomain, ServiceConfig, ModelInvalidParamsException
from app.common.error import InvalidUsage
from app.common.string import random_str
from app.common.request import validate_req_params
from app.common.url import join_query
from app.validators import NormalizerUtils
from app.admin import bp, site_before_request, check_acl_service_id, admin_role_editor_required


@bp.before_request
@site_before_request
def before_request():
    pass


@bp.route('/shorten-urls/<string:service_id>', methods=['POST', 'GET'])
@cognito_auth_required
@admin_role_editor_required
def url_list(service_id):
    check_acl_service_id(service_id)

    if request.method == 'POST':
        schema = validation_schema_url_post()
        vals = validate_req_params(schema, request.json)
        vals['serviceId'] = service_id

        created_by = current_cognito_jwt.get('cognito:username', '')
        if created_by:
            vals['createdBy'] = created_by

        url_id = get_new_url_id()
        if not url_id:
            raise InvalidUsage('Create new url_id failed', 500)
        vals['urlId'] = url_id
        vals['locationTo'] = generate_redirect_url(service_id, vals)

        parsed_url = urlparse(vals.get('url'))
        domain = parsed_url.netloc
        vals['serviceIdDomain'] = f'{service_id}#{domain}'
        vals['domain'] = domain
        try:
            res = ShortenUrl.create(vals)

        except ModelInvalidParamsException as e:
            raise InvalidUsage(e.message, 400)

        except Exception as e:
            print(traceback.format_exc())
            raise InvalidUsage('Server Error', 500)

        # If not exists in domains table, add domain
        check_not_exists_and_create_domain_item(service_id, domain)

    else:
        params = {}
        for key in ['count', 'order']:
            params[key] = request.args.get(key)
        vals = validate_req_params(validation_schema_url_list_get(), params)
        key_name =  'pagerKey'
        vals['index'] = 'createdAtGsi'
        pager_key = request.args.get('pagerKey')
        if pager_key:
            params = {key_name:json.loads(pager_key)}
            vals_pager_key = validate_req_params(validation_schema_url_list_get(), params)
            vals['ExclusiveStartKey'] = vals_pager_key[key_name]

        hkey = {'name':'serviceId', 'value': service_id}
        res = ShortenUrl.query_pager(hkey, vals)

    return jsonify(res), 200


@bp.route('/shorten-urls/<string:service_id>/<string:url_id>',
          methods=['POST', 'GET', 'HEAD', 'DELETE'])
@cognito_auth_required
@admin_role_editor_required
def url_detail(service_id, url_id):
    validate_req_params(validation_schema_url_id(), {'urlId': url_id})
    query_keys = {'p': {'key':'urlId', 'val':url_id}}
    saved = ShortenUrl.get_one(query_keys)
    if not saved:
        raise InvalidUsage('UrlId does not exist', 404)

    if service_id != saved['serviceId']:
        raise InvalidUsage('ServiceId is invalid', 400)

    check_acl_service_id(saved['serviceId'])

    if request.method == 'POST':
        schema = validation_schema_url_post()
        vals = validate_req_params(schema, request.json)
        vals['updatedBy'] = current_cognito_jwt.get('cognito:username', '')
        vals['locationTo'] = generate_redirect_url(service_id, vals)

        domain_upd = ''
        if vals.get('url'):
            parsed_url = urlparse(vals.get('url'))
            domain_upd = parsed_url.netloc
            vals['serviceIdDomain'] = f'{service_id}#{domain_upd}'
            vals['domain'] = domain_upd

        try:
            updated = ShortenUrl.update(query_keys, vals, True)

        except ModelInvalidParamsException as e:
            raise InvalidUsage(e.message, 400)

        except Exception as e:
            print(traceback.format_exc())
            raise InvalidUsage('Server Error', 500)

        # If updated domain
        if domain_upd and domain_upd != saved['domain']:
            check_exists_in_urls_and_delete_domain(service_id, saved['domain'])

            # If new domain not saved, Add new domain to domains table
            check_not_exists_and_create_domain_item(service_id, domain_upd)

        response = updated

    elif request.method == 'DELETE':
        ShortenUrl.delete({'urlId':url_id})
        check_exists_in_urls_and_delete_domain(service_id, saved['domain'])
        return jsonify(), 204

    elif request.method == 'HEAD':
        return jsonify(), 200

    else:
        response = saved

    return jsonify(response), 200


@bp.route('/shorten-urls/<string:service_id>/domains', methods=['GET'])
@cognito_auth_required
@admin_role_editor_required
def url_domain_list(service_id):
    check_acl_service_id(service_id)
    keys = {'p':{'key':'serviceId', 'val':service_id}}
    domains = ShortenUrlDomain.get_all(keys, False, 'serviceIdIndex')
    return jsonify(domains), 200


def get_new_url_id():
    query_keys = {'p': {'key':'urlId'}}
    url_id = ''
    url = ''
    i = 0
    limit = 10
    while not url_id or (url and i < limit):
        url_id = random_str(10)
        query_keys['p']['val'] = url_id
        url = ShortenUrl.get_one(query_keys)
        i += 1

    return url_id


def generate_redirect_url(service_id, vals):
    service_confs = ServiceConfig.get_all_by_service(service_id, True, True, True)
    url = vals.get('url')
    pkey = vals.get('paramKey')
    pval = vals.get('paramValue')
    via_jump = vals.get('isViaJumpPage')

    add_query = ''
    if pkey and pval:
        add_query = '%s=%s' % (pkey, pval)

    if via_jump:
        has_jump_data = (service_confs\
                and service_confs.get('jumpPageUrl')\
                and service_confs.get('jumpPageParamKey'))
        if not has_jump_data:
            raise InvalidUsage('JumpPage data not exists', 500)

        jump_page = service_confs['jumpPageUrl']
        jump_pkey = service_confs['jumpPageParamKey']

        quoted = quote(url, safe='')
        if add_query:
            add_query += '&'
        add_query += '%s=%s' % (jump_pkey, quoted)
        res = join_query(jump_page, add_query)

    else:
        res = join_query(url, add_query)

    return res


def check_not_exists_and_create_domain_item(service_id, domain):
    # If new domain not saved, Add new domain to domains table
    service_id_domain = f'{service_id}#{domain}'
    query_keys = {'p': {'key':'serviceIdDomain', 'val':service_id_domain}}
    domain_item = ShortenUrlDomain.get_one(query_keys)
    if domain_item:
        return

    vals = {
        'serviceIdDomain': service_id_domain,
        'serviceId': service_id,
        'domain': domain,
    }
    try:
        res = ShortenUrlDomain.create(vals)

    except ModelInvalidParamsException as e:
        raise InvalidUsage(e.message, 400)

    except Exception as e:
        print(traceback.format_exc())
        raise InvalidUsage('Server Error', 500)

    return res



def check_exists_in_urls_and_delete_domain(service_id, domain):
    # If old domain not exits in urls table, delete from domains table
    domain_key = f'{service_id}#{domain}'
    query_keys = {'p': {'key':'serviceIdDomain', 'val':domain_key}}
    url_item = ShortenUrl.get_one(query_keys, False, 'serviceIdDomainIndex')
    if url_item:
        return

    try:
        res_delete_domain = ShortenUrlDomain.delete({'serviceIdDomain':domain_key})

    except ModelInvalidParamsException as e:
        raise InvalidUsage(e.message, 400)

    except Exception as e:
        print(traceback.format_exc())
        raise InvalidUsage('Server Error', 500)


def validation_schema_url_id():
    return {
        'urlId': {
            'type': 'string',
            'coerce': (str, NormalizerUtils.trim),
            'required': True,
            'empty': False,
            'maxlength': 10,
            'regex': r'^[0-9a-zA-Z]{10}$',
        }
    }


def validation_schema_url_post():
    return {
        'url': {
            'type': 'string',
            'coerce': (NormalizerUtils.rtrim),
            'required': True,
            'nullable': False,
            'empty': False,
            'valid_url': True,
        },
        'name': {
            'type': 'string',
            'coerce': (NormalizerUtils.trim),
            'required': False,
            'nullable': True,
            'empty': True,
            'default': '',
        },
        'description': {
            'type': 'string',
            'coerce': (NormalizerUtils.rtrim),
            'required': False,
            'nullable': True,
            'empty': True,
            'default': '',
        },
        'isViaJumpPage': {
            'type': 'boolean',
            'coerce': (str, NormalizerUtils.to_bool),
            'required': False,
            'empty': False,
            'default': False,
        },
        'paramKey': {
            'type': 'string',
            'coerce': (NormalizerUtils.trim),
            'required': False,
            'nullable': True,
            'empty': True,
            'default': '',
            'dependencies': 'paramValue',
        },
        'paramValue': {
            'type': 'string',
            'coerce': (NormalizerUtils.trim),
            'required': False,
            'nullable': True,
            'empty': True,
            'default': '',
            'dependencies': 'paramKey',
        },
    }


def validation_schema_url_list_get():
    return {
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
        'pagerKey' : {
            'type': 'dict',
            'schema': {
                'serviceId': {
                    'type': 'string',
                    'required': True,
                    'empty': False,
                },
                'urlId': {
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
