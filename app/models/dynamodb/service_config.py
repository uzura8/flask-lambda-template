import json
from boto3.dynamodb.conditions import Key
from app.models.dynamodb import Base
from app.common.date import utc_iso


class ServiceConfig(Base):
    table_name = 'service-config'

    public_attrs = [
        'configName',
        'configVal',
    ]
    response_attrs = public_attrs + []
    private_attrs = [
        'isJson',
    ]
    all_attrs = public_attrs + private_attrs

    alloweds = [
        {
            'configName': 'outerSiteUrl',
            'isJson': False,
            'default': '',
        },
        {
            'configName': 'frontendPostDetailUrlPrefix',
            'isJson': False,
            'default': '',
        },
        {
            'configName': 'mediaUploadAcceptMimetypesImage',
            'isJson': True,
            'default': '["image/png","image/gif","image/jpeg"]',
        },
        {
            'configName': 'mediaUploadImageSizes',
            'isJson': True,
            'default': '["1200x1200","800x800","400x400","400x400xs"]',
        },
        {
            'configName': 'mediaUploadSizeLimitMBImage',
            'isJson': False,
            'default': 5,
        },
        {
            'configName': 'mediaUploadAcceptMimetypesFile',
            'isJson': True,
            'default': '["image/png","image/gif","image/jpeg","application/pdf"]',
        },
        {
            'configName': 'mediaUploadSizeLimitMBFile',
            'isJson': False,
            'default': 5,
        },
        {
            'configName': 'jumpPageUrl',
            'isJson': False,
            'default': '',
        },
        {
            'configName': 'jumpPageParamKey',
            'isJson': False,
            'default': '',
        },
        {
            'configName': 'analysisParamKeyDefault',
            'isJson': False,
            'default': '',
        },
    ]

    @classmethod
    def get_val(self, service_id, name):
        item = self.get_one_by_name(service_id, name)
        return item['configVal']


    @classmethod
    def get_one_by_name(self, service_id, name, is_json_loads=True, supply_if_empty=False):
        table = self.get_table()
        res = table.query(
            KeyConditionExpression=Key('serviceId').eq(service_id) & Key('configName').eq(name)
        )

        item = {}
        if res.get('Items'):
            item = res['Items'][0]

        elif supply_if_empty:
            searched = [ i for i in self.alloweds if i['configName'] == name ]
            allowed = searched[0] if searched else None
            if not allowed:
                return None

            item = {
                'configName': name,
                'configVal': allowed['default'],
                'isJson': allowed['isJson'],
            }

        if not item:
            return None

        if item.get('isJson') and is_json_loads:
            item['configVal'] = json.loads(item['configVal'])

        return item


    @classmethod
    def get_all_by_service(self, service_id, as_object=False, is_json_loads=True, supply_if_empty=False):
        saveds = self.get_all_by_pkey({'key':'serviceId', 'val':service_id})
        res = []
        if supply_if_empty:
            for allowed in self.alloweds:
                name = allowed['configName']
                item = None
                if saveds:
                    searched = [ s for s in saveds if s['configName'] == name ]
                    item = searched[0] if searched else None

                if not item:
                    item = {
                        'serviceId': service_id,
                        'configName': name,
                        'configVal': allowed['default'],
                    }

                if allowed['isJson'] and is_json_loads:
                    item['configVal'] = json.loads(item['configVal'])
                res.append(item)
        else:
            if not saveds:
                return []
            for saved in saveds:
                item = saved
                if item['isJson'] and is_json_loads:
                    item['configVal'] = json.loads(item['configVal'])
                res.append(item)

        if not as_object:
            return res

        obj = {}
        for item in res:
            key = item['configName']
            obj[key] = item['configVal']

        return obj


    @classmethod
    def save(self, service_id, name, val):
        save_val = val
        is_json = False
        if isinstance(val, (list, dict)):
            save_val = json.dumps(val)
            is_json = True

        time = utc_iso(False, True)
        table = self.get_table()
        item = self.get_one_by_name(service_id, name)
        if not item:
            item = {
                'serviceId': service_id,
                'configName': name,
                'configVal': save_val,
                'isJson': is_json,
                'updatedAt': time,
            }
            table.put_item(Item=item)
            return item

        comp_val = json.dumps(item['configVal']) if item['isJson'] else item['configVal']
        if save_val == comp_val:
            return item

        table.update_item(
            Key={
                'serviceId': service_id,
                'configName': name,
            },
            AttributeUpdates={
                'configVal': {
                    'Value': save_val
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
            'isJson': is_json,
            'updatedAt': time,
        }


    @classmethod
    def increament_number(self, service_id, name):
        item = self.get_one_by_name(service_id, name)
        if not item:
            self.save(service_id, name, 1)
            return 1

        table = self.get_table()
        table.update_item(
            Key={
                'serviceId': service_id,
                'configName': name
            },
            UpdateExpression='ADD configVal :incr',
            ExpressionAttributeValues={':incr': 1}
        )
        return self.get_val(service_id, name)
