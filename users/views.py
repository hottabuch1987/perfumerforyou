from django.contrib import messages
from django.shortcuts import redirect, render
from django.contrib.auth import logout
from django.views import View
from .forms import LoginUserForm, EditPasswordForm
from .models import Profile
from orders.models import Order
from django.urls import reverse_lazy
from django.views.generic import UpdateView
from django.contrib.auth.views import LoginView
from django.contrib.auth import update_session_auth_hash
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.views.generic import UpdateView


from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.shortcuts import redirect

class LoginUser(LoginView):
    form_class = LoginUserForm
    template_name = 'users/login.html'
    success_url = reverse_lazy('users:profile')
    redirect_authenticated_user = True  # Автоматический редирект для авторизованных

    def form_valid(self, form):
        remember_me = form.cleaned_data.get('remember_me', False)
        
        # Настройка времени жизни сессии и куки
        if remember_me:
            self.request.session.set_expiry(1209600)  # 2 недели
            self.request.session.modified = True  # Принудительное обновление
        else:
            self.request.session.set_expiry(0)  # Сессия до закрытия браузера
            self.request.session.modified = True
            
        return super().form_valid(form)

    # Дополнительная проверка для GET-запросов
    def get(self, request, *args, **kwargs):
        if self.request.user.is_authenticated:
            return redirect(self.get_success_url())
        return super().get(request, *args, **kwargs)
    


def logout_user(request):
    # Сброс сессии
    request.session.flush()
    messages.success(request, "Вы успешно вышли из системы!")
    return redirect('users:login')


@method_decorator(login_required, name='dispatch')
class Profile(View):
    template_name = 'users/profile.html'

    def get(self, request):
        
        user = request.user.profile  # Получаем профиль текущего пользователя
        orders = Order.objects.filter(user=request.user.profile)
        return render(request, self.template_name, {'user': user, 'orders': orders})




@method_decorator(login_required, name='dispatch')
class EditProfile(UpdateView):
    model = Profile
    form_class = EditPasswordForm
    template_name = 'users/edit_profile.html'  # Замените на ваш шаблон

    def get_object(self, queryset=None):
        # Получаем профиль текущего пользователя
        return self.request.user.profile  # Предполагается, что профиль связан с пользователем
    
    def form_valid(self, form):
        new_password = form.cleaned_data['new_password']
        user = self.request.user

        # Устанавливаем новый пароль
        user.set_password(new_password)
        user.save()

        # Обновляем сессию, чтобы сохранить аутентификацию пользователя
        update_session_auth_hash(self.request, user) 
        
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('users:profile')
