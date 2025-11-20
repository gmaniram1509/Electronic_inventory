from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import pre_delete, post_save, post_delete
from django.dispatch import receiver
from django.core.exceptions import ValidationError
import boto3
from django.conf import settings

# Import from inventory_calculator library
from inventory_calculator import is_low_stock, validate_transaction, StockValidationError


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['name']

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=200)
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='products')
    description = models.TextField(blank=True)
    sku = models.CharField(max_length=50, unique=True)
    quantity = models.IntegerField(default=0)
    min_stock_level = models.IntegerField(default=10)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    datasheet = models.FileField(upload_to='datasheets/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.sku})"

    @property
    def is_low_stock(self):
        """Check if product stock is low using inventory_calculator library"""
        return is_low_stock(self.quantity, self.min_stock_level)


class Transaction(models.Model):
    TRANSACTION_TYPES = (
        ('IN', 'Stock In'),
        ('OUT', 'Stock Out'),
    )

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='transactions')
    transaction_type = models.CharField(max_length=3, choices=TRANSACTION_TYPES)
    quantity = models.IntegerField()
    notes = models.TextField(blank=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.transaction_type} - {self.product.name} - {self.quantity}"

    def clean(self):
        """Validate transaction using inventory_calculator library"""
        super().clean()

        try:
            # Use library validation
            validate_transaction(
                transaction_type=self.transaction_type,
                quantity=self.quantity,
                current_stock=self.product.quantity
            )
        except StockValidationError as e:
            # Convert library exception to Django ValidationError
            raise ValidationError({'quantity': str(e)})

    def save(self, *args, **kwargs):
        """Override save to call clean validation"""
        self.clean()
        super().save(*args, **kwargs)


# Signal handlers for S3 file deletion
@receiver(pre_delete, sender=Product)
def delete_product_files_from_s3(sender, instance, **kwargs):
    """
    Delete product image and datasheet from S3 when product is deleted
    Fixes bug: S3 files were not being deleted when product was deleted
    """
    if not settings.AWS_STORAGE_BUCKET_NAME:
        return  # Skip if not using S3

    try:
        s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION
        )

        # Delete image from S3
        if instance.image:
            try:
                s3_client.delete_object(
                    Bucket=settings.AWS_STORAGE_BUCKET_NAME,
                    Key=str(instance.image.name)
                )
                print(f"Deleted image from S3: {instance.image.name}")
            except Exception as e:
                print(f"Error deleting image from S3: {str(e)}")

        # Delete datasheet from S3
        if instance.datasheet:
            try:
                s3_client.delete_object(
                    Bucket=settings.AWS_STORAGE_BUCKET_NAME,
                    Key=str(instance.datasheet.name)
                )
                print(f"Deleted datasheet from S3: {instance.datasheet.name}")
            except Exception as e:
                print(f"Error deleting datasheet from S3: {str(e)}")

    except Exception as e:
        print(f"Error connecting to S3: {str(e)}")


# Signal for logging activity to DynamoDB
@receiver(post_save, sender=Product)
def log_product_change_to_dynamodb(sender, instance, created, **kwargs):
    """Log product creation/update to DynamoDB"""
    try:
        from .aws_utils import log_activity_to_dynamodb
        action = 'CREATE' if created else 'UPDATE'
        log_activity_to_dynamodb(
            action=action,
            resource_type='Product',
            resource_id=str(instance.id),
            details=f"{action} product: {instance.name} (SKU: {instance.sku})"
        )
    except:
        pass  # Don't fail if DynamoDB logging fails


@receiver(post_delete, sender=Product)
def log_product_deletion_to_dynamodb(sender, instance, **kwargs):
    """Log product deletion to DynamoDB"""
    try:
        from .aws_utils import log_activity_to_dynamodb
        log_activity_to_dynamodb(
            action='DELETE',
            resource_type='Product',
            resource_id=str(instance.id),
            details=f"DELETE product: {instance.name} (SKU: {instance.sku})"
        )
    except:
        pass  # Don't fail if DynamoDB logging fails


@receiver(post_save, sender=Transaction)
def update_product_quantity(sender, instance, created, **kwargs):
    """
    Update product quantity when transaction is created
    IN transactions increase quantity, OUT transactions decrease quantity
    """
    if not created:
        return  # Only process new transactions

    try:
        product = instance.product
        if instance.transaction_type == 'IN':
            product.quantity += instance.quantity
        elif instance.transaction_type == 'OUT':
            product.quantity -= instance.quantity
        product.save()
    except Exception as e:
        print(f"Error updating product quantity: {str(e)}")


@receiver(post_save, sender=Transaction)
def process_transaction_with_lambda(sender, instance, created, **kwargs):
    """
    Trigger Lambda function to process transaction asynchronously
    Lambda will update stock levels and send notifications if needed
    """
    if not created:
        return  # Only process new transactions

    try:
        from .aws_utils import trigger_transaction_lambda
        trigger_transaction_lambda(instance)
    except:
        pass  # Don't fail if Lambda trigger fails


@receiver(post_save, sender=Transaction)
def send_sns_notification_for_transaction(sender, instance, created, **kwargs):
    """Send SNS notification when transaction is created"""
    if not created:
        return

    try:
        from .aws_utils import send_sns_notification
        message = f"New {instance.get_transaction_type_display()}: {instance.product.name} - {instance.quantity} units"
        send_sns_notification(
            subject='Inventory Transaction',
            message=message
        )
    except:
        pass  # Don't fail if SNS fails

