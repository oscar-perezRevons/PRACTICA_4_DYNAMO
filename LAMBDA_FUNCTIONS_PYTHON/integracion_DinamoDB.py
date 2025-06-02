import json
import boto3

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('smart_light_sensor') 

def lambda_handler(event, context):
    try:
        data_item = {
            'thing_name': event.get('thing_name'),
            'timestamp': event.get('timestamp'),
            'light_level': event.get('light_level'),
            'light_intensity': event.get('light_intensity'),
            'servo_angle': event.get('servo_angle'),
            'last_update': event.get('last_update')
        }

        response = table.put_item(Item=data_item)
        return {
            'statusCode': 200,
            'body': 'Data stored successfully'
        }

    except Exception as e:
        print(f"Exception: {e}")
        return {
            'statusCode': 500,
            'body': f"Error: {e}"
        }