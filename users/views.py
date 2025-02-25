from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth import login, logout
from django.views import View
from .forms import LoginUserForm, EditPasswordForm
from django.urls import reverse_lazy
from django.views.generic import UpdateView
from django.contrib.auth.views import LoginView
from product.models import Product
from orders.models import Order
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib import messages



class LoginUser(LoginView):
    form_class = LoginUserForm
    template_name = 'users/login.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = self.get_form(self.get_form_class())
        return context


def logout_user(request):
    messages.success(request, f"Вы вышли из системы {request.user.profile}!")
    logout(request)
    return redirect('users:login')


@method_decorator(login_required, name='dispatch')
class Profile(View):
    template_name = 'users/profile.html'

    def get(self, request):
        
        user = request.user.profile  # Получаем профиль текущего пользователя
        orders = Order.objects.filter(user=request.user.profile)
        messages.success(request, f"Вы вошли в систему {request.user.profile}!")
        return render(request, self.template_name, {'user': user, 'orders': orders})


@method_decorator(login_required, name='dispatch')
class EditProfile(UpdateView):
    model = Profile
    form_class = EditPasswordForm
    template_name = 'users/edit_profile.html'  # Замените на ваш шаблон
    success_url = reverse_lazy('users:profile')

    def get_object(self, queryset=None):
        # Получаем профиль текущего пользователя
        return self.request.user.profile

    def form_valid(self, form):
        new_password = form.cleaned_data['new_password']
        user = self.request.user

        # Устанавливаем новый пароль
        user.set_password(new_password)
        user.save()
        
        return super().form_valid(form)
