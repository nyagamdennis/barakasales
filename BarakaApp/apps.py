from django.apps import AppConfig


class BarakaappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'BarakaApp'


    def ready(self):
        import BarakaApp.signals





# class YourAppConfig(AppConfig):
#     name = 'yourapp'

#     def ready(self):
#         import yourapp.signals
