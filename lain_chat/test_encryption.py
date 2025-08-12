import os
import sys
import django

# Configuration Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lain_chat.settings')
django.setup()

from anonymization.encryption import LayerEncryption, generate_secure_session
from anonymization.models import AnonymousMessage, TrueAnonymousLayer
import uuid

def test_encryption_system():
    """Test complet du système de chiffrement"""
    
    print(" LAIN CHAT - Test du système de chiffrement")
    print("=" * 50)
    
    try:
        # Test 1: Chiffrement de base
        print("\n1. Test de chiffrement de base...")
        encryptor = LayerEncryption()
        
        test_message = "Present day, present time. This is a test message from the Wired."
        layer_id = str(uuid.uuid4())
        room_name = "test_room"
        
        # Chiffrer
        encrypted_data, nonce, salt = encryptor.encrypt_message(test_message, layer_id, room_name)
        print(f"    Message chiffré (taille: {len(encrypted_data)} bytes)")
        print(f"    Nonce généré: {nonce[:16]}...")
        print(f"    Sel généré: {len(salt)} bytes")
        
        # Déchiffrer
        decrypted_message = encryptor.decrypt_message(encrypted_data, nonce, salt)
        print(f"    Message déchiffré: {decrypted_message[:50]}...")
        
        # Vérifier l'intégrité
        if decrypted_message == test_message:
            print("    Intégrité vérifiée - chiffrement/déchiffrement OK")
        else:
            print("    ERREUR: Intégrité compromise !")
            return False
        
        # Test 2: Session sécurisée
        print("\n2. Test de génération de session...")
        session1 = generate_secure_session()
        session2 = generate_secure_session()
        
        print(f"    Session 1: {session1[:16]}...")
        print(f"    Session 2: {session2[:16]}...")
        
        if session1 != session2 and len(session1) == 64:
            print("    Sessions uniques et sécurisées")
        else:
            print("    ERREUR: Problème de génération de session")
            return False
        
        # Test 3: Sauvegarde en base avec chiffrement
        print("\n3. Test de sauvegarde en base...")
        
        # Créer un message chiffré en base
        message = AnonymousMessage()
        message.room_name = "test_room"
        
        test_content = "God knows what you are. This message should be encrypted in database."
        message.save_encrypted(test_content, layer_id, "test_room")
        
        print(f"    Message sauvé en base (ID: {str(message.message_id)[:8]}...)")
        
        # Récupérer et déchiffrer
        retrieved_message = AnonymousMessage.objects.get(message_id=message.message_id)
        decrypted_content = retrieved_message.get_decrypted_content()
        
        if decrypted_content == test_content:
            print("    Récupération et déchiffrement depuis base OK")
        else:
            print("   ERREUR: Problème de récupération depuis base")
            return False
        
        # Vérifier que le contenu n'est pas en clair en base
        raw_encrypted = retrieved_message.encrypted_content
        if test_content.encode() not in raw_encrypted:
            print("    Contenu bien chiffré en base (pas de plaintext)")
        else:
            print("    ERREUR: Contenu en clair détecté en base !")
            return False
        
        # Test 4: Vérification d'intégrité
        print("\n4. Test de vérification d'intégrité...")
        
        if retrieved_message.verify_integrity():
            print("    Intégrité du message vérifiée")
        else:
            print("    ERREUR: Intégrité compromise")
            return False
        
        # Cleanup
        retrieved_message.delete()
        print("    Cleanup effectué")
        
        print("\n" + "=" * 50)
        print(" TOUS LES TESTS PASSÉS - Chiffrement opérationnel !")
        print(" Niveau de sécurité: PRODUCTION")
        print("=" * 50)
        
        return True
        
    except Exception as e:
        print(f"\n ERREUR CRITIQUE: {e}")
        print(" Le système de chiffrement a échoué !")
        return False

def test_performance():
    """Test de performance du chiffrement"""
    print("\n Test de performance...")
    
    import time
    
    encryptor = LayerEncryption()
    test_message = "Performance test message " * 100  
    
    
    start_time = time.time()
    
    for i in range(100):
        encrypted_data, nonce, salt = encryptor.encrypt_message(test_message)
        decrypted = encryptor.decrypt_message(encrypted_data, nonce, salt)
    
    end_time = time.time()
    duration = end_time - start_time
    
    print(f"    100 cycles chiffrement/déchiffrement en {duration:.3f}s")
    print(f"    Performance: {200/duration:.1f} opérations/seconde")
    
    if duration < 5.0:  
        print("    Performance acceptable pour production")
    else:
        print("     Performance à optimiser")

if __name__ == "__main__":
    success = test_encryption_system()
    
    if success:
        test_performance()
        print("\n Le système de chiffrement est prêt pour la PHASE 2 !")
    else:
        print("\n Corriger les erreurs avant de continuer")
        sys.exit(1)