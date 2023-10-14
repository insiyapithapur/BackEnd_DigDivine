from django.apps import AppConfig


class ProteinworldConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'proteinWorld'

    def ready(self):
        import proteinWorld.signals
