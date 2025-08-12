import os
import hashlib
import secrets
import time
import base64
from typing import Tuple, Optional
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from django.conf import settings
from django.core.cache import cache
import logging


logger = logging.getLogger('lain_encryption')

class LayerEncryption:
    
    
    def __init__(self):
        self.master_key = self._get_or_create_master_key()
        self.fernet = Fernet(self.master_key)
        self.key_creation_date = self._get_key_creation_date()
        
        # Vérifier si rotation nécessaire (tous les 7 jours)
        if self._should_rotate_key():
            self._rotate_master_key()
    
    def _get_master_key_path(self) -> str:
        """Chemin sécurisé pour la clé maître"""
        keys_dir = os.path.join(settings.BASE_DIR, '.lain_keys')
        
        
        if not os.path.exists(keys_dir):
            os.makedirs(keys_dir, mode=0o700)  
        
        return os.path.join(keys_dir, 'master.key')
    
    def _get_or_create_master_key(self) -> bytes:
        """Génère ou récupère la clé maître AES-256"""
        key_path = self._get_master_key_path()
        
        try:
            # Essayer de charger la clé existante
            if os.path.exists(key_path):
                with open(key_path, 'rb') as f:
                    key_data = f.read()
                
                # Vérifier que c'est une clé Fernet valide
                test_fernet = Fernet(key_data)
                # Test de chiffrement/déchiffrement
                test_data = b"test_integrity"
                encrypted = test_fernet.encrypt(test_data)
                decrypted = test_fernet.decrypt(encrypted)
                
                if decrypted == test_data:
                    logger.info("Master key loaded successfully")
                    return key_data
                else:
                    raise ValueError("Key integrity check failed")
            
        except Exception as e:
            logger.warning(f"Could not load existing key: {e}")
        
        # Générer nouvelle clé 
        return self._generate_new_master_key()
    
    def _generate_new_master_key(self) -> bytes:
        """Génère une nouvelle clé maître"""
        logger.info("Generating new master key")
        
        # Générer clé Fernet 
        new_key = Fernet.generate_key()
        key_path = self._get_master_key_path()
        
        try:
            
            with open(key_path, 'wb') as f:
                f.write(new_key)
            
            
            os.chmod(key_path, 0o600)
            
            # Enregistrer la date de création
            self._save_key_creation_date()
            
            logger.info("New master key generated and saved")
            return new_key
            
        except Exception as e:
            logger.error(f"Failed to save master key: {e}")
            raise
    
    def _get_key_creation_date(self) -> float:
        """Récupère la date de création de la clé"""
        date_file = os.path.join(os.path.dirname(self._get_master_key_path()), 'key_date.txt')
        
        try:
            if os.path.exists(date_file):
                with open(date_file, 'r') as f:
                    return float(f.read().strip())
        except:
            pass
        
        return time.time()  
    
    def _save_key_creation_date(self):
        date_file = os.path.join(os.path.dirname(self._get_master_key_path()), 'key_date.txt')
        
        try:
            with open(date_file, 'w') as f:
                f.write(str(time.time()))
            os.chmod(date_file, 0o600)
        except Exception as e:
            logger.warning(f"Could not save key creation date: {e}")
    
    def _should_rotate_key(self) -> bool:
        
        # Rotation tous les 7 jours
        rotation_interval = 7 * 24 * 3600  
        return (time.time() - self.key_creation_date) > rotation_interval
    
    def _rotate_master_key(self):
        """Effectue la rotation de la clé maître"""
        logger.info("Starting master key rotation")
        old_key_path = self._get_master_key_path()
        backup_path = f"{old_key_path}.backup.{int(time.time())}"
        
        try:
            # Sauvegarde l'ancienne clé
            if os.path.exists(old_key_path):
                os.rename(old_key_path, backup_path)
                os.chmod(backup_path, 0o600)
            
            # Génére nouvelle clé
            self.master_key = self._generate_new_master_key()
            self.fernet = Fernet(self.master_key)
            
            logger.info("Master key rotation completed")
            
        except Exception as e:
            logger.error(f"Key rotation failed: {e}")
            # Restaure l'ancienne clé en cas d'erreur
            if os.path.exists(backup_path):
                os.rename(backup_path, old_key_path)
            raise
    
    def encrypt_message(self, message: str, layer_id: str = None, room_name: str = None) -> Tuple[bytes, str, bytes]:
        
        try:
            # Génére sel cryptographique unique
            salt = secrets.token_bytes(32)  
            
            # Génére nonce unique pour ce message
            nonce = secrets.token_hex(16)  
            
            metadata = {
                'layer_id': layer_id or 'anonymous',
                'room_name': room_name or 'unknown',
                'timestamp': int(time.time()),
                'nonce': nonce
            }
            
            
            full_payload = f"{metadata['layer_id']}|{metadata['room_name']}|{metadata['timestamp']}|{nonce}|{message}"
            
            
            salted_payload = salt.hex() + '|' + full_payload
            
            
            encrypted_data = self.fernet.encrypt(salted_payload.encode('utf-8'))
            
            logger.debug(f"Message encrypted successfully (nonce: {nonce[:8]}...)")
            
            return encrypted_data, nonce, salt
            
        except Exception as e:
            logger.error(f"Encryption failed: {e}")
            raise ValueError(f"Message encryption failed: {str(e)}")
    
    def decrypt_message(self, encrypted_data: bytes, nonce: str, salt: bytes = None) -> str:
       
        try:
            
            decrypted_data = self.fernet.decrypt(encrypted_data)
            salted_payload = decrypted_data.decode('utf-8')
            
            
            parts = salted_payload.split('|', 1)
            if len(parts) != 2:
                raise ValueError("Invalid encrypted payload format")
            
            extracted_salt, payload = parts
            
            
            payload_parts = payload.split('|', 4)
            if len(payload_parts) != 5:
                raise ValueError("Invalid payload structure")
            
            layer_id, room_name, timestamp, extracted_nonce, message = payload_parts
            
            
            if extracted_nonce != nonce:
                logger.warning("Nonce mismatch during decryption")
            
            logger.debug(f"Message decrypted successfully (nonce: {nonce[:8]}...)")
            
            return message
            
        except Exception as e:
            logger.error(f"Decryption failed: {e}")
            raise ValueError(f"Message decryption failed: {str(e)}")
    
    def generate_secure_hash(self, data: str, salt: bytes = None, iterations: int = 100000) -> Tuple[str, bytes]:
        
        if salt is None:
            salt = secrets.token_bytes(32)  # 256 bits de sel
        
        try:
            # PBKDF2 avec SHA-256
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,  # 256 bits de sortie
                salt=salt,
                iterations=iterations,
            )
            
            key = kdf.derive(data.encode('utf-8'))
            hash_b64 = base64.urlsafe_b64encode(key).decode('utf-8')
            
            return hash_b64, salt
            
        except Exception as e:
            logger.error(f"Hash generation failed: {e}")
            raise ValueError(f"Hash generation failed: {str(e)}")

class SecureSessionManager:
    """Gestionnaire de sessions anonymes sécurisées"""
    
    @staticmethod
    def generate_anonymous_session() -> str:
        """Génère un ID de session cryptographiquement sécurisé"""
        
        random_bytes = secrets.token_bytes(32)
        
        
        timestamp = int(time.time() * 1000000)  # Microsecondes
        
        
        hasher = hashlib.blake2b(digest_size=32)
        hasher.update(random_bytes)
        hasher.update(timestamp.to_bytes(8, 'big'))
        
       
        try:
            system_random = os.urandom(16)
            hasher.update(system_random)
        except:
            pass  # Fallback silencieux
        
        return hasher.hexdigest()
    
    @staticmethod
    def generate_layer_hash(layer_name: str, user_context: str = None, rotation_days: int = 1) -> str:
        
        # Sel de rotation basé sur les jours 
        rotation_salt = int(time.time() // (86400 * rotation_days))  # Rotation tous  jours
        
        
        day_entropy = secrets.token_bytes(16)
        
        
        hasher = hashlib.blake2b(digest_size=32)
        hasher.update(layer_name.encode('utf-8'))
        hasher.update(rotation_salt.to_bytes(8, 'big'))
        hasher.update(day_entropy)
        
        if user_context:
            hasher.update(user_context.encode('utf-8'))
        
        return hasher.hexdigest()


_encryption_instance = None

def get_encryption_instance() -> LayerEncryption:
    """Récupère l'instance singleton du système de chiffrement"""
    global _encryption_instance
    
    if _encryption_instance is None:
        _encryption_instance = LayerEncryption()
    
    return _encryption_instance


def encrypt_message(message: str, layer_id: str = None, room_name: str = None) -> Tuple[bytes, str, bytes]:
    """Fonction de convenance pour chiffrer un message"""
    return get_encryption_instance().encrypt_message(message, layer_id, room_name)

def decrypt_message(encrypted_data: bytes, nonce: str, salt: bytes = None) -> str:
    """Fonction de convenance pour déchiffrer un message"""
    return get_encryption_instance().decrypt_message(encrypted_data, nonce, salt)

def generate_secure_session() -> str:
    """Fonction de convenance pour générer une session sécurisée"""
    return SecureSessionManager.generate_anonymous_session()

def generate_layer_hash(layer_name: str, user_context: str = None) -> str:
    """Fonction de convenance pour générer un hash de layer"""
    return SecureSessionManager.generate_layer_hash(layer_name, user_context)



class ZeroKnowledgeAuth:
    """
    Système d'authentification zero-knowledge pour les layers
    Compatible avec l'architecture Lain existante
    """
    
    def __init__(self):
        self.session_manager = SecureSessionManager()
    
    def generate_layer_proof(self, layer_name: str, user_context: str = None) -> str:
        
        try:
            
            challenge = secrets.token_bytes(32)
            
            
            layer_hash = self.session_manager.generate_layer_hash(layer_name, user_context)
            
            
            hasher = hashlib.blake2b(digest_size=32)
            hasher.update(challenge)
            hasher.update(layer_hash.encode('utf-8'))
            hasher.update(layer_name.encode('utf-8'))
            
            proof = hasher.hexdigest()
            
            logger.debug(f"Generated layer proof for {layer_name}")
            return proof
            
        except Exception as e:
            logger.error(f"Failed to generate layer proof: {e}")
            raise ValueError(f"Proof generation failed: {str(e)}")
    
    def verify_layer_access(self, layer_name: str, proof: str, user_context: str = None) -> bool:
        
        try:
            
            expected_proof = self.generate_layer_proof(layer_name, user_context)
            
            
            return secrets.compare_digest(proof.encode('utf-8'), expected_proof.encode('utf-8'))
            
        except Exception as e:
            logger.warning(f"Layer access verification failed: {e}")
            return False
    
    def create_anonymous_session(self, layer_access_proofs: list = None) -> dict:
        
        try:
            session_id = self.session_manager.generate_anonymous_session()
            
            session_info = {
                'session_id': session_id,
                'created_at': int(time.time()),
                'layer_proofs': layer_access_proofs or [],
                'anonymization_level': 1
            }
            
            # Hash de la session pour vérification
            session_hash = hashlib.sha256(
                f"{session_id}:{session_info['created_at']}".encode('utf-8')
            ).hexdigest()
            
            session_info['session_hash'] = session_hash
            
            logger.info(f"Created anonymous session (hash: {session_hash[:8]}...)")
            return session_info
            
        except Exception as e:
            logger.error(f"Failed to create anonymous session: {e}")
            raise ValueError(f"Session creation failed: {str(e)}")
    
    def validate_session(self, session_info: dict) -> bool:
      
        try:
            if not all(key in session_info for key in ['session_id', 'created_at', 'session_hash']):
                return False
            
            
            expected_hash = hashlib.sha256(
                f"{session_info['session_id']}:{session_info['created_at']}".encode('utf-8')
            ).hexdigest()
            
           
            hash_valid = secrets.compare_digest(
                session_info['session_hash'].encode('utf-8'),
                expected_hash.encode('utf-8')
            )
            
            # Vérifier que la session n'est pas expirée 
            session_age = time.time() - session_info['created_at']
            not_expired = session_age < (24 * 3600)  
            
            return hash_valid and not_expired
            
        except Exception as e:
            logger.warning(f"Session validation failed: {e}")
            return False