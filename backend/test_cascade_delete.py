"""
Script de test pour vérifier la suppression en cascade
"""
import sys
from datetime import datetime, date
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Configuration de la base de données
DATABASE_URL = "mysql+pymysql://root:@localhost:3306/sante_plus_ia"

def test_cascade_delete():
    """
    Test de la suppression en cascade d'un patient avec ses consultations
    """
    print("=" * 80)
    print("TEST DE SUPPRESSION EN CASCADE")
    print("=" * 80)
    
    # Créer la connexion
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    
    try:
        # 1. Créer un patient de test
        print("\n1️⃣ Création d'un patient de test...")
        result = db.execute(text("""
            INSERT INTO patients (nom, prenoms, date_naissance, sexe, telephone, email)
            VALUES ('TEST', 'Patient', '1990-01-01', 'M', '0000000000', 'test@test.com')
        """))
        db.commit()
        
        # Récupérer l'ID du patient créé
        patient_id = result.lastrowid
        print(f"   ✅ Patient créé avec ID: {patient_id}")
        
        # 2. Créer des consultations pour ce patient
        print("\n2️⃣ Création de consultations pour ce patient...")
        for i in range(3):
            db.execute(text("""
                INSERT INTO consultations (patient_id, nom_patient, date_heure, motif, statut)
                VALUES (:patient_id, 'TEST Patient', NOW(), :motif, 'terminée')
            """), {"patient_id": patient_id, "motif": f"Consultation test {i+1}"})
        db.commit()
        
        # Compter les consultations
        count_result = db.execute(text("""
            SELECT COUNT(*) as count FROM consultations WHERE patient_id = :patient_id
        """), {"patient_id": patient_id})
        count = count_result.fetchone()[0]
        print(f"   ✅ {count} consultations créées")
        
        # 3. Vérifier les données avant suppression
        print("\n3️⃣ État AVANT suppression:")
        print(f"   📊 Patient ID {patient_id}: existe")
        print(f"   📊 Consultations: {count}")
        
        # 4. Supprimer le patient via SQLAlchemy (pour tester le cascade)
        print("\n4️⃣ Suppression du patient via l'API...")
        from app.models.patient import Patient
        patient = db.query(Patient).filter(Patient.patient_id == patient_id).first()
        
        if patient:
            db.delete(patient)
            db.commit()
            print(f"   ✅ Patient supprimé")
        
        # 5. Vérifier les données après suppression
        print("\n5️⃣ État APRÈS suppression:")
        
        # Vérifier le patient
        patient_check = db.execute(text("""
            SELECT COUNT(*) as count FROM patients WHERE patient_id = :patient_id
        """), {"patient_id": patient_id})
        patient_exists = patient_check.fetchone()[0]
        
        # Vérifier les consultations
        consult_check = db.execute(text("""
            SELECT COUNT(*) as count FROM consultations WHERE patient_id = :patient_id
        """), {"patient_id": patient_id})
        consult_count = consult_check.fetchone()[0]
        
        print(f"   📊 Patient ID {patient_id}: {'existe' if patient_exists > 0 else 'supprimé ✅'}")
        print(f"   📊 Consultations: {consult_count} {'(SUPPRIMÉES ✅)' if consult_count == 0 else '(ERREUR ❌)'}")
        
        # 6. Résultat du test
        print("\n" + "=" * 80)
        if patient_exists == 0 and consult_count == 0:
            print("✅ TEST RÉUSSI : La suppression en cascade fonctionne correctement !")
            print("   - Le patient a été supprimé")
            print("   - Toutes ses consultations ont été supprimées automatiquement")
        else:
            print("❌ TEST ÉCHOUÉ : La suppression en cascade ne fonctionne pas")
            if patient_exists > 0:
                print("   - Le patient n'a pas été supprimé")
            if consult_count > 0:
                print(f"   - {consult_count} consultation(s) n'ont pas été supprimées")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n❌ ERREUR: {str(e)}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    test_cascade_delete()
