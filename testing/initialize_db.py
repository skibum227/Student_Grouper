import boto3

# Run the below to start the db image
# docker run -p 8000:8000 amazon/dynamodb-local

def bring_db_up():
    dynamodb = boto3.resource('dynamodb', endpoint_url='http://localhost:8000')
    try:
        table = dynamodb.create_table(
            TableName='rosters',
            KeySchema=[
                {
                    'AttributeName': 'class_name',
                    'KeyType': 'HASH'
                },
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'class_name',
                    'AttributeType': 'S'
                },
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 25,
                'WriteCapacityUnits': 25
            }
        )

        # Wait until the table exists.
        table.wait_until_exists()
    except:
        print("db exists")


if __name__ == "__main__":
    bring_db_up()
