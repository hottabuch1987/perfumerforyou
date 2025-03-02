# cart/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from decimal import Decimal
from .models import Cart, CartItem
from product.models import Product
from app_settings.models import GlobalSettings
from product.utils import annotate_product_prices
from django.http import JsonResponse


@login_required
def cart_view(request):
    user_profile = request.user.profile
    cart, created = Cart.objects.get_or_create(profile=user_profile)
    cart_items = cart.items.select_related('product').all()
    
    # Получаем актуальные цены
    products = Product.objects.filter(
        id__in=cart_items.values_list('product_id', flat=True)
    )
    annotated_products = annotate_product_prices(products, user_profile)
    price_map = {p.id: p.display_final_price for p in annotated_products}
    
    # Обновляем текущие цены и считаем сумму по актуальным ценам
    total = Decimal('0.00')
    for item in cart_items:
        item.current_price = price_map.get(item.product_id, item.product.price)
        total += item.current_price * item.quantity  # Используем ТЕКУЩИЕ цены
    
    return render(request, 'cart/cart.html', {
        'cart_items': cart_items,
        'total': total,
        'global': GlobalSettings.get_instance(),
    })


@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id, is_visible=True, quantity__gt=0)
    user_profile = request.user.profile
    global_settings = GlobalSettings.get_instance()

    # Рассчитываем цену с наценкой
    markup = user_profile.markup_percentage if user_profile.markup_percentage > 0 else global_settings.global_mark_up
    final_price = product.price * (1 + markup / Decimal(100))

    # Получаем или создаем корзину
    cart, created = Cart.objects.get_or_create(profile=user_profile)

    # Пытаемся получить существующий элемент корзины
    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        defaults={'price': final_price, 'quantity': 1}  # Добавляем 1 единицу товара
    )

    if not created:
        # Если товар уже в корзине, не добавляем его количество, т.к. мы хотим добавлять только по 1
        messages.warning(request, f"Товар {product.name} уже в корзине.")
    else:
        messages.success(request, f"Товар {product.name} добавлен в корзину.")

    total_items = cart.items.count()  # Подсчитываем общее количество товаров в корзине

    return JsonResponse({
        'success': True,
        'total_items': total_items,  # Возвращаем общее количество товаров в корзине
    })



@login_required
def update_cart(request, cart_item_id):
    if request.method == 'POST':
        new_quantity = int(request.POST.get('quantity', 1))
        user_profile = request.user.profile
        cart_item = get_object_or_404(CartItem, id=cart_item_id, cart__profile=user_profile)

        if new_quantity > cart_item.product.quantity:
            new_quantity = cart_item.product.quantity
            messages.warning(request, f"Максимальное количество товара {cart_item.product.name} - {cart_item.product.quantity}")

        global_settings = GlobalSettings.get_instance()
        markup = user_profile.markup_percentage if user_profile.markup_percentage > 0 else global_settings.global_mark_up
        final_price = cart_item.product.price * (1 + markup / Decimal(100))

        cart_item.quantity = new_quantity
        cart_item.price = final_price
        cart_item.save()

        # Calculate totals
        cart = user_profile.cart
        cart_items = cart.items.all()
        cart_total = sum(item.price * item.quantity for item in cart_items)

        return JsonResponse({
            'id': cart_item.id,
            'quantity': cart_item.quantity,
            'display_final_price': str(final_price.quantize(Decimal('0.00'))),
            'total_price': str((final_price * cart_item.quantity).quantize(Decimal('0.00'))),
            'cart_total': str(cart_total.quantize(Decimal('0.00')))
        })

    return JsonResponse({'status': 'fail'}, status=400)


@login_required
def delete_from_cart(request, cart_item_id):
    if request.method == 'DELETE':
        user_profile = request.user.profile
        cart_item = get_object_or_404(CartItem, id=cart_item_id, cart__profile=user_profile)
        cart_item.delete()

        # Recalculate cart total
        cart = user_profile.cart
        cart_items = cart.items.all()
        cart_total = sum(item.price * item.quantity for item in cart_items) if cart_items else 0

        return JsonResponse({
            'status': 'success',
            'cart_total': str(cart_total.quantize(Decimal('0.00'))) if cart_total else '0.00'
        })
    return JsonResponse({'status': 'fail'}, status=400)

@login_required
def clear_cart(request):
    if request.method == 'DELETE':
        user_profile = request.user.profile
        cart = user_profile.cart
        cart.items.all().delete()
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'fail'}, status=400)

