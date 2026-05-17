"""
Script pour vérifier les patients en double dans la base de données
"""
import sys
import os

# Ajouter le répertoire backend au path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Charger les variables d'environnement
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker
from app.models.patient import Patient
from app.config import settings

# Créer la connexion à la base de données
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()

try:
    # Trouver les patients avec le même nom et prénom
    duplicates = (
        db.query(
            Patient.nom,
            Patient.prenoms,
            func.count(Patient.patient_id).label('count')
        )
        .group_by(Patient.nom, Patient.prenoms)
        .having(func.count(Patient.patient_id) > 1)
        .all()
    )
    
    if duplicates:
        print(f"\n🔍 {len(duplicates)} patient(s) en double trouvé(s):\n")
        for nom, prenoms, count in duplicates:
            print(f"  • {prenoms} {nom} - {count} enregistrements")
            
            # Afficher les détails de chaque doublon
            patients = db.query(Patient).filter(
                Patient.nom == nom,
                Patient.prenoms == prenoms
            ).all()
            
            for p in patients:
                print(f"    - ID: {p.patient_id}, Date naissance: {p.date_naissance}, Téléphone: {p.telephone}")
        
        print("\n💡 Solution: Vous devez supprimer les doublons manuellement ou fusionner les dossiers.")
    else:
        print("\n✅ Aucun patient en double trouvé dans la base de données.")
        print("Le problème vient peut-être d'ailleurs (cache, frontend, etc.)")
        
finally:
    db.close()
