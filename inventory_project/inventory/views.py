from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import models
from .models import Product, Category, Transaction

# Import from inventory_calculator library for enhanced features
from inventory_calculator import StockCalculator, get_stock_status, calculate_reorder_quantity


@login_required
def dashboard(request):
    products = Product.objects.all()
    low_stock_products = Product.objects.filter(quantity__lte=models.F('min_stock_level'))
    categories = Category.objects.all()
    recent_transactions = Transaction.objects.all()[:10]

    # Enhanced: Use inventory_calculator library for additional insights
    product_stats = []
    for product in products:
        # Use StockCalculator for detailed info
        calc = StockCalculator(
            current_quantity=product.quantity,
            min_stock_level=product.min_stock_level,
            unit_price=float(product.unit_price)
        )

        product_stats.append({
            'product': product,
            'status': calc.get_stock_status(),  # OUT_OF_STOCK, LOW_STOCK, NORMAL, OVERSTOCKED
            'stock_value': calc.calculate_stock_value(),
            'reorder_quantity': calc.calculate_reorder_quantity(),
            'is_low_stock': calc.is_low_stock()
        })

    context = {
        'products': products,
        'low_stock_products': low_stock_products,
        'categories': categories,
        'recent_transactions': recent_transactions,
        'product_stats': product_stats,  # Enhanced data from library
    }
    return render(request, 'inventory/dashboard.html', context)


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password')

    return render(request, 'inventory/login.html')


def logout_view(request):
    logout(request)
    return redirect('login')

