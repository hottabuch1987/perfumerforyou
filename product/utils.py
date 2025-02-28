# markup_utils.py
from decimal import Decimal
from django.db.models import F, ExpressionWrapper, DecimalField
from app_settings.models import GlobalSettings

def annotate_product_prices(products, user_profile):
    # Всегда получаем гарантированный экземпляр GlobalSettings
    global_settings = GlobalSettings.get_instance()
    
    # Получаем наценку пользователя
    user_markup = user_profile.markup_percentage or Decimal(0)
    
    # Определяем наценку глобальная или пользовательская
    markup = user_markup if user_markup > 0 else global_settings.global_mark_up or Decimal(0)

    # Аннотация
    products = products.annotate(
        display_final_price=ExpressionWrapper(
            F('price') * (1 + markup / Decimal(100)),
            output_field=DecimalField(max_digits=12, decimal_places=2)
        )
    )
    
    return products
