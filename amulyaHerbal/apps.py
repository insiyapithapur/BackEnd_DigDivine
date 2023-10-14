from django.apps import AppConfig


class AmulyaherbalConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'amulyaHerbal'

    def ready(self):
        import amulyaHerbal.signals