# admin.py
from django.contrib import admin
from django.urls import path, reverse
from django.shortcuts import render, redirect
from django import forms
from django.contrib import messages
from django.utils.html import format_html
from .models import Supplier
from product.models import Product
import openpyxl
import xlrd
from decimal import Decimal, InvalidOperation
from tempfile import NamedTemporaryFile
import os
from openpyxl.utils.exceptions import InvalidFileException
# admin.py
from django import forms
from .utils import excel_column_to_index
from app_settings.models import GlobalSettings

#если выбрана валюта доллар долже пересчитать по курсу

# admin.py
class ImportProductsForm(forms.Form):
    excel_file = forms.FileField(
        label="Excel файл с товарами",
        help_text="Поддерживаемые форматы: .xls и .xlsx"
    )
    article_col = forms.CharField(
        label="Колонка с артикулом (например: C)",
        initial="C",
        max_length=3
    )
    name_col = forms.CharField(
        label="Колонка с названием (например: A)",
        initial="A",
        max_length=3
    )
    price_col = forms.CharField(
        label="Колонка с ценой (например: B)",
        initial="B",
        max_length=3
    )
    currency = forms.ChoiceField(
        label="Валюта в файле",
        choices=(('RUB', 'Рубль'), ('USD', 'Доллар США')),
        initial='RUB',
        widget=forms.RadioSelect
    )

    def clean(self):
        cleaned_data = super().clean()
        # Конвертация колонок
        columns = ['article_col', 'name_col', 'price_col']
        for col in columns:
            try:
                cleaned_data[f'{col}_index'] = excel_column_to_index(cleaned_data.get(col, ''))
            except ValueError:
                self.add_error(col, "Некорректное обозначение колонки")
        
        # Проверка наличия курса доллара
        currency = cleaned_data.get('currency')
        if currency == 'USD':
            global_settings = GlobalSettings.get_instance()
            if not global_settings.dollar_exchange_rate:
                self.add_error('currency', "Курс доллара не установлен в глобальных настройках")
        
        return cleaned_data


class ProductInline(admin.TabularInline):
    model = Product
    extra = 1




@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'import_products_link')
    inlines = [ProductInline]
    search_fields = ('name', 'email')

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
        form = ImportProductsForm(request.POST or None, request.FILES or None)

        if request.method == 'POST' and form.is_valid():
            tmp_file = None
            try:
                # Получаем индексы колонок
                currency = form.cleaned_data['currency']
                global_settings = GlobalSettings.get_instance()
                usd_rate = global_settings.dollar_exchange_rate
                article_col = form.cleaned_data['article_col_index']
                name_col = form.cleaned_data['name_col_index']
                price_col = form.cleaned_data['price_col_index']

                excel_file = form.cleaned_data['excel_file']
                file_extension = os.path.splitext(excel_file.name)[1].lower()

                # Обработка файла
                with NamedTemporaryFile(delete=False, suffix=file_extension) as tmp:
                    for chunk in excel_file.chunks():
                        tmp.write(chunk)
                    tmp_file = tmp.name

                rows = []
                if file_extension == '.xlsx':
                    wb = openpyxl.load_workbook(tmp_file, data_only=True, read_only=True)
                    ws = wb.active
                    rows = ws.iter_rows(min_row=2)
                elif file_extension == '.xls':
                    wb = xlrd.open_workbook(tmp_file)
                    ws = wb.sheet_by_index(0)
                    rows = [ws.row(rowx) for rowx in range(1, ws.nrows)]

                created = updated = 0
                errors = []

                for row_idx, row in enumerate(rows, start=2):
                    try:
                        # Обработка строки
                        if file_extension == '.xlsx':
                            cells = row
                            get_val = lambda cell: cell.value
                        else:
                            cells = row
                            get_val = lambda cell: cell.value

                        # Проверка наличия всех колонок
                        max_col = max(article_col, name_col, price_col)
                        if max_col >= len(cells):
                            raise IndexError(f"Недостаточно колонок в строке {row_idx}")
                        
                        


                        # Извлечение значений с обработкой None
                        article = str(get_val(cells[article_col])) if cells[article_col].value else None
                        name = str(get_val(cells[name_col])) if cells[name_col].value else None
                        price = str(get_val(cells[price_col])) if cells[price_col].value else None
                        

                        # Валидация обязательных полей
                        if not all([article, name, price]):
                            raise ValueError("Заполните все обязательные поля")
                        
                        try:
                            price_value = Decimal(str(price).replace(',', '.'))
                        except InvalidOperation as e:
                            raise ValueError(f"Некорректная цена: {str(e)}")

                        # Конвертация валюты
                        if currency == 'USD':
                            price_value = price_value * usd_rate  # Теперь price_value определена

                        # Преобразование данных
                        data = {
                            'name': name.strip(),
                            'price': price_value,
                            'article': article.strip(),
                            'supplier': supplier,
                            'is_visible': True,
                            'quantity': 100  # Добавляем значение по умолчанию
                        }

                        # Создание/обновление записи
                        _, created_flag = Product.objects.update_or_create(
                            supplier=supplier,
                            article=data['article'],
                            defaults=data
                        )

                        if created_flag:
                            created += 1
                        else:
                            updated += 1

                    except Exception as e:
                        errors.append(f"Строка {row_idx}: {str(e)}")

                # Формирование отчета
                msg = f"Успешно обработано: {created + updated} записей. Создано: {created}, Обновлено: {updated}"
                if errors:
                    msg += f" | Ошибки: {len(errors)}"
                    messages.warning(request, f"{msg} | Первые 5 ошибок: {', '.join(errors[:5])}")
                else:
                    messages.success(request, msg)

                return redirect(reverse('admin:%s_%s_changelist' % (Product._meta.app_label, Product._meta.model_name)))

            except Exception as e:
                messages.error(request, f"Ошибка обработки файла: {str(e)}")
            finally:
                if tmp_file and os.path.exists(tmp_file):
                    os.unlink(tmp_file)

        context = self.admin_site.each_context(request)
        context.update({
            'form': form,
            'supplier': supplier,
            'opts': self.model._meta,
            'title': 'Импорт товаров'
        })
        return render(request, 'admin/import_products.html', context)