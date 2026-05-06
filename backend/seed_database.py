"""
Script pour insérer des données de test dans la base de données
Date: 2026-05-05
"""
from sqlalchemy import create_engine, text
from app.config import settings

def seed_database():
    """Insère les données de test"""
    try:
        engine = create_engine(settings.DATABASE_URL)
        
        print("=" * 80)
        print("📊 INSERTION DES DONNÉES DE TEST")
        print("=" * 80)
        
        with engine.connect() as conn:
            # Lire le fichier SQL
            with open('seed_data_complete.sql', 'r', encoding='utf-8') as f:
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
            print(f"\n🔄 Exécution de {len(commands)} commandes SQL...\n")
            
            for i, command in enumerate(commands, 1):
                try:
                    # Afficher un aperçu de la commande
                    if 'INSERT INTO' in command:
                        table_name = command.split('INSERT INTO')[1].split('(')[0].strip().replace('`', '')
                        print(f"[{i}/{len(commands)}] Insertion dans {table_name}...")
                    else:
                        preview = command[:60].replace('\n', ' ')
                        print(f"[{i}/{len(commands)}] {preview}...")
                    
                    conn.execute(text(command))
                    conn.commit()
                    
                except Exception as e:
                    print(f"  ⚠️  Erreur: {e}")
                    continue
            
            print("\n✅ Données insérées avec succès !")
            print("\n📊 Résumé des insertions:")
            
            # Compter les enregistrements
            tables = {
                'patients': 'Patients',
                'infirmiers': 'Infirmiers',
                'medecins': 'Médecins',
                'consultations': 'Consultations',
                'symptomes': 'Symptômes',
                'signes_vitaux': 'Signes vitaux',
                'dossiers_medicaux': 'Dossiers médicaux'
            }
            
            for table, label in tables.items():
                try:
                    result = conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
                    count = result.scalar()
                    print(f"  ✓ {label}: {count} enregistrement(s)")
                except:
                    print(f"  ✗ {label}: erreur")
            
            print("\n🎉 Base de données prête pour les tests !")
        
    except FileNotFoundError:
        print("❌ Erreur: Le fichier seed_data_complete.sql est introuvable")
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    seed_database()
