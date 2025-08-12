import uuid
import os
import hashlib
import time
from django.db import models
from django.utils import timezone
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import logging

logger = logging.getLogger('lain_models')

class TrueAnonymousLayer(models.Model):
    layer_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    layer_name = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    last_active = models.DateTimeField(auto_now=True)
    auto_destroy_at = models.DateTimeField(null=True, blank=True)
    corruption_level = models.IntegerField(default=0)
    
    class Meta:
        db_table = 'anonymous_layers'
        verbose_name = 'Anonymous Layer'
        verbose_name_plural = 'Anonymous Layers'
    
    def __str__(self):
        return f"Layer: {self.layer_name} ({str(self.layer_id)[:8]}...)"
    
    def is_expired(self):
        """Vérifie si le layer doit être détruit"""
        if self.auto_destroy_at:
            return timezone.now() > self.auto_destroy_at
        return False
    
    def burn_layer(self):
        """Destruction définitive du layer"""
        self.delete()
        return True

class LayerMapping(models.Model):
    """Table de mapping chiffrée - potentiellement en base séparée"""
    mapping_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_hash = models.CharField(max_length=64) 
    layer_id = models.UUIDField()  
    encrypted_link = models.BinaryField()  
    salt = models.CharField(max_length=32)  
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'anonymous_mapping'
        unique_together = ['user_hash', 'layer_id']
    
    @staticmethod
    def generate_user_hash(user_id, salt=None):
        """Génère hash anonyme pour l'utilisateur"""
        if salt is None:
            salt = os.urandom(16).hex()
        
        data = f"{user_id}:{salt}:{int(time.time() // 3600)}"  # Change chaque heure
        hash_obj = hashlib.pbkdf2_hmac('sha256', data.encode(), salt.encode(), 100000)
        return hash_obj.hex(), salt
    
    @staticmethod
    def encrypt_link(layer_id, user_id, key):
        """Chiffre le lien user->layer"""
        f = Fernet(key)
        link_data = f"{user_id}:{layer_id}:{int(time.time())}"
        return f.encrypt(link_data.encode())

class DataFragment(models.Model):
    """Fragmentation des données sensibles"""
    fragment_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    fragment_index = models.IntegerField()  
    encrypted_data = models.BinaryField()  
    checksum = models.CharField(max_length=64)  
    belongs_to_type = models.CharField(max_length=50)  
    belongs_to_id = models.UUIDField()  
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'data_fragments'
        unique_together = ['belongs_to_id', 'fragment_index']
    
    def verify_integrity(self):
        """Vérifie l'intégrité"""
        computed_checksum = hashlib.sha256(self.encrypted_data).hexdigest()
        return computed_checksum == self.checksum

class AnonymousMessage(models.Model):
    """Messages AES-256"""
    message_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    layer_id = models.UUIDField()
    room_name = models.CharField(max_length=100)
    
    content_hash = models.CharField(max_length=64)
    encrypted_content = models.BinaryField()  # AES-256
    encryption_nonce = models.CharField(max_length=32)  
    encryption_salt = models.BinaryField(null=True, blank=True) 
    
    
    timestamp = models.DateTimeField(auto_now_add=True)
    is_ephemeral = models.BooleanField(default=False)
    auto_destroy_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'anonymous_messages'
        indexes = [
            models.Index(fields=['layer_id', 'timestamp']),
            models.Index(fields=['room_name', 'timestamp']),
            models.Index(fields=['auto_destroy_at']),  
        ]
    
    def save_encrypted(self, plaintext_message: str, layer_id: str, room_name: str = None):
        
        try:
            from .encryption import encrypt_message  
            
            
            encrypted_data, nonce, salt = encrypt_message(
                message=plaintext_message,
                layer_id=layer_id,
                room_name=room_name or self.room_name
            )
            
            # Stockage des données chiffrées
            self.encrypted_content = encrypted_data
            self.encryption_nonce = nonce
            self.encryption_salt = salt
            
            
            self.content_hash = hashlib.sha256(plaintext_message.encode()).hexdigest()
            
        
            self.layer_id = uuid.UUID(layer_id) if isinstance(layer_id, str) else layer_id
            if room_name:
                self.room_name = room_name
            
           
            self.save()
            
            logger.info(f"Message encrypted and saved (ID: {str(self.message_id)[:8]}...)")
            
        except Exception as e:
            logger.error(f"Failed to save encrypted message: {e}")
            raise ValueError(f"Could not save encrypted message: {str(e)}")
    
    def get_decrypted_content(self) -> str:
        
        try:
            from .encryption import decrypt_message  
            
            if not self.encrypted_content:
                raise ValueError("No encrypted content to decrypt")
            
            
            plaintext = decrypt_message(
                encrypted_data=self.encrypted_content,
                nonce=self.encryption_nonce,
                salt=self.encryption_salt
            )
            
            
            computed_hash = hashlib.sha256(plaintext.encode()).hexdigest()
            if computed_hash != self.content_hash:
                logger.warning(f"Content hash mismatch for message {self.message_id}")
            
            return plaintext
            
        except Exception as e:
            logger.error(f"Failed to decrypt message {self.message_id}: {e}")
            raise ValueError(f"Could not decrypt message: {str(e)}")
    
    def verify_integrity(self) -> bool:
        
        try:
            plaintext = self.get_decrypted_content()
            computed_hash = hashlib.sha256(plaintext.encode()).hexdigest()
            return computed_hash == self.content_hash
        except:
            return False
    
    def is_expired(self):
        """Vérifie si le message doit être détruit"""
        if self.auto_destroy_at:
            return timezone.now() > self.auto_destroy_at
        return False
    
    def __str__(self):
        return f"Encrypted Msg from Layer {str(self.layer_id)[:8]}... at {self.timestamp}"

class KeyRotation(models.Model):
    """Historique de rotation des clés"""
    rotation_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    rotated_at = models.DateTimeField(auto_now_add=True)
    key_type = models.CharField(max_length=50)  
    affected_objects_count = models.IntegerField()  
    rotation_reason = models.CharField(max_length=100, default='scheduled')
    
    class Meta:
        db_table = 'key_rotations'
    
    def __str__(self):
        return f"Key rotation {self.key_type} at {self.rotated_at}"

class EmergencyBurn(models.Model):
    """Log des destructions d'urgence"""
    burn_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    burn_type = models.CharField(max_length=50)  
    burned_at = models.DateTimeField(auto_now_add=True)
    objects_destroyed_count = models.IntegerField()
    triggered_by_hash = models.CharField(max_length=64)  
    reason = models.CharField(max_length=200, default='emergency')
    
    class Meta:
        db_table = 'emergency_burns'
    
    def __str__(self):
        return f"Emergency burn {self.burn_type} at {self.burned_at}"

class MessageCleanupManager:
    """Gestionnaire pour la destruction des messages"""
    
    @staticmethod
    def cleanup_expired_messages():
        """Nettoie les messages expirés"""
        try:
            expired_count = AnonymousMessage.objects.filter(
                auto_destroy_at__lt=timezone.now()
            ).delete()[0]
            
            if expired_count > 0:
                logger.info(f"Cleaned up {expired_count} expired messages")
            
            return expired_count
            
        except Exception as e:
            logger.error(f"Cleanup failed: {e}")
            return 0
    
    @staticmethod
    def emergency_burn_all_messages():
        """Destruction d'urgence de tous les messages"""
        try:
            total_count = AnonymousMessage.objects.count()
            AnonymousMessage.objects.all().delete()
            
       
            EmergencyBurn.objects.create(
                burn_type='all_messages',
                objects_destroyed_count=total_count,
                triggered_by_hash='emergency_protocol',
                reason='Emergency burn executed'
            )
            
            logger.critical(f"EMERGENCY BURN: {total_count} messages destroyed")
            
            return total_count
            
        except Exception as e:
            logger.error(f"Emergency burn failed: {e}")
            raise