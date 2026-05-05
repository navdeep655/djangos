from django.apps import AppConfig


class App2Config(AppConfig):
    default_auto_fields="djnago.db.models.BigAutoField"
    name = 'account'

    def ready(self):
        import account.signals
