from django.apps import AppConfig


class MyAppConfig(AppConfig):
    name = 'backend'

    def ready(self):
        from .main_functions import startup
        startup.start_app()
