"""
Script pour ajouter des utilisateurs de test dans la base de données
Crée 3 utilisateurs: admin, médecin, infirmier
"""
import sys
from pathlib import Path
from datetime import datetime

# Ajouter le dossier parent au path
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.user import User
from app.config import settings
import hashlib

def hash_password(password: str) -> str:
    """Hash simple du mot de passe (en production, utiliser bcrypt)"""
    return hashlib.sha256(password.encode()).hexdigest()

def seed_users():
    """
    Ajoute des utilisateurs de test
    """
    print("=" * 80)
    print("🌱 SEED: Ajout des utilisateurs de test")
    print("=" * 80)
    
    # Créer la connexion
    engine = create_engine(settings.DATABASE_URL)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    
    try:
        # Vérifier si des utilisateurs existent déjà
        existing_count = db.query(User).count()
        
        if existing_count > 0:
            print(f"\n⚠️  {existing_count} utilisateur(s) déjà présent(s) dans la base")
            response = input("Voulez-vous les supprimer et recréer? (o/n): ")
            
            if response.lower() == 'o':
                db.query(User).delete()
                db.commit()
                print("✅ Utilisateurs existants supprimés")
            else:
                print("❌ Opération annulée")
                return
        
        # Utilisateurs à créer
        users_data = [
            {
                "nom": "Admin",
                "prenom": "Système",
                "email": "admin@sante.com",
                "mot_de_passe": "admin123",
                "role": "admin"
            },
            {
                "nom": "Dubois",
                "prenom": "Marie",
                "email": "marie.dubois@sante.com",
                "mot_de_passe": "medecin123",
                "role": "medecin"
            },
            {
                "nom": "Martin",
                "prenom": "Pierre",
                "email": "pierre.martin@sante.com",
                "mot_de_passe": "infirmier123",
                "role": "infirmier"
            }
        ]
        
        print("\n📝 Création des utilisateurs...")
        print("-" * 80)
        
        created_users = []
        
        for user_data in users_data:
            # Hasher le mot de passe
            password = user_data.pop("mot_de_passe")
            hashed_password = hash_password(password)
            
            # Créer l'utilisateur
            user = User(
                **user_data,
                mot_de_passe=hashed_password,
                actif=True
            )
            
            db.add(user)
            db.flush()  # Pour obtenir l'ID
            
            created_users.append({
                "id": user.id,
                "nom": user.nom,
                "prenom": user.prenom,
                "email": user.email,
                "role": user.role,
                "password": password  # Mot de passe en clair pour affichage
            })
            
            print(f"✅ {user.role.upper():12} - {user.prenom} {user.nom:15} ({user.email})")
        
        # Commit
        db.commit()
        
        print("-" * 80)
        print(f"\n✅ {len(created_users)} utilisateurs créés avec succès!")
        
        # Afficher les credentials
        print("\n" + "=" * 80)
        print("🔑 CREDENTIALS DE CONNEXION")
        print("=" * 80)
        
        for user in created_users:
            print(f"\n{user['role'].upper()}:")
            print(f"  Email:        {user['email']}")
            print(f"  Mot de passe: {user['password']}")
            print(f"  ID:           {user['id']}")
        
        print("\n" + "=" * 80)
        print("💡 NOTES:")
        print("   - Ces mots de passe sont pour le développement uniquement")
        print("   - En production, utilisez des mots de passe forts")
        print("   - Le hachage actuel est simple (SHA256)")
        print("   - Pour la production, utilisez bcrypt ou argon2")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n❌ ERREUR: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    try:
        seed_users()
    except Exception as e:
        print(f"\n❌ Échec du seed: {e}")
        sys.exit(1)
