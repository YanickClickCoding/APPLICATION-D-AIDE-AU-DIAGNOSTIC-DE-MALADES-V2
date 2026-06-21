"""
Patients API Router (US-001, US-004)
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_, cast, String
from typing import List
from uuid import UUID

from ..database import get_db
from pydantic import BaseModel
from typing import Optional
from ..models import (
    Patient, Consultation, Symptome, SignesVitaux,
    AnalyseIA, Diagnostic, Examen, Traitement, Ordonnance, Medicament, Suivi
)
from ..models.prediction_history import PredictionHistory
from ..models.dossier_medical import DossierMedical
from ..schemas.patient_schema import PatientCreate, PatientResponse, PatientUpdate
from .auth import get_current_non_admin, get_current_user


class DossierUpdate(BaseModel):
    antecedents_personnels: Optional[str] = None
    antecedents_familiaux: Optional[str] = None
    allergies: Optional[str] = None

router = APIRouter(
    prefix="/patients",
    tags=["Patients"],
    dependencies=[Depends(get_current_non_admin)],
)


@router.get("/{patient_id}/dossier")
def get_dossier(patient_id: int, db: Session = Depends(get_db)):
    """Retourne le dossier médical d'un patient (antécédents + allergies)."""
    dossier = db.query(DossierMedical).filter(DossierMedical.patient_id == patient_id).first()
    if not dossier:
        raise HTTPException(status_code=404, detail="Dossier médical introuvable")
    return {
        "dossier_id": dossier.dossier_id,
        "numero_dossier": dossier.numero_dossier,
        "antecedents_personnels": dossier.antecedents_personnels,
        "antecedents_familiaux": dossier.antecedents_familiaux,
        "allergies": dossier.allergies,
    }


@router.patch("/{patient_id}/dossier")
def update_dossier(patient_id: int, payload: DossierUpdate, db: Session = Depends(get_db)):
    """Met à jour les antécédents et allergies du dossier médical d'un patient."""
    dossier = db.query(DossierMedical).filter(DossierMedical.patient_id == patient_id).first()
    if not dossier:
        raise HTTPException(status_code=404, detail="Dossier médical introuvable")
    if payload.antecedents_personnels is not None:
        dossier.antecedents_personnels = payload.antecedents_personnels or None
    if payload.antecedents_familiaux is not None:
        dossier.antecedents_familiaux = payload.antecedents_familiaux or None
    if payload.allergies is not None:
        dossier.allergies = payload.allergies or None
    db.commit()
    db.refresh(dossier)
    return {
        "success": True,
        "antecedents_personnels": dossier.antecedents_personnels,
        "antecedents_familiaux": dossier.antecedents_familiaux,
        "allergies": dossier.allergies,
    }


@router.get("/search")
def search_patients(q: str = Query(..., min_length=1), db: Session = Depends(get_db)):
    """
    Recherche de patients par nom, prénoms ou ID (ex: "#0091", "0091" ou "91").
    Retourne les patients avec leur dernière consultation (si elle existe et est EN ATTENTE).
    """
    # ── Recherche par ID (préfixe « # ») ─────────────────────────────────────
    # « # » seul        → tous les patients
    # « #0 », « #00 », … → patients dont l'ID commence par ces chiffres
    # On filtre par préfixe sur l'ID casté en texte (sans zéros de tête saisis).
    q_strip = q.strip()
    if q_strip.startswith("#"):
        id_token = q_strip.lstrip("#").strip().lstrip("0")
        id_str = cast(Patient.patient_id, String)
        if id_token == "":
            # « # » (ou « #000 ») : aucun chiffre significatif → tous les patients,
            # les plus récents (ID le plus élevé) en premier.
            patients = (
                db.query(Patient)
                .order_by(Patient.patient_id.desc())
                .distinct()
                .limit(100)
                .all()
            )
        else:
            patients = (
                db.query(Patient)
                .filter(id_str.like(f"{id_token}%"))
                .order_by(Patient.patient_id.desc())
                .distinct()
                .limit(100)
                .all()
            )
    else:
        # ── Recherche par nom / prénoms (+ ID exact si purement numérique) ────
        filtres = [
            Patient.nom.ilike(f"%{q}%"),
            Patient.prenoms.ilike(f"%{q}%"),
        ]
        if q_strip.isdigit():
            filtres.append(cast(Patient.patient_id, String).like(f"{q_strip.lstrip('0') or '0'}%"))
        # Utiliser distinct() pour éviter les doublons et group by patient_id
        patients = db.query(Patient).filter(or_(*filtres)).distinct().limit(10).all()

    results = []
    seen_patient_ids = set()  # Pour éviter les doublons
    
    for p in patients:
        # Éviter les doublons
        if p.patient_id in seen_patient_ids:
            continue
        seen_patient_ids.add(p.patient_id)
        
        # Chercher la dernière consultation COMPLÈTEMENT préparée par l'infirmier
        # (statut en_attente_medecin = workflow-partiel terminé, symptômes + signes vitaux enregistrés)
        pending = (
            db.query(Consultation)
            .filter(
                Consultation.patient_id == p.patient_id,
                Consultation.statut == "en_attente_medecin",
            )
            .order_by(Consultation.date_heure.desc())
            .first()
        )
        # Consultation NON terminée que l'infirmier peut reprendre (brouillon en
        # cours de saisie, pas encore transmis au médecin OU en attente médecin).
        en_cours = (
            db.query(Consultation)
            .filter(
                Consultation.patient_id == p.patient_id,
                Consultation.statut.in_(["en attente", "en cours", "en_attente_medecin"]),
            )
            .order_by(Consultation.date_heure.desc())
            .first()
        )
        # Sinon, la dernière consultation quel que soit le statut
        latest = pending or en_cours or (
            db.query(Consultation)
            .filter(Consultation.patient_id == p.patient_id)
            .order_by(Consultation.date_heure.desc())
            .first()
        )
        results.append({
            "patient_id": p.patient_id,
            "nom": p.nom,
            "prenoms": p.prenoms,
            "sexe": p.sexe,
            "date_naissance": str(p.date_naissance) if p.date_naissance else None,
            "derniere_consultation_id": latest.consultation_id if latest else None,
            "derniere_consultation_statut": latest.statut if latest else None,
            "derniere_consultation_date": str(latest.date_heure) if latest else None,
            "consultation_en_attente_id": pending.consultation_id if pending else None,
            "consultation_en_attente_medecin_id": pending.medecin_id if pending else None,
            # Consultation reprenable par l'infirmier (toute consultation non terminée)
            "consultation_en_cours_id": en_cours.consultation_id if en_cours else None,
            "consultation_en_cours_statut": en_cours.statut if en_cours else None,
        })
    return results


@router.post("", response_model=PatientResponse, status_code=status.HTTP_201_CREATED)
def create_patient(patient: PatientCreate, db: Session = Depends(get_db)):
    """
    US-001: Enregistrement d'un nouveau patient
    """
    # Vérifier si le patient existe déjà (par numéro sécu)
    if patient.numero_securite_sociale:
        existing = db.query(Patient).filter(
            Patient.numero_securite_sociale == patient.numero_securite_sociale
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Un patient avec ce numéro de sécurité sociale existe déjà"
            )
    
    # Créer le patient
    db_patient = Patient(**patient.model_dump())
    db.add(db_patient)
    db.commit()
    db.refresh(db_patient)
    
    return db_patient


@router.get("", response_model=List[PatientResponse])
def list_patients(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Liste tous les patients
    """
    patients = (
        db.query(Patient)
        .options(joinedload(Patient.dossier_medical))
        .order_by(Patient.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    return patients


@router.get("/{patient_id}", response_model=PatientResponse)
def get_patient(patient_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    """
    Récupère un patient par son ID (INT)
    """
    if current_user.role == "infirmier":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Les infirmiers n'ont pas accès au dossier médical."
        )
        
    patient = (
        db.query(Patient)
        .options(joinedload(Patient.dossier_medical))
        .filter(Patient.patient_id == patient_id)
        .first()
    )
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient non trouvé"
        )

    # Créer le dossier médical à la volée si absent (patients créés avant ce correctif)
    if patient.dossier_medical is None:
        from datetime import datetime
        from ..models import DossierMedical
        ts = datetime.now().strftime('%Y%m%d%H%M%S')
        dossier = DossierMedical(
            patient_id=patient.patient_id,
            numero_dossier=f"DM-{ts}-{patient.patient_id}",
        )
        db.add(dossier)
        db.commit()
        db.refresh(patient)

    return patient


@router.put("/{patient_id}", response_model=PatientResponse)
def update_patient(
    patient_id: int,
    patient_update: PatientUpdate,
    db: Session = Depends(get_db)
):
    """
    Met à jour un patient
    """
    patient = db.query(Patient).filter(Patient.patient_id == patient_id).first()
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient non trouvé"
        )
    
    # Mettre à jour les champs
    update_data = patient_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(patient, field, value)
    
    db.commit()
    db.refresh(patient)
    
    return patient


@router.get("/{patient_id}/ordonnances")
def get_patient_ordonnances(patient_id: int, db: Session = Depends(get_db)):
    """Retourne toutes les ordonnances d'un patient avec leurs médicaments."""
    from ..models import Medecin
    ordonnances = (
        db.query(Ordonnance)
        .options(joinedload(Ordonnance.medicaments), joinedload(Ordonnance.medecin))
        .filter(Ordonnance.patient_id == patient_id)
        .order_by(Ordonnance.date_emission.desc())
        .all()
    )
    result = []
    for o in ordonnances:
        medecin_nom = f"Dr. {o.medecin.prenoms} {o.medecin.nom}" if o.medecin else None
        result.append({
            "ordonnance_id": o.ordonnance_id,
            "date_emission": o.date_emission.isoformat() if o.date_emission else None,
            "renouvelable": o.renouvelable,
            "medecin_nom": medecin_nom,
            "medicaments": [
                {
                    "medicament_id": m.medicament_id,
                    "nom_commercial": m.nom_commercial,
                    "denomination_commune": m.denomination_commune,
                    "dosage": m.dosage,
                    "forme": m.forme,
                    "frequence": m.frequence,
                    "duree_jours": m.duree_jours,
                }
                for m in o.medicaments
            ],
        })
    return result


@router.delete("/{patient_id}")
def delete_patient(patient_id: int, db: Session = Depends(get_db)):
    """
    Supprime un patient et toutes ses données liées (cascade manuelle — MyISAM).
    Ordre : medicaments → ordonnances → traitements → diagnostics → analyses_ia
            → examens → signes_vitaux → symptomes → suivis → doctor_feedback
            → prediction_history → prescriptions → consultation_infirmiers
            → consultations → dossiers_medicaux → patient
    """
    patient = db.query(Patient).filter(Patient.patient_id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient non trouvé")

    nom_complet = f"{patient.prenoms} {patient.nom}"

    # 1. Récupérer tous les IDs des consultations du patient
    cids = [c.consultation_id for c in
            db.query(Consultation.consultation_id)
            .filter(Consultation.patient_id == patient_id).all()]

    if cids:
        # 2. Remonter la chaîne diagnostic → traitement → ordonnance → médicament
        diag_ids = [d.diagnostic_id for d in
                    db.query(Diagnostic.diagnostic_id)
                    .filter(Diagnostic.consultation_id.in_(cids)).all()]

        if diag_ids:
            trait_ids = [t.traitement_id for t in
                         db.query(Traitement.traitement_id)
                         .filter(Traitement.diagnostic_id.in_(diag_ids)).all()]

            if trait_ids:
                ord_ids = [o.ordonnance_id for o in
                           db.query(Ordonnance.ordonnance_id)
                           .filter(Ordonnance.traitement_id.in_(trait_ids)).all()]

                if ord_ids:
                    db.query(Medicament).filter(
                        Medicament.ordonnance_id.in_(ord_ids)
                    ).delete(synchronize_session=False)

                db.query(Ordonnance).filter(
                    Ordonnance.traitement_id.in_(trait_ids)
                ).delete(synchronize_session=False)

            db.query(Traitement).filter(
                Traitement.diagnostic_id.in_(diag_ids)
            ).delete(synchronize_session=False)

        # 3. Supprimer les tables directement liées aux consultations
        db.query(Diagnostic).filter(Diagnostic.consultation_id.in_(cids)).delete(synchronize_session=False)
        db.query(AnalyseIA).filter(AnalyseIA.consultation_id.in_(cids)).delete(synchronize_session=False)
        db.query(Examen).filter(Examen.consultation_id.in_(cids)).delete(synchronize_session=False)
        db.query(SignesVitaux).filter(SignesVitaux.consultation_id.in_(cids)).delete(synchronize_session=False)
        db.query(Symptome).filter(Symptome.consultation_id.in_(cids)).delete(synchronize_session=False)
        db.query(PredictionHistory).filter(PredictionHistory.consultation_id.in_(cids)).delete(synchronize_session=False)
        db.query(Suivi).filter(Suivi.consultation_id.in_(cids)).delete(synchronize_session=False)

    # 4. Supprimer les données liées directement au patient (hors consultations)
    db.query(Suivi).filter(Suivi.patient_id == patient_id).delete(synchronize_session=False)
    db.query(PredictionHistory).filter(PredictionHistory.patient_id == patient_id).delete(synchronize_session=False)
    # Ordonnances liées directement au patient (hors chaîne traitement)
    db.query(Ordonnance).filter(Ordonnance.patient_id == patient_id).delete(synchronize_session=False)

    # 5. Supprimer les consultations et le dossier médical
    if cids:
        db.query(Consultation).filter(Consultation.patient_id == patient_id).delete(synchronize_session=False)

    from ..models import DossierMedical
    db.query(DossierMedical).filter(DossierMedical.patient_id == patient_id).delete(synchronize_session=False)

    # 6. Supprimer le patient
    db.delete(patient)
    db.commit()

    return {
        "success": True,
        "message": f"Patient {nom_complet} et toutes ses données associées ont été supprimés"
    }
