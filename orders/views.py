# orders/views.py
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.db import transaction
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import Order, OrderItem
from cart.cart import Cart
from django.http import Http404
from django.db.models import F


def order_list(request):
    """Список заказов пользователя с пагинацией"""
    if not request.user.is_authenticated:
        messages.error(request, "Для просмотра заказов необходимо авторизоваться")
        return redirect("users:login")
    
    orders = Order.objects.filter(
        user=request.user.profile
    ).select_related('user').prefetch_related('items').order_by('-created')
        
    return render(request, 'orders/list_order.html', {'orders': orders})


def order_create(request):
    """Создание заказа с обработкой GET и POST запросов"""
    if not request.user.is_authenticated:
        messages.error(request, "Для оформления заказа необходимо авторизоваться")
        return redirect("users:login")
    
    cart = Cart(request)
    
    if not cart:
        messages.warning(request, "Ваша корзина пуста")
        return redirect("product:product_list")
    
    if request.method == 'POST':
        address_pvz = request.POST.get('address_pvz')
        delivery = request.POST.get('delivery') 
        if not address_pvz or not delivery:
            messages.warning(request, "Пожалуйста, заполните все обязательные поля.")
            return render(request, 'orders/create_order.html', {'cart': cart})
        try:
            with transaction.atomic():
                order = Order.objects.create(
                    user=request.user.profile,
                    status='pending',
                    address_pvz=address_pvz, 
                    delivery=delivery
                )
                
                # Создаем элементы заказа и обновляем количество товаров
                for item in cart:
                    product = item['product']
                    quantity = item['qty']
                    
                    # Проверка доступного количества
                    if product.quantity < quantity:
                        raise ValueError(
                            f"Недостаточно товара '{product.name}'. "
                            f"Доступно: {product.quantity}, Заказано: {quantity}"
                        )
                    
                    # Создаем запись в заказе
                    OrderItem.objects.create(
                        order=order,
                        product=product,
                        price=item['price'],
                        quantity=quantity
                    )
                    
                    # Уменьшаем количество товара на складе
                    product.quantity = F('quantity') - quantity
                    product.save(update_fields=['quantity'])
                
                # Очищаем корзину только после успешного оформления
                cart.clear()
                
                messages.success(request, f"Заказ №{order.order_number} успешно оформлен!")
                return redirect("orders:detail_order", order_id=order.id)
        
        except Exception as e:
            messages.error(request, f"Ошибка при создании заказа: {str(e)}")
            return redirect("cart:cart-view")
    
    # GET запрос - показать страницу подтверждения
    return render(request, 'orders/create_order.html', {'cart': cart})



def order_detail(request, order_id):
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