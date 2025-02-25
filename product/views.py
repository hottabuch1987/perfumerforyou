from django.shortcuts import render
from decimal import Decimal
from django.db.models import F, ExpressionWrapper, DecimalField
from .models import Product
from .forms import SearchForm
from django.contrib.auth.decorators import login_required
from app_settings.models import GlobalSettings


@login_required
def product_list(request):
    form = SearchForm()
    name_query = request.GET.get('name_query')
    price_query = request.GET.get('price_query')
    products = Product.objects.filter(is_visible=True)
    
    # Всегда получаем гарантированный экземпляр GlobalSettings
    global_settings = GlobalSettings.get_instance()
    
    # Профиль пользователя
    user_profile = request.user.profile
    user_markup = user_profile.markup_percentage or Decimal(0)
    global_markup = global_settings.global_mark_up if global_settings else Decimal(0)
    
    # Общая накрутка
    total_markup = user_markup + global_markup
    
    # Аннотация
    products = products.annotate(
        display_final_price=ExpressionWrapper(
            F('price') * (1 + total_markup / Decimal(100)),
            output_field=DecimalField(max_digits=12, decimal_places=2)
        )
    )

    # Фильтрация
    if name_query:
        products = products.filter(name__icontains=name_query)
    
    if price_query:
        products = products.filter(price__icontains=price_query)
    
    return render(request, 'product/product_list.html', {
        'form': form,
        'products': products,
        'name_query': name_query,
        'price_query': price_query,
        'global': global_settings
    })