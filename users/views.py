from django.shortcuts import redirect, render
from django.contrib.auth import login, logout
from django.views import View
from .forms import LoginUserForm, EditPasswordForm
from django.urls import reverse_lazy
from django.views.generic import UpdateView
from django.contrib.auth.views import LoginView


class LoginUser(LoginView):
    form_class = LoginUserForm
    template_name = 'users/login.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = self.get_form(self.get_form_class())
        return context


def logout_user(request):
    logout(request)
    return redirect('users:login')


class Profile(View):
    template_name = 'users/profile.html'

    def get(self, request):
        if request.user.is_authenticated:
            user = request.user.profile  # Получаем профиль текущего пользователя
            return render(request, self.template_name, {'user': user})
        else:
            return redirect('users:login')


class EditProfile(UpdateView):
    model = Profile
    form_class = EditPasswordForm
    template_name = 'users/edit_profile.html'  # Замените на ваш шаблон
    success_url = reverse_lazy('profile')

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
