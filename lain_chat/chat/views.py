from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, Http404
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.conf import settings
import json
import uuid
import hashlib
import random

try:
    from anonymization.models import TrueAnonymousLayer, AnonymousMessage
    ANONYMIZATION_AVAILABLE = True
except ImportError:
    ANONYMIZATION_AVAILABLE = False


LAIN_ROOMS = {
    'general': {
        'name': 'General',
        'description': 'The main Wired connection point',
        'theme': 'default',
        'corruption_level': 0,
        'reality_anchor': True
    },
    'cyberia': {
        'name': 'Cyberia',
        'description': 'The club where reality blurs with dreams',
        'theme': 'cyberia',
        'corruption_level': 2,
        'reality_anchor': False
    },
    'protocol7': {
        'name': 'Protocol 7',
        'description': 'The consciousness layer',
        'theme': 'protocol',
        'corruption_level': 1,
        'reality_anchor': True
    },
    'knights': {
        'name': 'Knights of Eastern Calculus',
        'description': 'Digital purity',
        'theme': 'knights',
        'corruption_level': 0,
        'reality_anchor': True
    },
    'wired': {
        'name': 'The Wired',
        'description': 'Pure information space',
        'theme': 'wired',
        'corruption_level': 3,
        'reality_anchor': False
    },
    'navi': {
        'name': 'NAVI Interface',
        'description': 'Direct neural interface layer',
        'theme': 'navi',
        'corruption_level': 1,
        'reality_anchor': True
    },
    'phantom': {
        'name': 'Phantom Layer',
        'description': 'Between digital and analog existence',
        'theme': 'ph',
        'corruption_level': 4,
        'reality_anchor': False
    },
    'masami': {
        'name': 'Masami Domain',
        'description': ' god realm',
        'theme': 'undefined',
        'corruption_level': 5,
        'reality_anchor': False
    }
}

def index(request):
    """Page d'accueil avec liste des rooms"""
    return render(request, 'chat/index.html', {
        'rooms': LAIN_ROOMS,
        'total_rooms': len(LAIN_ROOMS)
    })

def room(request, room_name):
    if room_name not in LAIN_ROOMS:
        messages.error(request, f'Room "{room_name}" does not exist in the Wired.')
        return redirect('chat:index')
    
    room_info = LAIN_ROOMS[room_name]
    
    
    session_id = generate_anonymous_session_id(request)
    
    context = {
        'room_name': room_name,
        'room_info': room_info,
        'session_id': session_id,
        'rooms': LAIN_ROOMS,
        'anonymization_enabled': ANONYMIZATION_AVAILABLE,
    }
    
    return render(request, 'chat/room.html', context)

def room_list(request):
    """API pour obtenir la liste des rooms"""
    rooms_data = []
    for room_id, room_info in LAIN_ROOMS.items():
        user_count = random.randint(1, 15)
        
        rooms_data.append({
            'id': room_id,
            'name': room_info['name'],
            'description': room_info['description'],
            'theme': room_info['theme'],
            'user_count': user_count,
            'corruption_level': room_info['corruption_level'],
            'reality_anchor': room_info['reality_anchor']
        })
    
    return JsonResponse({
        'rooms': rooms_data,
        'total': len(rooms_data)
    })

def create_layer(request):
    if request.method == 'POST':
        return handle_layer_creation(request)
    
    return render(request, 'chat/create_layer.html', {
        'existing_rooms': LAIN_ROOMS
    })

@require_http_methods(["POST"])
def handle_layer_creation(request):
    try:
        layer_name = request.POST.get('layer_name', '').strip()
        layer_description = request.POST.get('layer_description', '').strip()
        corruption_level = int(request.POST.get('corruption_level', 0))
        reality_anchor = request.POST.get('reality_anchor') == 'on'
        theme = request.POST.get('theme', 'default')
        
        
        if not layer_name:
            messages.error(request, 'Layer name is required.')
            return redirect('chat:create_layer')
        
        if len(layer_name) > 50:
            messages.error(request, 'Layer name too long (max 50 characters).')
            return redirect('chat:create_layer')
        
        
        layer_id = generate_layer_id(layer_name)
        
        
        if layer_id in LAIN_ROOMS:
            messages.error(request, 'A layer with this name already exists.')
            return redirect('chat:create_layer')
        
        
        new_layer = {
            'name': layer_name,
            'description': layer_description or f'Custom layer: {layer_name}',
            'theme': theme,
            'corruption_level': max(0, min(corruption_level, 10)),
            'reality_anchor': reality_anchor,
            'created_at': timezone.now(),
            'is_custom': True
        }
        
        
        LAIN_ROOMS[layer_id] = new_layer
        
        
        if ANONYMIZATION_AVAILABLE:
            try:
                create_anonymous_layer(layer_id, new_layer)
                messages.success(request, f'Layer "{layer_name}" created successfully in the Wired.')
            except Exception as e:
                messages.warning(request, f'Layer created but anonymization failed: {str(e)}')
        else:
            messages.success(request, f'Layer "{layer_name}" created successfully.')
        
        
        return redirect('chat:room', room_name=layer_id)
        
    except Exception as e:
        messages.error(request, f'Failed to create layer: {str(e)}')
        return redirect('chat:create_layer')

def layer_info(request, room_name):
   
    if room_name not in LAIN_ROOMS:
        return JsonResponse({'error': 'Layer not found'}, status=404)
    
    room_info = LAIN_ROOMS[room_name]
    user_count = random.randint(1, 15)  
    
    return JsonResponse({
        'id': room_name,
        'name': room_info['name'],
        'description': room_info['description'],
        'theme': room_info['theme'],
        'corruption_level': room_info['corruption_level'],
        'reality_anchor': room_info['reality_anchor'],
        'user_count': user_count,
        'is_custom': room_info.get('is_custom', False)
    })

@csrf_exempt
def layer_status(request, room_name):
    if room_name not in LAIN_ROOMS:
        return JsonResponse({'error': 'Layer not found'}, status=404)
    
    # Simuler des stat (mettre des vrai un jour si pas flemme)
    stats = {
        'active_connections': random.randint(1, 12),
        'messages_today': random.randint(50, 500),
        'corruption_events': random.randint(0, 5),
        'reality_distortions': random.randint(0, 3),
        'uptime_minutes': random.randint(60, 1440)
    }
    
    return JsonResponse({
        'room_name': room_name,
        'status': 'active',
        'stats': stats,
        'timestamp': timezone.now().isoformat()
    })

def delete_layer(request, room_name):
    """Suppression d'un layer personnalisé"""
    if request.method == 'POST':
        if room_name in LAIN_ROOMS and LAIN_ROOMS[room_name].get('is_custom', False):
            del LAIN_ROOMS[room_name]
            messages.success(request, f'Layer "{room_name}" deleted from the Wired.')
        else:
            messages.error(request, 'Cannot delete default Wired layers.')
    
    return redirect('chat:index')



def generate_anonymous_session_id(request):
    """Génère un ID de session anonyme"""
    timestamp = str(int(timezone.now().timestamp()))
    random_data = str(random.randint(10000, 99999))
    session_data = f"anonymous_{timestamp}_{random_data}"
    return hashlib.sha256(session_data.encode()).hexdigest()[:16]

def generate_layer_id(layer_name):
    """Génère un ID unique pour un layer"""
    clean_name = ''.join(c.lower() for c in layer_name if c.isalnum())
    if len(clean_name) > 20:
        clean_name = clean_name[:20]
    
    timestamp = int(timezone.now().timestamp())
    return f"{clean_name}_{timestamp % 10000}"

def create_anonymous_layer(layer_id, layer_data):
    if not ANONYMIZATION_AVAILABLE:
        return None
    
    try:
        layer = TrueAnonymousLayer.objects.create(
            layer_id=layer_id,
            layer_name=layer_data['name'],
            corruption_level=layer_data['corruption_level'],
            created_at=timezone.now(),
            last_active=timezone.now(),
            is_ephemeral=False,
            max_users=25,
            auto_destroy_hours=None
        )
        return layer
    except Exception:
        return None

def random_lain_quote(request):
    quotes = [
        "Present day, present time.",
        "God is here.",
        "I am connected.",
        "The border between the real and the virtual is unclear.",
        "Let's all love Lain.",
        "No matter where you are, everyone is connected.",
        "The Wired is a world such as this one.",
        "Reality is what you make of it.",
        "Are you happy?",
        "Who are you?",
        "I don't need to stay the way I am now.",
        "Everyone is connected."
    ]
    
    quote = random.choice(quotes)
    return JsonResponse({
        'quote': quote,
        'timestamp': timezone.now().isoformat()
    })

# Vue d'erreur personnalisée pour les rooms
def room_not_found(request, room_name):
    return render(request, 'chat/room_not_found.html', {
        'room_name': room_name,
        'available_rooms': LAIN_ROOMS
    }, status=404)