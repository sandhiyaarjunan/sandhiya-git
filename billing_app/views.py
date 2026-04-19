from django.shortcuts import render, redirect
from .models import Product, Bill, BillItem
from .tasks import send_async_invoice
import math
from kombu.exceptions import OperationalError 

def calculate_denominations(amount):
    """
    Calculates the breakdown of currency notes for the balance amount.
    Uses a greedy algorithm to determine the count of each denomination.
    """
    denoms = [500, 50, 20, 10, 5, 2, 1]
    result = {}
    remaining = int(amount)
    
    for d in denoms:
        count = remaining // d
        if count > 0:
            result[d] = count
            remaining %= d
    return result

def billing_page(request):
    """
    Handles the main billing logic:
    1. GET: Renders the product selection page.
    2. POST: Calculates totals, taxes, balance denominations, and triggers email.
    """
    if request.method == "POST":
        # Extract data from the POST request
        email = request.POST.get('email')
        product_ids = request.POST.getlist('product_id[]')
        quantities = request.POST.getlist('quantity[]')
        
        # Safe handling of cash paid input
        cash_val = request.POST.get('cash_paid', '0').strip()
        cash_paid = float(cash_val) if cash_val else 0.0
        
        bill_items_data = []
        grand_total = 0
        total_tax = 0

        # Process each selected product
        for p_id, qty in zip(product_ids, quantities):
            product = Product.objects.get(product_id=p_id)
            qty = int(qty)
            
            # Calculate tax and total for the specific line item
            tax_payable = (product.price * product.tax_percentage / 100) * qty
            total_price = (product.price * qty) + tax_payable
            
            item_info = {
                'product_id': p_id,
                'unit_price': product.price,
                'qty': qty,
                'tax': tax_payable,
                'total': total_price
            }
            bill_items_data.append(item_info)
            
            # Aggregate totals for the grand summary
            grand_total += total_price
            total_tax += tax_payable

        # Calculate change to be returned and its denominations
        balance = cash_paid - float(grand_total)
        balance_denoms = calculate_denominations(balance)

        # Prepare context for template rendering and Celery task
        context = {
            'customer_email': email,
            'items': bill_items_data,
            'total_without_tax': grand_total - total_tax,
            'total_tax': total_tax,
            'net_price': grand_total,
            'balance': balance,
            'denoms': balance_denoms
        }

        # Trigger Asynchronous Email via Celery
        try:
            # We pass the context to the task to be handled by the worker
            send_async_invoice(context)
        except Exception as e:
            # Fallback log if the message broker (Redis) is unavailable
            print(f"Email queue error: {e}")

        # Render the final invoice/summary page
        return render(request, 'billing/page2.html', context)

    # If GET request, display the initial billing form
    return render(request, 'billing/page1.html')