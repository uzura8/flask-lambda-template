import boto3

# Table name for copy from
source_table_name = 'table-name-copied-from'

# Table name for copy to
destination_table_name = 'table-name-copied-to'

# AWS Region
#region_name = 'ap-northeast-1'

#dynamodb = boto3.resource('dynamodb', region_name=region_name)
dynamodb = boto3.resource('dynamodb')

# Get table copied from
source_table = dynamodb.Table(source_table_name)

# Get table copied to
destination_table = dynamodb.Table(destination_table_name)

# Get all items from table copied from
response = source_table.scan()

# Put all items to table copied to
with destination_table.batch_writer() as batch:
    for item in response['Items']:
        batch.put_item(Item=item)
