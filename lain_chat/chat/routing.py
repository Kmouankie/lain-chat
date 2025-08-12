from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    
    re_path(
        r'ws/chat/(?P<room_name>\w+)/$',
        consumers.ChatConsumer.as_asgi(),
        name='chat_websocket'
    ),
    
    re_path(
        r'ws/layer/(?P<layer_id>[0-9a-f-]+)/$',
        consumers.LayerConsumer.as_asgi(),
        name='layer_websocket'
    ),
    
    re_path(
        r'ws/test/$',
        consumers.TestConsumer.as_asgi(),
        name='test_websocket'
    ),
]