"""
Script pour vérifier les patients dans la base de données
"""
from sqlalchemy import create_engine, text
from app.config import settings

def check_patients():
    """Vérifie les patients dans la base de données"""
    try:
        engine = create_engine(settings.DATABASE_URL)
        
        with engine.connect() as conn:
            # Récupérer tous les patients
            result = conn.execute(text("""
                SELECT id, nom, prenoms, date_naissance, sexe, telephone
                FROM patients
                ORDER BY created_at DESC
                LIMIT 10
            """))
            
            patients = result.fetchall()
            
            print(f"\n📋 {len(patients)} patient(s) dans la base:\n")
            print(f"{'ID':<38} {'Nom':<20} {'Prénom':<20} {'Sexe':<5}")
            print("-" * 90)
            
            for p in patients:
                print(f"{p[0]:<38} {p[1]:<20} {p[2]:<20} {p[4]:<5}")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")

if __name__ == "__main__":
    check_patients()
