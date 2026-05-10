#!/usr/bin/env python3
"""
Script de vérification de la fonctionnalité d'inscription
Vérifie que tous les composants sont en place et fonctionnels
"""

import sys
import os
import requests
from pathlib import Path

# Couleurs pour le terminal
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def print_success(message):
    print(f"{GREEN}✅ {message}{RESET}")

def print_error(message):
    print(f"{RED}❌ {message}{RESET}")

def print_warning(message):
    print(f"{YELLOW}⚠️  {message}{RESET}")

def print_info(message):
    print(f"{BLUE}ℹ️  {message}{RESET}")

def check_file_exists(filepath, description):
    """Vérifie qu'un fichier existe"""
    if Path(filepath).exists():
        print_success(f"{description} existe : {filepath}")
        return True
    else:
        print_error(f"{description} manquant : {filepath}")
        return False

def check_backend_running():
    """Vérifie que le backend est démarré"""
    try:
        response = requests.get('http://localhost:8000/docs', timeout=2)
        if response.status_code == 200:
            print_success("Backend démarré sur http://localhost:8000")
            return True
        else:
            print_error(f"Backend répond avec le code {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print_error("Backend non accessible sur http://localhost:8000")
        print_warning("Démarrez le backend avec : cd backend && python -m app.main")
        return False
    except Exception as e:
        print_error(f"Erreur lors de la vérification du backend : {e}")
        return False

def check_register_endpoint():
    """Vérifie que l'endpoint d'inscription existe"""
    try:
        # Test avec des données invalides pour vérifier que l'endpoint existe
        response = requests.post(
            'http://localhost:8000/api/auth/register',
            json={
                "nom": "TEST",
                "prenoms": "Verification",
                "email": f"test_verification_{os.urandom(4).hex()}@test.com",
                "mot_de_passe": "testpass123",
                "role": "medecin"
            },
            timeout=5
        )
        
        if response.status_code in [200, 201, 400, 422]:
            print_success("Endpoint /api/auth/register accessible")
            
            # Si le compte a été créé, afficher les détails
            if response.status_code in [200, 201]:
                data = response.json()
                print_info(f"Compte de test créé : {data.get('email')} (actif={data.get('actif')})")
            
            return True
        else:
            print_error(f"Endpoint répond avec le code {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print_error("Impossible de contacter l'endpoint d'inscription")
        return False
    except Exception as e:
        print_error(f"Erreur lors du test de l'endpoint : {e}")
        return False

def check_env_file():
    """Vérifie le fichier .env du backend"""
    env_path = Path('backend/.env')
    if not env_path.exists():
        print_error("Fichier backend/.env manquant")
        return False
    
    print_success("Fichier backend/.env existe")
    
    # Vérifier les variables importantes
    with open(env_path, 'r', encoding='utf-8') as f:
        content = f.read()
        
        checks = {
            'DATABASE_URL': 'Configuration de la base de données',
            'SECRET_KEY': 'Clé secrète pour JWT',
            'CORS_ORIGINS': 'Configuration CORS'
        }
        
        all_ok = True
        for var, desc in checks.items():
            if var in content:
                print_success(f"{desc} ({var}) présent")
            else:
                print_warning(f"{desc} ({var}) manquant")
                all_ok = False
        
        return all_ok

def check_frontend_config():
    """Vérifie la configuration du frontend"""
    config_path = Path('frontend/src/config.ts')
    if not config_path.exists():
        print_error("Fichier frontend/src/config.ts manquant")
        return False
    
    print_success("Fichier frontend/src/config.ts existe")
    
    with open(config_path, 'r', encoding='utf-8') as f:
        content = f.read()
        if 'API_BASE_URL' in content:
            print_success("API_BASE_URL configuré")
            return True
        else:
            print_warning("API_BASE_URL non trouvé dans config.ts")
            return False

def main():
    print("\n" + "="*60)
    print("🔍 VÉRIFICATION DE LA FONCTIONNALITÉ D'INSCRIPTION")
    print("="*60 + "\n")
    
    results = []
    
    # 1. Vérifier les fichiers
    print("📁 Vérification des fichiers...\n")
    results.append(check_file_exists('backend/app/routers/auth.py', 'Router d\'authentification'))
    results.append(check_file_exists('frontend/src/pages/Register.tsx', 'Page d\'inscription'))
    results.append(check_file_exists('frontend/src/config.ts', 'Configuration frontend'))
    results.append(check_env_file())
    
    # 2. Vérifier le backend
    print("\n🔧 Vérification du backend...\n")
    backend_running = check_backend_running()
    results.append(backend_running)
    
    if backend_running:
        results.append(check_register_endpoint())
    else:
        print_warning("Impossible de tester l'endpoint sans backend démarré")
    
    # 3. Résumé
    print("\n" + "="*60)
    print("📊 RÉSUMÉ")
    print("="*60 + "\n")
    
    total = len(results)
    passed = sum(results)
    
    if passed == total:
        print_success(f"Tous les tests sont passés ({passed}/{total})")
        print_info("\n✨ La fonctionnalité d'inscription est prête à être testée !")
        print_info("\nPour tester :")
        print_info("1. Ouvrez http://localhost:5173/register")
        print_info("2. Créez un compte")
        print_info("3. Connectez-vous en tant qu'admin pour l'activer")
    else:
        print_warning(f"{passed}/{total} tests passés")
        print_info("\n📋 Actions recommandées :")
        
        if not backend_running:
            print_info("1. Démarrez le backend : cd backend && python -m app.main")
        
        print_info("2. Consultez DEMARRAGE_RAPIDE_INSCRIPTION.md pour plus de détails")
    
    print("\n" + "="*60 + "\n")
    
    return 0 if passed == total else 1

if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  Vérification interrompue par l'utilisateur")
        sys.exit(1)
    except Exception as e:
        print_error(f"\n❌ Erreur inattendue : {e}")
        sys.exit(1)
