from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.contrib.auth.decorators import login_required
from decimal import Decimal
from app_settings.models import GlobalSettings
from product.models import Product

from .cart import Cart

@login_required
def cart_view(request):
    cart = Cart(request)

    context = {
        'cart': cart
    }

    return render(request, 'cart/cart-view.html', context)


@login_required
def cart_add(request):
    cart = Cart(request)
    if request.POST.get('action') == 'post':
        product_id = int(request.POST.get('product_id'))
        product_qty = int(request.POST.get('product_qty'))
        product = get_object_or_404(Product, id=product_id)

        # Рассчёт наценки
        global_settings = GlobalSettings.get_instance()
        user_profile = request.user.profile
        user_markup = user_profile.markup_percentage or Decimal(0)
        global_markup = global_settings.global_mark_up if global_settings else Decimal(0)
        total_markup = user_markup + global_markup

        # Итоговая цена
        final_price = product.price * (1 + total_markup / Decimal(100))
        final_price = final_price.quantize(Decimal('0.01'))  # Округление

        # Добавление в корзину с итоговой ценой
        cart.add(product=product, quantity=product_qty, price=final_price)

        return JsonResponse({
            'qty': cart.__len__(),
            'product': product.name
        })
    

@login_required  
def cart_delete(request):
    cart = Cart(request)

    if request.POST.get('action') == 'post':
        product_id = int(request.POST.get('product_id'))
        
        cart.delete(product=product_id)
        
        cart_qty = cart.__len__()
        
        cart_total = cart.get_total_price()

        response = JsonResponse({'qty': cart_qty, 'total': cart_total})

        return response



from django.http import JsonResponse

def cart_update(request):
    cart = Cart(request)
    if request.POST.get('action') == 'post':
        product_id = int(request.POST.get('product_id'))
        product_qty = int(request.POST.get('product_qty'))
        product = get_object_or_404(Product, id=product_id)
        
        if product_qty > product.quantity:
            return JsonResponse({
                'error': f'Недостаточно товара. Доступно: {product.quantity}'
            })
        
        cart.update(product=product, quantity=product_qty)
        
        return JsonResponse({
            'qty': cart.__len__(),
            'total': cart.get_total_price()
        })

