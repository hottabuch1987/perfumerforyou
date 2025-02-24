from django.shortcuts import render
from .models import Product
from .forms import SearchForm


# def product_list(request):
#     form = SearchForm()
#     query = request.GET.get('q')
#     products = Product.objects.all()

#     if query:
#         products = products.filter(name__icontains=query, is_visible=True)

#     return render(request, 'product/product_list.html', {'form': form, 'products': products, 'query': query})


def product_list(request):
    form = SearchForm()
    name_query = request.GET.get('name_query')
    price_query = request.GET.get('price_query')
    products = Product.objects.all()

    if name_query:
        products = products.filter(name__icontains=name_query, is_visible=True)

    if price_query:
        products = products.filter(price__icontains=price_query, is_visible=True)

    return render(request, 'product/product_list.html', {
        'form': form,
        'products': products,
        'name_query': name_query,
        'price_query': price_query
    })
