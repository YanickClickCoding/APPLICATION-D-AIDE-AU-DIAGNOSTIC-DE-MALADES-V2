"""
Script de test pour l'authentification
"""
import requests
import json

# Test de connexion
url = "http://localhost:8000/api/auth/login"
data = {
    "email": "aya.kouassi@sante.com",
    "password": "admin123"
}

print("=" * 80)
print("🔐 TEST D'AUTHENTIFICATION")
print("=" * 80)
print(f"\nURL: {url}")
print(f"Email: {data['email']}")
print(f"Password: {data['password']}")
print("\n" + "-" * 80)

try:
    response = requests.post(url, json=data)
    
    print(f"\nStatus Code: {response.status_code}")
    print(f"Headers: {dict(response.headers)}")
    print(f"\nResponse:")
    print(response.text)
    
    if response.status_code == 200:
        print("\n✅ AUTHENTIFICATION RÉUSSIE!")
        result = response.json()
        print(f"\nToken: {result['access_token'][:50]}...")
        print(f"User: {result['user']}")
    else:
        print(f"\n❌ ERREUR {response.status_code}")
        
except Exception as e:
    print(f"\n❌ EXCEPTION: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 80)
