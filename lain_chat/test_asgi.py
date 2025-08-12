#!/usr/bin/env python
import os
import sys
import django

# Ajouter le projet au path
sys.path.append('.')

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lain_chat.settings')
django.setup()

print("🧪 Test d'import ASGI")
print("=" * 40)

try:
    from lain_chat.asgi import application
    print("✅ ASGI import OK")
    print(f"Type: {type(application)}")
except Exception as e:
    print(f"❌ ASGI import ERROR: {e}")
    import traceback
    traceback.print_exc()

try:
    from chat.consumers import ChatConsumer
    print("ChatConsumer import OK")
except Exception as e:
    print(f" ChatConsumer import ERROR: {e}")
    import traceback
    traceback.print_exc()

try:
    from chat.routing import websocket_urlpatterns
    print(" Routing import OK")
    print(f"Patterns: {len(websocket_urlpatterns)} found")
    for pattern in websocket_urlpatterns:
        print(f"  - {pattern.pattern.pattern}")
except Exception as e:
    print(f" Routing import ERROR: {e}")
    import traceback
    traceback.print_exc()

print("\ Configuration:")
from django.conf import settings
print(f"ASGI_APPLICATION: {getattr(settings, 'ASGI_APPLICATION', 'NOT SET')}")
print(f"CHANNEL_LAYERS: {getattr(settings, 'CHANNEL_LAYERS', 'NOT SET')}")

print("\n Test terminé")