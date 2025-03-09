from django.contrib import admin
from .models import Product


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('supplier_name', 'name', 'quantity', 'price', 'article',  'updated_at', 'is_visible')
    search_fields = ('article', 'name', 'price')
    list_editable = ('is_visible',)
    readonly_fields = ('updated_at',)

    fieldsets = (
        (None, {
            'fields': ('supplier', 'name', 'quantity', 'price', 'article', 'is_visible', 'updated_at'),
        }),
    )

    def supplier_name(self, obj):
        return obj.supplier.name if obj.supplier else 'Нет поставщика'

    supplier_name.short_description = 'Название поставщика'  

    