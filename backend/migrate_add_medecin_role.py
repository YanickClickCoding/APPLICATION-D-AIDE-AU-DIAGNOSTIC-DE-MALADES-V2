"""
Migration: Ajouter la colonne role à la table medecins
"""
import sys
from pathlib import Path

# Ajouter le dossier parent au path
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy import text
from app.database import engine

def migrate():
    """Ajoute la colonne role à la table medecins"""
    print("=" * 80)
    print("MIGRATION: Ajout de la colonne role à la table medecins")
    print("=" * 80)
    
    try:
        with engine.connect() as conn:
            # Vérifier si la colonne existe déjà
            result = conn.execute(text("""
                SELECT COUNT(*) as count
                FROM information_schema.COLUMNS
                WHERE TABLE_SCHEMA = DATABASE()
                AND TABLE_NAME = 'medecins'
                AND COLUMN_NAME = 'role'
            """))
            
            exists = result.fetchone()[0] > 0
            
            if exists:
                print("✅ La colonne 'role' existe déjà dans la table 'medecins'")
                print("   Aucune action nécessaire.")
                return
            
            # Ajouter la colonne
            print("\n📝 Ajout de la colonne 'role'...")
            conn.execute(text("""
                ALTER TABLE medecins
                ADD COLUMN role VARCHAR(100) NULL
            """))
            conn.commit()
            
            print("✅ Colonne 'role' ajoutée avec succès!")
            
            # Vérifier le résultat
            result = conn.execute(text("""
                SELECT COUNT(*) as count
                FROM information_schema.COLUMNS
                WHERE TABLE_SCHEMA = DATABASE()
                AND TABLE_NAME = 'medecins'
                AND COLUMN_NAME = 'role'
            """))
            
            if result.fetchone()[0] > 0:
                print("✅ Vérification: La colonne a bien été ajoutée")
            else:
                print("❌ Erreur: La colonne n'a pas été ajoutée")
            
            print("\n" + "=" * 80)
            print("MIGRATION TERMINÉE AVEC SUCCÈS")
            print("=" * 80)
            
    except Exception as e:
        print(f"\n❌ ERREUR lors de la migration: {e}")
        print("\nSi l'erreur persiste, vous pouvez exécuter manuellement:")
        print("ALTER TABLE medecins ADD COLUMN role VARCHAR(100) NULL;")
        sys.exit(1)

if __name__ == "__main__":
    migrate()
