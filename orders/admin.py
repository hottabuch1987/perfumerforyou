from django.contrib import admin
from .models import Order, OrderItem 


class OrderAdmin(admin.ModelAdmin):
    # Настройте отображаемые поля в списке
    list_display = ('user', 'order_number', 'status', 'address_pvz', 'delivery')  
    list_filter = ('status',) 

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.exclude(status='Собран')

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'product', 'price', 'quantity', 'get_cost')
    list_display_links = ('id', 'order')
    search_fields = (
        'product__name', 
        'order__id'
    )
    list_filter = ('product',)
    raw_id_fields = ('product',)
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('order', 'product', 'quantity')
        }),
        ('Стоимость', {
            'fields': ('price',),
            'classes': ('collapse',)
        }),
    )
    
    def get_cost(self, obj):
        return obj.get_cost()
    get_cost.short_description = 'Стоимость позиции'

admin.site.register(Order, OrderAdmin)
