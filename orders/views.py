# cart/views.py
from django.contrib import messages
from django.shortcuts import get_object_or_404, render, redirect
from django.db import transaction
from django.contrib.auth.decorators import login_required
from orders.models import Order, OrderItem
from cart.models import Cart
from decimal import Decimal
from product.utils import annotate_product_prices
from product.models import Product

# orders/views.py
@login_required
def order_create(request):
    user_profile = request.user.profile
    
    if request.method == 'GET':
        cart = get_object_or_404(Cart, profile=user_profile)
        cart_items = cart.items.select_related('product')
        
        if not cart_items.exists():
            return redirect('cart:cart_view')
        
        # Получаем актуальные цены через аннотации
        product_ids = cart_items.values_list('product_id', flat=True)
        products = Product.objects.filter(id__in=product_ids)
        annotated_products = annotate_product_prices(products, user_profile)
        price_map = {p.id: p.display_final_price for p in annotated_products}
        
        # Рассчитываем общую сумму с актуальными ценами
        total = Decimal('0.00')
        for item in cart_items:
            item.current_price = price_map.get(item.product_id, item.product.price)
            total += item.current_price * item.quantity

        return render(request, 'orders/create.html', {
            'cart_items': cart_items,
            'total': total,
            'delivery_choices': Order.DELIVERY_WAY_CHOICES
        })
    
    elif request.method == 'POST':
        try:
            delivery_method = request.POST.get('delivery')
            address_pvz = request.POST.get('address_pvz')

            if not delivery_method or not address_pvz:
                messages.error(request, "Пожалуйста, заполните все обязательные поля.")
                return redirect('orders:create_order')

            with transaction.atomic():
                cart = Cart.objects.get(profile=user_profile)
                cart_items = cart.items.select_related('product')
                product_ids = cart_items.values_list('product_id', flat=True)
                
                # Получаем актуальные цены для всех товаров в корзине
                annotated_products = annotate_product_prices(
                    Product.objects.filter(id__in=product_ids), 
                    user_profile
                )
                price_map = {p.id: p.display_final_price for p in annotated_products}

                # Проверка остатков и подготовка данных
                order_items = []
                for item in cart_items:
                    current_price = price_map.get(item.product_id, item.product.price)
                    
                    if item.product.quantity < item.quantity:
                        messages.error(request, 
                            f"Недостаточно товара {item.product.name} (осталось: {item.product.quantity})")
                        return redirect('cart:cart_view')
                    
                    order_items.append(OrderItem(
                        order=None,  # Будет установлено позже
                        product=item.product,
                        price=current_price,
                        quantity=item.quantity,
                        total_price=current_price * item.quantity
                    ))

                # Создание заказа и привязка элементов
                order = Order.objects.create(
                    user=user_profile,
                    delivery=delivery_method,
                    address_pvz=address_pvz,
                    status='pending'
                )
                
                # Обновляем order для всех элементов
                for item in order_items:
                    item.order = order
                OrderItem.objects.bulk_create(order_items)

                # Обновление остатков и очистка корзины
                for item in cart_items:
                    item.product.quantity -= item.quantity
                    item.product.save(update_fields=['quantity'])
                cart.items.all().delete()

                messages.success(request, f"Заказ #{order.order_number} успешно создан!")
                return redirect('orders:detail_order', order_id=order.id)

        except Exception as e:
            messages.error(request, f"Ошибка создания заказа: {str(e)}")
            return redirect('cart:cart_view')

            
@login_required
def order_detail(request, order_id):
    # Получаем заказ конкретного пользователя
    order = get_object_or_404(
        Order, 
        id=order_id,
        user=request.user.profile
    )
    
    # Получаем все товары в заказе
    order_items = OrderItem.objects.filter(order=order).select_related('product')
    
    # Рассчитываем общую стоимость
    total_price = order.get_total_price
    
    context = {
        'order': order,
        'order_items': order_items,
        'total_price': total_price,
    }
    
    return render(request, 'orders/detail.html', context)


