from django.contrib import admin
from .models import Product


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('supplier', 'name',  'price', 'article', 'is_visible', 'quantity', 'updated_at')
    list_filter = ('article', 'name')
    search_fields = ('article', 'name', 'price')
    list_editable = ('is_visible',)
    
    fieldsets = (
        (None, {
            'fields': ('supplier', 'name',  'quantity', 'price', 'article', 'is_visible'),
        }),
    )

    def supplier_name(self, obj):
        return obj.supplier.name if obj.supplier else 'Нет поставщика'
        
    supplier_name.short_description = 'Название поставщика'  

    list_display = ('supplier_name', 'name',  'quantity',  'price', 'article', 'is_visible')



   
    