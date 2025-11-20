"""
AWS Lambda Function for Transaction Processing
This function is deployed to AWS Lambda and processes inventory transactions asynchronously

Deploy this function to AWS Lambda with Python 3.11 runtime
"""

import json
import boto3
from decimal import Decimal


def lambda_handler(event, context):
    """
    Lambda function to process inventory transactions

    Event structure:
    {
        "transaction_id": 123,
        "product_id": 456,
        "transaction_type": "IN" or "OUT",
        "quantity": 10,
        "timestamp": "123456789"
    }
    """

    print(f"Processing transaction: {json.dumps(event)}")

    try:
        # Extract transaction details
        transaction_id = event.get('transaction_id')
        product_id = event.get('product_id')
        transaction_type = event.get('transaction_type')
        quantity = event.get('quantity')
        timestamp = event.get('timestamp')

        # Log to CloudWatch
        print(f"Transaction {transaction_id}: {transaction_type} - Product {product_id} - Qty {quantity}")

        # Here you can add additional processing logic:
        # - Update inventory levels
        # - Send notifications
        # - Update analytics
        # - Trigger other AWS services

        # Example: Log to DynamoDB
        dynamodb = boto3.client('dynamodb')

        try:
            dynamodb.put_item(
                TableName='inventory-transaction-logs',
                Item={
                    'transaction_id': {'S': str(transaction_id)},
                    'product_id': {'S': str(product_id)},
                    'type': {'S': transaction_type},
                    'quantity': {'N': str(quantity)},
                    'timestamp': {'N': str(timestamp)},
                    'processed_at': {'N': str(int(context.request_id) if hasattr(context, 'request_id') else timestamp)},
                    'status': {'S': 'PROCESSED'}
                }
            )
            print(f"Transaction logged to DynamoDB successfully")
        except Exception as e:
            print(f"Error logging to DynamoDB: {str(e)}")

        # Return success response
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Transaction processed successfully',
                'transaction_id': transaction_id,
                'status': 'SUCCESS'
            })
        }

    except Exception as e:
        print(f"Error processing transaction: {str(e)}")

        # Return error response
        return {
            'statusCode': 500,
            'body': json.dumps({
                'message': 'Error processing transaction',
                'error': str(e),
                'status': 'FAILED'
            })
        }


# For local testing
if __name__ == '__main__':
    # Test event
    test_event = {
        'transaction_id': 1,
        'product_id': 10,
        'transaction_type': 'IN',
        'quantity': 5,
        'timestamp': '1234567890'
    }

    class MockContext:
        request_id = '12345'

    result = lambda_handler(test_event, MockContext())
    print(json.dumps(result, indent=2))
