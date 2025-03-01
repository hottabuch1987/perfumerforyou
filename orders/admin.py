from django.contrib import admin
from .models import Order, OrderItem 

class OrderItemInline(admin.TabularInline):  # Или admin.StackedInline для другого вида
    model = OrderItem
    extra = 1  # Количество дополнительных полей для добавления
    fields = ('product', 'quantity', 'price')  # Поля, которые будут отображаться
    # readonly_fields = ('get_cost',)  # Поле с вычисленной стоимостью только для чтения

    def get_cost(self, obj):
        return obj.get_cost()
    get_cost.short_description = 'Стоимость позиции'

class OrderAdmin(admin.ModelAdmin):
    # Настройте отображаемые поля в списке
    list_display = ('user', 'order_number', 'status', 'address_pvz', 'delivery')  
    list_filter = ('status',) 
    inlines = [OrderItemInline]  # Включаем элементы заказа как вспомогательные

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.exclude(status='Собран')

admin.site.register(Order, OrderAdmin)
