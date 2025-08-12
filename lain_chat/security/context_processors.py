from django.conf import settings
from django.utils import timezone
import hashlib
import time

def security_context(request):
    
    
    
    session_hash = None
    if request.user.is_authenticated:
        session_data = f"{request.user.id}:{timezone.now().date()}"
        session_hash = hashlib.sha256(session_data.encode()).hexdigest()[:8]
    
    
    current_hour = timezone.now().hour
    anonymization_level = (current_hour % 5) + 1  
    
    
    system_status = {
        'anonymization_active': settings.ANONYMIZATION_CONFIG.get('ENABLED', True),
        'zero_knowledge_mode': settings.ANONYMIZATION_CONFIG.get('ZERO_KNOWLEDGE_AUTH', True),
        'encryption_status': 'AES-256-ACTIVE',
        'wired_connection': 'STABLE',
        'reality_border': 'DEGRADED',  # Easter egg Lain
        'protocol_seven': True
    }
    
    return {
        'security_context': {
            'session_hash': session_hash,
            'anonymization_level': anonymization_level,
            'system_status': system_status,
            'current_time': timezone.now().isoformat(),
            'is_wired_mode': request.session.get('wired_mode', False),
            'is_nobody_mode': request.session.get('nobody_mode', False),
            'csrf_token': request.META.get('CSRF_COOKIE'),
        }
    }