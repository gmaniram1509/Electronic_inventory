import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'inventory_project.settings')
django.setup()

from inventory.models import Category, Product, Transaction
from django.contrib.auth import get_user_model

User = get_user_model()

# Get or create admin user
admin_user = User.objects.filter(username='admin').first()

# Create Categories
categories_data = [
    {'name': 'Microcontrollers', 'description': 'Arduino, ESP32, Raspberry Pi, etc.'},
    {'name': 'Sensors', 'description': 'Temperature, Humidity, Motion sensors'},
    {'name': 'Power Supplies', 'description': 'Batteries, Adapters, Voltage Regulators'},
    {'name': 'Resistors', 'description': 'Various resistance values'},
    {'name': 'Capacitors', 'description': 'Ceramic, Electrolytic capacitors'},
]

categories = {}
for cat_data in categories_data:
    category, created = Category.objects.get_or_create(
        name=cat_data['name'],
        defaults={'description': cat_data['description']}
    )
    categories[cat_data['name']] = category
    print(f"{'Created' if created else 'Found'} category: {category.name}")

# Create Products
products_data = [
    {'name': 'Arduino Uno R3', 'category': 'Microcontrollers', 'sku': 'MCU-ARD-UNO', 'quantity': 15, 'min_stock_level': 10, 'unit_price': 25.99},
    {'name': 'ESP32 DevKit', 'category': 'Microcontrollers', 'sku': 'MCU-ESP-32', 'quantity': 8, 'min_stock_level': 10, 'unit_price': 12.50},
    {'name': 'Raspberry Pi 4 4GB', 'category': 'Microcontrollers', 'sku': 'MCU-RPI-4', 'quantity': 5, 'min_stock_level': 5, 'unit_price': 55.00},
    {'name': 'DHT22 Temperature Sensor', 'category': 'Sensors', 'sku': 'SEN-DHT-22', 'quantity': 25, 'min_stock_level': 15, 'unit_price': 8.99},
    {'name': 'PIR Motion Sensor', 'category': 'Sensors', 'sku': 'SEN-PIR-01', 'quantity': 12, 'min_stock_level': 10, 'unit_price': 4.50},
    {'name': 'Ultrasonic Sensor HC-SR04', 'category': 'Sensors', 'sku': 'SEN-US-04', 'quantity': 18, 'min_stock_level': 12, 'unit_price': 3.25},
    {'name': '5V 2A Power Supply', 'category': 'Power Supplies', 'sku': 'PWR-5V-2A', 'quantity': 20, 'min_stock_level': 15, 'unit_price': 7.99},
    {'name': 'LM7805 Voltage Regulator', 'category': 'Power Supplies', 'sku': 'PWR-7805', 'quantity': 50, 'min_stock_level': 30, 'unit_price': 0.50},
    {'name': '9V Battery', 'category': 'Power Supplies', 'sku': 'PWR-BAT-9V', 'quantity': 6, 'min_stock_level': 12, 'unit_price': 2.99},
    {'name': '220 Ohm Resistor Pack (100pcs)', 'category': 'Resistors', 'sku': 'RES-220-100', 'quantity': 10, 'min_stock_level': 5, 'unit_price': 3.50},
    {'name': '1k Ohm Resistor Pack (100pcs)', 'category': 'Resistors', 'sku': 'RES-1K-100', 'quantity': 8, 'min_stock_level': 5, 'unit_price': 3.50},
    {'name': '100uF Electrolytic Capacitor', 'category': 'Capacitors', 'sku': 'CAP-100UF', 'quantity': 30, 'min_stock_level': 20, 'unit_price': 0.35},
    {'name': '0.1uF Ceramic Capacitor', 'category': 'Capacitors', 'sku': 'CAP-0.1UF', 'quantity': 45, 'min_stock_level': 25, 'unit_price': 0.15},
]

products = []
for prod_data in products_data:
    category = categories[prod_data.pop('category')]
    product, created = Product.objects.get_or_create(
        sku=prod_data['sku'],
        defaults={**prod_data, 'category': category}
    )
    products.append(product)
    print(f"{'Created' if created else 'Found'} product: {product.name} (Stock: {product.quantity})")

# Create some sample transactions
if admin_user and Transaction.objects.count() == 0:
    transactions_data = [
        {'product': products[0], 'type': 'IN', 'quantity': 10},
        {'product': products[1], 'type': 'IN', 'quantity': 15},
        {'product': products[3], 'type': 'IN', 'quantity': 30},
        {'product': products[0], 'type': 'OUT', 'quantity': 5},
        {'product': products[8], 'type': 'OUT', 'quantity': 6},
    ]

    for trans_data in transactions_data:
        transaction = Transaction.objects.create(
            product=trans_data['product'],
            transaction_type=trans_data['type'],
            quantity=trans_data['quantity'],
            user=admin_user,
            notes=f"Sample {'stock in' if trans_data['type'] == 'IN' else 'stock out'} transaction"
        )
        print(f"Created transaction: {transaction}")

from django.db import models
print("\nSample data created successfully!")
print(f"Total Categories: {Category.objects.count()}")
print(f"Total Products: {Product.objects.count()}")
print(f"Total Transactions: {Transaction.objects.count()}")
low_stock_count = len([p for p in Product.objects.all() if p.quantity <= p.min_stock_level])
print(f"Low Stock Products: {low_stock_count}")
