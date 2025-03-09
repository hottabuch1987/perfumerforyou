# product/utils.py
from decimal import Decimal
from django.db.models import F, ExpressionWrapper, DecimalField
from app_settings.models import GlobalSettings




def annotate_product_prices(products, user_profile, currency='RUB'):
    global_settings = GlobalSettings.get_instance()
    user_markup = user_profile.markup_percentage or Decimal(0)
    markup = user_markup if user_markup > 0 else global_settings.global_mark_up
    
    base_price = F('price') * (1 + markup / Decimal(100))

    
    if currency == 'USD':
        final_price = base_price / global_settings.dollar_exchange_rate
    else:
        final_price = base_price

    return products.annotate(
        display_final_price=ExpressionWrapper(
            final_price,
            output_field=DecimalField(max_digits=12, decimal_places=2)
        )
    )