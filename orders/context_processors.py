def cart_count(request):
    if request.user.is_authenticated:
        cart = getattr(request.user, 'cart', None)

        if cart:
            return {'cart_count': cart.items.count()}

    return {'cart_count': 0}