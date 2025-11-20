"""
Management command to check for low stock items and send email alerts
Usage: python manage.py check_low_stock
"""

from django.core.management.base import BaseCommand
from inventory.aws_utils import LowStockAlertService, log_to_cloudwatch


class Command(BaseCommand):
    help = 'Check inventory for low stock items and send email alerts via AWS SES'

    def handle(self, *args, **options):
        self.stdout.write('Checking for low stock items...')

        try:
            LowStockAlertService.check_and_send_alerts()
            self.stdout.write(self.style.SUCCESS('Low stock check completed successfully'))

            # Log to CloudWatch
            log_to_cloudwatch('Low stock check command executed successfully')

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error: {str(e)}'))
            log_to_cloudwatch(f'Low stock check failed: {str(e)}', level='ERROR')
            raise
