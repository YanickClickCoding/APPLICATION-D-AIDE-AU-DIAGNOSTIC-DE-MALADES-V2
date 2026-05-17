"""
Script pour rechercher tous les patients nommés Mathieux
"""
import sys
import os

# Ajouter le répertoire backend au path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Charger les variables d'environnement
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

from sqlalchemy import create_engine, or_
from sqlalchemy.orm import sessionmaker
from app.models.patient import Patient
from app.config import settings

# Créer la connexion à la base de données
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()

try:
    # Rechercher tous les patients avec "Mathieux" dans le nom ou prénom
    patients = db.query(Patient).filter(
        or_(
            Patient.nom.ilike("%Mathieux%"),
            Patient.prenoms.ilike("%Mathieux%"),
        )
    ).all()
    
    if patients:
        print(f"\n🔍 {len(patients)} patient(s) trouvé(s) avec 'Mathieux':\n")
        for p in patients:
            print(f"  • ID: {p.patient_id}")
            print(f"    Nom: {p.nom}")
            print(f"    Prénoms: {p.prenoms}")
            print(f"    Sexe: {p.sexe}")
            print(f"    Date naissance: {p.date_naissance}")
            print(f"    Téléphone: {p.telephone}")
            print()
    else:
        print("\n❌ Aucun patient trouvé avec 'Mathieux'")
        
finally:
    db.close()
