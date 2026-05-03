"""
Script pour initialiser et démarrer le serveur backend
1. Vérifie la base de données
2. Ajoute les utilisateurs de test
3. Vérifie/charge le modèle ML
4. Démarre le serveur FastAPI
"""
import sys
import os
from pathlib import Path
import subprocess

def print_header(title):
    """Affiche un en-tête formaté"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)

def check_database():
    """Vérifie la connexion à la base de données"""
    print_header("🔍 VÉRIFICATION BASE DE DONNÉES")
    
    try:
        from app.database import engine
        from sqlalchemy import text
        
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print("✅ Connexion à la base de données réussie")
            return True
    except Exception as e:
        print(f"❌ Erreur de connexion à la base de données: {e}")
        print("\n💡 Vérifiez:")
        print("   1. MySQL est démarré")
        print("   2. La base 'sante_plus_ia' existe")
        print("   3. Les credentials dans .env sont corrects")
        return False

def seed_users():
    """Ajoute les utilisateurs de test"""
    print_header("🌱 AJOUT DES UTILISATEURS")
    
    try:
        result = subprocess.run(
            [sys.executable, "seed_users.py"],
            capture_output=False,
            text=True
        )
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Erreur lors du seed: {e}")
        return False

def check_model():
    """Vérifie si un modèle ML existe"""
    print_header("🤖 VÉRIFICATION MODÈLE ML")
    
    model_path = Path("ml_models")
    
    if not model_path.exists():
        print("⚠️  Dossier ml_models n'existe pas")
        model_path.mkdir(exist_ok=True)
        print("✅ Dossier ml_models créé")
    
    model_files = list(model_path.glob("*.joblib"))
    
    if not model_files:
        print("⚠️  Aucun modèle trouvé")
        print("\n💡 Pour entraîner un modèle:")
        print("   python train_initial_model.py")
        print("\n⚠️  Le serveur démarrera SANS modèle ML")
        print("   Les prédictions ne seront pas disponibles")
        return False
    else:
        latest_model = max(model_files, key=lambda p: p.stat().st_mtime)
        print(f"✅ Modèle trouvé: {latest_model.name}")
        return True

def start_server():
    """Démarre le serveur FastAPI"""
    print_header("🚀 DÉMARRAGE DU SERVEUR")
    
    print("\n📡 Le serveur va démarrer sur: http://localhost:8000")
    print("📚 Documentation API: http://localhost:8000/docs")
    print("\n⌨️  Appuyez sur Ctrl+C pour arrêter le serveur")
    print("\n" + "-" * 80 + "\n")
    
    try:
        # Démarrer uvicorn
        import uvicorn
        uvicorn.run(
            "app.main:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n\n" + "=" * 80)
        print("🛑 Serveur arrêté")
        print("=" * 80)
    except Exception as e:
        print(f"\n❌ Erreur lors du démarrage: {e}")
        return False
    
    return True

def main():
    """
    Fonction principale
    """
    print("\n" + "=" * 80)
    print("  🏥 MEDICAL DIAGNOSTIC AI SYSTEM - BACKEND")
    print("=" * 80)
    
    # 1. Vérifier la base de données
    if not check_database():
        print("\n❌ Impossible de continuer sans connexion à la base de données")
        sys.exit(1)
    
    # 2. Seed des utilisateurs
    print("\n")
    response = input("Voulez-vous ajouter/mettre à jour les utilisateurs de test? (o/n): ")
    if response.lower() == 'o':
        seed_users()
    else:
        print("⏭️  Seed des utilisateurs ignoré")
    
    # 3. Vérifier le modèle
    has_model = check_model()
    
    if not has_model:
        print("\n")
        response = input("Voulez-vous entraîner un modèle maintenant? (o/n): ")
        if response.lower() == 'o':
            print("\n🤖 Entraînement du modèle...")
            result = subprocess.run([sys.executable, "train_initial_model.py"])
            if result.returncode != 0:
                print("\n⚠️  Entraînement échoué, mais le serveur peut démarrer sans modèle")
        else:
            print("⏭️  Entraînement ignoré")
    
    # 4. Démarrer le serveur
    print("\n")
    input("Appuyez sur Entrée pour démarrer le serveur...")
    start_server()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Au revoir!")
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        sys.exit(1)
