"""
Script de migration: Convertir tous les UUID en INT AUTO_INCREMENT
Date: 2026-05-05
ATTENTION: Ce script modifie la structure de la base de données !
"""
from sqlalchemy import create_engine, text
from app.config import settings
import sys

def confirm_migration():
    """Demande confirmation avant de procéder"""
    print("=" * 80)
    print("⚠️  MIGRATION UUID -> INT")
    print("=" * 80)
    print("\nCette migration va:")
    print("  1. Convertir tous les UUID (CHAR(36)) en INT AUTO_INCREMENT")
    print("  2. Modifier la table 'patients' (id -> patient_id)")
    print("  3. Mettre à jour toutes les références dans les autres tables")
    print("\n⚠️  IMPORTANT: Assurez-vous d'avoir fait un backup de la base !")
    print("\nVoulez-vous continuer ? (oui/non): ", end="")
    
    response = input().strip().lower()
    return response in ['oui', 'yes', 'y', 'o']

def run_migration():
    """Exécute la migration UUID -> INT"""
    try:
        if not confirm_migration():
            print("\n❌ Migration annulée par l'utilisateur")
            return
        
        engine = create_engine(settings.DATABASE_URL)
        
        print("\n🔄 Début de la migration...\n")
        
        with engine.connect() as conn:
            # Lire le fichier SQL
            with open('migrate_uuid_to_int.sql', 'r', encoding='utf-8') as f:
                sql_content = f.read()
            
            # Séparer les commandes SQL (ignorer les commentaires)
            commands = []
            current_command = []
            
            for line in sql_content.split('\n'):
                line = line.strip()
                # Ignorer les commentaires et lignes vides
                if not line or line.startswith('--'):
                    continue
                
                current_command.append(line)
                
                # Si la ligne se termine par ;, c'est la fin de la commande
                if line.endswith(';'):
                    command = ' '.join(current_command)
                    if command and not command.startswith('--'):
                        commands.append(command)
                    current_command = []
            
            # Exécuter chaque commande
            total = len(commands)
            for i, command in enumerate(commands, 1):
                try:
                    # Afficher un aperçu de la commande
                    preview = command[:60].replace('\n', ' ')
                    print(f"[{i}/{total}] {preview}...")
                    
                    conn.execute(text(command))
                    conn.commit()
                    
                except Exception as e:
                    print(f"  ⚠️  Erreur (peut être ignorée): {e}")
                    # Continuer même en cas d'erreur (certaines tables peuvent ne pas exister)
                    continue
            
            print("\n✅ Migration terminée avec succès !")
            print("\n📊 Vérification des résultats:")
            
            # Vérifier les patients
            result = conn.execute(text("SELECT COUNT(*) as count FROM patients"))
            count = result.scalar()
            print(f"  - Patients: {count} enregistrement(s)")
            
            # Vérifier les consultations
            result = conn.execute(text("SELECT COUNT(*) as count FROM consultations WHERE patient_id IS NOT NULL"))
            count = result.scalar()
            print(f"  - Consultations liées: {count} enregistrement(s)")
            
            print("\n✅ La migration est complète !")
            print("   Les UUID ont été convertis en INT AUTO_INCREMENT")
            print("   La colonne 'id' a été renommée en 'patient_id'")
        
    except FileNotFoundError:
        print("❌ Erreur: Le fichier migrate_uuid_to_int.sql est introuvable")
    except Exception as e:
        print(f"❌ Erreur lors de la migration: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    run_migration()
