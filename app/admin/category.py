import traceback
from flask import jsonify, request
from flask_cognito import cognito_auth_required, current_cognito_jwt
from app.models.dynamodb import Category, Service, ModelInvalidParamsException
from app.common.error import InvalidUsage
from app.common.request import validate_req_params
from app.validators import NormalizerUtils
from app.admin import bp, site_before_request, check_acl_service_id, admin_role_editor_required


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
        vals = validate_req_params(validation_schema_categories_post(), request.json)
        item = Category.get_one_by_slug(service_id, vals['slug'])
        if item:
            raise InvalidUsage('Slug already used', 400)

        parent = Category.get_one_by_slug(service_id, vals['parentCategorySlug'])
        if not parent:
            raise InvalidUsage('parentCategorySlug not exists', 400)

        vals['parentId'] = parent['id']
        vals['serviceId'] = service_id
        body = Category.create(vals)

    else:
        params = validate_req_params(validation_schema_categories_get(), request.args)
        if params.get('withChildren'):
            body = Category.get_all_by_service_id(service_id)
        else:
            body = Category.get_children_by_parent_path(service_id, '0', False, True, False)

    return jsonify(body), 200


@bp.route('/categories/<string:service_id>/slug', methods=['GET'])
@cognito_auth_required
@admin_role_editor_required
def category_slug(service_id):
    check_acl_service_id(service_id)
    params = {'slug':request.args.get('slug')}
    vals = validate_req_params(validation_schema_categories_get(), params)
    category = Category.get_one_by_slug(service_id, vals['slug'], False, False, False, False)
    is_not_exists = not category
    return jsonify(is_not_exists), 200


@bp.route('/categories/<string:service_id>/<string:slug>', methods=['POST', 'GET', 'HEAD'])
@cognito_auth_required
@admin_role_editor_required
def category_detail(service_id, slug):
    service = check_acl_service_id(service_id, True)
    category = Category.get_one_by_slug(service_id, slug, True, False, False, False)
    if not category:
        raise InvalidUsage('Not Found', 404)
    category_id = category['id']

    saved = None
    if request.method == 'POST':
        vals = validate_req_params(validation_schema_categories_post(), request.json)
        if vals['parentCategorySlug'] == slug:
            raise InvalidUsage('parentCategorySlug must have a different value from slug', 400)

        parent = Category.get_one_by_slug(service_id, vals['parentCategorySlug'])
        if not parent:
            raise InvalidUsage('parentCategorySlug not exists', 400)

        vals['parentId'] = parent['id']
        vals['serviceId'] = service_id
        vals['updatedBy'] = current_cognito_jwt.get('cognito:username', '')

        try:
            res = Category.update(category_id, vals)
            saved = res

        except ModelInvalidParamsException as e:
            raise InvalidUsage(e.message, 400)

        except Exception as e:
            print(traceback.format_exc())
            raise InvalidUsage('Server Error', 500)

        if not saved:
            saved = category

    #elif request.method == 'DELETE':
    #    try:
    #        Category.delete({'id':category_id})
    #        return jsonify(), 200

    #    except ModelInvalidParamsException as e:
    #        raise InvalidUsage(e.message, 400)

    #    except Exception as e:
    #        print(traceback.format_exc())
    #        raise InvalidUsage('Server Error', 500)

    if request.method == 'HEAD':
        return jsonify(), 200

    res = saved if saved else category
    res['service'] = service

    return jsonify(res), 200


validation_schema_slug = {
    'type': 'string',
    'coerce': (str, NormalizerUtils.trim),
    'required': True,
    'empty': False,
    'maxlength': 128,
    'regex': r'^[0-9a-z\-]+$',
}

def validation_schema_categories_get():
    return {
        'slug': validation_schema_slug,
        'withChildren': {
            'type': 'boolean',
            'coerce': (str, NormalizerUtils.to_bool),
            'required': False,
            'empty': False,
            'default': False,
        },
    }


def validation_schema_categories_post():
    return {
        'slug': validation_schema_slug,
        'label': {
            'type': 'string',
            'coerce': (NormalizerUtils.trim),
            'required': True,
            'empty': False,
        },
        'parentCategorySlug': validation_schema_slug,
    }
