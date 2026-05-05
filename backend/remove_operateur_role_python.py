"""
Script Python pour supprimer le rôle operateur
"""
import sys
from pathlib import Path

# Ajouter le dossier parent au path
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy import create_engine, text
from app.config import settings

def remove_operateur_role():
    """
    Supprime le rôle operateur de la base de données
    """
    print("=" * 80)
    print("🗑️  SUPPRESSION DU RÔLE OPERATEUR")
    print("=" * 80)
    
    # Créer la connexion
    engine = create_engine(settings.DATABASE_URL)
    
    try:
        with engine.connect() as conn:
            # Étape 1: Compter les utilisateurs avec le rôle operateur
            print("\n📊 Vérification des utilisateurs avec le rôle 'operateur'...")
            result = conn.execute(text("SELECT COUNT(*) FROM utilisateurs WHERE role = 'operateur'"))
            count = result.scalar()
            print(f"   Trouvé: {count} utilisateur(s) avec le rôle 'operateur'")
            
            if count > 0:
                print("\n🗑️  Suppression des utilisateurs avec le rôle 'operateur'...")
                conn.execute(text("DELETE FROM utilisateurs WHERE role = 'operateur'"))
                conn.commit()
                print(f"✅ {count} utilisateur(s) supprimé(s)")
            else:
                print("✅ Aucun utilisateur avec le rôle 'operateur'")
            
            # Étape 2: Modifier l'ENUM pour supprimer 'operateur'
            print("\n🔧 Modification de la colonne 'role' (suppression de 'operateur')...")
            try:
                conn.execute(text("""
                    ALTER TABLE utilisateurs 
                    MODIFY COLUMN role ENUM('admin', 'medecin', 'infirmier') DEFAULT 'medecin'
                """))
                conn.commit()
                print("✅ Colonne 'role' mise à jour (admin, medecin, infirmier)")
            except Exception as e:
                print(f"⚠️  Erreur lors de la modification: {e}")
            
            # Étape 3: Vérification
            print("\n📊 Vérification - Utilisateurs restants:")
            print("-" * 80)
            result = conn.execute(text("""
                SELECT utilisateur_id, nom, prenoms, email, role, created_at 
                FROM utilisateurs 
                ORDER BY FIELD(role, 'admin', 'medecin', 'infirmier'), nom
            """))
            
            users = result.fetchall()
            if users:
                for user in users:
                    user_id, nom, prenoms, email, role, created_at = user
                    print(f"  {role.upper():12} - {prenoms} {nom:15} ({email})")
            else:
                print("  Aucun utilisateur trouvé")
            
            print("\n📊 Statistiques par rôle:")
            print("-" * 80)
            result = conn.execute(text("""
                SELECT role, COUNT(*) as nombre 
                FROM utilisateurs 
                GROUP BY role 
                ORDER BY FIELD(role, 'admin', 'medecin', 'infirmier')
            """))
            
            stats = result.fetchall()
            for role, nombre in stats:
                print(f"  {role.upper():12} : {nombre}")
            
        print("\n" + "=" * 80)
        print("✅ Suppression du rôle 'operateur' terminée avec succès!")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n❌ ERREUR: {e}")
        raise

if __name__ == "__main__":
    try:
        remove_operateur_role()
    except Exception as e:
        print(f"\n❌ Échec de l'opération: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
