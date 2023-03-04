import boto3

# Table name for copy from
source_table_name = 'table-name-copied-from'

# Table name for copy to
destination_table_name = 'table-name-copied-to'


# Create boto3 DynamoDB client
dynamodb = boto3.resource('dynamodb')

# Get table copied from
source_table = dynamodb.Table(source_table_name)

# Get table copied to
destination_table = dynamodb.Table(destination_table_name)

# ExclusiveStartKey to set start position for scan
exclusive_start_key = None

while True:
    # Get items from table copied from to set start position
    scan_kwargs = {}
    if exclusive_start_key:
        scan_kwargs['ExclusiveStartKey'] = exclusive_start_key

    response = source_table.scan(**scan_kwargs)

    # Insert items to table copied to
    with destination_table.batch_writer() as batch:
        for item in response['Items']:
            batch.put_item(Item=item)

    # Break loop on not exits ExclusiveStartKey
    if 'LastEvaluatedKey' not in response:
        break

    # Set start potions for next scan
    exclusive_start_key = response['LastEvaluatedKey']
