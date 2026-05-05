"""
Script de migration pour ajouter les colonnes manquantes à la table utilisateurs
"""
import sys
from pathlib import Path

# Ajouter le dossier parent au path
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy import create_engine, text
from app.config import settings

def migrate_user_table():
    """
    Ajoute les colonnes actif et last_login à la table utilisateurs
    """
    print("=" * 80)
    print("🔧 MIGRATION: Table utilisateurs")
    print("=" * 80)
    
    # Créer la connexion
    engine = create_engine(settings.DATABASE_URL)
    
    try:
        with engine.connect() as conn:
            print("\n📝 Ajout de la colonne 'actif'...")
            try:
                conn.execute(text("""
                    ALTER TABLE utilisateurs 
                    ADD COLUMN actif BOOLEAN NOT NULL DEFAULT TRUE AFTER role
                """))
                conn.commit()
                print("✅ Colonne 'actif' ajoutée")
            except Exception as e:
                if "Duplicate column name" in str(e):
                    print("⚠️  Colonne 'actif' existe déjà")
                else:
                    raise
            
            print("\n📝 Ajout de la colonne 'last_login'...")
            try:
                conn.execute(text("""
                    ALTER TABLE utilisateurs 
                    ADD COLUMN last_login DATETIME NULL AFTER created_at
                """))
                conn.commit()
                print("✅ Colonne 'last_login' ajoutée")
            except Exception as e:
                if "Duplicate column name" in str(e):
                    print("⚠️  Colonne 'last_login' existe déjà")
                else:
                    raise
            
            print("\n📝 Mise à jour des rôles...")
            try:
                conn.execute(text("""
                    ALTER TABLE utilisateurs 
                    MODIFY COLUMN role ENUM('admin', 'operateur', 'medecin', 'infirmier') DEFAULT 'operateur'
                """))
                conn.commit()
                print("✅ Rôles mis à jour (admin, operateur, medecin, infirmier)")
            except Exception as e:
                print(f"⚠️  Erreur lors de la mise à jour des rôles: {e}")
            
            print("\n📊 Structure de la table utilisateurs:")
            print("-" * 80)
            result = conn.execute(text("DESCRIBE utilisateurs"))
            for row in result:
                print(f"  {row[0]:20} {row[1]:30} {row[2]:10} {row[3]:10}")
            
        print("\n" + "=" * 80)
        print("✅ Migration terminée avec succès!")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n❌ ERREUR: {e}")
        raise

if __name__ == "__main__":
    try:
        migrate_user_table()
    except Exception as e:
        print(f"\n❌ Échec de la migration: {e}")
        sys.exit(1)
