import json
import os
from app.common.media import get_ext_by_mimetype
from app.models.dynamodb import ServiceConfig


def get_service_config_value(config_name, service_configs=None, service_id=None):
    if service_configs and config_name in service_configs:
        val = service_configs[config_name]
        if val is not None:
            return val

    if service_id:
        val = ServiceConfig.get_one_by_name(service_id, config_name, True, True)
        if val is not None:
            return val

    return None


def media_accept_mimetypes(file_type, service_configs=None, service_id=None):
    if file_type not in ['image', 'file']:
        raise ValueError('file_type is invalid')

    config_name = f'mediaUploadAcceptMimetypes{file_type.capitalize()}'
    return get_service_config_value(config_name, service_configs, service_id)


def media_bucket_file_dir(service_id, file_type, file_id):
    items = [service_id]
    if file_type == 'image':
        items.extend(['images', file_id])
    else:
        items.append('docs')

    return '/'.join(items)


def media_bucket_file_path(service_id, file_type, file_id, mimetype, size_str=None):
    dir_path = media_bucket_file_dir(service_id, file_type, file_id)
    ext = get_ext_by_mimetype(mimetype)
    if file_type == 'image':
        if not size_str:
            raise ValueError('size_str is required')
        file_name = f'{size_str}.{ext}'
    else:
        file_name = f'{file_id}.{ext}'

    return f'{dir_path}/{file_name}'

