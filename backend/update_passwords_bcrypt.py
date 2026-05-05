"""
Script pour mettre à jour les mots de passe en bcrypt
Convertit tous les mots de passe SHA256 en bcrypt
"""
import sys
from pathlib import Path

# Ajouter le dossier parent au path
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.user import User
from app.config import settings
from passlib.context import CryptContext

# Configuration du hachage
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def update_passwords():
    """
    Met à jour tous les mots de passe en bcrypt
    """
    print("=" * 80)
    print("🔐 MISE À JOUR DES MOTS DE PASSE EN BCRYPT")
    print("=" * 80)
    
    # Créer la connexion
    engine = create_engine(settings.DATABASE_URL)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    
    try:
        # Récupérer tous les utilisateurs
        users = db.query(User).all()
        
        if not users:
            print("\n⚠️  Aucun utilisateur trouvé dans la base")
            return
        
        print(f"\n📝 {len(users)} utilisateur(s) trouvé(s)")
        print("-" * 80)
        
        # Mot de passe par défaut pour tous les utilisateurs
        default_password = "admin123"
        hashed_password = pwd_context.hash(default_password)
        
        updated_count = 0
        
        for user in users:
            # Mettre à jour le mot de passe
            user.mot_de_passe = hashed_password
            
            # S'assurer que actif est True
            if not hasattr(user, 'actif') or user.actif is None:
                user.actif = True
            
            updated_count += 1
            print(f"✅ {user.role.upper():12} - {user.prenoms} {user.nom:15} ({user.email})")
        
        # Commit
        db.commit()
        
        print("-" * 80)
        print(f"\n✅ {updated_count} mot(s) de passe mis à jour avec succès!")
        
        print("\n" + "=" * 80)
        print("🔑 NOUVEAU MOT DE PASSE POUR TOUS LES UTILISATEURS")
        print("=" * 80)
        print(f"\n   Mot de passe: {default_password}")
        print("\n" + "=" * 80)
        print("💡 NOTES:")
        print("   - Tous les utilisateurs ont maintenant le même mot de passe")
        print("   - Les mots de passe sont maintenant hachés avec bcrypt")
        print("   - Changez les mots de passe après la première connexion")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n❌ ERREUR: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    try:
        update_passwords()
    except Exception as e:
        print(f"\n❌ Échec de la mise à jour: {e}")
        sys.exit(1)
