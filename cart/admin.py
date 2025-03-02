from django.contrib import admin
from .models import Cart, CartItem

class CartItemInline(admin.TabularInline):  # Или admin.StackedInline для другого отображения
    model = CartItem
    extra = 1  # Количество дополнительных полей для добавления
    fields = ('product', 'quantity')  # Поля, которые будут отображаться
    # readonly_fields = ('price',)  # Поле с ценой только для чтения (если нужно)

class CartAdmin(admin.ModelAdmin):
    # Настройте отображаемые поля в списке
    list_display = ('profile', 'created_at', 'updated_at')  
    inlines = [CartItemInline]  # Включаем элементы корзины как вспомогательные

admin.site.register(Cart, CartAdmin)
