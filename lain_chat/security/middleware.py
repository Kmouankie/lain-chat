import hashlib
import time
import re
from django.utils.deprecation import MiddlewareMixin
from django.http import HttpResponse, HttpResponseForbidden
from django.conf import settings
from django.core.cache import cache
import logging
import secrets
from urllib.parse import urlparse


class SecureLogger:
    def __init__(self, name):
        self.logger = logging.getLogger(name)
    
    def log_security_event(self, level, event_type, details=None):
        
        timestamp = int(time.time())
        event_id = secrets.token_hex(8)
        
        
        safe_details = self._sanitize_details(details) if details else "None"
        
        message = f"SECURITY_EVENT:{event_type}:ID:{event_id}:DETAILS:{safe_details}"
        self.logger.log(level, message)
    
    def _sanitize_details(self, details):
        """Supprime toute information sensible des logs"""
        if isinstance(details, dict):
            sanitized = {}
            for key, value in details.items():
                if key.lower() in ['ip', 'user_agent', 'session', 'token', 'password', 'key']:
                    sanitized[key] = '[REDACTED]'
                else:
                    sanitized[key] = str(value)[:50] + '...' if len(str(value)) > 50 else str(value)
            return str(sanitized)
        return str(details)[:100] + '...' if len(str(details)) > 100 else str(details)


security_logger = SecureLogger('lain_security')

class SecurityHardeningMiddleware(MiddlewareMixin):
    
    
    def process_request(self, request):
       
        self.strip_identifying_headers(request)
        return None
    
    def process_response(self, request, response):
       
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY' 
        response['X-XSS-Protection'] = '1; mode=block'
        response['Referrer-Policy'] = 'no-referrer'
        
        
        if 'Server' in response:
            del response['Server']
        
        return response
    
    def strip_identifying_headers(self, request):
       
        headers_to_strip = [
            'HTTP_X_FORWARDED_FOR',
            'HTTP_X_REAL_IP', 
            'HTTP_CLIENT_IP',
            'HTTP_X_FORWARDED',
            'HTTP_FORWARDED_FOR',
            'HTTP_FORWARDED'
        ]
        
        for header in headers_to_strip:
            if header in request.META:
                del request.META[header]

class AnonymizationMiddleware(MiddlewareMixin):
    
    
    def process_request(self, request):
        """Anonymise les requêtes HTTP"""
        
        request.META['REMOTE_ADDR'] = '127.0.0.1'
        
        
        identifying_headers = [
            'HTTP_USER_AGENT',
            'HTTP_ACCEPT_LANGUAGE',
            'HTTP_ACCEPT_ENCODING',
            'HTTP_DNT',
            'HTTP_X_REQUESTED_WITH'
        ]
        
        for header in identifying_headers:
            if header in request.META:
                request.META[header] = 'anonymous'
        
        return None
    
    def process_response(self, request, response):
       
        # Supprimer les headers révélateurs
        headers_to_remove = ['Server', 'X-Powered-By', 'Via']
        for header in headers_to_remove:
            if header in response:
                del response[header]
        
        return response

class LayerIsolationMiddleware(MiddlewareMixin):
   
    
    def process_request(self, request):
        """Isole les requêtes par layer"""
        
        request.layer_isolated = True
        request.isolation_level = getattr(settings, 'DEFAULT_ISOLATION_LEVEL', 1)
        
        
        if not hasattr(request, 'anonymous_session_id'):
            random_component = secrets.token_hex(16)
            timestamp = str(int(time.time()))
            session_data = f"anonymous_{timestamp}_{random_component}"
            request.anonymous_session_id = hashlib.sha256(session_data.encode()).hexdigest()[:16]
        
        return None
    
    def process_response(self, request, response):
        
        if hasattr(request, 'anonymous_session_id'):
            response['X-Layer-Isolation'] = 'active'
        
        return response

class AdvancedSecurityMiddleware(MiddlewareMixin):
   
    
    def __init__(self, get_response):
        self.get_response = get_response
        
        
        self.attack_patterns = [
            r'<script.*?>.*?</script>',  
            r'javascript:',              
            r'on\w+\s*=',               
            r'union\s+select',          
            r'drop\s+table',            
            r'\'.*or.*\'.*=.*\'',       
            r'\.\./\.\.',               
            r'etc/passwd',              
            r'cmd\.exe',                
            r'powershell',              
            r'eval\s*\(',               
            r'exec\s*\(',               
            r'system\s*\(',            
        ]
        self.compiled_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in self.attack_patterns]
        
        
        self.rate_limits = {
            'default': {
                'requests': 60,     # 60 
                'window': 60,       
                'burst': 10         
            },
            'strict': {
                'requests': 20,     
                'window': 60,
                'burst': 5
            },
            'api': {
                'requests': 100,    
                'window': 60,
                'burst': 20
            }
        }
        
        
        self.memory_cache = {}
        self.cache_cleanup_interval = 300  
        self.last_cleanup = time.time()
        
        super().__init__(get_response)
    
    def process_request(self, request):
        """Traitement sécurisé ds requ entr"""
        
        
        self._anonymize_request(request)
        
        
        if self._is_rate_limited(request):
            security_logger.log_security_event(
                logging.WARNING,
                'RATE_LIMIT_EXCEEDED', 
                {'path': request.path, 'method': request.method}
            )
            return HttpResponseForbidden("Rate limit exceeded. Please slow down.")
        
        
        if self._detect_attack_patterns(request):
            security_logger.log_security_event(
                logging.WARNING, 
                'ATTACK_PATTERN_DETECTED',
                {'path': request.path, 'method': request.method}
            )
            return HttpResponseForbidden("Request blocked by security policy")
        
       
        if not self._validate_headers(request):
            security_logger.log_security_event(
                logging.WARNING,
                'INVALID_HEADERS',
                {'path': request.path}
            )
            return HttpResponseForbidden("Invalid request headers")
        
        
        self._add_security_metadata(request)
        
        return None
    
    
    
    def _anonymize_request(self, request):
        """Anonymisation complète des requêtes"""
        
        request.META['REMOTE_ADDR'] = '127.0.0.1'
        
        
        headers_to_anonymize = [
            'HTTP_USER_AGENT', 'HTTP_ACCEPT_LANGUAGE', 'HTTP_ACCEPT_ENCODING',
            'HTTP_DNT', 'HTTP_X_REQUESTED_WITH', 'HTTP_REFERER',
            'HTTP_X_FORWARDED_FOR', 'HTTP_X_REAL_IP', 'HTTP_CLIENT_IP',
            'HTTP_CF_CONNECTING_IP', 'HTTP_X_CLUSTER_CLIENT_IP',
            'HTTP_FORWARDED', 'HTTP_VIA', 'HTTP_X_FORWARDED_HOST',
            'HTTP_X_FORWARDED_PROTO', 'HTTP_X_ORIGINAL_FORWARDED_FOR'
        ]
        
        for header in headers_to_anonymize:
            if header in request.META:
                request.META[header] = 'anonymous'
        
        # Génération d'un fingerprint anonyme pr sess
        if not hasattr(request, 'anonymous_fingerprint'):
            
            timestamp_hour = str(int(time.time() // 3600))  # Change chaque heure
            path_hash = hashlib.md5(request.path.encode()).hexdigest()[:8]
            random_salt = secrets.token_hex(8)
            
            fingerprint_data = f"anonymous:{timestamp_hour}:{path_hash}:{random_salt}"
            request.anonymous_fingerprint = hashlib.sha256(fingerprint_data.encode()).hexdigest()[:16]
    
    def _is_rate_limited(self, request):
        """Système de rate limiting production"""
        self._cleanup_memory_cache()
        
        # Générer une clé unique basée sur l'empreinte anonyme
        client_key = f"rate_limit:{getattr(request, 'anonymous_fingerprint', 'unknown')}"
        
        # Déterminer le type de limite selon le path
        limit_type = self._get_limit_type(request.path)
        limit_config = self.rate_limits[limit_type]
        
        current_time = int(time.time())
        window_start = current_time - limit_config['window']
        
        # Essaye d'abord le cache Django
        try:
            rate_data = self._get_rate_data_from_cache(client_key, current_time, window_start)
        except Exception:
            # Fallback vers cache mémoire
            rate_data = self._get_rate_data_from_memory(client_key, current_time, window_start)
        
        
        return self._check_rate_limit_with_burst(
            rate_data, limit_config, client_key, current_time
        )
    
    def _get_limit_type(self, path):
        """Détermine le type de limite selon le path"""
        if path.startswith('/admin'):
            return 'strict'
        elif path.startswith('/api'):
            return 'api'
        else:
            return 'default'
    
    def _get_rate_data_from_cache(self, client_key, current_time, window_start):
        """Récupère les données de rate limiting depuis le cache Django"""
        rate_data = cache.get(client_key, {
            'requests': [],
            'tokens': 0,
            'last_refill': current_time
        })
        
       
        rate_data['requests'] = [
            (ts, count) for ts, count in rate_data['requests'] 
            if ts > window_start
        ]
        
        return rate_data
    
    def _get_rate_data_from_memory(self, client_key, current_time, window_start):
        """Fallback vers cache mémoire"""
        if client_key not in self.memory_cache:
            self.memory_cache[client_key] = {
                'requests': [],
                'tokens': 0,
                'last_refill': current_time
            }
        
        rate_data = self.memory_cache[client_key]
        
        
        rate_data['requests'] = [
            (ts, count) for ts, count in rate_data['requests'] 
            if ts > window_start
        ]
        
        return rate_data
    
    def _check_rate_limit_with_burst(self, rate_data, limit_config, client_key, current_time):
        """Vérifie la limite avec gestion des bursts"""
        
        total_requests = sum(count for _, count in rate_data['requests'])
        
        
        time_since_refill = current_time - rate_data['last_refill']
        tokens_to_add = int(time_since_refill * (limit_config['requests'] / limit_config['window']))
        
        rate_data['tokens'] = min(
            limit_config['burst'], 
            rate_data['tokens'] + tokens_to_add
        )
        rate_data['last_refill'] = current_time
        
       
        if total_requests >= limit_config['requests']:
            self._save_rate_data(client_key, rate_data)
            return True
        
        
        if rate_data['tokens'] <= 0:
          
            recent_requests = sum(
                count for ts, count in rate_data['requests'] 
                if current_time - ts <= 60  
            )
            
            if recent_requests >= (limit_config['requests'] // 2): 
                self._save_rate_data(client_key, rate_data)
                return True
        else:
            
            rate_data['tokens'] -= 1
        
        
        rate_data['requests'].append((current_time, 1))
        
        
        self._save_rate_data(client_key, rate_data)
        
        return False
    
    def _save_rate_data(self, client_key, rate_data):
        """Sauvegarde les données de rate limiting"""
        try:
            cache.set(client_key, rate_data, 3600)  # Cache pour 1 heure
        except Exception:
            self.memory_cache[client_key] = rate_data
    
    def _cleanup_memory_cache(self):
        """Nettoyage périodique du cache mémoire"""
        current_time = time.time()
        
        if current_time - self.last_cleanup < self.cache_cleanup_interval:
            return
        
        cutoff_time = current_time - 3600  # 1 heure
        keys_to_remove = []
        
        for key, data in self.memory_cache.items():
            if data.get('last_refill', 0) < cutoff_time:
                keys_to_remove.append(key)
        
        for key in keys_to_remove:
            del self.memory_cache[key]
        
        self.last_cleanup = current_time
        
        if keys_to_remove:
            security_logger.log_security_event(
                logging.INFO,
                'CACHE_CLEANUP',
                {'removed_entries': len(keys_to_remove)}
            )
    
    def _detect_attack_patterns(self, request):
        """Détection de patterns d'attaques courantes avec scoring"""
        attack_score = 0
        
        
        for key, value in request.GET.items():
            for pattern in self.compiled_patterns:
                if pattern.search(str(value)):
                    attack_score += 1
                    if attack_score >= 1: 
                        return True
        
       
        if request.method == 'POST' and hasattr(request, 'body'):
            try:
                body_str = request.body.decode('utf-8', errors='ignore')
                for pattern in self.compiled_patterns:
                    if pattern.search(body_str):
                        attack_score += 1
                        if attack_score >= 1:
                            return True
            except:
                pass
        for pattern in self.compiled_patterns:
            if pattern.search(request.path):
                attack_score += 1
                if attack_score >= 1:
                    return True
        
        return False
    
    def _validate_headers(self, request):
        """Validation des headers de requête"""
        required_headers = ['HTTP_HOST']
        
        for header in required_headers:
            if header not in request.META:
                return False
        
        host = request.META.get('HTTP_HOST', '')
        if not self._is_valid_host(host):
            return False
        
        return True
    
    def _is_valid_host(self, host):
        """Validation du header Host"""
        if not host:
            return False
        
        host_without_port = host.split(':')[0]
        
        allowed_hosts = getattr(settings, 'ALLOWED_HOSTS', ['localhost', '127.0.0.1'])
        
        return host_without_port in allowed_hosts or '*' in allowed_hosts
    
    def _add_security_metadata(self, request):
       
        request.security_level = 'high'
        request.anonymized = True
        request.scan_timestamp = int(time.time())
        request.rate_limit_checked = True
    
    def _set_advanced_security_headers(self, response):

        
       
        headers_to_clear = ['Content-Security-Policy', 'Content-Security-Policy-Report-Only', 'X-Content-Security-Policy']
        for header in headers_to_clear:
            if header in response:
                del response[header]
        
        
        csp_directives = [
            "default-src 'self'",
            "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdnjs.cloudflare.com",
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://fonts.gstatic.com",
            "font-src 'self' https://fonts.googleapis.com https://fonts.gstatic.com data:",
            "img-src 'self' data: blob:",
            "connect-src 'self' ws://127.0.0.1:8000 ws://localhost:8000 wss://127.0.0.1:8000 wss://localhost:8000",
            "media-src 'self' data:",
            "object-src 'none'",  
            "frame-src 'none'",
            "base-uri 'self'",
            "form-action 'self'",
            "frame-ancestors 'none'"
        ]
        
        response['Content-Security-Policy'] = '; '.join(csp_directives)
        
        print(f"[DEBUG] CSP Applied: {response.get('Content-Security-Policy', 'NOT FOUND')[:100]}...")
        
        response['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains; preload'
        
        response['X-Frame-Options'] = 'DENY'
        
        response['X-Content-Type-Options'] = 'nosniff'
        
        response['X-XSS-Protection'] = '1; mode=block'
        
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        
        permissions_policies = [
            'camera=()',
            'microphone=()',
            'geolocation=()',
            'payment=()',
            'usb=()',
            'magnetometer=()',
            'accelerometer=()',
            'gyroscope=()',
            'bluetooth=()',
            'midi=()'
            
        ]
        response['Permissions-Policy'] = ', '.join(permissions_policies)
        
        # Cache control sécurisé
        response['Cache-Control'] = 'no-cache, no-store, must-revalidate, private'
        response['Pragma'] = 'no-cache'
        response['Expires'] = '0'
    
    def _remove_fingerprinting_headers(self, response):
        """Supprime les headers qui peuvent être utilisés pour le fingerprinting"""
        headers_to_remove = [
            'Server', 'X-Powered-By', 'Via', 'X-AspNet-Version',
            'X-AspNetMvc-Version', 'X-Generator', 'X-Drupal-Cache',
            'X-Varnish', 'X-Served-By', 'X-Cache', 'X-Cache-Hits'
        ]
        
        for header in headers_to_remove:
            if header in response:
                del response[header]
        
        
        response['Server'] = 'WebServer/1.0'
    
    def _validate_response_content(self, response):
        
        # Vérifier qu'on ne leak pas d'infos sensibles dans le contenu
        if hasattr(response, 'content') and response.content:
            try:
                content_str = response.content.decode('utf-8', errors='ignore').lower()
                
                # Patterns à éviter dans les réponses
                sensitive_patterns = [
                    r'\b(?:\d{1,3}\.){3}\d{1,3}\b',  
                    r'password\s*[:=]\s*\w+',       
                    r'secret\s*[:=]\s*\w+',          
                    r'token\s*[:=]\s*\w+',          
                ]
                
                for pattern in sensitive_patterns:
                    if re.search(pattern, content_str):
                        security_logger.log_security_event(
                            logging.WARNING,
                            'SENSITIVE_DATA_LEAK',
                            {'pattern': pattern[:20]}
                        )
                        break
            except:
                pass  
    
   
    
    def process_response(self, request, response):
        """Sécurisation des réponses sortantes"""
        
        
        print(f"[DEBUG AVANT] CSP existant: {response.get('Content-Security-Policy', 'AUCUN')}")
        
        
        self._set_advanced_security_headers(response)
        
        
        final_csp = response.get('Content-Security-Policy', 'ECHEC!')
        print(f"[DEBUG APRÈS] CSP final: {final_csp[:150]}...")
        if 'fonts.googleapis.com' in final_csp:
            print("[DEBUG]  Google Fonts AUTORISÉES dans le CSP")
        else:
            print("[DEBUG]  Google Fonts PAS TROUVÉES dans le CSP !")
        
        self._remove_fingerprinting_headers(response)
        
        self._validate_response_content(response)
        
        return response

class WebSocketSecurityMiddleware:
    """Middleware de sécurité spécialement conçu pour les WebSockets"""
    
    def __init__(self, inner):
        self.inner = inner
        self.security_logger = SecureLogger('lain_websocket_security')
    
    async def __call__(self, scope, receive, send):
        if scope['type'] == 'websocket':
            
            scope = self._anonymize_websocket_scope(scope)
            
            
            if not self._validate_websocket_connection(scope):
                
                await send({
                    'type': 'websocket.close',
                    'code': 1008  
                })
                return
            
            scope['security_validated'] = True
            scope['anonymization_level'] = 'maximum'
        
        return await self.inner(scope, receive, send)
    
    def _anonymize_websocket_scope(self, scope):
        """Anonymisation robuste du scope WebSocket"""
        anonymized_scope = {
            'type': scope['type'],
            'path': scope['path'],
            'query_string': scope.get('query_string', b''),
            'root_path': scope.get('root_path', ''),
            'scheme': scope.get('scheme', 'ws'),
            'server': scope.get('server', ('localhost', 8000)),
            'subprotocols': scope.get('subprotocols', []),
        }
        
        
        anonymized_scope['client'] = ('127.0.0.1', 0)
        
        
        essential_headers = {
            b'host': b'127.0.0.1:8000',
            b'connection': b'Upgrade',
            b'upgrade': b'websocket',
            b'sec-websocket-version': b'13',
        }
        
       
        original_headers = dict(scope.get('headers', []))
        for key in [b'sec-websocket-key', b'sec-websocket-protocol']:
            if key in original_headers:
                essential_headers[key] = original_headers[key]
        
        anonymized_scope['headers'] = list(essential_headers.items())
        
        
        safe_fields = ['route', 'url_route', 'channel_layer']
        for key in safe_fields:
            if key in scope:
                anonymized_scope[key] = scope[key]
        
        return anonymized_scope
    
    def _validate_websocket_connection(self, scope):
        """Validation des connexions WebSocket"""
        # Vérifier que le path est autorisé
        allowed_paths = ['/ws/chat/', '/ws/layer/', '/ws/test/']
        
        path = scope['path']
        for allowed_path in allowed_paths:
            if path.startswith(allowed_path):
                return True
        
        # Log de tentative de connexion non autorisée
        self.security_logger.log_security_event(
            logging.WARNING,
            'UNAUTHORIZED_WEBSOCKET_PATH',
            {'path': path[:50]}
        )
        
        return False

class RequestSanitizationMiddleware(MiddlewareMixin):
    """Middleware pour nettoyer et valider toutes les entrées utilisateur"""
    
    def process_request(self, request):
        
        
        # Nettoyer les paramètres GET
        if request.GET:
            request.GET = self._sanitize_query_dict(request.GET)
        
        # Nettoyer les données POST
        if request.method == 'POST' and request.POST:
            request.POST = self._sanitize_query_dict(request.POST)
        
        return None
    
    def _sanitize_query_dict(self, query_dict):
        """Nettoyage d'un QueryDict"""
        sanitized = query_dict.copy()
        
        for key in sanitized.keys():
            values = sanitized.getlist(key)
            sanitized.setlist(key, [self._sanitize_string(value) for value in values])
        
        return sanitized
    
    def _sanitize_string(self, value):
        """Nettoyage d'une chaîne de caractères"""
        if not isinstance(value, str):
            return value
        
        value = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', value)
        
        if len(value) > 1000:
            value = value[:1000]
        
        value = value.replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;').replace("'", '&#x27;')
        
        return value

class AnonymousWebSocketMiddleware:
    """Middleware WebSocket d'anonymisation - Version production finale"""
    
    def __init__(self, inner):
        self.inner = inner
    
    async def __call__(self, scope, receive, send):
        """Point d'entrée ASGI3"""
        if scope['type'] == 'websocket':
            scope = self._anonymize_scope(scope)
        
        return await self.inner(scope, receive, send)
    
    def _anonymize_scope(self, scope):
        """Anonymisation complète et définitive du scope WebSocket"""
        anonymized_scope = {
            'type': scope['type'],
            'path': scope['path'],
            'query_string': scope.get('query_string', b''),
            'root_path': scope.get('root_path', ''),
            'scheme': scope.get('scheme', 'ws'),
            'server': scope.get('server', ('localhost', 8000)),
            'subprotocols': scope.get('subprotocols', []),
        }
        
        # IP anonymisée définitive toujours localhost
        anonymized_scope['client'] = ('127.0.0.1', 0)
        
        essential_headers = {
            b'host': b'127.0.0.1:8000',
            b'connection': b'Upgrade',
            b'upgrade': b'websocket',
            b'sec-websocket-version': b'13',
        }
        
        original_headers = dict(scope.get('headers', []))
        for key in [b'sec-websocket-key', b'sec-websocket-protocol']:
            if key in original_headers:
                essential_headers[key] = original_headers[key]
        
        anonymized_scope['headers'] = list(essential_headers.items())
        
        for key in scope:
            if key not in anonymized_scope and key not in ['client', 'headers']:
                if not self._is_identifying_field(key):
                    anonymized_scope[key] = scope[key]
        
        return anonymized_scope
    
    def _is_identifying_field(self, field_name):
        """Détermine si un champ peut être identifiant"""
        identifying_fields = {
            'user', 'session', 'cookies', 'auth', 
            'remote_addr', 'forwarded_for'
        }
        return field_name.lower() in identifying_fields



class LainAnonymizationMiddleware(AnonymizationMiddleware):
    """Alias pour compatibilité"""
    pass


class LainSecurityMiddleware(SecurityHardeningMiddleware):
    """Alias pour compatibilité"""
    pass