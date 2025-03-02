from django.contrib import messages
from django.shortcuts import render
from decimal import Decimal, InvalidOperation
from .models import Product
from .forms import SearchForm
from django.contrib.auth.decorators import login_required
from .utils import annotate_product_prices  # Импортируем функцию
from app_settings.models import GlobalSettings

@login_required
def product_list(request):
    form = SearchForm()
    name_query = request.GET.get('name_query')
    price_query = request.GET.get('price_query')

    # Получаем все доступные товары
    products = Product.objects.filter(is_visible=True, quantity__gt=0)

    # Профиль пользователя
    user_profile = request.user.profile

   

    # Фильтрация
    if name_query:
        products = products.filter(name__icontains=name_query)
        


    if price_query:
        try:
            price_value = Decimal(price_query)
            products = products.filter(price__lte=price_value)
        except (ValueError, InvalidOperation):
            messages.warning(request, "Введена некорректная цена. Пожалуйста, введите число.")

    # Если после фильтрации товаров не найдено, выводим все доступные товары
    if not products.exists():
        messages.info(request, "По вашему запросу товаров не найдено. Показаны все доступные товары.")
        products = Product.objects.filter(is_visible=True, quantity__gt=0)

    # Аннотация
    products = annotate_product_prices(products, user_profile)

    return render(request, 'product/product_list.html', {
        'form': form,
        'products': products,
        'name_query': name_query,
        'price_query': price_query,
        # 'global': GlobalSettings.get_instance(),
    })

