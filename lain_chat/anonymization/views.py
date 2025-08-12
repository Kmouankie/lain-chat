import json
import hashlib
import time
from django.shortcuts import render
from django.http import JsonResponse
from django.views.generic import TemplateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.conf import settings
from django.utils import timezone
from django.db import transaction

from .models import TrueAnonymousLayer, LayerMapping, AnonymousMessage, EmergencyBurn
from .encryption import LayerEncryption, ZeroKnowledgeAuth

class CreateLayerView(View):
    """Création d'un nouveau layer anonyme"""
    
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            layer_name = data.get('layer_name', f'layer_{int(time.time())}')
            anonymization_level = data.get('anonymization_level', 1)
            
            # Créer le layer anonyme
            with transaction.atomic():
                layer = TrueAnonymousLayer.objects.create(
                    layer_name=layer_name,
                    corruption_level=anonymization_level
                )
                
                # Créer le mapping chiffré si utilisateur connecté
                if request.user.is_authenticated:
                    user_hash, salt = LayerMapping.generate_user_hash(
                        request.user.id
                    )
                    
                    # Chiffrer le lien
                    encryption_key = settings.ENCRYPTION_CONFIG['MASTER_KEY'].encode()
                    encrypted_link = LayerMapping.encrypt_link(
                        layer.layer_id, 
                        request.user.id, 
                        encryption_key
                    )
                    
                    LayerMapping.objects.create(
                        user_hash=user_hash,
                        layer_id=layer.layer_id,
                        encrypted_link=encrypted_link,
                        salt=salt
                    )
                    
               
                    request.user.increment_layer_count()
            
            return JsonResponse({
                'success': True,
                'layer': {
                    'id': str(layer.layer_id),
                    'name': layer.layer_name,
                    'created_at': layer.created_at.isoformat(),
                    'corruption_level': layer.corruption_level
                },
                'message': f'Layer "{layer_name}" created successfully'
            })
            
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'error': 'Invalid JSON data'
            }, status=400)
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': 'Layer creation failed',
                'details': str(e) if settings.DEBUG else None
            }, status=500)

class SwitchLayerView(View):
    """Changement de layer actif"""
    
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            layer_name = data.get('layer_name')
            
            if not layer_name:
                return JsonResponse({
                    'success': False,
                    'error': 'Layer name required'
                }, status=400)
            
            
            try:
                layer = TrueAnonymousLayer.objects.get(layer_name=layer_name)
            except TrueAnonymousLayer.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'error': 'Layer not found'
                }, status=404)
            
            if request.user.is_authenticated:
                user_hash, _ = LayerMapping.generate_user_hash(request.user.id)
                
                if not LayerMapping.objects.filter(
                    user_hash=user_hash,
                    layer_id=layer.layer_id
                ).exists():
                    return JsonResponse({
                        'success': False,
                        'error': 'Access denied to this layer'
                    }, status=403)
            
            
            layer.last_active = timezone.now()
            layer.save()
            
            return JsonResponse({
                'success': True,
                'layer': {
                    'id': str(layer.layer_id),
                    'name': layer.layer_name,
                    'corruption_level': layer.corruption_level,
                    'last_active': layer.last_active.isoformat()
                },
                'message': f'Switched to layer "{layer_name}"'
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': 'Layer switch failed',
                'details': str(e) if settings.DEBUG else None
            }, status=500)

class BurnLayerView(View):
    """Destruction définitive d'un layer"""
    
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            layer_name = data.get('layer_name', 'current')
            
            if layer_name == 'current':
                # Brûler le layer actuel (logique à implémenter)
                return JsonResponse({
                    'success': False,
                    'error': 'Current Dead'
                }, status=501)
            
            # Chercher le layer à brûler
            try:
                layer = TrueAnonymousLayer.objects.get(layer_name=layer_name)
            except TrueAnonymousLayer.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'error': 'Layer not found'
                }, status=404)
            
            # Vérifier les permissions
            if request.user.is_authenticated:
                user_hash, _ = LayerMapping.generate_user_hash(request.user.id)
                
                if not LayerMapping.objects.filter(
                    user_hash=user_hash,
                    layer_id=layer.layer_id
                ).exists():
                    return JsonResponse({
                        'success': False,
                        'error': 'Access denied'
                    }, status=403)
            
            # Destruction complète
            with transaction.atomic():
                layer_id = layer.layer_id
                layer_name_copy = layer.layer_name
                
                # Supprimer tous les messages associés
                AnonymousMessage.objects.filter(layer_id=layer_id).delete()
                
                # Supprimer les mappings
                LayerMapping.objects.filter(layer_id=layer_id).delete()
                
                # Supprimer le layer
                layer.delete()
                
                # Log de l'événement (anonymisé)
                if request.user.is_authenticated:
                    trigger_hash = hashlib.sha256(
                        f"{request.user.id}:{time.time()}".encode()
                    ).hexdigest()
                else:
                    trigger_hash = "anonymous"
                
                EmergencyBurn.objects.create(
                    burn_type='single_layer',
                    objects_destroyed_count=1,
                    triggered_by_hash=trigger_hash,
                    reason=f'Manual burn of layer {layer_name_copy}'
                )
            
            return JsonResponse({
                'success': True,
                'message': f'Layer "{layer_name_copy}" burned successfully',
                'burn_id': 'classified'
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': 'Burn operation failed',
                'details': str(e) if settings.DEBUG else None
            }, status=500)

class FragmentIdentityView(View):
    """Fragmentation d'identité en plusieurs layers"""
    
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            fragment_count = min(data.get('fragment_count', 3), 10)  
            
            fragments = []
            
            with transaction.atomic():
                for i in range(fragment_count):
                    fragment_name = f"fragment_{i+1}_{int(time.time())}"
                    
                    layer = TrueAnonymousLayer.objects.create(
                        layer_name=fragment_name,
                        corruption_level=i + 1  
                    )
                    
                    
                    if request.user.is_authenticated:
                        user_hash, salt = LayerMapping.generate_user_hash(
                            request.user.id,
                            f"fragment_{i}"  
                        )
                        
                        encryption_key = settings.ENCRYPTION_CONFIG['FRAGMENT_KEY'].encode()
                        encrypted_link = LayerMapping.encrypt_link(
                            layer.layer_id,
                            request.user.id,
                            encryption_key
                        )
                        
                        LayerMapping.objects.create(
                            user_hash=user_hash,
                            layer_id=layer.layer_id,
                            encrypted_link=encrypted_link,
                            salt=salt
                        )
                    
                    fragments.append({
                        'id': str(layer.layer_id),
                        'name': layer.layer_name,
                        'corruption_level': layer.corruption_level
                    })
            
            return JsonResponse({
                'success': True,
                'fragments': fragments,
                'message': f'Identity fragmented into {fragment_count} layers',
                'warning': 'Each fragment is completely isolated'
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': 'Fragmentation failed',
                'details': str(e) if settings.DEBUG else None
            }, status=500)

class EmergencyBurnView(View):
    """Destruction d'urgence de toutes les données"""
    
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            confirmation = data.get('confirmation')
            
            if confirmation != 'BURN':
                return JsonResponse({
                    'success': False,
                    'error': 'Invalid confirmation code'
                }, status=400)
            
            destroyed_count = 0
            
            with transaction.atomic():
                # Compter avant destruction
                layers_count = TrueAnonymousLayer.objects.count()
                messages_count = AnonymousMessage.objects.count()
                mappings_count = LayerMapping.objects.count()
                
                # Destruction totale
                TrueAnonymousLayer.objects.all().delete()
                AnonymousMessage.objects.all().delete()
                LayerMapping.objects.all().delete()
                
                destroyed_count = layers_count + messages_count + mappings_count
                
                # Log de l'événement
                trigger_hash = hashlib.sha256(
                    f"{request.user.id if request.user.is_authenticated else 'anonymous'}:{time.time()}".encode()
                ).hexdigest()
                
                EmergencyBurn.objects.create(
                    burn_type='total_destruction',
                    objects_destroyed_count=destroyed_count,
                    triggered_by_hash=trigger_hash,
                    reason='Emergency burn - total data destruction'
                )
            
            return JsonResponse({
                'success': True,
                'message': 'Emergency burn completed',
                'objects_destroyed': destroyed_count,
                'warning': 'All data has been permanently destroyed'
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': 'Emergency burn failed',
                'details': str(e) if settings.DEBUG else None
            }, status=500)

class LayerListAPIView(View):
    """API pour lister les layers accessibles"""
    
    def get(self, request, *args, **kwargs):
        try:
            layers = []
            
            if request.user.is_authenticated:
                # Récupérer les layers via les mappings
                user_hash, _ = LayerMapping.generate_user_hash(request.user.id)
                
                mappings = LayerMapping.objects.filter(user_hash=user_hash)
                layer_ids = [mapping.layer_id for mapping in mappings]
                
                user_layers = TrueAnonymousLayer.objects.filter(
                    layer_id__in=layer_ids
                ).order_by('-last_active')
                
                for layer in user_layers:
                    layers.append({
                        'id': str(layer.layer_id)[:8] + '...',  
                        'name': layer.layer_name,
                        'corruption_level': layer.corruption_level,
                        'last_active': layer.last_active.isoformat(),
                        'is_expired': layer.is_expired()
                    })
            else:
                # Mode anonyme - pas de layers persistants
                layers = [{
                    'id': 'anonymous',
                    'name': 'anonymous',
                    'corruption_level': 0,
                    'last_active': timezone.now().isoformat(),
                    'is_expired': False
                }]
            
            return JsonResponse({
                'success': True,
                'layers': layers,
                'count': len(layers)
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': 'Failed to list layers',
                'details': str(e) if settings.DEBUG else None
            }, status=500)

class AnonymizationStatusAPIView(View):
    """Status de l'anonymisation système"""
    
    def get(self, request, *args, **kwargs):
        try:
            # Statistiques anonymisées
            total_layers = TrueAnonymousLayer.objects.count()
            total_messages = AnonymousMessage.objects.count()
            total_burns = EmergencyBurn.objects.count()
            
            
            
            status = {
                'anonymization_enabled': settings.ANONYMIZATION_CONFIG.get('ENABLED', True),
                'zero_knowledge_auth': settings.ANONYMIZATION_CONFIG.get('ZERO_KNOWLEDGE_AUTH', True),
                'encryption_active': True,
                'total_layers': total_layers,
                'total_messages': total_messages,
                'emergency_burns': total_burns,
                'layer_rotation_hours': settings.ANONYMIZATION_CONFIG.get('LAYER_ROTATION_HOURS', 24),
                'message_retention_days': settings.ANONYMIZATION_CONFIG.get('MESSAGE_RETENTION_DAYS', 7),
                'system_status': 'operational',
                'wired_connection': 'stable',
                'reality_border_integrity': 'degraded',  # Easter egg
                'protocol_seven_active': True
            }
            
            return JsonResponse({
                'success': True,
                'status': status,
                'message': 'Present day, present time'
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': 'Status check failed',
                'details': str(e) if settings.DEBUG else None
            }, status=500)


class NobodyModeView(TemplateView):
    template_name = 'anonymization/nobody.html'

class GodKnowsModeView(TemplateView):
    template_name = 'anonymization/god_knows.html'