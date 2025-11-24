# fabrica/apps.py
from django.apps import AppConfig

class FabricaConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'fabrica'

    def ready(self):
        import fabrica.signals