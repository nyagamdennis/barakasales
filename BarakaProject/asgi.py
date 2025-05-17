# # """
# # ASGI config for BarakaProject project.

# # It exposes the ASGI callable as a module-level variable named ``application``.

# # For more information on this file, see
# # https://docs.djangoproject.com/en/4.2/howto/deployment/asgi/
# # """

# # import os

# # from django.core.asgi import get_asgi_application

# # os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'BarakaProject.settings')

# # application = get_asgi_application()
# # BarakaProject/asgi.py


# import os
# import django
# from channels.routing import ProtocolTypeRouter, URLRouter
# from channels.auth import AuthMiddlewareStack
# from django.core.asgi import get_asgi_application
# from BarakaApp.routing import websocket_urlpatterns  # ⬅️ your app routing

# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "BarakaProject.settings")
# django.setup()

# application = ProtocolTypeRouter({
#     "http": get_asgi_application(),  # HTTP requests handled as normal
#     "websocket": AuthMiddlewareStack(
#         URLRouter(websocket_urlpatterns)  # WebSocket routes
#     ),
# })
# BarakaProject/asgi.py

import os
import django
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.core.asgi import get_asgi_application
import BarakaApp.routing  # <-- this should match your app name

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'BarakaProject.settings')
django.setup()

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            BarakaApp.routing.websocket_urlpatterns  # import from your app
        )
    ),
})
