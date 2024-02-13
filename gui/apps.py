from django.apps import AppConfig


class GuiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'gui'

    # Ensure that the signal handlers in signals.py are registered when Django starts
    def ready(self):
        import gui.signals
