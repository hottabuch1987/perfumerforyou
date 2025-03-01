from django.contrib import admin
from django.urls import path, reverse
from django.shortcuts import render, redirect
from django import forms
from django.contrib import messages
from django.utils.html import format_html
from .models import Supplier
from product.models import Product
import openpyxl
from decimal import Decimal

class ImportProductsForm(forms.Form):
    excel_file = forms.FileField(label="Excel файл с товарами")

@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'import_products_link')
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                '<path:object_id>/import-products/',
                self.admin_site.admin_view(self.import_products_view),
                name='import_products'
            ),
        ]
        return custom_urls + urls
    
    def import_products_link(self, obj):
        return format_html(
            '<a href="{}" class="button">📥 Импорт товаров</a>',
            reverse('admin:import_products', args=[obj.pk])
        )
    import_products_link.short_description = "Импорт"
    
    def import_products_view(self, request, object_id):
        supplier = Supplier.objects.get(pk=object_id)
        
        if request.method == 'POST':
            form = ImportProductsForm(request.POST, request.FILES)
            if form.is_valid():
                try:
                    wb = openpyxl.load_workbook(
                        form.cleaned_data['excel_file'],
                        data_only=True
                    )
                    ws = wb.active
                    
                    created = updated = 0
                    errors = []
                    
                    for row in ws.iter_rows(min_row=2):
                        try:
                            data = {
                                'name': row[0].value,
                                'price': Decimal(str(row[1].value)),
                                'article': row[2].value,
                                'quantity': int(row[3].value),
                                'supplier': supplier,
                                'is_visible': True
                            }
                            
                            obj, created_flag = Product.objects.update_or_create(
                                supplier=supplier,
                                article=data['article'],
                                defaults=data
                            )
                            
                            if created_flag:
                                created += 1
                            else:
                                updated += 1
                                
                        except Exception as e:
                            errors.append(f"Строка {row[0].row}: {str(e)}")
                    
                    msg = f"Импорт завершен. Создано: {created}, Обновлено: {updated}"
                    if errors:
                        msg += f" | Ошибки: {', '.join(errors)}"
                        messages.warning(request, msg)
                    else:
                        messages.success(request, msg)
                        
                    # Исправленный редирект
                    return redirect(reverse(
                        'admin:%s_%s_changelist' % (
                            Product._meta.app_label,
                            Product._meta.model_name
                        )
                    ))
                
                except Exception as e:
                    messages.error(request, f"Ошибка обработки файла: {str(e)}")
                    return redirect('.')
        
        form = ImportProductsForm()
        
        context = self.admin_site.each_context(request)
        context.update({
            'form': form,
            'supplier': supplier,
            'opts': self.model._meta,
            'Product': Product,  # Передаем модель в контекст
            'title': 'Импорт товаров'
        })
        return render(request, 'admin/import_products.html', context)