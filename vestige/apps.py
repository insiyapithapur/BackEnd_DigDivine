from django.apps import AppConfig


class VestigeConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'vestige'

    def ready(self):
        import vestige.signals