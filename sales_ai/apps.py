from django.apps import AppConfig


class SalesAiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'sales_ai'



    def ready(self):
        import sales_ai.signals  # 👈 Make sure this is imported