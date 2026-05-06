"""
Script pour créer des patients à partir des consultations et les lier
"""
from sqlalchemy import create_engine, text
from app.config import settings
import uuid
from datetime import datetime, date

def link_consultations():
    """Crée des patients et lie les consultations"""
    try:
        engine = create_engine(settings.DATABASE_URL)
        
        with engine.connect() as conn:
            # Récupérer les consultations sans patient_id
            result = conn.execute(text("""
                SELECT DISTINCT nom_patient
                FROM consultations
                WHERE patient_id IS NULL
            """))
            
            patients_names = result.fetchall()
            
            print(f"\n🔄 Traitement de {len(patients_names)} patient(s) unique(s)...\n")
            
            for (nom_complet,) in patients_names:
                # Séparer nom et prénom (approximatif)
                parts = nom_complet.strip().split()
                if len(parts) >= 2:
                    prenom = parts[0]
                    nom = ' '.join(parts[1:])
                else:
                    prenom = nom_complet
                    nom = "Inconnu"
                
                # Générer un UUID pour le patient
                patient_id = str(uuid.uuid4())
                
                # Vérifier si le patient existe déjà
                check = conn.execute(text("""
                    SELECT id FROM patients 
                    WHERE nom = :nom AND prenoms = :prenom
                """), {"nom": nom, "prenom": prenom})
                
                existing = check.fetchone()
                
                if existing:
                    patient_id = existing[0]
                    print(f"✓ Patient existant: {prenom} {nom} (ID: {patient_id[:8]}...)")
                else:
                    # Créer le patient
                    conn.execute(text("""
                        INSERT INTO patients (id, nom, prenoms, date_naissance, sexe, created_at)
                        VALUES (:id, :nom, :prenom, :date_naissance, :sexe, :created_at)
                    """), {
                        "id": patient_id,
                        "nom": nom,
                        "prenom": prenom,
                        "date_naissance": date(1990, 1, 1),  # Date par défaut
                        "sexe": "M",  # Sexe par défaut
                        "created_at": datetime.now()
                    })
                    print(f"✓ Patient créé: {prenom} {nom} (ID: {patient_id[:8]}...)")
                
                # Lier les consultations à ce patient
                result = conn.execute(text("""
                    UPDATE consultations 
                    SET patient_id = :patient_id 
                    WHERE nom_patient = :nom_complet AND patient_id IS NULL
                """), {"patient_id": patient_id, "nom_complet": nom_complet})
                
                updated = result.rowcount
                print(f"  → {updated} consultation(s) liée(s)\n")
            
            conn.commit()
            print("✅ Toutes les consultations ont été liées aux patients !")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        raise

if __name__ == "__main__":
    link_consultations()
