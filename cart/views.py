# cart/views.py
from django.contrib import messages
from django.http import JsonResponse
from decimal import Decimal
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from app_settings.models import GlobalSettings
from .models import Cart, CartItem
from product.models import Product
from product.utils import annotate_product_prices



def get_cart_total(cart, user_profile, currency):
    """Рассчитывает общую сумму корзины с учетом валюты"""
    global_settings = GlobalSettings.get_instance()
    cart_items = cart.items.select_related('product').all()
    product_ids = cart_items.values_list('product_id', flat=True)
    products = Product.objects.filter(id__in=product_ids)
    
    # Аннотируем цены с учетом валюты
    annotated_products = annotate_product_prices(products, user_profile, currency)
    price_map = {p.id: p.display_final_price for p in annotated_products}
    
    total = Decimal('0.00')
    for item in cart_items:
        item_price = price_map.get(item.product_id, Decimal('0'))
        total += item_price * item.quantity
    
    return total.quantize(Decimal('0.00'))


@login_required
def cart_view(request):
    currency = request.GET.get('currency', 'RUB').upper()
    user_profile = request.user.profile
    cart, created = Cart.objects.get_or_create(profile=user_profile)
    
    # Получаем актуальные цены в выбранной валюте
    cart_items = cart.items.select_related('product').all()
    products = Product.objects.filter(id__in=cart_items.values_list('product_id', flat=True))
    annotated_products = annotate_product_prices(products, user_profile, currency)
    price_map = {p.id: p.display_final_price for p in annotated_products}
    
    total = Decimal('0.00')
    for item in cart_items:
        item.current_price = price_map.get(item.product_id, Decimal('0'))
        total += item.current_price * item.quantity
    
    return render(request, 'cart/cart.html', {
        'cart_items': cart_items,
        'total': total,
        'currency': currency,
        'global': GlobalSettings.get_instance(),
    })


@login_required
def add_to_cart(request, product_id):
    currency = request.GET.get('currency', 'RUB').upper()
    product = get_object_or_404(Product, id=product_id, is_visible=True, quantity__gt=0)
    user_profile = request.user.profile
    cart, _ = Cart.objects.get_or_create(profile=user_profile)

    # Получаем цену с учетом валюты
    annotated_product = annotate_product_prices(
        Product.objects.filter(id=product.id), 
        user_profile, 
        currency
    ).first()
    final_price = annotated_product.display_final_price if annotated_product else product.price

    cart_item, created = CartItem.objects.get_or_create(
        cart=cart, 
        product=product,
        defaults={'quantity': 1}
    )

    return JsonResponse({
        'success': True,
        'total_items': cart.items.count(),
        'price': str(final_price.quantize(Decimal('0.00'))),
        'currency': currency
    })



# views.py
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

@require_http_methods(["DELETE"])
def delete_from_cart(request, cart_item_id):
    try:
        currency = request.GET.get('currency', 'RUB').upper()
        user_profile = request.user.profile
        cart_item = CartItem.objects.get(id=cart_item_id, cart__profile=user_profile)
        cart_item.delete()
        
        cart_total = get_cart_total(user_profile.cart, user_profile, currency)
        
        return JsonResponse({
            'status': 'success',
            'cart_total': str(cart_total),
            'currency_symbol': '$' if currency == 'USD' else '₽'
        })
        
    except CartItem.DoesNotExist:
        return JsonResponse({
            'status': 'error',
            'error': 'Товар не найден в корзине'
        }, status=404)
        
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'error': str(e)
        }, status=500)

@login_required
def update_cart(request, cart_item_id):
    if request.method == 'POST':
        try:
            currency = request.GET.get('currency', 'RUB').upper()
            new_quantity = int(request.POST.get('quantity', 1))
            user_profile = request.user.profile
            cart_item = CartItem.objects.get(id=cart_item_id, cart__profile=user_profile)
            
            cart_item.quantity = new_quantity
            cart_item.save()

            # Получаем актуальную цену
            annotated_product = annotate_product_prices(
                Product.objects.filter(id=cart_item.product.id), 
                user_profile, 
                currency
            ).first()
            final_price = annotated_product.display_final_price if annotated_product else cart_item.product.price

            # Расчеты
            item_total = final_price * new_quantity
            cart_total = get_cart_total(user_profile.cart, user_profile, currency)
            
            return JsonResponse({
                'id': cart_item.id,
                'quantity': cart_item.quantity,
                'price': str(final_price),
                'total_price': str(item_total),
                'cart_total': str(cart_total),
                'currency': currency
            })
            
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'error': str(e)
            }, status=400)
    
@login_required
def clear_cart(request):
    if request.method == 'DELETE':
        user_profile = request.user.profile
        cart = user_profile.cart
        cart.items.all().delete()
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'fail'}, status=400)
