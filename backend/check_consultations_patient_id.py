"""
Script pour vérifier les patient_id dans les consultations
"""
from sqlalchemy import create_engine, text
from app.config import settings

def check_consultations():
    """Vérifie les consultations et leurs patient_id"""
    try:
        engine = create_engine(settings.DATABASE_URL)
        
        with engine.connect() as conn:
            # Récupérer toutes les consultations
            result = conn.execute(text("""
                SELECT consultation_id, patient_id, nom_patient, date_heure, statut
                FROM consultations
                ORDER BY date_heure DESC
                LIMIT 10
            """))
            
            consultations = result.fetchall()
            
            print(f"\n📋 {len(consultations)} consultation(s) récente(s):\n")
            print(f"{'ID':<6} {'Patient ID':<38} {'Nom Patient':<30} {'Statut':<15}")
            print("-" * 95)
            
            null_count = 0
            for c in consultations:
                pid = c[1] if c[1] else "NULL"
                if not c[1]:
                    null_count += 1
                print(f"{c[0]:<6} {pid:<38} {c[2]:<30} {c[4]:<15}")
            
            print(f"\n⚠️  {null_count} consultation(s) sans patient_id")
            
            if null_count > 0:
                print("\n💡 Pour lier les consultations aux patients:")
                print("   1. Créez d'abord les patients dans la table 'patients'")
                print("   2. Puis mettez à jour les consultations avec:")
                print("      UPDATE consultations SET patient_id = '<uuid>' WHERE consultation_id = <id>;")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")

if __name__ == "__main__":
    check_consultations()
