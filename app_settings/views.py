# from django.shortcuts import render, redirect
# from django.http import JsonResponse
# import json

# # product/views.py
# from django.views.decorators.csrf import csrf_exempt  # Импортируем, если еще не импортировано

# @csrf_exempt  # Это может быть нужно, если используете fetch и CSRF
# def set_currency(request):
#     if request.method == 'POST':
#         currency = json.loads(request.body).get('currency', 'RUB').upper()
#         print(currency, "currency")
#         if currency in ['RUB', 'USD']:
#             request.session['currency'] = currency
#             return JsonResponse({'status': 'success'})
#     return JsonResponse({'status': 'error'}, status=400)



