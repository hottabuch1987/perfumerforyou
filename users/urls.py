from django.urls import path
from django.views.generic import RedirectView
from .views import *

app_name = 'users'

urlpatterns = [
    path('', LoginUser.as_view(), name='login'),
    path('accounts/profile/', Profile.as_view(), name='profile'),
    path('accounts/logout/', logout_user, name='logout'),
    path('accounts/edit-profile/', EditProfile.as_view(), name='edit'),
   


]
