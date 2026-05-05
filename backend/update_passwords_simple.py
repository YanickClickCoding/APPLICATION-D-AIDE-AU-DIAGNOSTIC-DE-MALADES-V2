"""
Script simple pour mettre à jour les mots de passe
Utilise bcrypt directement
"""
import sys
from pathlib import Path
import bcrypt

# Ajouter le dossier parent au path
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy import create_engine, text
from app.config import settings

def hash_password(password: str) -> str:
    """Hash un mot de passe avec bcrypt"""
    # Convertir en bytes
    password_bytes = password.encode('utf-8')
    # Générer le salt et hasher
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    # Retourner en string
    return hashed.decode('utf-8')

def update_passwords():
    """
    Met à jour tous les mots de passe en bcrypt
    """
    print("=" * 80)
    print("🔐 MISE À JOUR DES MOTS DE PASSE EN BCRYPT")
    print("=" * 80)
    
    # Créer la connexion
    engine = create_engine(settings.DATABASE_URL)
    
    try:
        with engine.connect() as conn:
            # Récupérer tous les utilisateurs
            result = conn.execute(text("SELECT utilisateur_id, email, nom, prenoms, role FROM utilisateurs"))
            users = result.fetchall()
            
            if not users:
                print("\n⚠️  Aucun utilisateur trouvé dans la base")
                return
            
            print(f"\n📝 {len(users)} utilisateur(s) trouvé(s)")
            print("-" * 80)
            
            # Mot de passe par défaut
            default_password = "admin123"
            hashed_password = hash_password(default_password)
            
            updated_count = 0
            
            for user in users:
                user_id, email, nom, prenoms, role = user
                
                # Mettre à jour le mot de passe et actif
                conn.execute(
                    text("""
                        UPDATE utilisateurs 
                        SET mot_de_passe = :password, actif = TRUE 
                        WHERE utilisateur_id = :user_id
                    """),
                    {"password": hashed_password, "user_id": user_id}
                )
                
                updated_count += 1
                print(f"✅ {role.upper():12} - {prenoms} {nom:15} ({email})")
            
            # Commit
            conn.commit()
            
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
        raise

if __name__ == "__main__":
    try:
        update_passwords()
    except Exception as e:
        print(f"\n❌ Échec de la mise à jour: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
