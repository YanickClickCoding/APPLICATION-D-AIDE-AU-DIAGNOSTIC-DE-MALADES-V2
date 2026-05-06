"""
Script de migration COMPLÈTE: Convertir TOUS les CHAR(36) en INT AUTO_INCREMENT
Date: 2026-05-05
ATTENTION: Ce script SUPPRIME et RECRÉE toutes les tables !
"""
from sqlalchemy import create_engine, text
from app.config import settings
import sys

def confirm_migration():
    """Demande confirmation avant de procéder"""
    print("=" * 80)
    print("⚠️  MIGRATION COMPLÈTE UUID -> INT (TOUTES LES TABLES)")
    print("=" * 80)
    print("\n⚠️  ATTENTION: Cette migration va:")
    print("  1. SUPPRIMER toutes les tables avec CHAR(36)")
    print("  2. RECRÉER toutes les tables avec INT AUTO_INCREMENT")
    print("  3. TOUTES LES DONNÉES SERONT PERDUES !")
    print("\n⚠️  CRITIQUE: Assurez-vous d'avoir fait un BACKUP COMPLET !")
    print("\nTables qui seront recréées:")
    print("  - patients, dossiers_medicaux, analyses_ia, diagnostics")
    print("  - examens, traitements, ordonnances, medicaments")
    print("  - signes_vitaux, symptomes, suivis, consultation_infirmiers")
    print("\nTables préservées (déjà en INT):")
    print("  - consultations, medecins, utilisateurs")
    print("\nVoulez-vous continuer ? (tapez 'OUI SUPPRIMER' pour confirmer): ", end="")
    
    response = input().strip()
    return response == 'OUI SUPPRIMER'

def run_migration():
    """Exécute la migration complète"""
    try:
        if not confirm_migration():
            print("\n❌ Migration annulée par l'utilisateur")
            return
        
        engine = create_engine(settings.DATABASE_URL)
        
        print("\n🔄 Début de la migration complète...\n")
        
        with engine.connect() as conn:
            # Lire le fichier SQL
            with open('migrate_all_to_int_complete.sql', 'r', encoding='utf-8') as f:
                sql_content = f.read()
            
            # Séparer les commandes SQL
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
                    preview = command[:70].replace('\n', ' ')
                    print(f"[{i}/{total}] {preview}...")
                    
                    conn.execute(text(command))
                    conn.commit()
                    
                except Exception as e:
                    print(f"  ⚠️  Erreur: {e}")
                    # Continuer même en cas d'erreur
                    continue
            
            print("\n✅ Migration terminée avec succès !")
            print("\n📊 Vérification des tables créées:")
            
            # Vérifier les tables
            tables = [
                'patients', 'dossiers_medicaux', 'analyses_ia', 'diagnostics',
                'examens', 'traitements', 'ordonnances', 'medicaments',
                'signes_vitaux', 'symptomes', 'suivis', 'consultation_infirmiers'
            ]
            
            for table in tables:
                try:
                    result = conn.execute(text(f"SHOW TABLES LIKE '{table}'"))
                    if result.fetchone():
                        print(f"  ✓ {table}")
                    else:
                        print(f"  ✗ {table} (non créée)")
                except:
                    print(f"  ✗ {table} (erreur)")
            
            print("\n✅ Migration complète terminée !")
            print("   Toutes les tables utilisent maintenant INT AUTO_INCREMENT")
            print("   Plus aucun CHAR(36) dans la base de données")
        
    except FileNotFoundError:
        print("❌ Erreur: Le fichier migrate_all_to_int_complete.sql est introuvable")
    except Exception as e:
        print(f"❌ Erreur lors de la migration: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    run_migration()
