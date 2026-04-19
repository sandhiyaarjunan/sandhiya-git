from django.shortcuts import render, redirect
from .models import Product, Bill, BillItem
from .tasks import send_async_invoice
import math
from kombu.exceptions import OperationalError  # Add this import





def calculate_denominations(amount):
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
    if request.method == "POST":
        email = request.POST.get('email')
        product_ids = request.POST.getlist('product_id[]')
        quantities = request.POST.getlist('quantity[]')
        cash_val = request.POST.get('cash_paid', '0').strip()
        cash_paid = float(cash_val) if cash_val else 0.0
        bill_items_data = []
        grand_total = 0
        total_tax = 0

        for p_id, qty in zip(product_ids, quantities):
            product = Product.objects.get(product_id=p_id)
            qty = int(qty)
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
            grand_total += total_price
            total_tax += tax_payable

        balance = cash_paid - float(grand_total)
        balance_denoms = calculate_denominations(balance)

        # Trigger Asynchronous Email
        context = {
            'customer_email': email,
            'items': bill_items_data,
            'total_without_tax': grand_total - total_tax,
            'total_tax': total_tax,
            'net_price': grand_total,
            'balance': balance,
            'denoms': balance_denoms
        }
        try:
            send_async_invoice(context)
        except Exception as e:
            print(f"Email queue error: {e}")
            # We don't return here, we just let the code continue

        # Ensure this is NOT inside the 'try' or 'except' block
        return render(request, 'billing/page2.html', context)

    return render(request, 'billing/page1.html')