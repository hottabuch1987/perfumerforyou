from .models import GlobalSettings

def global_settings(request):
    settings = GlobalSettings.get_instance()
    return {
        'global_settings': settings
    }
# settings/context_processors.py
def currency_context(request):
    return {
        'current_currency': request.GET.get('currency', 'RUB')
    }