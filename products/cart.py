from products.models import Product

class Cart:
    def __init__(self, request):
        self.session = request.session
        cart = self.session.get('cart')

        if not cart:
            cart = self.session['cart'] = {}

        self.cart = cart

    def add(self, product, quantity=1):
        product_id = str(product.id)

        if product_id in self.cart:
            self.cart[product_id]['quantity'] += quantity
        else:
            self.cart[product_id] = {
                'quantity': quantity,
                'price': str(product.price),
                'name': product.name
            }

        self.save()

    def remove(self, product_id):
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()

    def save(self):
        self.session.modified = True

    def clear(self):
        self.session['cart'] = {}
        self.save()

    def items(self):
        product_ids = self.cart.keys()
        products = Product.objects.filter(id__in=product_ids)

        cart_items = []

        for product in products:
            item = self.cart[str(product.id)]
            cart_items.append({
                'product': product,
                'quantity': item['quantity'],
                'total': float(item['price']) * item['quantity']
            })

        return cart_items

    def total_price(self):
        return sum(item['total'] for item in self.items())