from django.contrib import admin
from .models import Supplier
from product.models import Product

class ProductInline(admin.TabularInline):
    model = Product
    extra = 1  # Количество пустых форм для добавления новых элементов

class SupplierAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'created', 'updated')
    inlines = [ProductInline]
    search_fields = ('name', 'email')

    fieldsets = (
        (None, {
            'fields': ('name', 'email'),
        }),
    )

admin.site.register(Supplier, SupplierAdmin)
