from django.contrib import admin
from django.http import HttpResponse
from openpyxl import Workbook
from .models import Order, OrderItem
from django.urls import path


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1
    fields = ('product', 'quantity', 'price', 'total_price')
    
    def get_cost(self, obj):
        return obj.get_cost()
    get_cost.short_description = 'Стоимость позиции'

class OrderAdmin(admin.ModelAdmin):
    list_display = ('user', 'order_number', 'status', 'address_pvz', 'delivery')
    list_filter = ('status',)
    inlines = [OrderItemInline]
    actions = ['export_pending_orders']
    change_list_template = 'admin/orders_change_list.html'  # Добавляем кастомный шаблон

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.exclude(status='Собран')

    # Новый метод для экспорта
    def export_pending_orders(self, request, queryset):
        queryset = queryset.filter(status='Ожидает подтверждения')
        
        wb = Workbook()
        ws = wb.active
        ws.title = "Pending Orders"
        
        # Заголовки
        headers = [
            'Номер заказа', 
            'Пользователь', 
            'Статус',
            'Адрес ПВЗ', 
            'Способ доставки',
            'Общая сумма'
        ]
        ws.append(headers)
        
        # Данные
        for order in queryset:
            ws.append([
                order.order_number,
                str(order.user),
                order.get_status_display(),
                order.address_pvz,
                order.get_delivery_display(),
                order.get_total_price()
            ])
        
        # Формирование ответа
        response = HttpResponse(
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            headers={'Content-Disposition': 'attachment; filename="pending_orders.xlsx"'},
        )
        wb.save(response)
        return response
    
    export_pending_orders.short_description = "📤 Экспорт выбранных закасов (ожидающие)"

    # Добавляем URL для экспорта всех
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('export-all-pending/', self.export_all_pending, name='export_all_pending'),
        ]
        return custom_urls + urls

    def export_all_pending(self, request):
        return self.export_pending_orders(
            request, 
            Order.objects.filter(status='Ожидает подтверждения')
        )

admin.site.register(Order, OrderAdmin)
