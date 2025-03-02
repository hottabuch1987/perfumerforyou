from .models import GlobalSettings

def global_settings(request):
    settings = GlobalSettings.get_instance()
    return {
        'global_settings': settings
    }
