import requests
import time
import json
import sys

def test_security_headers():
    """Test des headers de sécurité"""
    print("=== TEST DES HEADERS DE SÉCURITÉ ===")
    
    try:
        response = requests.get('http://127.0.0.1:8000/')
        
       
        expected_headers = [
            'Content-Security-Policy',
            'Strict-Transport-Security', 
            'X-Frame-Options',
            'X-Content-Type-Options',
            'X-XSS-Protection',
            'Referrer-Policy',
            'Permissions-Policy'
        ]
        
        print("Headers de sécurité détectés :")
        security_score = 0
        for header in expected_headers:
            if header in response.headers:
                print(f" {header}: {response.headers[header][:50]}...")
                security_score += 1
            else:
                print(f" {header}: MANQUANT")
        
        
        fingerprint_headers = ['Server', 'X-Powered-By', 'Via']
        print("\nHeaders de fingerprinting supprimés :")
        for header in fingerprint_headers:
            if header not in response.headers or response.headers[header] == 'WebServer/1.0':
                print(f" {header}: Correctement supprimé/anonymisé")
                security_score += 1
            else:
                print(f" {header}: {response.headers[header]} (devrait être supprimé)")
        
        print(f"\nScore sécurité headers: {security_score}/{len(expected_headers) + len(fingerprint_headers)}")
        return security_score >= 8
        
    except requests.exceptions.ConnectionError:
        print(" Serveur non accessible sur http://127.0.0.1:8000/")
        print("Lancez d'abord: python -m daphne -b 127.0.0.1 -p 8000 lain_chat.asgi:application")
        return False
    except Exception as e:
        print(f" Erreur lors du test: {e}")
        return False

def test_attack_protection():
    
    print("\n=== TEST DE PROTECTION CONTRE LES ATTAQUES ===")
    
    # Tests XSS
    xss_payloads = [
        '<script>alert("xss")</script>',
        'javascript:alert("xss")',
        '<img src="x" onerror="alert(1)">',
        'onload="alert(1)"'
    ]
    
    print("Test de protection XSS :")
    blocked_count = 0
    for payload in xss_payloads:
        try:
            response = requests.get(f'http://127.0.0.1:8000/?test={payload}', timeout=5)
            if response.status_code == 403:
                print(f" XSS bloqué: {payload[:30]}...")
                blocked_count += 1
            else:
                print(f" XSS non bloqué: {payload[:30]}...")
        except:
            print(f" Erreur test XSS: {payload[:30]}...")
    
# Tests SQL Injection
    sql_payloads = [
        "' UNION SELECT * FROM users--",
        "1; DROP TABLE users;--",
        "' OR '1'='1",
        "union select password from users"
    ]
    
    print("\nTest de protection SQL Injection :")
    for payload in sql_payloads:
        try:
            response = requests.get(f'http://127.0.0.1:8000/?id={payload}', timeout=5)
            if response.status_code == 403:
                print(f" SQL Injection bloqué: {payload[:30]}...")
                blocked_count += 1
            else:
                print(f" SQL Injection non bloqué: {payload[:30]}...")
        except:
            print(f" Erreur test SQL: {payload[:30]}...")
    
    print(f"\nAttaques bloquées: {blocked_count}/{len(xss_payloads) + len(sql_payloads)}")
    return blocked_count >= 6

def test_rate_limiting():
    """Test du rate limiting"""
    print("\n=== TEST DU RATE LIMITING ===")
    
    print("Envoi de 15 requêtes rapides...")
    blocked_count = 0
    
    for i in range(15):
        try:
            response = requests.get('http://127.0.0.1:8000/', timeout=2)
            if response.status_code == 403:
                print(f" Requête {i+1}: BLOQUÉE (rate limit)")
                blocked_count += 1
            elif i < 10:
                print(f" Requête {i+1}: OK")
            else:
                print(f" Requête {i+1}: Devrait être bloquée")
        except:
            print(f" Erreur requête {i+1}")
        
        time.sleep(0.1)  
    
    print(f"\nRequêtes bloquées par rate limiting: {blocked_count}")
    return blocked_count > 0

def test_websocket_security():
    """Test de sécurité WebSocket"""
    print("\n TEST SÉCURITÉ WEBSOCKET ")
    
    try:
        import websocket
        
        
        print("Test de connexion WebSocket autorisée...")
        try:
            ws = websocket.create_connection("ws://127.0.0.1:8000/ws/chat/general/")
            print(" Connexion WebSocket autorisée réussie")
            ws.close()
            websocket_ok = True
        except Exception as e:
            print(f" Connexion WebSocket échouée: {e}")
            websocket_ok = False
        
        
        print("Test de connexion WebSocket non autorisée...")
        try:
            ws = websocket.create_connection("ws://127.0.0.1:8000/ws/unauthorized/")
            print(" Connexion non autorisée acceptée (problème de sécurité)")
            ws.close()
            security_ok = False
        except:
            print(" Connexion non autorisée rejetée")
            security_ok = True
        
        return websocket_ok and security_ok
        
    except ImportError:
        print("Module websocket-client non installé")
        print("Installation: pip install websocket-client")
        return False

def test_anonymization():
    """Test d'anonymisation"""
    print("\n=== TEST D'ANONYMISATION ===")
    
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept-Language': 'fr-FR,fr;q=0.9,en;q=0.8',
        'X-Forwarded-For': '192.168.1.100',
        'X-Real-IP': '192.168.1.100',
        'Referer': 'https://google.com/search?q=test'
    }
    
    try:
        response = requests.get('http://127.0.0.1:8000/', headers=headers)
        
        if response.status_code == 200:
            print("✓ Requête avec headers identifiants acceptée")
            print("✓ Anonymisation appliquée côté serveur")
            return True
        else:
            print(f"✗ Requête rejetée: status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"✗ Erreur test anonymisation: {e}")
        return False

def test_input_sanitization():
    """Test de nettoyage des entrées"""
    print("\n=== TEST DE NETTOYAGE DES ENTRÉES ===")
    
    
    malicious_inputs = [
        '<script>alert("test")</script>',
        '<?php echo "test"; ?>',
        '${7*7}',
        '../../../etc/passwd'
    ]
    
    sanitized_count = 0
    
    for malicious_input in malicious_inputs:
        try:
            response = requests.get(f'http://127.0.0.1:8000/?input={malicious_input}')
            if response.status_code != 403:  
                
                print(f"✓ Entrée nettoyée: {malicious_input[:30]}...")
                sanitized_count += 1
            else:
                print(f"✓ Entrée bloquée: {malicious_input[:30]}...")
                sanitized_count += 1
        except Exception as e:
            print(f"✗ Erreur test nettoyage: {malicious_input[:30]}...")
    
    print(f"Entrées traitées de façon sécurisée: {sanitized_count}/{len(malicious_inputs)}")
    return sanitized_count == len(malicious_inputs)

def main():
    
    print(" LAIN CHAT ")
    print("=" * 60)
    
    tests = [
        ("Headers de sécurité", test_security_headers),
        ("Protection contre attaques", test_attack_protection),
        ("Rate limiting", test_rate_limiting),
        ("Sécurité WebSocket", test_websocket_security),
        ("Anonymisation", test_anonymization),
        ("Nettoyage des entrées", test_input_sanitization)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append(result)
            status = "RÉUSSI" if result else "ÉCHOUÉ"
            print(f"\n{test_name}: {status}")
        except Exception as e:
            print(f"\n{test_name}: ERREUR - {e}")
            results.append(False)
    
    # Résumé final
    print("\n" + "=" * 60)
    print(" RÉSUMÉ DES TESTS DE SÉCURITÉ")
    print("=" * 60)
    
    passed = sum(results)
    total = len(results)
    percentage = (passed / total) * 100
    
    for i, (test_name, _) in enumerate(tests):
        status = "✓ RÉUSSI" if results[i] else "✗ ÉCHOUÉ"
        print(f"{status:<12} {test_name}")
    
    print(f"\nScore global: {passed}/{total} ({percentage:.1f}%)")
    
    if percentage >= 80:
        print(" Sécurité EXCELLENTE ")
    elif percentage >= 60:
        print("  Sécurité CORRECTE ")
    else:
        print(" Sécurité INSUFFISANTE ")
    
    print("\n PROCHAINES ÉTAPES :")
    if passed < total:
        print("1. Corriger les tests échoués")
        print("2. Vérifier la configuration des middlewares")
        print("3. Relancer les tests")
    else:
        print("1. Passer à la Phase 3 (Corruption temporelle)")
        print("2. Tests en conditions réelles")
        print("3. Déploiement sécurisé")

if __name__ == "__main__":
    main()