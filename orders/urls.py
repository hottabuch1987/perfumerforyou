from django.urls import path
from .views import order_create, order_detail

app_name = 'orders'

urlpatterns = [
    path("create/", order_create, name="create_order"),
    path("order/<uuid:order_id>/", order_detail, name="detail_order"),

    
]
