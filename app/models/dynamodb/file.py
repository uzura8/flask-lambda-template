from app.models.dynamodb.base import Base, ModelInvalidParamsException
from app.models.dynamodb.service import Service
from app.common.date import utc_iso
from app.common.string import new_uuid


class File(Base):
    table_name = 'file'
    response_attrs = [
        'fileId',
        'createdAt',
        'fileType',
        'mimeType',
        'name',
        'size',
        {'key':'fileStatus', 'label':'status'},
    ]
    status_allowed = ['reserved', 'reserveFailed', 'published', 'removed']


    @classmethod
    def check_fileId_exists(self, file_id):
        item = self.get_one({'p': {'key':'fileId', 'val':file_id}})
        return bool(item)


    @classmethod
    def create(self, vals):
        service_id = vals.get('serviceId')
        if not service_id:
            raise ModelInvalidParamsException('serviceId is required')

        if not Service.check_exists(service_id):
            raise ModelInvalidParamsException('serviceId not exists')

        status = vals.get('fileStatus')
        if status not in self.status_allowed:
            raise ModelInvalidParamsException('status is invalid')

        if vals.get('fileId'):
            file_id = vals['fileId']
            if self.check_fileId_exists(file_id):
                raise ModelInvalidParamsException('fileId already exists')
        else:
            file_id = new_uuid()

        time = utc_iso(False, True)
        file_type = vals['fileType']

        table = self.get_table()
        item = {
            'fileId': file_id,
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


    @classmethod
    def update_status(self, file_id, status):
        if status not in self.status_allowed:
            raise ModelInvalidParamsException('status is invalid')

        saved = self.get_one_by_pkey('fileId', file_id, True)
        if not saved:
            raise ModelInvalidParamsException('fileId is invalid')

        if status == saved.get('status'):
            return None

        if not saved['createdAt']:
            raise ModelInvalidParamsException('createdAt not exists on item: %s' % file_id)
        created_at = saved['createdAt']

        if not saved['fileType']:
            raise ModelInvalidParamsException('fileType not exists on item: %s' % file_id)
        file_type = saved['fileType']

        exp_items = []
        exp_vals = {}

        exp_items.append('fileStatus=:fs')
        exp_vals[':fs'] = status

        exp_items.append('statusCreatedAt=:sca')
        exp_vals[':sca'] = '#'.join([status, created_at])

        exp_items.append('fileTypeStatusCreatedAt=:fsc')
        exp_vals[':fsc'] = '#'.join([file_type, status, created_at])

        updated_at = utc_iso(False, True)
        exp_items.append('updatedAt=:ua')
        exp_vals[':ua'] = updated_at

        table = self.get_table()
        res = table.update_item(
            Key={
                'fileId': file_id,
            },
            UpdateExpression='SET ' +  ', '.join(exp_items),
            ExpressionAttributeValues=exp_vals,
            ReturnValues='UPDATED_NEW'
        )
        for attr, val in res['Attributes'].items():
            if attr not in saved:
                continue
            saved[attr] = val

        return saved


    @classmethod
    def bulk_update_status(self, file_ids, status):
        if status not in self.status_allowed:
            raise ModelInvalidParamsException('status is invalid')

        update_file_ids = []
        for file_id in file_ids:
            key = {'p': {'key':'fileId', 'val':file_id}}
            file = self.get_one(key)
            if not file:
                raise ModelInvalidParamsException('fileId %s not exists' % file_id)

            if file['fileStatus'] == status:
                continue

            update_file_ids.append(file_id)

        updateds = []
        if not update_file_ids:
            return []

        for file_id in update_file_ids:
            updated = self.update_status(file_id, status)
            updateds.append(updated)

        return updateds
