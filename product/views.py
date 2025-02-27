from django.contrib import messages
from django.shortcuts import render
from decimal import Decimal, InvalidOperation
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
    products = Product.objects.filter(is_visible=True, quantity__gt=0)
    
    # Всегда получаем гарантированный экземпляр GlobalSettings
    global_settings = GlobalSettings.get_instance()
    
    # Профиль пользователя
    user_profile = request.user.profile
    user_markup = user_profile.markup_percentage or Decimal(0)
    
    # Определяем марку
    markup = user_markup if user_markup > 0 else global_settings.global_mark_up or Decimal(0)
    
    # Аннотация
    products = products.annotate(
        display_final_price=ExpressionWrapper(
            F('price') * (1 + markup / Decimal(100)),
            output_field=DecimalField(max_digits=12, decimal_places=2)
        )
    )
    
    # Фильтрация

    if name_query:
        products = products.filter(name__icontains=name_query)
       
    
    if price_query:
        try:
            price_value = Decimal(price_query)
            # показываю все цены до указанного в поле поиска
            products = products.filter(price__lte=price_value)
        except (ValueError, InvalidOperation):
            # Обработка ошибок преобразования
            
            messages.error(request, "Введена некорректная цена. Пожалуйста, введите число.")

    return render(request, 'product/product_list.html', {
        'form': form,
        'products': products,
        'name_query': name_query,
        'price_query': price_query,
        'global': global_settings,
        
    })
