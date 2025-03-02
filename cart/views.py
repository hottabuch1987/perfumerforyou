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



def get_cart_total(cart, user_profile):
    """Рассчитывает общую сумму корзины с актуальными ценами."""
    cart_items = cart.items.select_related('product').all()
    product_ids = cart_items.values_list('product_id', flat=True)
    products = Product.objects.filter(id__in=product_ids)
    annotated_products = annotate_product_prices(products, user_profile)
    price_map = {p.id: p.display_final_price for p in annotated_products}
    
    total = Decimal('0.00')
    for item in cart_items:
        item_price = price_map.get(item.product_id, item.product.price)
        total += item_price * item.quantity
    return total


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
    cart, _ = Cart.objects.get_or_create(profile=user_profile)

    # Получение актуальной цены через annotate_product_prices
    annotated_product = annotate_product_prices(Product.objects.filter(id=product.id), user_profile).first()
    final_price = annotated_product.display_final_price if annotated_product else product.price

    cart_item, created = CartItem.objects.get_or_create(
        cart=cart, 
        product=product,
        defaults={'quantity': 1}
    )

    if not created:
        messages.warning(request, f"Товар {product.name} уже в корзине.")
    else:
        messages.success(request, f"Товар {product.name} добавлен в корзину.")

    return JsonResponse({
        'success': True,
        'total_items': cart.items.count()
    })

@login_required
def update_cart(request, cart_item_id):
    if request.method == 'POST':
        new_quantity = int(request.POST.get('quantity', 1))
        user_profile = request.user.profile
        cart_item = get_object_or_404(CartItem, id=cart_item_id, cart__profile=user_profile)
        
        if new_quantity > cart_item.product.quantity:
            new_quantity = cart_item.product.quantity
            messages.warning(request, f"Максимальное количество товара {cart_item.product.name} - {new_quantity}")

        # Обновление количества
        cart_item.quantity = new_quantity
        cart_item.save()

        # Получение актуальной цены
        annotated_product = annotate_product_prices(Product.objects.filter(id=cart_item.product.id), user_profile).first()
        final_price = annotated_product.display_final_price if annotated_product else cart_item.product.price

        # Расчет сумм
        item_total = final_price * new_quantity
        cart_total = get_cart_total(user_profile.cart, user_profile)

        return JsonResponse({
            'id': cart_item.id,
            'quantity': cart_item.quantity,
            'display_final_price': str(final_price.quantize(Decimal('0.00'))),
            'total_price': str(item_total.quantize(Decimal('0.00'))),
            'cart_total': str(cart_total.quantize(Decimal('0.00')))
        })

@login_required
def delete_from_cart(request, cart_item_id):
    if request.method == 'DELETE':
        user_profile = request.user.profile
        cart_item = get_object_or_404(CartItem, id=cart_item_id, cart__profile=user_profile)
        cart_item.delete()
        
        cart_total = get_cart_total(user_profile.cart, user_profile)
        return JsonResponse({
            'status': 'success',
            'cart_total': str(cart_total.quantize(Decimal('0.00'))) if cart_total else '0.00'
        })
    
@login_required
def clear_cart(request):
    if request.method == 'DELETE':
        user_profile = request.user.profile
        cart = user_profile.cart
        cart.items.all().delete()
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'fail'}, status=400)

