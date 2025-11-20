from django.contrib import admin
from .models import Category, Product, Transaction


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_at']
    search_fields = ['name']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'sku', 'category', 'quantity', 'min_stock_level', 'unit_price', 'created_at']
    list_filter = ['category', 'created_at']
    search_fields = ['name', 'sku']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['product', 'transaction_type', 'quantity', 'user', 'created_at']
    list_filter = ['transaction_type', 'created_at']
    search_fields = ['product__name', 'notes']
    readonly_fields = ['created_at']
