import json

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

from products.models import Product
from orders.models import Cart, CartItem


@login_required
@csrf_exempt
def add_to_cart(request, product_id):
    if request.method == "POST":
        product = get_object_or_404(Product, id=product_id)

        if product.product_type != 'cart':
            return JsonResponse({"success": False, "error": "Product not available for cart"})

        quantity = 1
        if request.content_type and 'application/json' in request.content_type:
            try:
                payload = json.loads(request.body)
                quantity = int(payload.get('quantity', 1) or 1)
            except (TypeError, ValueError, json.JSONDecodeError):
                quantity = 1
        else:
            quantity = int(request.POST.get('quantity', 1) or 1)

        if quantity < 1:
            return JsonResponse({"success": False, "error": "Quantity must be at least 1"})

        cart, _ = Cart.objects.get_or_create(user=request.user)
        item, created = CartItem.objects.get_or_create(cart=cart, product=product)

        new_quantity = item.quantity + quantity if not created else quantity

        if new_quantity > product.stock:
            return JsonResponse({
                "success": False,
                "error": f"Only {product.stock} item(s) available in stock."
            })

        if not created:
            item.quantity = new_quantity
            item.save()
        else:
            item.quantity = quantity
            item.save()

        return JsonResponse({
            "success": True,
            "count": cart.items.count()
        })

    return JsonResponse({"success": False, "error": "Invalid request method"})


@login_required
def cart_view(request):
    cart, _ = Cart.objects.get_or_create(user=request.user)
    items = cart.items.select_related('product')

    for item in items:
        item.subtotal = item.quantity * item.product.price

    total = sum(item.subtotal for item in items)

    return render(request, 'cart/cart.html', {
        'cart': cart,
        'items': items,
        'total': total
    })


@login_required
@csrf_exempt
def update_cart_quantity(request):
    if request.method == "POST":
        data = json.loads(request.body)
        item_id = data.get("item_id")
        quantity = int(data.get("quantity"))

        item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)

        if quantity < 1:
            return JsonResponse({"success": False, "error": "Quantity must be at least 1"}, status=400)

        if quantity > item.product.stock:
            return JsonResponse({
                "success": False,
                "error": f"Only {item.product.stock} item(s) available in stock."
            }, status=400)

        item.quantity = quantity
        item.save()

        subtotal = item.quantity * item.product.price
        return JsonResponse({
            "success": True,
            "subtotal": float(subtotal),
        })

    return JsonResponse({"success": False, "error": "Invalid request method."}, status=400)


@login_required
def remove_cart_item(request, item_id):
    item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    item.delete()
    return redirect('cart')
