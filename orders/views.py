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

                # Создание элементов заказа
                OrderItem.objects.bulk_create([
                    OrderItem(
                        order=order,
                        product=item.product,
                        price=item.price,
                        quantity=item.quantity
                    ) for item in cart_items
                ])

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
# orders/views.py
# from django.contrib import messages
# from django.shortcuts import render, redirect, get_object_or_404
# from django.db import transaction
# from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
# from .models import Order, OrderItem
# from cart.cart import Cart
# from django.http import Http404
# from django.db.models import F


# def order_list(request):
#     """Список заказов пользователя с пагинацией"""
#     if not request.user.is_authenticated:
#         messages.error(request, "Для просмотра заказов необходимо авторизоваться")
#         return redirect("users:login")
    
#     orders = Order.objects.filter(
#         user=request.user.profile
#     ).select_related('user').prefetch_related('items').order_by('-created')
        
#     return render(request, 'orders/list_order.html', {'orders': orders})


# def order_create(request):
#     """Создание заказа с обработкой GET и POST запросов"""
#     if not request.user.is_authenticated:
#         messages.error(request, "Для оформления заказа необходимо авторизоваться")
#         return redirect("users:login")
    
#     cart = Cart(request)
    
#     if not cart:
#         messages.warning(request, "Ваша корзина пуста")
#         return redirect("product:product_list")
    
#     if request.method == 'POST':
#         address_pvz = request.POST.get('address_pvz')
#         delivery = request.POST.get('delivery') 
#         if not address_pvz or not delivery:
#             messages.warning(request, "Пожалуйста, заполните все обязательные поля.")
#             return render(request, 'orders/create_order.html', {'cart': cart})
#         try:
#             with transaction.atomic():
#                 order = Order.objects.create(
#                     user=request.user.profile,
#                     status='pending',
#                     address_pvz=address_pvz, 
#                     delivery=delivery
#                 )
                
#                 # Создаем элементы заказа и обновляем количество товаров
#                 for item in cart:
#                     product = item['product']
#                     quantity = item['qty']
                    
#                     # Проверка доступного количества
#                     if product.quantity < quantity:
#                         raise ValueError(
#                             f"Недостаточно товара '{product.name}'. "
#                             f"Доступно: {product.quantity}, Заказано: {quantity}"
#                         )
                    
#                     # Создаем запись в заказе
#                     OrderItem.objects.create(
#                         order=order,
#                         product=product,
#                         price=item['price'],
#                         quantity=quantity
#                     )
                    
#                     # Уменьшаем количество товара на складе
#                     product.quantity = F('quantity') - quantity
#                     product.save(update_fields=['quantity'])
                
#                 # Очищаем корзину только после успешного оформления
#                 cart.clear()
                
#                 messages.success(request, f"Заказ №{order.order_number} успешно оформлен!")
#                 return redirect("orders:detail_order", order_id=order.id)
        
#         except Exception as e:
#             messages.error(request, f"Ошибка при создании заказа: {str(e)}")
#             return redirect("cart:cart-view")
    
#     # GET запрос - показать страницу подтверждения
#     return render(request, 'orders/create_order.html', {'cart': cart})



# def order_detail(request, order_id):
    """Детализация заказа с проверкой прав доступа"""
    try:
        order = get_object_or_404(
            Order.objects.select_related('user').prefetch_related('items'),
            id=order_id,
            user=request.user.profile
        )
    except Http404:
        messages.error(request, "Заказ не найден или у вас нет доступа")
        return redirect('orders:order_list')
    
    return render(request, "orders/detail_order.html", {"order": order})