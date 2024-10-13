import json
import boto3

# Initialize the DynamoDB resource
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('ResumeVisitorCounter')

def lambda_handler(event, context):
    body = {}
    statusCode = 200
    headers = {
        "Content-Type": "application/json"
    }
    
    try:
        if event['routeKey'] == "GET /getCount":
            # Retrieve the current visitor count from DynamoDB
            response = table.get_item(Key={'visitorCounter': 'count'})
            if 'Item' in response:
                count = int(response['Item']['count'])
                body = {'visitorCount': count}
            else:
                statusCode = 404
                body = {
                    'error': 'Visitor count not found',
                    'Response': response
                }

        elif event['routeKey'] == "POST /updateCount":
            # Increment the visitor count in DynamoDB
            response = table.get_item(Key={'visitorCounter': 'count'})
            if 'Item' in response:
                count = int(response['Item']['count']) + 1
                table.update_item(
                    Key={'visitorCounter': 'count'},
                    UpdateExpression='SET #count = :new_count',
                    ExpressionAttributeNames={'#count': 'count'},
                    ExpressionAttributeValues={':new_count': count}
                )
                body = {'newVisitorCount': count}
            else:
                # Initialize count if not found
                table.put_item(Item={'visitorCounter': 'count', 'count': 1})
                body = {'newVisitorCount': 1}
        else:
            statusCode = 400
            body = {'error': 'Unsupported route: ' + event['routeKey']}
    
    except Exception as e:
        statusCode = 500
        body = {'error': str(e)}
    
    return {
        'statusCode': statusCode,
        'headers': headers,
        'body': json.dumps(body)
    }
