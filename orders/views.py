# cart/views.py
from django.contrib import messages
from django.http import JsonResponse
from django.db import IntegrityError
from django.shortcuts import get_object_or_404, render, redirect
from django.db import transaction
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from orders.models import Order, OrderItem
from cart.models import Cart


# orders/views.py
from django.views.decorators.http import require_POST
from django.db import transaction

# orders/views.py
@login_required
def order_create(request):
    user_profile = request.user.profile
    
    if request.method == 'GET':
        cart = get_object_or_404(Cart, profile=user_profile)
        cart_items = cart.items.select_related('product')
        
        if not cart_items.exists():
            return redirect('cart:cart_view')
        
        # Добавляем выборку вариантов доставки из модели
        return render(request, 'orders/create.html', {
            'cart_items': cart_items,
            'total': sum(item.price * item.quantity for item in cart_items),
            'delivery_choices': Order.DELIVERY_WAY_CHOICES  # Передаем варианты в контекст
        })
    
    # Остальная часть представления без изменений...
    elif request.method == 'POST':
        try:
            delivery_method = request.POST.get('delivery')
            address_pvz = request.POST.get('address_pvz')

            # Проверка обязательных полей
            if not delivery_method or not address_pvz:
                messages.error(request, "Пожалуйста, заполните все обязательные поля (способ и адрес доставки).")
                return redirect('orders:create_order')

            with transaction.atomic():
                cart = Cart.objects.get(profile=user_profile)
                cart_items = cart.items.select_related('product')

                # Проверки остатков
                for item in cart_items:
                    if item.product.quantity < item.quantity:
                        messages.error(request, 
                            f"Недостаточно товара {item.product.name} (осталось: {item.product.quantity})")
                        return redirect('cart:cart_view')

                # Создание заказа
                order = Order.objects.create(
                    user=user_profile,
                    delivery=delivery_method,
                    address_pvz=address_pvz,
                    status='pending'
                )

                # Создание элементов заказа с учетом итоговой стоимости
                order_items = []
                for item in cart_items:
                    total_price = item.price * item.quantity
                    order_items.append(OrderItem(
                        order=order,
                        product=item.product,
                        price=item.price,
                        quantity=item.quantity,
                        total_price=total_price  # Сохраняем итоговую стоимость
                    ))

                OrderItem.objects.bulk_create(order_items)

                # Обновление остатков и очистка корзины
                for item in cart_items:
                    item.product.quantity -= item.quantity
                    item.product.save()
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


