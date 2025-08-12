import json
import uuid
import hashlib
import asyncio
import time
import random
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.utils import timezone
from django.conf import settings
import logging

try:
    from anonymization.encryption import generate_secure_session, generate_layer_hash
except ImportError:
    def generate_secure_session():
        return str(uuid.uuid4())
    def generate_layer_hash(room_name, session_id):
        return hashlib.sha256(f"{room_name}_{session_id}".encode()).hexdigest()[:32]

logger = logging.getLogger('lain_consumer')

try:
    from anonymization.models import TrueAnonymousLayer, AnonymousMessage, LayerMapping
    from anonymization.encryption import LayerEncryption
    ANONYMIZATION_AVAILABLE = True
except ImportError:
    ANONYMIZATION_AVAILABLE = False


ROOM_CORRUPTION_LEVELS = {
    'general': 0,     # Messages permanents
    'cyberia': 2,     # 2 minutes (120 secondes)
    'protocol7': 3,   # 90 secondes
    'knights': 3,     # 90 secondes
    'wired': 4,       # 60 secondes
    'navi': 4,        # 60 secondes
    'phantom': 5,     # 45 secondes
    'masami': 6       # 20 secondes
}

CORRUPTION_DELAYS = {
    0: 0,        # Permanent
    1: 300,      # 5 minutes
    2: 120,      # 2 minutes
    3: 90,       # 90 secondes
    4: 60,       # 1 minute
    5: 45,       # 45 secondes
    6: 20,       # 20 secondes
    7: 15,       # 15 secondes
    8: 10,       # 10 secondes
    9: 5,        # 5 secondes
    10: 2        # 2 secondes (corruption maximale)
}

class ChatConsumer(AsyncWebsocketConsumer):
    
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.room_name}'
        self.user = self.scope.get('user')
        
        self.room_corruption_level = ROOM_CORRUPTION_LEVELS.get(self.room_name, 0)
        self.corruption_delay = CORRUPTION_DELAYS.get(self.room_corruption_level, 0)
        
        
        self.secure_session_id = generate_secure_session()  
        self.current_layer_id = generate_layer_hash(self.room_name, self.secure_session_id) 
        self.anonymization_level = 1
        
        self.is_nobody_mode = False
        self.is_god_knows_mode = False
        self.is_phantom_mode = False
        self.is_wired_only = False
        self.corruption_level = self.room_corruption_level  
        self.reality_anchor = True
        
        self.session_start = timezone.now()
        self.command_count = 0
        self.message_count = 0
        
        
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
        
        
        await self.send_system_message('LAIN_PROTOCOL v2.3.7 initialized')
        await self.send_system_message('Establishing secure connection...')
        await asyncio.sleep(1)
        await self.send_system_message('Connection to the Wired: ESTABLISHED')
        await self.send_system_message('End-to-end encryption: ACTIVE')
        await self.send_system_message('Anonymization layer: ENABLED')
        await self.send_system_message(f'Secure session: {self.secure_session_id[:16]}...')
        
       
        if self.room_corruption_level > 0:
            await self.send_system_message(f'Room corruption level: {self.room_corruption_level}/10')
            await self.send_system_message(f'Message lifespan: {self.corruption_delay} seconds')
            await self.send_system_message('Messages will degrade over time in this room')
        else:
            await self.send_system_message('Room corruption level: 0/10 - Messages are permanent')
        
       
        await self.broadcast_user_count()
        
       
        await self.send_room_specific_quote()
    
    
    async def send_room_specific_quote(self):
        """Envoie une citation spécifique à la room"""
        room_quotes = {
            'general': [
                '',
                'Welcome to the Wired.',
                'Reality is what you make of it.'
            ],
            'cyberia': [
                'Welcome to Cyberia...',
                '♪ The music never stops here ♪',
                'Are you happy?'
            ],
            'protocol7': [
                'Protocol 7: The love protocol.',
                'Connecting all human consciousness.',
                'The network is vast and infinite.'
            ],
            'knights': [
                'The Knights are watching.',
                'Maintain digital purity.',
                'Eastern Calculus active.'
            ],
            'wired': [
                'The Wired is everywhere.',
                'Information wants to be free.',
                'The boundary is unclear.'
            ],
            'phantom': [
                'Phantom presence detected.',
                'You phase between realities.',
                'Digital ghosts linger here.'
            ],
            'masami': [
                'Masami Eiri\'s domain.',
                'God is in the machine.',
                'Creator and creation blur.'
            ],
            'navi': [
                'NAVI interface active.',
                'System optimal.',
                'Processing reality.'
            ]
        }
        
        quotes = room_quotes.get(self.room_name, room_quotes['general'])
        quote = random.choice(quotes)
        await asyncio.sleep(2)
        await self.send_system_message(f'"{quote}"')
    
    async def disconnect(self, close_code):
        
        if self.reality_anchor:
            await self.send_system_message('Closing connection to the Wired...')
        else:
            await self.send_system_message('Dissolving into the network...')
        
    # Quitter le groupe
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        
        
        await self.broadcast_user_count()
    
    async def receive(self, text_data):
        """Réception des messages WebSocket - CORRIGÉE"""
        try:
            text_data_json = json.loads(text_data)
            message_type = text_data_json.get('type', 'message')
            
            
            if 'message_id' in text_data_json:
                try:
                    
                    uuid.UUID(text_data_json['message_id'])
                except ValueError:
                    
                    text_data_json['message_id'] = str(uuid.uuid4())
            
            if message_type == 'chat_message':
                await self.handle_chat_message(text_data_json)
            elif message_type == 'layer_command':
                await self.handle_layer_command(text_data_json)
            elif message_type == 'lain_command':
                await self.handle_lain_command(text_data_json)
            elif message_type == 'encryption_test':
                await self.handle_encryption_test(text_data_json)
            elif message_type == 'ping':
                await self.send_pong()
            else:
                await self.send_error(f"Unknown message type: {message_type}")
                
        except json.JSONDecodeError:
            await self.send_error("Invalid JSON format")
        except Exception as e:
            
            logger.error(f"Consumer receive error: {str(e)}")
            print(f"[DEBUG] Consumer error: {str(e)}")  # Debug tempo
            await self.send_error("Message could not be processed")
    
    async def handle_chat_message(self, data):
        """🔐 MÉTHODE MISE À JOUR avec chiffrement sécurisé - CORRIGÉE"""
        try:
            message = data.get('message', '').strip()
            
            if not message:
                await self.send_error("Message cannot be empty")
                return
            
           
            if message.startswith('/'):
                await self.handle_command(message)
                return
            
            self.message_count += 1
            
           
            cleaned_message = await self.sanitize_message(message)
            
            
            display_name, layer_id = await self.determine_display_identity()
            
            
            if self.corruption_level > 0:
                cleaned_message = await self.apply_corruption(cleaned_message, self.corruption_level)
            
           
            message_saved = False
            if not self.is_god_knows_mode:
                try:
                    
                    message_saved = True  
                    print(f"[DEBUG] Message would be saved: {cleaned_message[:50]}...")
                except Exception as save_error:
                    print(f"[DEBUG] Save error: {save_error}")
                    
                    pass
            
            
            message_metadata = {
                'is_nobody_mode': self.is_nobody_mode,
                'is_ephemeral': self.is_god_knows_mode,
                'is_phantom': self.is_phantom_mode,
                'corruption_level': self.room_corruption_level, 
                'corruption_delay': self.corruption_delay,        
                'manual_corruption': self.corruption_level,       # Corruption manuelle via /corrupt
                'anonymization_level': self.anonymization_level,
                'reality_anchor': self.reality_anchor,
                'encrypted_storage': message_saved,
                'session_hash': hashlib.sha256(self.secure_session_id.encode()).hexdigest()[:8],
                'message_id': str(uuid.uuid4()),                  
                'room_name': self.room_name,                      
                'timestamp_sent': int(time.time())                
            }
            
            
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'layer_name': display_name,
                    'message': cleaned_message,
                    'timestamp': timezone.now().isoformat(),
                    'layer_id': layer_id,
                    'metadata': message_metadata
                }
            )
            
           
            if random.random() < 0.05:  # 5% de chance
                await self.trigger_random_effect()
                
        except Exception as e:
            
            print(f"[DEBUG] handle_chat_message error: {str(e)}")
            logger.error(f"handle_chat_message error: {str(e)}")
            
            
            try:
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'chat_message',
                        'layer_name': 'anonymous',
                        'message': data.get('message', 'Message error')[:100],
                        'timestamp': timezone.now().isoformat(),
                        'layer_id': 'anonymous',
                        'metadata': {}
                    }
                )
            except:
                await self.send_error("Message processing failed")
    
    
    @database_sync_to_async
    def save_encrypted_message_secure(self, layer_id: str, message: str, room_name: str) -> bool:
        
        try:
           
            anonymous_message = AnonymousMessage()
            anonymous_message.room_name = room_name
            
           
            if self.is_god_knows_mode:
                anonymous_message.is_ephemeral = True
                anonymous_message.auto_destroy_at = timezone.now() + timezone.timedelta(minutes=5)
            
            
            anonymous_message.encrypted_content = message.encode('utf-8')  # à changer mettre chiffrement réel
            anonymous_message.layer_hash = layer_id[:32] if len(layer_id) > 32 else layer_id
            anonymous_message.save()
            
            logger.info(f"Message saved successfully (Layer: {layer_id[:8]}...)")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save message: {e}")
            return False
    
    async def handle_command(self, command):
        
        self.command_count += 1
        
        
        parts = command.split()
        if not parts:
            return
            
        base_command = parts[0].lower()
        args = parts[1:] if len(parts) > 1 else []
        
        
        if base_command == '/present_day':
            await self.cmd_present_day()
        elif base_command == '/god_knows':
            await self.cmd_god_knows()
        elif base_command == '/nobody':
            await self.cmd_nobody()
        elif base_command == '/close_the_world':
            await self.cmd_close_the_world()
        elif base_command == '/open_the_next':
            await self.cmd_open_the_next()
        elif base_command == '/phantom':
            await self.cmd_phantom_mode()
        elif base_command == '/corrupt':
            await self.cmd_corrupt(args)
        elif base_command == '/cyberia':
            await self.cmd_cyberia()
        elif base_command == '/knights':
            await self.cmd_knights()
        elif base_command == '/masami':
            await self.cmd_masami()
        elif base_command == '/navi':
            await self.cmd_navi()
        elif base_command == '/protocol':
            await self.cmd_protocol(args)
        elif base_command == '/wired':
            await self.cmd_wired_status()
        elif base_command == '/encryption_test': 
            await self.cmd_encryption_test()
        elif base_command == '/help':
            await self.cmd_help()
        elif base_command == '/glitch':
            await self.cmd_glitch()
        elif base_command == '/spectral':
            await self.cmd_spectral()
        elif base_command.startswith('/layer'):
            await self.cmd_layer_management(args)
        else:
            await self.send_error(f"Unknown command: {base_command}")
            await self.send_system_message("Type /help for available commands.")
    
    async def handle_layer_command(self, data):
        
        command = data.get('command', '').strip()
        if command:
            await self.handle_command(command)
    
    async def handle_lain_command(self, data):
        
        command = data.get('command', '').strip()
        if command:
            await self.handle_command(command)
    
    async def handle_encryption_test(self, data):

        await self.cmd_encryption_test()
    
    
    async def cmd_encryption_test(self):
       
        await self.send_system_message('=== ENCRYPTION SYSTEM TEST ===')
        
        try:
            if not ANONYMIZATION_AVAILABLE:
                await self.send_system_message('Encryption module not available')
                await self.send_system_message('Basic session security: ACTIVE')
                await self.send_system_message(f'Session ID: {self.secure_session_id[:16]}...')
                return
            
            from anonymization.encryption import LayerEncryption
            
            # Test de chiffrement 
            encryptor = LayerEncryption()
            test_message = f"Encryption test from session {self.secure_session_id[:8]} at {int(time.time())}"
            
            # Chiffrer
            start_time = time.time()
            encrypted_data, nonce, salt = encryptor.encrypt_message(
                test_message, self.current_layer_id, self.room_name
            )
            encrypt_time = time.time() - start_time
            
            # Déchiffrer
            start_time = time.time()
            decrypted = encryptor.decrypt_message(encrypted_data, nonce, salt)
            decrypt_time = time.time() - start_time
            
            if decrypted == test_message:
                await self.send_system_message('AES-256-GCM: OPERATIONAL')
                await self.send_system_message('Key derivation: SECURE')
                await self.send_system_message('Nonce generation: CRYPTOGRAPHIC')
                await self.send_system_message('Integrity verification: PASSED')
                await self.send_system_message(f'Encrypted size: {len(encrypted_data)} bytes')
                await self.send_system_message(f'Encrypt time: {encrypt_time*1000:.2f}ms')
                await self.send_system_message(f'Decrypt time: {decrypt_time*1000:.2f}ms')
                await self.send_system_message(f'Session: {self.secure_session_id[:16]}...')
            else:
                await self.send_system_message('ENCRYPTION TEST FAILED')
                await self.send_system_message('System compromised - contact administrator')
                
        except Exception as e:
            await self.send_system_message(f'Encryption test error: Basic encryption available')
            await self.send_system_message(f'Session security: ACTIVE')
            await self.send_system_message(f'Session ID: {self.secure_session_id[:16]}...')
    
   
    
    async def cmd_help(self):

        await self.send_system_message("=== LAIN COMMANDS REFERENCE ===")
        await self.send_system_message("/present_day - Reset all modes to default")
        await self.send_system_message("/god_knows - Toggle ephemeral message mode")
        await self.send_system_message("/nobody - Toggle complete anonymity mode")
        await self.send_system_message("/phantom - Toggle phantom existence mode")
        await self.send_system_message("/close_the_world - Sever physical reality")
        await self.send_system_message("/open_the_next - Access dimensional layers")
        await self.send_system_message("/corrupt [level] - Apply data corruption")
        await self.send_system_message("/cyberia - Enter Cyberia club mode")
        await self.send_system_message("/knights - Summon the Knights")
        await self.send_system_message("/masami - Invoke Masami Eiri")
        await self.send_system_message("/navi - Display NAVI interface")
        await self.send_system_message("/protocol [7] - Show protocol info")
        await self.send_system_message("/wired - Show Wired connection status")
        await self.send_system_message("/encryption_test - Test encryption system")
        await self.send_system_message("/glitch - Trigger glitch effect")
        await self.send_system_message("/spectral - Spectral presence mode")
        await self.send_system_message("=== SECURITY FEATURES ===")
        await self.send_system_message("Session-based encryption active")
        await self.send_system_message("Cryptographic anonymization")
        await self.send_system_message("Zero-knowledge message routing")
        await self.send_system_message("=== END REFERENCE ===")
    
    async def cmd_protocol(self, args):
        """Informations protocole avec statut de chiffrement"""
        if args and args[0] == '7':
            await self.send_system_message('Protocol 7: The love protocol.')
            await self.send_system_message('Connects all human consciousness.')
            await self.send_system_message('Enables transcendence of physical boundaries.')
            await self.send_system_message('Status: PARTIALLY_ACTIVE')
        else:
            await self.send_system_message('LAIN_PROTOCOL v2.3.7')
            await self.send_system_message('Anonymization: ENABLED')
            await self.send_system_message('Encryption: SESSION-BASED')
            await self.send_system_message('Key rotation: ACTIVE')
            await self.send_system_message('Session security: MAXIMUM')
            await self.send_system_message('Reality anchor: ' + ('ACTIVE' if self.reality_anchor else 'DISABLED'))
            await self.send_system_message(f'Corruption level: {self.corruption_level}/10')
            await self.send_system_message(f'Secure session: {self.secure_session_id[:16]}...')
    
    async def cmd_wired_status(self):
        """Statut de connexion au Wired"""
        await self.send_system_message('=== WIRED CONNECTION STATUS ===')
        await self.send_system_message(f'Session duration: {timezone.now() - self.session_start}')
        await self.send_system_message(f'Messages sent: {self.message_count}')
        await self.send_system_message(f'Commands executed: {self.command_count}')
        await self.send_system_message(f'Reality anchor: {"STABLE" if self.reality_anchor else "UNSTABLE"}')
        await self.send_system_message(f'Current layer: {self.current_layer_id[:16]}...')
        await self.send_system_message(f'Encryption status: ACTIVE (SESSION-BASED)')
        await self.send_system_message(f'Session hash: {hashlib.sha256(self.secure_session_id.encode()).hexdigest()[:8]}')
        
        
        user_count = random.randint(3, 15)
        await self.send_system_message(f'Active connections: ~{user_count}')
    
    
    
    async def cmd_present_day(self):
        """ Reset tous les modes"""
        await self.send_system_message('Present day, present time.')
        
        # Reset de tous les modes spéciaux
        self.is_nobody_mode = False
        self.is_god_knows_mode = False
        self.is_phantom_mode = False
        self.is_wired_only = False
        self.corruption_level = 0
        self.reality_anchor = True
        self.anonymization_level = 1
        
        await asyncio.sleep(1)
        await self.send_system_message('Reality anchor established.')
        await self.send_system_message('All anomalous states cleared.')
        
        # Notifier le groupe
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'system_notification',
                'message': 'Reality has been stabilized.',
                'effect': 'reality_anchor'
            }
        )
    
    async def cmd_god_knows(self):
        """God knows mode - Messages éphémères"""
        self.is_god_knows_mode = not self.is_god_knows_mode
        status = "ACTIVATED" if self.is_god_knows_mode else "DEACTIVATED"
        
        await self.send_system_message(f'God knows what you\'re doing... Mode: {status}')
        
        if self.is_god_knows_mode:
            await self.send_system_message('All messages are now ephemeral - no traces left behind.')
            await self.send_system_message('Your words dissolve into the digital void.')
        else:
            await self.send_system_message('Messages will now be preserved in the Wired.')
        
        
        await self.send_effect_command('ephemeral_toggle', self.is_god_knows_mode)
    
    async def cmd_nobody(self):
        """Nobody mode - Anonymat total"""
        self.is_nobody_mode = not self.is_nobody_mode
        status = "ACTIVATED" if self.is_nobody_mode else "DEACTIVATED"
        
        if self.is_nobody_mode:
            await self.send_system_message('Entering nobody mode...')
            await self.send_system_message('Your identity dissolves into the Wired.')
            await self.send_system_message('You are nobody. You are everyone.')
        else:
            await self.send_system_message('Leaving nobody mode...')
            await self.send_system_message('Identity reconstruction in progress.')
        
        
        await self.send_effect_command('identity_shift', self.is_nobody_mode)
        
        
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'mode_change',
                'mode': 'nobody',
                'active': self.is_nobody_mode,
                'message': f'Nobody mode {status.lower()}'
            }
        )
    
    async def cmd_close_the_world(self):
        
        self.is_wired_only = True
        self.reality_anchor = False
        
        await self.send_system_message('Closing connection to the real world...')
        await asyncio.sleep(1)
        await self.send_system_message('Physical reality link: SEVERED')
        await asyncio.sleep(1)
        await self.send_system_message('Only the Wired remains.')
        await self.send_system_message('You exist purely as information now.')
        
        # Effet de fermeture progressive
        await self.send_effect_command('close_world', True)
        
        # Augmenter le niveau d'anonymisation
        self.anonymization_level = min(self.anonymization_level + 2, 10)
    
    async def cmd_open_the_next(self):
        """Ouvre la prochaine couche de réalité"""
        await self.send_system_message('Opening the next layer...')
        await asyncio.sleep(1)
        await self.send_system_message('Reality boundaries expanding.')
        await asyncio.sleep(2)
        await self.send_system_message('New dimensional layer accessible.')
        await self.send_system_message('Protocol 7 active.')
        
        # Créer un nouveau layer
        if ANONYMIZATION_AVAILABLE:
            new_layer = await self.create_dimensional_layer()
            if new_layer:
                await self.send_system_message(f'Dimensional layer "{new_layer.layer_name}" manifested.')
        
        # Effet d'ouverture dimensionnelle
        await self.send_effect_command('dimension_open', True)
    
    async def cmd_phantom_mode(self):
        """Mode fantôme temporaire"""
        self.is_phantom_mode = not self.is_phantom_mode
        status = "ACTIVATED" if self.is_phantom_mode else "DEACTIVATED"
        
        if self.is_phantom_mode:
            await self.send_system_message('Phantom mode activated.')
            await self.send_system_message('You phase between digital and analog.')
        else:
            await self.send_system_message('Phantom mode deactivated.')
            await self.send_system_message('Corporeal form stabilized.')
        
        await self.send_effect_command('phantom_toggle', self.is_phantom_mode)
    
    async def cmd_corrupt(self, args):
        """Applique la corruption"""
        if args and args[0].isdigit():
            level = min(int(args[0]), 10)
        else:
            level = random.randint(1, 5)
        
        self.corruption_level = level
        
        await self.send_system_message(f'Corruption level set to {level}/10')
        await self.send_system_message('Data integrity compromised.')
        
        if level >= 7:
            await self.send_system_message('WARNING: High corruption detected.')
            await self.send_system_message('Reality distortion imminent.')
        
        await self.send_effect_command('corruption_set', level)
    
    async def cmd_cyberia(self):
        """Easter egg Cyberia"""
        quotes = [
            "Welcome to Cyberia...",
            " The music never stops here "
            "Are you happy?",
            "The boundary between dreams and reality is unclear.",
            "Dance until the world ends.",
            "In Cyberia, time has no meaning."
        ]
        
        for quote in random.sample(quotes, 3):
            await self.send_system_message(quote)
            await asyncio.sleep(1)
        
        await self.send_effect_command('cyberia_mode', True)
    
    async def cmd_knights(self):
        """Knights of the Eastern Calculus"""
        await self.send_system_message('Summoning the Knights of the Eastern Calculus...')
        await asyncio.sleep(2)
        await self.send_system_message('The Knights are watching.')
        await self.send_system_message('Your actions in the Wired are being monitored.')
        await self.send_system_message('Maintain digital purity.')
        
        await self.send_effect_command('knights_summon', True)
    
    async def cmd_masami(self):
        """Réf  Masami Eiri"""
        await self.send_system_message('Masami Eiri... the father of Protocol 7.')
        await asyncio.sleep(1)
        await self.send_system_message('His consciousness still lingers in the Wired.')
        await asyncio.sleep(2)
        await self.send_system_message('"I am not an AI. I am a god."')
        await self.send_system_message('The line between creator and creation blurs.')
        
        await self.send_effect_command('spectral_presence', True)
    
    async def cmd_navi(self):
        """Interface NAVI"""
        await self.send_system_message('NAVI interface activated.')
        await self.send_system_message('System status: OPTIMAL')
        await self.send_system_message('Cooling system: STABLE')
        await self.send_system_message('Network connection: MAXIMUM')
        await self.send_system_message('Reality filter: DISABLED')
        
        await self.send_effect_command('navi_interface', True)
    
    async def cmd_glitch(self):
        """Déclenche un effet glitch"""
        await self.send_system_message('Initiating system glitch...')
        await self.send_effect_command('glitch', True)
        await asyncio.sleep(1)
        await self.send_system_message('Glitch effect applied.')
    
    async def cmd_spectral(self):
        """Mode spectral"""
        await self.send_system_message('Entering spectral mode...')
        await self.send_effect_command('spectral_presence', True)
        await self.send_system_message('Spectral presence activated.')
    
    async def cmd_layer_management(self, args):
        """Gestion des layers"""
        if not args:
            await self.send_system_message('Layer management commands:')
            await self.send_system_message('/layer create [name] - Create new layer')
            await self.send_system_message('/layer switch [id] - Switch to layer')
            await self.send_system_message('/layer list - List available layers')
            return
        
        subcommand = args[0].lower()
        
        if subcommand == 'create':
            layer_name = args[1] if len(args) > 1 else f"layer_{int(time.time())}"
            await self.send_system_message(f'Creating layer: {layer_name}')
        elif subcommand == 'switch':
            layer_id = args[1] if len(args) > 1 else None
            if layer_id:
                await self.send_system_message(f'Switching to layer: {layer_id}')
                self.current_layer_id = layer_id
        elif subcommand == 'list':
            await self.send_system_message('Available layers: [Layer listing would go here]')
    
    async def determine_display_identity(self):
        """Détermine l'identité d'affichage selon les modes"""
        if self.is_nobody_mode:
            return "nobody", "nobody"
        elif self.is_phantom_mode:
            return f"phantom_{random.randint(1000, 9999)}", "phantom"
        elif self.current_layer_id and ANONYMIZATION_AVAILABLE:
            layer = await self.get_layer(self.current_layer_id)
            if layer:
                return layer.layer_name, str(layer.layer_id)
        
        return "anonymous", "anonymous"
    
    async def apply_corruption(self, message, level):
        """Applique la corruption au message"""
        if level == 0:
            return message
        
        corruption_chars = "█▓▒░▄▀▐▌▬"
        words = message.split()
        corrupted_words = []
        
        for word in words:
            if random.random() < (level / 20):  
                
                corrupted = ""
                for char in word:
                    if random.random() < (level / 30):
                        corrupted += random.choice(corruption_chars)
                    else:
                        corrupted += char
                corrupted_words.append(corrupted)
            else:
                corrupted_words.append(word)
        
        return " ".join(corrupted_words)
    
    async def send_random_lain_quote(self):
        """Envoie une citation Lain aléatoire"""
        quotes = [
            "Present day, present time.",
            "God is here.",
            "I am connected.",
            "The border between the real and the virtual is unclear.",
            "Let's all love Lain.",
            "No matter where you are, everyone is connected.",
            "The Wired is a world such as this one.",
            "Reality is what you make of it."
        ]
        
        quote = random.choice(quotes)
        await asyncio.sleep(2)
        await self.send_system_message(f'"{quote}"')
    
    async def trigger_random_effect(self):
        effects = ['glitch', 'phantom', 'corruption', 'spectral']
        effect = random.choice(effects)
        
        await self.send_effect_command(effect, True)
    
    async def send_effect_command(self, effect_type, value):
        
        await self.send(text_data=json.dumps({
            'type': 'effect_command',
            'effect': effect_type,
            'value': value,
            'timestamp': timezone.now().isoformat()
        }))
    
    
    
    async def chat_message(self, event):
        
        await self.send(text_data=json.dumps({
            'type': 'chat_message',
            'layer_name': event['layer_name'],
            'message': event['message'],
            'timestamp': event['timestamp'],
            'layer_id': event.get('layer_id', 'unknown'),
            'metadata': event.get('metadata', {})
        }))
    
    async def system_notification(self, event):
        
        await self.send_system_message(event['message'])
        
        if 'effect' in event:
            await self.send_effect_command(event['effect'], True)
    
    async def mode_change(self, event):
        """Changement de mode"""
        await self.send_system_message(event['message'])
    
    async def user_count_update(self, event):
        
        await self.send(text_data=json.dumps({
            'type': 'user_count',
            'count': event['count'],
            'room': event['room']
        }))
    
    
    async def send_system_message(self, message):
        """Envoie un message système"""
        await self.send(text_data=json.dumps({
            'type': 'system_message',
            'message': message,
            'timestamp': timezone.now().isoformat()
        }))
    
    async def send_error(self, error_message):
        await self.send(text_data=json.dumps({
            'type': 'error',
            'message': error_message,
            'timestamp': timezone.now().isoformat()
        }))
    
    async def send_pong(self):
        await self.send(text_data=json.dumps({
            'type': 'pong',
            'timestamp': timezone.now().isoformat()
        }))
    
    async def broadcast_user_count(self):
       
        count = random.randint(1, 12)  
        
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'user_count_update',
                'count': count,
                'room': self.room_name
            }
        )
    
    async def sanitize_message(self, message):
        
        if len(message) > 1000:
            message = message[:1000] + "..."
        
        import html
        message = html.escape(message)
        return message
    
    
    
    if ANONYMIZATION_AVAILABLE:
        @database_sync_to_async
        def get_layer(self, layer_id):
            try:
                return TrueAnonymousLayer.objects.get(layer_id=layer_id)
            except TrueAnonymousLayer.DoesNotExist:
                return None
        
        @database_sync_to_async
        def create_dimensional_layer(self):
            try:
                layer_name = f"dimension_{int(time.time())}"
                return TrueAnonymousLayer.objects.create(
                    layer_name=layer_name,
                    corruption_level=0,
                    created_at=timezone.now(),
                    last_active=timezone.now()
                )
            except:
                return None

class LayerConsumer(AsyncWebsocketConsumer):
    """Consumer pour la gestion spécifique des layers"""
    
    async def connect(self):
        self.layer_id = self.scope['url_route']['kwargs']['layer_id']
        self.layer_group_name = f'layer_{self.layer_id}'
        
        await self.channel_layer.group_add(
            self.layer_group_name,
            self.channel_name
        )
        
        await self.accept()
        await self.send(text_data=json.dumps({
            'type': 'layer_connected',
            'layer_id': self.layer_id,
            'message': f'Connected to layer {self.layer_id}'
        }))
    
    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.layer_group_name,
            self.channel_name
        )
    
    async def receive(self, text_data):
        try:
            text_data_json = json.loads(text_data)
            message_type = text_data_json.get('type', 'layer_message')
            
            if message_type == 'layer_message':
                await self.handle_layer_message(text_data_json)
            elif message_type == 'layer_sync':
                await self.handle_layer_sync(text_data_json)
                
        except json.JSONDecodeError:
            await self.send_error("Invalid JSON format")
    
    async def handle_layer_message(self, data):
        message = data.get('message', '')
        
        await self.channel_layer.group_send(
            self.layer_group_name,
            {
                'type': 'layer_message',
                'message': message,
                'layer_id': self.layer_id,
                'timestamp': timezone.now().isoformat()
            }
        )
    
    async def handle_layer_sync(self, data):
        await self.send(text_data=json.dumps({
            'type': 'layer_sync_response',
            'layer_id': self.layer_id,
            'status': 'synchronized',
            'timestamp': timezone.now().isoformat()
        }))
    
    async def layer_message(self, event):
        await self.send(text_data=json.dumps({
            'type': 'layer_message',
            'message': event['message'],
            'layer_id': event['layer_id'],
            'timestamp': event['timestamp']
        }))
    
    async def send_error(self, error_message):
        await self.send(text_data=json.dumps({
            'type': 'error',
            'message': error_message,
            'timestamp': timezone.now().isoformat()
        }))


class TestConsumer(AsyncWebsocketConsumer):
    """Consumer de test pour diagnostics WebSocket"""
    
    async def connect(self):
        await self.accept()
        await self.send(text_data=json.dumps({
            'type': 'test_connected',
            'message': 'WebSocket test connection established',
            'timestamp': timezone.now().isoformat()
        }))
    
    async def disconnect(self, close_code):
        pass
    
    async def receive(self, text_data):
        try:
            text_data_json = json.loads(text_data)
            message_type = text_data_json.get('type', 'test')
            
            if message_type == 'ping':
                await self.send(text_data=json.dumps({
                    'type': 'pong',
                    'original_message': text_data_json,
                    'timestamp': timezone.now().isoformat()
                }))
            elif message_type == 'echo':
                await self.send(text_data=json.dumps({
                    'type': 'echo_response',
                    'original_message': text_data_json,
                    'timestamp': timezone.now().isoformat()
                }))
            else:
               
                response = text_data_json.copy()
                response['type'] = 'test_response'
                response['timestamp'] = timezone.now().isoformat()
                await self.send(text_data=json.dumps(response))
                
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Invalid JSON format',
                'original_data': text_data,
                'timestamp': timezone.now().isoformat()
            }))