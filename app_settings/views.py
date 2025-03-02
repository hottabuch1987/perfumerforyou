from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.shortcuts import render, redirect
from django.contrib import messages
from django.views import View
from .models import GlobalSettings
from .forms import GlobalSettingsForm  # Предполагается, что у вас есть форма для настройки

@method_decorator(login_required, name='dispatch')
class GlobalSettingsView(View):
    template_name = 'admin/global_settings.html'  # Укажите путь к вашему шаблону

    def get(self, request):
        settings = GlobalSettings.get_instance()
        form = GlobalSettingsForm(instance=settings)
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        settings = GlobalSettings.get_instance()
        form = GlobalSettingsForm(request.POST, instance=settings)
        
        if form.is_valid():
            result = form.save()  # Попытка сохранить настройки
            if isinstance(result, str):
                # Если вернулось сообщение
                messages.error(request, result)
                return redirect('global_settings')  # Замените на нужный вам URL
            else:
                messages.success(request, _("Настройки успешно обновлены."))
                return redirect('global_settings')  # Замените на нужный вам URL
        else:
            messages.error(request, _("Исправьте ошибки в форме."))

        return render(request, self.template_name, {'form': form})
