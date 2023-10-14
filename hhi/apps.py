from django.apps import AppConfig


class HhiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'hhi'

    def ready(self):
        import hhi.signals