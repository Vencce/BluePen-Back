# fabrica/apps.py
from django.apps import AppConfig

class FabricaConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'fabrica'

    # --- ADICIONE ESTA FUNÇÃO ---
    def ready(self):
        # Importa os signals quando a aplicação estiver pronta
        import fabrica.signals 
    # ---------------------------