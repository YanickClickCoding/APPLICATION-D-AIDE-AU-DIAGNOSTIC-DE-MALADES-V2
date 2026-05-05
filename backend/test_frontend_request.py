"""
Simule exactement la requête que le frontend envoie
"""
import requests
import json

url = "http://localhost:8000/api/auth/login"
headers = {
    "Content-Type": "application/json",
    "Origin": "http://localhost:5173",  # Simuler le frontend
}
data = {
    "email": "aya.kouassi@sante.com",
    "password": "admin123"
}

print("=" * 80)
print("🌐 TEST REQUÊTE FRONTEND")
print("=" * 80)
print(f"\nURL: {url}")
print(f"Headers: {json.dumps(headers, indent=2)}")
print(f"Body: {json.dumps(data, indent=2)}")
print("\n" + "-" * 80)

try:
    response = requests.post(url, json=data, headers=headers)
    
    print(f"\n📥 RÉPONSE:")
    print(f"Status: {response.status_code}")
    print(f"Headers: {dict(response.headers)}")
    print(f"\nBody:")
    print(json.dumps(response.json(), indent=2))
    
    if response.status_code == 200:
        print("\n✅ SUCCÈS - Le frontend devrait fonctionner!")
    else:
        print(f"\n❌ ERREUR {response.status_code}")
        
except Exception as e:
    print(f"\n❌ EXCEPTION: {e}")

print("\n" + "=" * 80)
