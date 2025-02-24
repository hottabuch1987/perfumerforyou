from django.urls import path
from django.views.generic import RedirectView
from .views import *

app_name = 'users'

urlpatterns = [
    # path('', RedirectView.as_view(url='/login/')),
    path('', LoginUser.as_view(), name='login'),
    path('accounts/profile/', Profile.as_view(), name='profile'),
    path('accounts/logout/', logout_user, name='logout'),
    path('accounts/edit-profile/', EditProfile.as_view(), name='edit'),
    # path('accounts/profile/cart/', cart_view, name='cart-view'),
    # path('accounts/profile/add/', card_add, name='add-to-cart'),
    # path('accounts/profile/delete/', cart_delete, name='delete-to-cart'),
    # path('accounts/profile/update/', cart_update, name='update-to-cart'),


]
