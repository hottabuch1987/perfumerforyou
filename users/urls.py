from django.urls import path
from django.views.generic import RedirectView
from .views import *

app_name = 'accounts'

urlpatterns = [
    path('', RedirectView.as_view(url='/login/')),
    path('login/', LoginUser.as_view(), name='login'),
    path('accounts/profile/', Profile.as_view(), name='profile'),
    path('accounts/profile/cart/', Profile.as_view(), name='cart'),
    path('accounts/logout/', logout_user, name='logout'),
    path('accounts/edit-profile/', EditProfile.as_view(), name='edit'),
]
