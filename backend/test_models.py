"""Test script to verify all models are correctly configured"""
from app.database import SessionLocal
from app.models.patient import Patient
from app.models.consultation import Consultation
from app.models.dossier_medical import DossierMedical

def test_models():
    db = SessionLocal()
    
    try:
        print("✅ Modèles chargés avec succès!")
        
        # Test patients
        patients = db.query(Patient).limit(3).all()
        print(f"\n📊 {len(patients)} patients trouvés")
        for p in patients:
            print(f"  - ID: {p.patient_id}, Nom: {p.nom} {p.prenoms}")
        
        # Test consultations
        consultations = db.query(Consultation).filter(
            Consultation.patient_id.isnot(None)
        ).limit(3).all()
        print(f"\n📋 {len(consultations)} consultations trouvées")
        for c in consultations:
            print(f"  - ID: {c.consultation_id}, Patient ID: {c.patient_id}, Nom: {c.nom_patient}")
        
        # Test dossiers médicaux
        dossiers = db.query(DossierMedical).limit(3).all()
        print(f"\n📁 {len(dossiers)} dossiers médicaux trouvés")
        for d in dossiers:
            print(f"  - Dossier ID: {d.dossier_id}, Patient ID: {d.patient_id}, Numéro: {d.numero_dossier}")
        
        print("\n✅ Test réussi! Tous les modèles fonctionnent correctement.")
        
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    test_models()
