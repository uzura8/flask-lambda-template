from boto3.dynamodb.conditions import Key
from app.models.dynamodb import Base
from app.common.date import utc_iso


class ServiceConfig(Base):
    table_name = 'service-config'

    public_attrs = []
    response_attrs = public_attrs + [
        'configs'
    ]
    private_attrs = []
    all_attrs = public_attrs + private_attrs


    @classmethod
    def get_val(self, service_id, name):
        item = self.get_one_by_name(service_id, name)
        return item['configVal'] if item else None


    @classmethod
    def get_one_by_name(self, service_id, name):
        table = self.get_table()
        res = table.query(
            KeyConditionExpression=Key('serviceId').eq(service_id) & Key('configName').eq(name)
        )
        return res['Items'][0] if 'Items' in res and res['Items'] else None


    @classmethod
    def get_all_by_service(self, service_id, as_object=False):
        items = self.get_all_by_pkey({'key':'serviceId', 'val':service_id})
        if not items:
            return None

        if not as_object:
            return items

        obj = {}
        for item in items:
            key = self.conv_save_name_to_key(item['configName'])
            obj[key] = item['configVal']

        return obj


    @classmethod
    def save(self, service_id, name, val):
        time = utc_iso(False, True)
        table = self.get_table()
        item = self.get_one_by_name(service_id, name)
        if not item:
            item = {
                'serviceId': service_id,
                'configName': name,
                'configVal': val,
                'updatedAt': time,
            }
            table.put_item(Item=item)
            return item

        if item['configVal'] == val:
            return item

        table.update_item(
            Key={
                'serviceId': service_id,
                'configName': name,
            },
            AttributeUpdates={
                'configVal': {
                    'Value': val
                },
                'updatedAt': {
                    'Value': time
                }
            },
        )
        return {
            'serviceId': service_id,
            'configName': name,
            'configVal': val,
            'updatedAt': time,
        }


    @classmethod
    def increament_number(self, service_id, name):
        item = self.get_one_by_name(service_id, name)
        if not item:
            self.save(service_id, name, 1)
            return 1

        table = self.get_table()
        #service_id_name = '#'.join([service_id, name])
        table.update_item(
            Key={
                'serviceId': service_id,
                'configName': name
            },
            UpdateExpression='ADD configVal :incr',
            ExpressionAttributeValues={':incr': 1}
        )
        return self.get_val(service_id, name)


    @staticmethod
    def conv_key_to_save_name(key):
        if key == 'jumpPageUrl':
            return 'urlShortener-jumpPageUrl'

        if key == 'jumpPageParamKey':
            return 'urlShortener-jumpPageParamKey'

        return ''


    @staticmethod
    def conv_save_name_to_key(save_name):
        if save_name == 'urlShortener-jumpPageUrl':
            return 'jumpPageUrl'

        if save_name == 'urlShortener-jumpPageParamKey':
            return 'jumpPageParamKey'

        return ''
