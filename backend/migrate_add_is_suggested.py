"""
Migration: Ajouter la colonne is_suggested à la table examens
"""
import sys
from pathlib import Path

# Ajouter le dossier parent au path
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy import text
from app.database import engine

def migrate():
    """Ajoute la colonne is_suggested à la table examens"""
    print("=" * 80)
    print("MIGRATION: Ajout de la colonne is_suggested à la table examens")
    print("=" * 80)
    
    try:
        with engine.connect() as conn:
            # Vérifier si la colonne existe déjà
            result = conn.execute(text("""
                SELECT COUNT(*) as count
                FROM information_schema.COLUMNS
                WHERE TABLE_SCHEMA = DATABASE()
                AND TABLE_NAME = 'examens'
                AND COLUMN_NAME = 'is_suggested'
            """))
            
            exists = result.fetchone()[0] > 0
            
            if exists:
                print("✅ La colonne 'is_suggested' existe déjà dans la table 'examens'")
                print("   Aucune action nécessaire.")
                return
            
            # Ajouter la colonne
            print("\n📝 Ajout de la colonne 'is_suggested'...")
            conn.execute(text("""
                ALTER TABLE examens
                ADD COLUMN is_suggested BOOLEAN DEFAULT FALSE
            """))
            conn.commit()
            
            print("✅ Colonne 'is_suggested' ajoutée avec succès!")
            
            # Vérifier le résultat
            result = conn.execute(text("""
                SELECT COUNT(*) as count
                FROM information_schema.COLUMNS
                WHERE TABLE_SCHEMA = DATABASE()
                AND TABLE_NAME = 'examens'
                AND COLUMN_NAME = 'is_suggested'
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
        print("ALTER TABLE examens ADD COLUMN is_suggested BOOLEAN DEFAULT FALSE;")
        sys.exit(1)

if __name__ == "__main__":
    migrate()
