from app.models.dynamodb.base import Base, ModelInvalidParamsException
from app.models.dynamodb.service import Service
from app.common.date import utc_iso
from app.common.string import new_uuid


class File(Base):
    table_name = 'file'
    response_attr = [
        'fileId',
        'createdAt',
        'fileType',
        'mimeType',
        'name',
        'size',
        {'key':'fileStatus', 'label':'status'},
    ]


    @classmethod
    def create(self, vals):
        service_id = vals.get('serviceId')
        if not service_id:
            raise ModelInvalidParamsException('serviceId is required')

        if not Service.check_exists(service_id):
            raise ModelInvalidParamsException('serviceId not exists')

        status = vals.get('fileStatus')
        if status not in ['reserved', 'reserveFailed', 'published', 'removed']:
            raise ModelInvalidParamsException('status is invalid')

        time = utc_iso(False, True)
        file_type = vals['fileType']

        table = self.get_table()
        item = {
            'fileId': new_uuid(),
            'createdAt': time,
            'createdBy': vals.get('createdBy'),
            'serviceId': service_id,
            'fileType': file_type,
            'mimeType': vals.get('mimeType'),
            'fileStatus': status,
            'statusCreatedAt': '#'.join([status, time]),
            'fileTypeStatusCreatedAt': '#'.join([file_type, status, time]),
            'name': vals.get('name'),
            'size': vals.get('size'),
        }
        table.put_item(Item=item)
        return item
