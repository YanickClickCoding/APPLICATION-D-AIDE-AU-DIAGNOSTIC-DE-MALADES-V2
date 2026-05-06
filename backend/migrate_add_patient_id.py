"""
Script de migration: Ajouter patient_id à la table consultations
Date: 2026-05-05
"""
from sqlalchemy import create_engine, text
from app.config import settings

def run_migration():
    """Exécute la migration SQL pour ajouter patient_id"""
    try:
        # Créer l'engine SQLAlchemy
        engine = create_engine(settings.DATABASE_URL)
        
        print("🔄 Début de la migration...")
        
        with engine.connect() as conn:
            # Vérifier si la colonne existe déjà
            result = conn.execute(text("""
                SELECT COUNT(*) 
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_NAME = 'consultations' 
                AND COLUMN_NAME = 'patient_id'
            """))
            
            exists = result.scalar()
            
            if exists:
                print("✅ La colonne patient_id existe déjà dans la table consultations")
                return
            
            # Ajouter la colonne patient_id
            print("📝 Ajout de la colonne patient_id...")
            conn.execute(text("""
                ALTER TABLE `consultations` 
                ADD COLUMN `patient_id` CHAR(36) NULL AFTER `nom_patient`,
                ADD INDEX `idx_patient_id` (`patient_id`)
            """))
            
            conn.commit()
            print("✅ Migration réussie ! La colonne patient_id a été ajoutée.")
            print("⚠️  Note: Les consultations existantes ont patient_id = NULL")
            print("   Vous devrez les mettre à jour manuellement si nécessaire.")
        
    except Exception as e:
        print(f"❌ Erreur lors de la migration: {e}")
        raise

if __name__ == "__main__":
    run_migration()
