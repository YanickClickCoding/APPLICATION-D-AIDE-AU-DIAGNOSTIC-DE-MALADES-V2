"""
Consultations API Router (US-002, US-003, US-005)
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from ..database import get_db
from ..models import Consultation, Patient, Symptome, SignesVitaux
from ..schemas.consultation_schema import ConsultationCreate, ConsultationResponse

router = APIRouter(prefix="/consultations", tags=["Consultations"])


@router.post("/", response_model=ConsultationResponse, status_code=status.HTTP_201_CREATED)
def create_consultation(consultation: ConsultationCreate, db: Session = Depends(get_db)):
    """
    US-002, US-003: Créer une consultation avec symptômes et signes vitaux
    """
    # Vérifier que le patient existe
    patient = db.query(Patient).filter(Patient.id == consultation.patient_id).first()
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient non trouvé"
        )
    
    # US-005: Validation - au moins 1 symptôme requis
    if not consultation.symptomes or len(consultation.symptomes) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Au moins un symptôme est requis"
        )
    
    # Créer la consultation
    db_consultation = Consultation(
        patient_id=consultation.patient_id,
        medecin_id=consultation.medecin_id,
        motif=consultation.motif,
        statut="en_cours"
    )
    db.add(db_consultation)
    db.flush()  # Pour obtenir l'ID
    
    # Ajouter les symptômes
    for symptome_input in consultation.symptomes:
        db_symptome = Symptome(
            consultation_id=db_consultation.id,
            nom=symptome_input.nom,
            present=symptome_input.present,
            severite=symptome_input.severite,
            duree_jours=symptome_input.duree_jours
        )
        db.add(db_symptome)
    
    # Ajouter les signes vitaux
    signes_data = consultation.signes_vitaux.model_dump()
    db_signes = SignesVitaux(
        consultation_id=db_consultation.id,
        **signes_data
    )
    db.add(db_signes)
    
    db.commit()
    db.refresh(db_consultation)
    
    return db_consultation


@router.get("/", response_model=List[ConsultationResponse])
def list_consultations(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Liste toutes les consultations
    """
    consultations = db.query(Consultation).offset(skip).limit(limit).all()
    return consultations


@router.get("/{consultation_id}", response_model=ConsultationResponse)
def get_consultation(consultation_id: int, db: Session = Depends(get_db)):
    """
    Récupère une consultation par son ID
    """
    consultation = db.query(Consultation).filter(Consultation.id == consultation_id).first()
    if not consultation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Consultation non trouvée"
        )
    return consultation


@router.get("/patient/{patient_id}", response_model=List[ConsultationResponse])
def get_patient_consultations(patient_id: UUID, db: Session = Depends(get_db)):
    """
    US-004: Récupère l'historique des consultations d'un patient
    """
    consultations = db.query(Consultation).filter(
        Consultation.patient_id == patient_id
    ).order_by(Consultation.date_consultation.desc()).all()
    
    return consultations


@router.post("/workflow", status_code=status.HTTP_201_CREATED)
def create_consultation_workflow(data: dict, db: Session = Depends(get_db)):
    """
    Endpoint pour le workflow complet de consultation avec diagnostic IA
    Enregistre: patient, consultation, symptômes, signes vitaux, analyse IA, diagnostic
    """
    try:
        import uuid
        from datetime import datetime
        from ..models import AnalyseIA, Diagnostic, DossierMedical
        
        # Extraire les données
        patient_data = data.get('patient', {})
        symptomes_data = data.get('symptomes', [])
        signes_vitaux_data = data.get('signes_vitaux', {})
        examens_data = data.get('examens', [])
        motif = data.get('motif', '')
        prediction_ia = data.get('prediction_ia', {})
        diagnostic_final = data.get('diagnostic_final', '')
        
        # 1. Créer ou récupérer le patient
        patient_email = patient_data.get('email', '').strip()
        patient = None
        
        if patient_email:
            patient = db.query(Patient).filter(Patient.email == patient_email).first()
        
        if not patient:
            patient_id = str(uuid.uuid4())
            patient = Patient(
                id=patient_id,
                nom=patient_data.get('nom', ''),
                prenoms=patient_data.get('prenoms', ''),
                date_naissance=datetime.strptime(patient_data.get('date_naissance'), '%Y-%m-%d').date() if patient_data.get('date_naissance') else None,
                sexe=patient_data.get('sexe', 'M'),
                telephone=patient_data.get('telephone'),
                email=patient_email if patient_email else None,
                adresse=None
            )
            db.add(patient)
            db.flush()
        
        # 2. Créer la consultation
        db_consultation = Consultation(
            nom_patient=f"{patient_data.get('prenoms', '')} {patient_data.get('nom', '')}",
            date_heure=datetime.now(),
            motif=motif,
            medecin_id=None,  # À définir si disponible
            statut="terminée"
        )
        db.add(db_consultation)
        db.flush()
        
        # 3. Enregistrer les symptômes
        for symptome_input in symptomes_data:
            # Mapper la sévérité du frontend vers le format DB
            severite_map = {
                'Légère': 'LEGER',
                'Modérée': 'MODERE',
                'Sévère': 'SEVERE'
            }
            severite_db = severite_map.get(symptome_input.get('severite', 'Modérée'), 'MODERE')
            
            db_symptome = Symptome(
                id=str(uuid.uuid4()),
                consultation_id=str(db_consultation.consultation_id),
                nom=symptome_input.get('nom', ''),
                description=symptome_input.get('description'),
                severite=severite_db,
                duree_jours=symptome_input.get('duree_jours', 1),
                frequence=None
            )
            db.add(db_symptome)
        
        # 4. Enregistrer les signes vitaux
        db_signes = SignesVitaux(
            id=str(uuid.uuid4()),
            consultation_id=str(db_consultation.consultation_id),
            infirmier_id=None,  # À définir si disponible
            tension_systolique=signes_vitaux_data.get('tension_systolique'),
            tension_diastolique=signes_vitaux_data.get('tension_diastolique'),
            frequence_cardiaque=signes_vitaux_data.get('frequence_cardiaque'),
            temperature=signes_vitaux_data.get('temperature'),
            frequence_respiratoire=signes_vitaux_data.get('frequence_respiratoire'),
            saturation_oxygene=signes_vitaux_data.get('saturation_o2'),
            poids=signes_vitaux_data.get('poids'),
            taille=signes_vitaux_data.get('taille'),
            imc=None  # Calculé automatiquement si nécessaire
        )
        db.add(db_signes)
        
        # 4.5. Enregistrer les examens médicaux
        from ..models import Examen
        for examen_input in examens_data:
            db_examen = Examen(
                id=str(uuid.uuid4()),
                consultation_id=str(db_consultation.consultation_id),
                type=examen_input.get('type', 'BIOLOGIE'),
                nom=examen_input.get('nom', ''),
                description=examen_input.get('description'),
                resultats=examen_input.get('resultats'),
                valeur_numerique=examen_input.get('valeur_numerique'),
                unite_mesure=examen_input.get('unite_mesure'),
                statut='REALISE',
                date_examen=datetime.strptime(examen_input.get('date_examen'), '%Y-%m-%d').date() if examen_input.get('date_examen') else None
            )
            db.add(db_examen)
        
        # 5. Enregistrer l'analyse IA
        if prediction_ia:
            db_analyse_ia = AnalyseIA(
                id=str(uuid.uuid4()),
                consultation_id=str(db_consultation.consultation_id),
                modele_ia="RandomForest_v1.0",
                probabilite=prediction_ia.get('confiance', 0.0),
                diagnostics_suggeres=prediction_ia.get('top_3_predictions', []),
                scoring_confiance=prediction_ia.get('confiance', 0.0),
                donnees_entree={
                    'symptomes': symptomes_data,
                    'signes_vitaux': signes_vitaux_data,
                    'examens': examens_data
                },
                temps_traitement=None
            )
            db.add(db_analyse_ia)
            db.flush()
            analyse_ia_id = db_analyse_ia.id
        else:
            analyse_ia_id = None
        
        # 6. Créer ou récupérer le dossier médical du patient
        dossier = db.query(DossierMedical).filter(DossierMedical.patient_id == patient.id).first()
        if not dossier:
            dossier = DossierMedical(
                id=str(uuid.uuid4()),
                patient_id=patient.id,
                numero_dossier=f"DM-{datetime.now().strftime('%Y%m%d')}-{patient.id[:8]}",
                antecedents_familiaux=None,
                antecedents_personnels=None,
                allergies=None
            )
            db.add(dossier)
            db.flush()
        
        # 7. Enregistrer le diagnostic final
        if diagnostic_final:
            db_diagnostic = Diagnostic(
                id=str(uuid.uuid4()),
                consultation_id=str(db_consultation.consultation_id),
                analyse_ia_id=analyse_ia_id,
                medecin_id=None,  # À définir si disponible
                dossier_id=dossier.id,
                code_icd10=None,
                nom_maladie=diagnostic_final,
                description=f"Diagnostic validé par le médecin. Suggestion IA: {prediction_ia.get('maladie_predite', 'N/A')}",
                certitude=prediction_ia.get('confiance', 0.0) if prediction_ia else None,
                statut='CONFIRMÉ',
                severite=None,
                justification=None,
                date_validation=datetime.now().date()
            )
            db.add(db_diagnostic)
        
        # Commit final
        db.commit()
        db.refresh(db_consultation)
        
        return {
            "success": True,
            "message": "Consultation enregistrée avec succès",
            "consultation_id": db_consultation.consultation_id,
            "patient_id": patient.id
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de l'enregistrement: {str(e)}"
        )
