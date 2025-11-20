"""
AWS Utilities for Electronic Inventory System
Handles integration with 10 AWS services:
1. EC2 - Application hosting
2. RDS - PostgreSQL database
3. S3 - File storage
4. SES - Email notifications
5. CloudWatch - Logging and monitoring
6. SNS - Push notifications
7. DynamoDB - Activity logging
8. Lambda - Serverless processing
9. ElastiCache - Redis caching
10. Secrets Manager - Credential management
"""

import boto3
import logging
import json
import time
from datetime import datetime
from django.conf import settings
from django.core.mail import send_mail
from django.core.cache import cache
from botocore.exceptions import ClientError
import uuid

# Configure logging
logger = logging.getLogger(__name__)


class AWSCloudWatch:
    """CloudWatch logging and metrics"""

    def __init__(self):
        self.client = boto3.client(
            'logs',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION
        )
        self.log_group = '/aws/inventory-app'
        self.log_stream = 'application-logs'
        self._ensure_log_group_exists()

    def _ensure_log_group_exists(self):
        """Create log group and stream if they don't exist"""
        try:
            self.client.create_log_group(logGroupName=self.log_group)
        except self.client.exceptions.ResourceAlreadyExistsException:
            pass

        try:
            self.client.create_log_stream(
                logGroupName=self.log_group,
                logStreamName=self.log_stream
            )
        except self.client.exceptions.ResourceAlreadyExistsException:
            pass

    def log_event(self, message, level='INFO'):
        """Send log event to CloudWatch"""
        try:
            import time
            self.client.put_log_events(
                logGroupName=self.log_group,
                logStreamName=self.log_stream,
                logEvents=[{
                    'message': f'[{level}] {message}',
                    'timestamp': int(time.time() * 1000)
                }]
            )
        except Exception as e:
            logger.error(f"Failed to send log to CloudWatch: {str(e)}")


class LowStockAlertService:
    """
    Service to send low stock alerts via AWS SES
    """

    @staticmethod
    def check_and_send_alerts():
        """Check inventory and send email alerts for low stock items"""
        from .models import Product

        # Get low stock products
        low_stock_products = [p for p in Product.objects.all() if p.is_low_stock]

        if not low_stock_products:
            logger.info("No low stock items found")
            return

        # Prepare email content
        subject = f'Low Stock Alert - {len(low_stock_products)} Items Need Restocking'

        message_lines = [
            'Low Stock Alert - Electronic Inventory System',
            '=' * 50,
            '',
            f'The following {len(low_stock_products)} items are running low on stock:',
            ''
        ]

        for product in low_stock_products:
            message_lines.append(
                f'- {product.name} (SKU: {product.sku}): '
                f'{product.quantity} units (Min: {product.min_stock_level})'
            )

        message_lines.extend([
            '',
            '=' * 50,
            'Please restock these items soon.',
            '',
            'Login to manage inventory: http://your-server-url/admin/'
        ])

        message = '\n'.join(message_lines)

        # Send email
        try:
            recipient_email = getattr(settings, 'LOW_STOCK_ALERT_EMAIL',
                                     getattr(settings, 'SES_FROM_EMAIL'))

            send_mail(
                subject=subject,
                message=message,
                from_email=settings.SES_FROM_EMAIL,
                recipient_list=[recipient_email],
                fail_silently=False,
            )

            logger.info(f"Low stock alert sent for {len(low_stock_products)} items")

            # Log to CloudWatch
            try:
                cloudwatch = AWSCloudWatch()
                cloudwatch.log_event(
                    f"Low stock alert sent for {len(low_stock_products)} items",
                    level='WARNING'
                )
            except:
                pass  # Don't fail if CloudWatch logging fails

        except Exception as e:
            logger.error(f"Failed to send low stock alert: {str(e)}")
            raise


class S3StorageHelper:
    """Helper functions for S3 storage operations"""

    @staticmethod
    def get_file_url(file_path):
        """Get public URL for a file in S3"""
        if not file_path:
            return None

        if settings.AWS_STORAGE_BUCKET_NAME:
            return f"https://{settings.AWS_S3_CUSTOM_DOMAIN}/{file_path}"
        return file_path

    @staticmethod
    def upload_file(file_obj, destination_path):
        """Upload a file to S3"""
        try:
            s3_client = boto3.client(
                's3',
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                region_name=settings.AWS_REGION
            )

            s3_client.upload_fileobj(
                file_obj,
                settings.AWS_STORAGE_BUCKET_NAME,
                destination_path,
                ExtraArgs={'ACL': 'public-read'}
            )

            return S3StorageHelper.get_file_url(destination_path)
        except ClientError as e:
            logger.error(f"Failed to upload file to S3: {str(e)}")
            return None


def log_to_cloudwatch(message, level='INFO'):
    """Convenience function to log to CloudWatch"""
    try:
        if settings.AWS_ACCESS_KEY_ID and settings.AWS_SECRET_ACCESS_KEY:
            cloudwatch = AWSCloudWatch()
            cloudwatch.log_event(message, level)
    except Exception as e:
        logger.error(f"CloudWatch logging failed: {str(e)}")


# ============================================================================
# NEW AWS SERVICES INTEGRATION
# ============================================================================

class AWSSNSNotification:
    """AWS SNS - Simple Notification Service for real-time alerts"""

    def __init__(self):
        self.client = boto3.client(
            'sns',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION
        )
        self.topic_arn = getattr(settings, 'SNS_TOPIC_ARN', None)

    def publish_message(self, subject, message):
        """Publish a message to SNS topic"""
        if not self.topic_arn:
            logger.warning("SNS Topic ARN not configured")
            return False

        try:
            response = self.client.publish(
                TopicArn=self.topic_arn,
                Subject=subject,
                Message=message,
                MessageAttributes={
                    'app': {'DataType': 'String', 'StringValue': 'inventory'},
                    'timestamp': {'DataType': 'String', 'StringValue': str(int(time.time()))}
                }
            )
            logger.info(f"SNS message published: {response['MessageId']}")
            return True
        except Exception as e:
            logger.error(f"Failed to publish SNS message: {str(e)}")
            return False


def send_sns_notification(subject, message):
    """Convenience function to send SNS notification"""
    try:
        sns = AWSSNSNotification()
        return sns.publish_message(subject, message)
    except Exception as e:
        logger.error(f"SNS notification failed: {str(e)}")
        return False


class AWSDynamoDBLogger:
    """AWS DynamoDB - Activity and audit logging"""

    def __init__(self):
        self.client = boto3.client(
            'dynamodb',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION
        )
        self.table_name = getattr(settings, 'DYNAMODB_TABLE_NAME', 'inventory-logs')
        self._ensure_table_exists()

    def _ensure_table_exists(self):
        """Create DynamoDB table if it doesn't exist"""
        try:
            self.client.describe_table(TableName=self.table_name)
        except self.client.exceptions.ResourceNotFoundException:
            try:
                self.client.create_table(
                    TableName=self.table_name,
                    KeySchema=[
                        {'AttributeName': 'log_id', 'KeyType': 'HASH'},
                        {'AttributeName': 'timestamp', 'KeyType': 'RANGE'}
                    ],
                    AttributeDefinitions=[
                        {'AttributeName': 'log_id', 'AttributeType': 'S'},
                        {'AttributeName': 'timestamp', 'AttributeType': 'N'}
                    ],
                    BillingMode='PAY_PER_REQUEST'
                )
                logger.info(f"Created DynamoDB table: {self.table_name}")
            except Exception as e:
                logger.error(f"Failed to create DynamoDB table: {str(e)}")

    def log_activity(self, action, resource_type, resource_id, details, user=None):
        """Log an activity to DynamoDB"""
        try:
            log_id = str(uuid.uuid4())
            timestamp = int(time.time() * 1000)

            item = {
                'log_id': {'S': log_id},
                'timestamp': {'N': str(timestamp)},
                'action': {'S': action},
                'resource_type': {'S': resource_type},
                'resource_id': {'S': resource_id},
                'details': {'S': details},
                'date': {'S': datetime.now().isoformat()}
            }

            if user:
                item['user'] = {'S': str(user)}

            self.client.put_item(
                TableName=self.table_name,
                Item=item
            )
            logger.info(f"Activity logged to DynamoDB: {action} - {resource_type}")
            return True
        except Exception as e:
            logger.error(f"Failed to log activity to DynamoDB: {str(e)}")
            return False

    def get_recent_logs(self, limit=100):
        """Retrieve recent logs from DynamoDB"""
        try:
            response = self.client.scan(
                TableName=self.table_name,
                Limit=limit
            )
            return response.get('Items', [])
        except Exception as e:
            logger.error(f"Failed to retrieve logs from DynamoDB: {str(e)}")
            return []


def log_activity_to_dynamodb(action, resource_type, resource_id, details, user=None):
    """Convenience function to log activity to DynamoDB"""
    try:
        dynamo_logger = AWSDynamoDBLogger()
        return dynamo_logger.log_activity(action, resource_type, resource_id, details, user)
    except Exception as e:
        logger.error(f"DynamoDB logging failed: {str(e)}")
        return False


class AWSLambdaProcessor:
    """AWS Lambda - Serverless transaction processing"""

    def __init__(self):
        self.client = boto3.client(
            'lambda',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION
        )
        self.function_name = getattr(settings, 'LAMBDA_FUNCTION_NAME', 'inventory-transaction-processor')

    def invoke_transaction_processor(self, transaction_data):
        """Invoke Lambda function to process transaction"""
        try:
            payload = json.dumps({
                'transaction_id': transaction_data.get('id'),
                'product_id': transaction_data.get('product_id'),
                'transaction_type': transaction_data.get('type'),
                'quantity': transaction_data.get('quantity'),
                'timestamp': str(int(time.time()))
            })

            response = self.client.invoke(
                FunctionName=self.function_name,
                InvocationType='Event',  # Asynchronous invocation
                Payload=payload
            )

            logger.info(f"Lambda function invoked: {self.function_name}")
            return True
        except self.client.exceptions.ResourceNotFoundException:
            logger.warning(f"Lambda function not found: {self.function_name}")
            return False
        except Exception as e:
            logger.error(f"Failed to invoke Lambda function: {str(e)}")
            return False


def trigger_transaction_lambda(transaction):
    """Trigger Lambda function for transaction processing"""
    try:
        lambda_processor = AWSLambdaProcessor()
        transaction_data = {
            'id': transaction.id,
            'product_id': transaction.product.id,
            'type': transaction.transaction_type,
            'quantity': transaction.quantity
        }
        return lambda_processor.invoke_transaction_processor(transaction_data)
    except Exception as e:
        logger.error(f"Lambda trigger failed: {str(e)}")
        return False


class AWSSecretsManager:
    """AWS Secrets Manager - Secure credential storage"""

    def __init__(self):
        self.client = boto3.client(
            'secretsmanager',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION
        )

    def get_secret(self, secret_name):
        """Retrieve a secret from Secrets Manager"""
        try:
            response = self.client.get_secret_value(SecretId=secret_name)
            if 'SecretString' in response:
                return json.loads(response['SecretString'])
            return None
        except Exception as e:
            logger.error(f"Failed to retrieve secret from Secrets Manager: {str(e)}")
            return None

    def create_secret(self, secret_name, secret_value):
        """Create a new secret in Secrets Manager"""
        try:
            self.client.create_secret(
                Name=secret_name,
                SecretString=json.dumps(secret_value)
            )
            logger.info(f"Secret created: {secret_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to create secret: {str(e)}")
            return False

    def update_secret(self, secret_name, secret_value):
        """Update an existing secret"""
        try:
            self.client.update_secret(
                SecretId=secret_name,
                SecretString=json.dumps(secret_value)
            )
            logger.info(f"Secret updated: {secret_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to update secret: {str(e)}")
            return False


def get_database_credentials_from_secrets_manager():
    """Get database credentials from AWS Secrets Manager"""
    try:
        secrets = AWSSecretsManager()
        return secrets.get_secret('inventory/database')
    except Exception as e:
        logger.error(f"Failed to get DB credentials from Secrets Manager: {str(e)}")
        return None


class ElastiCacheHelper:
    """AWS ElastiCache (Redis) - Caching layer"""

    @staticmethod
    def cache_product_data(product_id, data, timeout=3600):
        """Cache product data in ElastiCache/Redis"""
        try:
            cache_key = f'product_{product_id}'
            cache.set(cache_key, data, timeout)
            logger.info(f"Product {product_id} cached")
            return True
        except Exception as e:
            logger.error(f"Failed to cache product data: {str(e)}")
            return False

    @staticmethod
    def get_cached_product(product_id):
        """Retrieve cached product data"""
        try:
            cache_key = f'product_{product_id}'
            return cache.get(cache_key)
        except Exception as e:
            logger.error(f"Failed to retrieve cached product: {str(e)}")
            return None

    @staticmethod
    def invalidate_product_cache(product_id):
        """Invalidate product cache"""
        try:
            cache_key = f'product_{product_id}'
            cache.delete(cache_key)
            logger.info(f"Product {product_id} cache invalidated")
            return True
        except Exception as e:
            logger.error(f"Failed to invalidate cache: {str(e)}")
            return False

    @staticmethod
    def cache_inventory_summary(data, timeout=300):
        """Cache inventory summary data"""
        try:
            cache.set('inventory_summary', data, timeout)
            return True
        except Exception as e:
            logger.error(f"Failed to cache inventory summary: {str(e)}")
            return False

    @staticmethod
    def get_inventory_summary():
        """Get cached inventory summary"""
        try:
            return cache.get('inventory_summary')
        except Exception as e:
            logger.error(f"Failed to get cached inventory summary: {str(e)}")
            return None


# ============================================================================
# ENHANCED INTEGRATIONS WITH NEW SERVICES
# ============================================================================

class EnhancedLowStockAlertService(LowStockAlertService):
    """
    Enhanced low stock alert service using SNS + SES + DynamoDB
    """

    @staticmethod
    def check_and_send_alerts():
        """Check inventory and send alerts via multiple channels"""
        from .models import Product

        # Get low stock products
        low_stock_products = [p for p in Product.objects.all() if p.is_low_stock]

        if not low_stock_products:
            logger.info("No low stock items found")
            return

        # Send email via SES (existing functionality)
        LowStockAlertService.check_and_send_alerts()

        # Send SNS notification
        try:
            message = f"{len(low_stock_products)} products are running low on stock"
            send_sns_notification(
                subject='Inventory Low Stock Alert',
                message=message
            )
        except:
            pass

        # Log to DynamoDB
        try:
            for product in low_stock_products:
                log_activity_to_dynamodb(
                    action='LOW_STOCK_ALERT',
                    resource_type='Product',
                    resource_id=str(product.id),
                    details=f"Low stock: {product.name} ({product.quantity} units)"
                )
        except:
            pass

        # Log to CloudWatch
        try:
            log_to_cloudwatch(
                f"Low stock alert sent for {len(low_stock_products)} products",
                level='WARNING'
            )
        except:
            pass
