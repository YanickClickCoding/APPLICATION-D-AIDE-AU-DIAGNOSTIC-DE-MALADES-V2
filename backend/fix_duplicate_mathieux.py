"""
Script pour corriger les consultations dupliquées de Mathieux AHOUANNOU
"""
from app.database import SessionLocal
from app.models.patient import Patient
from app.models.consultation import Consultation
from sqlalchemy import text

def fix_mathieux_duplicates():
    db = SessionLocal()
    try:
        # Le vrai patient Mathieux AHOUANNOU
        correct_patient_id = 50
        
        # Trouver toutes les consultations de Mathieux AHOUANNOU
        consultations = db.query(Consultation).filter(
            Consultation.nom_patient.like('%Mathieux%AHOUANNOU%')
        ).all()
        
        print(f"Trouvé {len(consultations)} consultations pour Mathieux AHOUANNOU")
        
        # Mettre à jour toutes les consultations pour pointer vers le bon patient_id
        updated_count = 0
        for consultation in consultations:
            if consultation.patient_id != correct_patient_id:
                old_id = consultation.patient_id
                consultation.patient_id = correct_patient_id
                print(f"  Consultation {consultation.consultation_id}: patient_id {old_id} -> {correct_patient_id}")
                updated_count += 1
        
        db.commit()
        print(f"\n✅ {updated_count} consultations mises à jour")
        
        # Vérifier les patients orphelins (qui n'ont plus de consultations)
        print("\n🔍 Recherche des patients orphelins...")
        orphan_ids = [51, 52, 53, 54, 55, 56, 57, 58]
        for patient_id in orphan_ids:
            patient = db.query(Patient).filter(Patient.patient_id == patient_id).first()
            if patient:
                # Vérifier si ce patient a encore des consultations
                consult_count = db.query(Consultation).filter(
                    Consultation.patient_id == patient_id
                ).count()
                if consult_count == 0:
                    print(f"  Patient {patient_id} ({patient.nom} {patient.prenoms}) n'a plus de consultations - peut être supprimé")
                else:
                    print(f"  Patient {patient_id} a encore {consult_count} consultation(s)")
            else:
                print(f"  Patient {patient_id} n'existe pas dans la table patients")
        
        print("\n✅ Correction terminée!")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    fix_mathieux_duplicates()
