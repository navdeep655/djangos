from django.urls import re_path
from . import consumers

# websocket_urlpatterns = [
#     re_path(r'ws/chat/(?P<room_name>\w+)/(?P<username>\w+)/$', consumers.ChatConsumer.as_asgi()),
# ]
websocket_urlpatterns = [
    re_path(r"ws/chat/(?P<room_id>\d+)/$", consumers.ChatConsumer.as_asgi()),
]

# websocket_urlpatterns=[
#     re_path(r'ws/chat/$',consumers.chat.as_asgi())
# ]