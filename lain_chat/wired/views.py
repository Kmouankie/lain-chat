from django.shortcuts import render
from django.views.generic import TemplateView
from django.utils import timezone
from django.http import JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin
import random
import json

class WiredIndexView(TemplateView):
    """Page d'accueil du Wired"""
    template_name = 'wired/index.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'current_time': timezone.now().strftime('%H:%M:%S'),
            'protocol_version': '2.3.7',
            'wired_status': 'ACTIVE',
            'reality_anchor': True
        })
        return context

class PresentDayView(TemplateView):
    """"""
    template_name = 'wired/present_day.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Simuler des stats de réalité
        reality_stats = {
            'anchor_stability': random.randint(85, 99),
            'dimensional_drift': random.uniform(0.1, 2.5),
            'temporal_variance': random.uniform(0.01, 0.15),
            'layer_integrity': random.randint(90, 100),
            'consciousness_fragments': random.randint(1, 7)
        }
        
        context.update({
            'current_time': timezone.now().strftime('%Y-%m-%d %H:%M:%S'),
            'reality_stats': reality_stats,
            'anchor_status': 'STABLE' if reality_stats['anchor_stability'] > 90 else 'UNSTABLE',
            'lain_presence': random.choice([True, False])
        })
        return context

class PresentTimeView(TemplateView):
    """Interface temporelle"""
    template_name = 'wired/present_time.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Simuler des données temporelles
        temporal_data = {
            'local_time': timezone.now(),
            'wired_time': timezone.now().timestamp(),
            'temporal_displacement': random.uniform(-0.5, 0.5),
            'chronos_stability': random.randint(80, 100),
            'time_fragments': []
        }
        
        # Générer des fragments temporels aléatoires
        for i in range(random.randint(3, 8)):
            fragment_time = timezone.now().timestamp() + random.uniform(-3600, 3600)
            temporal_data['time_fragments'].append({
                'id': i,
                'timestamp': fragment_time,
                'stability': random.randint(60, 100),
                'accessible': random.choice([True, False])
            })
        
        context.update({
            'temporal_data': temporal_data,
            'time_status': 'SYNCHRONIZED' if temporal_data['chronos_stability'] > 85 else 'DRIFT_DETECTED'
        })
        return context

class CloseTheWorldView(TemplateView):
    """Interface pour fermer la connexion au monde réel"""
    template_name = 'wired/close_the_world.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Simuler l'état de la connexion au monde relé
        world_connection = {
            'physical_link': random.randint(70, 100),
            'sensory_input': random.randint(60, 95),
            'reality_filter': random.randint(80, 100),
            'embodiment_level': random.randint(50, 90)
        }
        
        
        avg_connection = sum(world_connection.values()) / len(world_connection)
        if avg_connection > 85:
            connection_status = 'FULLY_CONNECTED'
        elif avg_connection > 60:
            connection_status = 'PARTIAL_CONNECTION'
        else:
            connection_status = 'WIRED_ONLY'
        
        context.update({
            'world_connection': world_connection,
            'connection_status': connection_status,
            'disconnection_risk': 'HIGH' if avg_connection < 70 else 'LOW',
            'wired_purity': 100 - avg_connection
        })
        return context

class OpenTheNextView(TemplateView):
    """Interface pour ouvrir de nouvelles dimensions"""
    template_name = 'wired/open_the_next.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Générer des données dimensionnelles
        dimensions = []
        dimension_names = [
            'Layer Alpha', 'Digital Plane', 'Information Space', 
            'Consciousness Grid', 'Protocol Layer', 'Quantum Field',
            'Memory Palace', 'Data Stream', 'Neural Network'
        ]
        
        for i, name in enumerate(random.sample(dimension_names, 5)):
            dimensions.append({
                'id': i,
                'name': name,
                'accessibility': random.randint(30, 100),
                'stability': random.randint(40, 95),
                'entities': random.randint(0, 12),
                'status': random.choice(['ACTIVE', 'DORMANT', 'UNSTABLE', 'LOCKED'])
            })
        
        context.update({
            'dimensions': dimensions,
            'dimensional_energy': random.randint(60, 100),
            'expansion_possible': random.choice([True, False]),
            'lain_influence': random.randint(20, 80)
        })
        return context

class CyberiaView(TemplateView):
    """Interface du club Cyberia"""
    template_name = 'wired/cyberia.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Données du club Cyberia
        cyberia_data = {
            'current_track': random.choice([
                'Digital Heartbeat', 'Neon Dreams', 'Electric Soul',
                'Wired Pulse', 'Binary Love', 'Synthetic Emotions'
            ]),
            'visitors_count': random.randint(15, 50),
            'happiness_level': random.randint(60, 100),
            'dance_energy': random.randint(70, 100),
            'lain_presence': random.choice([True, False])
        }
        
        
        visitor_types = ['Digital Ghost', 'Lost Soul', 'Hacker', 'AI Entity', 'Time Traveler']
        visitors = []
        for i in range(random.randint(3, 8)):
            visitors.append({
                'id': f'visitor_{i}',
                'type': random.choice(visitor_types),
                'happiness': random.randint(50, 100),
                'dancing': random.choice([True, False])
            })
        
        context.update({
            'cyberia_data': cyberia_data,
            'visitors': visitors,
            'club_mood': 'EUPHORIC' if cyberia_data['happiness_level'] > 80 else 'MELANCHOLIC'
        })
        return context

class KnightsView(TemplateView):
    """Interface des Knights of the Eastern Calculus"""
    template_name = 'wired/knights.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Données des Knights
        knights_data = {
            'active_knights': random.randint(3, 7),
            'monitoring_level': random.randint(80, 100),
            'protocol_compliance': random.randint(90, 100),
            'threat_level': random.choice(['NONE', 'LOW', 'MEDIUM', 'HIGH']),
            'last_activity': timezone.now()
        }
        
        # Générer des activités 
        activities = [
            'Monitoring Protocol 7 compliance',
            'Scanning for unauthorized access',
            'Maintaining digital purity',
            'Investigating anomalous patterns',
            'Protecting Wired integrity',
            'Analyzing consciousness fragments'
        ]
        
        knight_activities = random.sample(activities, random.randint(3, 5))
        
        context.update({
            'knights_data': knights_data,
            'knight_activities': knight_activities,
            'user_status': 'MONITORED' if random.choice([True, False]) else 'CLEAR',
            'compliance_score': random.randint(75, 100)
        })
        return context

class Protocol7View(TemplateView):
    """Interface Protocol 7"""
    template_name = 'wired/protocol7.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        
        protocol7_data = {
            'activation_level': random.randint(15, 45),  
            'love_connections': random.randint(100, 1000),
            'consciousness_links': random.randint(50, 200),
            'masami_influence': random.randint(20, 60),
            'lain_integration': random.randint(30, 80)
        }
        
        
        connections = []
        for i in range(random.randint(5, 12)):
            connections.append({
                'id': f'conn_{i}',
                'type': random.choice(['Love', 'Memory', 'Fear', 'Joy', 'Sadness']),
                'strength': random.randint(40, 100),
                'stability': random.randint(60, 95),
                'participants': random.randint(2, 8)
            })
        
        context.update({
            'protocol7_data': protocol7_data,
            'connections': connections,
            'protocol_status': 'PARTIAL_ACTIVATION',
            'warning_level': 'CAUTION' if protocol7_data['activation_level'] > 35 else 'SAFE'
        })
        return context


class WiredStatusAPIView(TemplateView):
    
    
    def get(self, request, *args, **kwargs):
        if request.headers.get('Accept') == 'application/json':
            status_data = {
                'timestamp': timezone.now().isoformat(),
                'wired_status': 'ONLINE',
                'reality_anchor': random.choice([True, False]),
                'active_connections': random.randint(50, 500),
                'protocol7_level': random.randint(15, 45),
                'dimensional_stability': random.randint(80, 100),
                'lain_presence': {
                    'detected': random.choice([True, False]),
                    'intensity': random.randint(20, 80),
                    'last_seen': timezone.now().isoformat()
                },
                'system_health': {
                    'encryption': 'ACTIVE',
                    'anonymization': 'ENABLED',
                    'corruption_level': random.randint(0, 3),
                    'uptime': random.randint(100, 10000)
                }
            }
            return JsonResponse(status_data)
        
        return super().get(request, *args, **kwargs)

class RealityControlAPIView(TemplateView):
    
    
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            action = data.get('action', '')
            
            if action == 'close_world':
                result = {
                    'success': True,
                    'message': 'Connection to real world severed',
                    'reality_level': random.randint(10, 30),
                    'wired_purity': random.randint(70, 90)
                }
            elif action == 'open_dimension':
                dimension_name = data.get('dimension_name', f'Layer_{random.randint(1000, 9999)}')
                result = {
                    'success': True,
                    'message': f'Dimension "{dimension_name}" opened',
                    'dimension_id': f'dim_{random.randint(100, 999)}',
                    'stability': random.randint(60, 95)
                }
            elif action == 'anchor_reality':
                result = {
                    'success': True,
                    'message': 'Reality anchor established',
                    'anchor_strength': random.randint(85, 100),
                    'temporal_stability': random.randint(90, 100)
                }
            else:
                result = {
                    'success': False,
                    'message': f'Unknown action: {action}'
                }
            
            return JsonResponse(result)
            
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'message': 'Invalid JSON'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Server error: {str(e)}'
            })

class LainQuoteAPIView(TemplateView):
    
    
    def get(self, request, *args, **kwargs):
        quotes = [
            {
                'text': 'Present day, present time.',
                'context': 'Reality anchor',
                'frequency': 'common'
            },
            {
                'text': 'God is here.',
                'context': 'Divine presence',
                'frequency': 'rare'
            },
            {
                'text': 'I am connected.',
                'context': 'Network awareness',
                'frequency': 'common'
            },
            {
                'text': 'The border between the real and the virtual is unclear.',
                'context': 'Reality questioning',
                'frequency': 'uncommon'
            },
            {
                'text': 'Let\'s all love Lain.',
                'context': 'Universal connection',
                'frequency': 'common'
            },
            {
                'text': 'No matter where you are, everyone is connected.',
                'context': 'Protocol 7',
                'frequency': 'uncommon'
            },
            {
                'text': 'The Wired is a world such as this one.',
                'context': 'Digital reality',
                'frequency': 'rare'
            },
            {
                'text': 'I don\'t need a body.',
                'context': 'Digital transcendence',
                'frequency': 'rare'
            }
        ]
        
        
        rarity = request.GET.get('rarity', 'any')
        if rarity != 'any':
            quotes = [q for q in quotes if q['frequency'] == rarity]
        
        selected_quote = random.choice(quotes)
        
        return JsonResponse({
            'quote': selected_quote,
            'timestamp': timezone.now().isoformat(),
            'source': 'Serial Experiments Lain'
        })

class CorruptionEngineView(TemplateView):
    """Moteur de corruption pour les effets visuels"""
    
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            corruption_type = data.get('type', 'glitch')
            intensity = min(int(data.get('intensity', 1)), 10)
            
            corruption_effects = {
                'glitch': {
                    'visual_distortion': intensity * 10,
                    'text_scramble': intensity > 3,
                    'color_shift': intensity * 15,
                    'scan_lines': intensity > 2
                },
                'phantom': {
                    'opacity_variation': intensity * 8,
                    'phase_shift': intensity > 4,
                    'temporal_echo': intensity > 6,
                    'dimensional_blur': intensity * 5
                },
                'spectral': {
                    'ethereal_glow': intensity * 12,
                    'transparency': intensity * 7,
                    'flickering': intensity > 2,
                    'astral_projection': intensity > 8
                },
                'dimensional': {
                    'perspective_shift': intensity * 6,
                    'reality_bend': intensity > 5,
                    'space_distortion': intensity * 8,
                    'layer_separation': intensity > 7
                }
            }
            
            effects = corruption_effects.get(corruption_type, corruption_effects['glitch'])
            
            return JsonResponse({
                'success': True,
                'corruption_type': corruption_type,
                'intensity': intensity,
                'effects': effects,
                'duration': intensity * 500,  # ms
                'timestamp': timezone.now().isoformat()
            })
            
        except (json.JSONDecodeError, ValueError):
            return JsonResponse({
                'success': False,
                'message': 'Invalid request data'
            })



class WiredTerminalView(TemplateView):
    """Terminal dédié aux commandes Wired"""
    template_name = 'wired/terminal.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        
        wired_commands = {
            'reality': ['/present_day', '/close_the_world', '/open_the_next', '/anchor'],
            'lain': ['/god_knows', '/nobody', '/phantom', '/masami'],
            'system': ['/protocol', '/navi', '/wired', '/status'],
            'effects': ['/corrupt', '/glitch', '/spectral', '/dimensional'],
            'easter': ['/cyberia', '/knights', '/love_lain', '/serial_experiments']
        }
        
        context.update({
            'wired_commands': wired_commands,
            'terminal_id': f'wired_{int(timezone.now().timestamp())}',
            'access_level': random.choice(['USER', 'ADVANCED', 'SYSTEM']),
            'reality_mode': random.choice(['STABLE', 'UNSTABLE', 'TRANSCENDENT'])
        })
        return context

class DigitalTranscendenceView(TemplateView):
    """Interface pour la transcendance numérique"""
    template_name = 'wired/transcendence.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        
        transcendence_levels = [
            {'name': 'Physical', 'description': 'Corporeal existence', 'value': 100},
            {'name': 'Digital', 'description': 'Basic Wired presence', 'value': random.randint(60, 90)},
            {'name': 'Information', 'description': 'Pure data form', 'value': random.randint(40, 70)},
            {'name': 'Consciousness', 'description': 'Thought without form', 'value': random.randint(20, 50)},
            {'name': 'Universal', 'description': 'Connected to all', 'value': random.randint(5, 25)}
        ]
        
        current_level = random.choice(['Physical', 'Digital', 'Information'])
        
        context.update({
            'transcendence_levels': transcendence_levels,
            'current_level': current_level,
            'transcendence_progress': random.randint(30, 80),
            'lain_guidance': random.choice([True, False]),
            'protocol7_influence': random.randint(10, 40)
        })
        return context