from decimal import Decimal
from django.shortcuts import get_object_or_404
from product.models import Product
import uuid

class Cart:
    def __init__(self, request):
        self.session = request.session
        cart = self.session.get('cart')
        if not cart:
            cart = self.session['cart'] = {}
        self.cart = cart

    def __iter__(self):
        product_uuids = [uuid.UUID(key) for key in self.cart.keys()]
        products = Product.objects.filter(id__in=product_uuids)
        
        cart = self.cart.copy()
        for product in products:
            str_uuid = str(product.id)
            cart[str_uuid]['product'] = product
            cart[str_uuid]['price'] = Decimal(cart[str_uuid]['price'])
            cart[str_uuid]['total'] = cart[str_uuid]['price'] * cart[str_uuid]['qty']
        
        for item in cart.values():
            yield item

    def add(self, product, quantity=1):
        product_uuid = str(product.id)
        if product_uuid not in self.cart:
            self.cart[product_uuid] = {
                'qty': 0,
                'price': str(product.price)
            }
        
        # Проверка доступного количества
        new_qty = self.cart[product_uuid]['qty'] + quantity
        if new_qty > product.quantity:
            raise ValueError("Недостаточно товара на складе")
        
        self.cart[product_uuid]['qty'] = new_qty
        self.save()

    def remove(self, product):
        product_uuid = str(product.id)
        if product_uuid in self.cart:
            del self.cart[product_uuid]
            self.save()

    def update(self, product, quantity):
        product_uuid = str(product.id)
        if product_uuid in self.cart:
            if quantity > product.quantity:
                raise ValueError("Недостаточно товара на складе")
            
            self.cart[product_uuid]['qty'] = quantity
            self.save()

    def get_total_price(self):
        return sum(
            Decimal(item['price']) * item['qty']
            for item in self.cart.values()
        )

    def __len__(self):
        return sum(item['qty'] for item in self.cart.values())

    def save(self):
        self.session.modified = True