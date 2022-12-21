import json
import os
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
