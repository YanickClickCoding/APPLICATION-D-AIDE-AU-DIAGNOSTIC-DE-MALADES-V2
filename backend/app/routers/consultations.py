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
    patient = db.query(Patient).filter(Patient.patient_id == consultation.patient_id).first()
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
        nom_patient=f"{patient.prenoms} {patient.nom}",
        medecin_id=consultation.medecin_id,
        motif=consultation.motif,
        date_heure=__import__('datetime').datetime.now(),
        statut="en cours"
    )
    db.add(db_consultation)
    db.flush()  # Pour obtenir l'ID
    
    # Ajouter les symptômes
    import uuid as _uuid
    for symptome_input in consultation.symptomes:
        db_symptome = Symptome(
            id=str(_uuid.uuid4()),
            consultation_id=str(db_consultation.consultation_id),
            nom=symptome_input.nom,
            severite=symptome_input.severite,
            duree_jours=symptome_input.duree_jours
        )
        db.add(db_symptome)
    
    # Ajouter les signes vitaux
    signes_data = consultation.signes_vitaux.model_dump()
    db_signes = SignesVitaux(
        id=str(_uuid.uuid4()),
        consultation_id=str(db_consultation.consultation_id),
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
    consultation = db.query(Consultation).filter(Consultation.consultation_id == consultation_id).first()
    if not consultation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Consultation non trouvée"
        )
    return consultation


@router.get("/patient/{patient_id}", response_model=List[ConsultationResponse])
def get_patient_consultations(patient_id: int, db: Session = Depends(get_db)):
    """
    US-004: Récupère l'historique des consultations d'un patient
    """
    consultations = db.query(Consultation).filter(
        Consultation.patient_id == patient_id
    ).order_by(Consultation.date_heure.desc()).all()
    
    return consultations


@router.post("/workflow", status_code=status.HTTP_201_CREATED)
def create_consultation_workflow(data: dict, db: Session = Depends(get_db)):
    """
    Workflow complet de consultation assistée par IA (9 étapes).
    Enregistre : patient, consultation, symptômes, signes vitaux,
    examens, deux analyses IA (préliminaire + finale), diagnostic.
    """
    try:
        import uuid
        from datetime import datetime
        from ..models import AnalyseIA, Diagnostic, DossierMedical, Examen

        patient_data      = data.get('patient', {})
        symptomes_data    = data.get('symptomes', [])
        vitaux_data       = data.get('signes_vitaux', {})
        examens_data      = data.get('examens', [])
        motif             = data.get('motif', '')
        analyse_prelim    = data.get('analyse_preliminaire')
        analyse_finale    = data.get('analyse_finale')
        diagnostic_final  = data.get('diagnostic_final', '')
        validation_type   = data.get('validation_type', 'confirme')
        notes_validation  = data.get('notes_validation', '')

        # ── 1. Patient (integer PK, autoincrement) ──────────────────────────
        patient_email = (patient_data.get('email') or '').strip()
        patient = None
        if patient_email:
            patient = db.query(Patient).filter(Patient.email == patient_email).first()

        if not patient:
            dn = patient_data.get('date_naissance')
            patient = Patient(
                nom=patient_data.get('nom', ''),
                prenoms=patient_data.get('prenoms', ''),
                date_naissance=datetime.strptime(dn, '%Y-%m-%d').date() if dn else None,
                sexe=patient_data.get('sexe', 'M'),
                telephone=patient_data.get('telephone') or None,
                email=patient_email or None,
            )
            db.add(patient)
            db.flush()  # génère patient.patient_id

        # ── 2. Consultation (integer PK) ────────────────────────────────────
        db_consultation = Consultation(
            patient_id=patient.patient_id,
            nom_patient=f"{patient_data.get('prenoms', '')} {patient_data.get('nom', '')}".strip(),
            date_heure=datetime.now(),
            motif=motif,
            medecin_id=None,
            statut="terminée",
        )
        db.add(db_consultation)
        db.flush()  # génère db_consultation.consultation_id

        cid_int = db_consultation.consultation_id
        cid_str = str(cid_int)  # pour les FK CHAR(36) non encore migrées

        # ── 3. Symptômes (UUID PK, CHAR(36) FK consultation_id) ────────────
        sev_map = {'Légère': 'LEGER', 'Modérée': 'MODERE', 'Sévère': 'SEVERE'}
        for s in symptomes_data:
            if not (s.get('nom') or '').strip():
                continue
            db.add(Symptome(
                id=str(uuid.uuid4()),
                consultation_id=cid_str,
                nom=s['nom'].strip(),
                description=s.get('description') or None,
                severite=sev_map.get(s.get('severite', 'Modérée'), 'MODERE'),
                duree_jours=s.get('duree_jours', 1),
            ))

        # ── 4. Signes vitaux (UUID PK, CHAR(36) FK consultation_id) ────────
        imc = None
        poids, taille = vitaux_data.get('poids'), vitaux_data.get('taille')
        if poids and taille:
            imc = round(poids / (taille / 100) ** 2, 1)

        db.add(SignesVitaux(
            id=str(uuid.uuid4()),
            consultation_id=cid_str,
            tension_systolique=vitaux_data.get('tension_systolique'),
            tension_diastolique=vitaux_data.get('tension_diastolique'),
            frequence_cardiaque=vitaux_data.get('frequence_cardiaque'),
            temperature=vitaux_data.get('temperature'),
            frequence_respiratoire=vitaux_data.get('frequence_respiratoire'),
            saturation_oxygene=vitaux_data.get('saturation_o2'),
            poids=poids,
            taille=taille,
            imc=imc,
        ))

        # ── 5. Examens (integer PK, integer FK consultation_id) ─────────────
        for ex in examens_data:
            if not (ex.get('nom') or '').strip():
                continue
            de = ex.get('date_examen')
            db.add(Examen(
                consultation_id=cid_int,
                type=ex.get('type', 'BIOLOGIE'),
                nom=ex['nom'].strip(),
                description=ex.get('description') or None,
                resultats=ex.get('resultats') or None,
                valeur_numerique=ex.get('valeur_numerique'),
                unite_mesure=ex.get('unite_mesure') or None,
                statut='REALISE',
                date_examen=datetime.strptime(de, '%Y-%m-%d').date() if de else None,
            ))

        # ── 6. Dossier médical (integer PK, integer FK patient_id) ──────────
        dossier = db.query(DossierMedical).filter(
            DossierMedical.patient_id == patient.patient_id
        ).first()
        if not dossier:
            ts = datetime.now().strftime('%Y%m%d%H%M%S')
            dossier = DossierMedical(
                patient_id=patient.patient_id,
                numero_dossier=f"DM-{ts}-{patient.patient_id}",
            )
            db.add(dossier)
            db.flush()

        # ── 7. Analyse IA préliminaire (integer PK) ─────────────────────────
        prelim_analyse_id = None
        if analyse_prelim:
            rec = AnalyseIA(
                consultation_id=cid_int,
                modele_ia="RandomForest_v1.0_Preliminaire",
                probabilite=analyse_prelim.get('confiance', 0.0),
                diagnostics_suggeres=analyse_prelim.get('top_predictions', []),
                scoring_confiance=analyse_prelim.get('confiance', 0.0),
                donnees_entree={
                    'phase': 'preliminaire',
                    'symptomes': symptomes_data,
                    'signes_vitaux': vitaux_data,
                },
            )
            db.add(rec)
            db.flush()
            prelim_analyse_id = rec.analyse_id

        # ── 8. Analyse IA finale (integer PK) ───────────────────────────────
        finale_analyse_id = None
        if analyse_finale:
            rec = AnalyseIA(
                consultation_id=cid_int,
                modele_ia="RandomForest_v1.0_Finale",
                probabilite=analyse_finale.get('confiance', 0.0),
                diagnostics_suggeres=analyse_finale.get('top_predictions', []),
                scoring_confiance=analyse_finale.get('confiance', 0.0),
                donnees_entree={
                    'phase': 'finale',
                    'symptomes': symptomes_data,
                    'signes_vitaux': vitaux_data,
                    'examens': examens_data,
                },
            )
            db.add(rec)
            db.flush()
            finale_analyse_id = rec.analyse_id

        # ── 9. Diagnostic final (integer PK) ────────────────────────────────
        if diagnostic_final:
            ref = analyse_finale or analyse_prelim or {}
            confiance = ref.get('confiance', 0.0)
            statut_diag = 'CONFIRMÉ' if validation_type == 'confirme' else 'REJETÉ'
            ia_suggestion = ref.get('maladie_predite', 'N/A')
            db.add(Diagnostic(
                consultation_id=cid_int,
                analyse_ia_id=finale_analyse_id or prelim_analyse_id,
                medecin_id=None,
                dossier_id=dossier.dossier_id,
                nom_maladie=diagnostic_final,
                description=(
                    f"Validation : {statut_diag}. "
                    f"Suggestion IA : {ia_suggestion} ({confiance*100:.1f}%). "
                    f"Notes : {notes_validation}"
                ),
                certitude=confiance,
                statut=statut_diag,
                date_validation=datetime.now().date(),
            ))

        db.commit()
        db.refresh(db_consultation)

        return {
            "success": True,
            "message": "Consultation enregistrée avec succès",
            "consultation_id": db_consultation.consultation_id,
            "patient_id": patient.patient_id,
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de l'enregistrement: {str(e)}"
        )
