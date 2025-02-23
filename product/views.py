from django.shortcuts import render
from django.views.generic import ListView
from .models import Product

class ProductListView(ListView):
    model = Product
    template_name = 'product_list.html'  # Указываем шаблон для отображения
    context_object_name = 'products'  # Имя переменной, доступной в шаблоне
    paginate_by = 10  # Число товаров на странице (при необходимости)

    def get_queryset(self):
        # Возвращаем только видимые товары
        return Product.objects.filter(is_visible=True)
