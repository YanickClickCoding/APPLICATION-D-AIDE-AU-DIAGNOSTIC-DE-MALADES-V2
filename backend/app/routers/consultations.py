"""
Consultations API Router (US-002, US-003, US-005)
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from ..database import get_db
from ..models import Consultation, Patient, Symptome, SignesVitaux
from ..models.diagnostic import Diagnostic
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
    for symptome_input in consultation.symptomes:
        db_symptome = Symptome(
            consultation_id=db_consultation.consultation_id,
            nom=symptome_input.nom,
            severite=symptome_input.severite,
            duree_jours=symptome_input.duree_jours
        )
        db.add(db_symptome)

    # Ajouter les signes vitaux
    signes_data = consultation.signes_vitaux.model_dump()
    db_signes = SignesVitaux(
        consultation_id=db_consultation.consultation_id,
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


@router.get("/en-attente")
def get_consultations_en_attente(db: Session = Depends(get_db)):
    """
    Retourne toutes les consultations en attente de prise en charge par un médecin.
    """
    consultations = db.query(Consultation).filter(
        Consultation.statut == "en_attente_medecin"
    ).order_by(Consultation.date_heure.desc()).all()
    return [
        {
            "consultation_id": c.consultation_id,
            "nom_patient": c.nom_patient,
            "motif": c.motif,
            "date_heure": c.date_heure.isoformat() if c.date_heure else None,
            "medecin_id": c.medecin_id,
        }
        for c in consultations
    ]


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


@router.get("/patient/{patient_id}")
def get_patient_consultations(patient_id: int, db: Session = Depends(get_db)):
    """
    US-004: Récupère l'historique des consultations d'un patient avec diagnostics
    """
    consultations = db.query(Consultation).filter(
        Consultation.patient_id == patient_id
    ).order_by(Consultation.date_heure.desc()).all()

    result = []
    for c in consultations:
        diag = db.query(Diagnostic).filter(
            Diagnostic.consultation_id == c.consultation_id
        ).order_by(Diagnostic.diagnostic_id.desc()).first()

        item = {
            "consultation_id": c.consultation_id,
            "date_heure": c.date_heure.isoformat() if c.date_heure else None,
            "motif": c.motif,
            "statut": c.statut,
            "medecin_id": c.medecin_id,
            "nom_patient": c.nom_patient,
            "diagnostic": None,
        }
        if diag:
            item["diagnostic"] = {
                "nom_maladie": diag.nom_maladie,
                "certitude": round((diag.certitude or 0) * 100, 1),
                "statut": diag.statut,
                "description": diag.description,
                "date_validation": diag.date_validation.isoformat() if diag.date_validation else None,
            }
        result.append(item)

    return result


@router.post("/workflow", status_code=status.HTTP_201_CREATED)
def create_consultation_workflow(data: dict, db: Session = Depends(get_db)):
    """
    Workflow complet de consultation assistée par IA (9 étapes).
    Enregistre : patient, consultation, symptômes, signes vitaux,
    examens, deux analyses IA (préliminaire + finale), diagnostic.
    """
    try:
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

        # ── 1. Patient + Consultation ────────────────────────────────────────
        existing_cid = data.get('consultation_id')
        db_consultation = None
        if existing_cid:
            db_consultation = db.query(Consultation).filter(
                Consultation.consultation_id == int(existing_cid)
            ).first()

        if db_consultation:
            # Mettre à jour la consultation draft créée à l'étape 1
            if motif:
                db_consultation.motif = motif
            db_consultation.statut = 'terminée'
            db.flush()
            cid_int = db_consultation.consultation_id
            patient = db.query(Patient).filter(Patient.patient_id == db_consultation.patient_id).first()
        else:
            # Créer patient + consultation (flux sans init préalable)
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
                    groupe_sanguin=patient_data.get('groupe_sanguin') or None,
                )
                db.add(patient)
                db.flush()
            else:
                gs = patient_data.get('groupe_sanguin') or None
                if gs and not patient.groupe_sanguin:
                    patient.groupe_sanguin = gs

            db_consultation = Consultation(
                patient_id=patient.patient_id,
                nom_patient=f"{patient_data.get('prenoms', '')} {patient_data.get('nom', '')}".strip(),
                date_heure=datetime.now(),
                motif=motif,
                medecin_id=None,
                statut='terminée',
            )
            db.add(db_consultation)
            db.flush()
            cid_int = db_consultation.consultation_id

        # ── 3. Symptômes ────────────────────────────────────────────────────
        sev_map = {'Légère': 'LEGER', 'Modérée': 'MODERE', 'Sévère': 'SEVERE'}
        for s in symptomes_data:
            if not (s.get('nom') or '').strip():
                continue
            db.add(Symptome(
                consultation_id=cid_int,
                nom=s['nom'].strip(),
                description=s.get('description') or None,
                severite=sev_map.get(s.get('severite', 'Modérée'), 'MODERE'),
                duree_jours=s.get('duree_jours', 1),
            ))

        # ── 4. Signes vitaux ─────────────────────────────────────────────────
        imc = None
        poids, taille = vitaux_data.get('poids'), vitaux_data.get('taille')
        if poids and taille:
            imc = round(poids / (taille / 100) ** 2, 1)

        db.add(SignesVitaux(
            consultation_id=cid_int,
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
                is_suggested=ex.get('isSuggested', False),  # Marquer si suggéré par l'IA
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


@router.post("/init", status_code=status.HTTP_201_CREATED)
def init_consultation(data: dict, db: Session = Depends(get_db)):
    """
    Étape 1 du workflow : enregistre le patient et crée une consultation draft (en attente).
    Retourne consultation_id + patient_id pour continuer le workflow sans perte de données.
    """
    from datetime import datetime
    patient_data = data.get('patient', {})
    motif = data.get('motif', '')
    medecin_id = data.get('medecin_id') or None

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
            groupe_sanguin=patient_data.get('groupe_sanguin') or None,
        )
        db.add(patient)
        db.flush()

    nom_patient = f"{patient_data.get('prenoms', '')} {patient_data.get('nom', '')}".strip()
    db_consultation = Consultation(
        patient_id=patient.patient_id,
        nom_patient=nom_patient,
        date_heure=datetime.now(),
        motif=motif,
        medecin_id=medecin_id,
        statut='en attente',
    )
    db.add(db_consultation)
    db.commit()
    db.refresh(db_consultation)
    return {
        "success": True,
        "consultation_id": db_consultation.consultation_id,
        "patient_id": patient.patient_id,
    }


@router.post("/rapide", status_code=status.HTTP_201_CREATED)
def create_consultation_rapide(data: dict, db: Session = Depends(get_db)):
    """
    Crée une consultation rapide avec enregistrement du patient (nom, prenoms, sexe requis).
    """
    from datetime import datetime
    nom = (data.get('nom') or '').strip()
    prenoms = (data.get('prenoms') or '').strip()
    nom_patient = (data.get('nom_patient') or f"{prenoms} {nom}").strip()
    if not nom_patient:
        raise HTTPException(status_code=400, detail="Le nom du patient est requis")

    # Créer le patient si nom + prenoms fournis
    patient_id = None
    if nom and prenoms:
        sexe = data.get('sexe', 'M')
        dn = data.get('date_naissance')
        email = (data.get('email') or '').strip() or None
        patient = None
        if email:
            patient = db.query(Patient).filter(Patient.email == email).first()
        if not patient:
            patient = Patient(
                nom=nom,
                prenoms=prenoms,
                sexe=sexe,
                date_naissance=datetime.strptime(dn, '%Y-%m-%d').date() if dn else None,
                email=email,
            )
            db.add(patient)
            db.flush()
        patient_id = patient.patient_id

    date_str = data.get('date_heure')
    try:
        date_heure = datetime.fromisoformat(date_str) if date_str else datetime.now()
    except (ValueError, TypeError):
        date_heure = datetime.now()
    db_consultation = Consultation(
        patient_id=patient_id,
        nom_patient=nom_patient,
        motif=data.get('motif', ''),
        date_heure=date_heure,
        medecin_id=data.get('medecin_id') or None,
        statut=data.get('statut', 'en attente'),
    )
    db.add(db_consultation)
    db.commit()
    db.refresh(db_consultation)
    return {"success": True, "consultation_id": db_consultation.consultation_id, "patient_id": patient_id}


@router.put("/{consultation_id}/affecter-medecin")
def affecter_medecin(consultation_id: int, data: dict, db: Session = Depends(get_db)):
    """
    Affecte un médecin à une consultation.
    """
    c = db.query(Consultation).filter(Consultation.consultation_id == consultation_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Consultation non trouvée")
    medecin_id = data.get('medecin_id')
    if not medecin_id:
        raise HTTPException(status_code=400, detail="L'ID du médecin est requis")
    c.medecin_id = medecin_id
    db.commit()
    return {"success": True, "consultation_id": consultation_id, "medecin_id": medecin_id}


@router.patch("/{consultation_id}/statut")
def update_statut_consultation(consultation_id: int, data: dict, db: Session = Depends(get_db)):
    """
    Met à jour le statut d'une consultation.
    """
    c = db.query(Consultation).filter(Consultation.consultation_id == consultation_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Consultation non trouvée")
    new_statut = data.get('statut')
    if not new_statut:
        raise HTTPException(status_code=400, detail="Le statut est requis")
    c.statut = new_statut
    db.commit()
    return {"success": True}


@router.put("/{consultation_id}")
def update_consultation(consultation_id: int, data: dict, db: Session = Depends(get_db)):
    """
    Mise à jour générale d'une consultation (motif, nom_patient, date, medecin, statut).
    """
    from datetime import datetime
    c = db.query(Consultation).filter(Consultation.consultation_id == consultation_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Consultation non trouvée")
    if 'nom_patient' in data:
        c.nom_patient = data['nom_patient']
    if 'motif' in data:
        c.motif = data['motif']
    if 'date_heure' in data and data['date_heure']:
        try:
            c.date_heure = datetime.fromisoformat(data['date_heure'])
        except (ValueError, TypeError):
            pass
    if 'medecin_id' in data:
        c.medecin_id = data['medecin_id'] or None
    if 'statut' in data:
        c.statut = data['statut']
    db.commit()
    return {"success": True}


@router.delete("/{consultation_id}")
def delete_consultation(consultation_id: int, db: Session = Depends(get_db)):
    """
    Supprime définitivement une consultation et ses données liées.
    """
    c = db.query(Consultation).filter(Consultation.consultation_id == consultation_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Consultation non trouvée")
    db.delete(c)
    db.commit()
    return {"success": True}


@router.post("/workflow-partiel", status_code=status.HTTP_201_CREATED)
def create_consultation_partielle(data: dict, db: Session = Depends(get_db)):
    """
    Infirmier: enregistre les étapes 1-4 (patient, symptômes, signes vitaux, analyse IA préliminaire).
    Statut = en_attente_medecin.
    """
    try:
        from datetime import datetime
        from ..models import AnalyseIA

        patient_data    = data.get('patient', {})
        symptomes_data  = data.get('symptomes', [])
        vitaux_data     = data.get('signes_vitaux', {})
        motif           = data.get('motif', '')
        analyse_prelim  = data.get('analyse_preliminaire')
        medecin_id      = data.get('medecin_id')

        existing_cid = data.get('consultation_id')
        db_consultation = None
        if existing_cid:
            db_consultation = db.query(Consultation).filter(
                Consultation.consultation_id == int(existing_cid)
            ).first()

        if db_consultation:
            # Mettre à jour la consultation draft créée à l'étape 1
            if motif:
                db_consultation.motif = motif
            if medecin_id:
                db_consultation.medecin_id = medecin_id
            db_consultation.statut = 'en_attente_medecin'
            db.flush()
            cid = db_consultation.consultation_id
            patient = db.query(Patient).filter(Patient.patient_id == db_consultation.patient_id).first()
        else:
            # Créer patient + consultation (flux sans init préalable)
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
                    groupe_sanguin=patient_data.get('groupe_sanguin') or None,
                )
                db.add(patient)
                db.flush()

            db_consultation = Consultation(
                patient_id=patient.patient_id,
                nom_patient=f"{patient_data.get('prenoms', '')} {patient_data.get('nom', '')}".strip(),
                date_heure=datetime.now(),
                motif=motif,
                medecin_id=medecin_id,
                statut='en_attente_medecin',
            )
            db.add(db_consultation)
            db.flush()
            cid = db_consultation.consultation_id

        sev_map = {'Légère': 'LEGER', 'Modérée': 'MODERE', 'Sévère': 'SEVERE'}
        for s in symptomes_data:
            if not (s.get('nom') or '').strip():
                continue
            db.add(Symptome(
                consultation_id=cid,
                nom=s['nom'].strip(),
                description=s.get('description') or None,
                severite=sev_map.get(s.get('severite', 'Modérée'), 'MODERE'),
                duree_jours=s.get('duree_jours', 1),
            ))

        poids, taille = vitaux_data.get('poids'), vitaux_data.get('taille')
        imc = round(poids / (taille / 100) ** 2, 1) if poids and taille else None
        db.add(SignesVitaux(
            consultation_id=cid,
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

        if analyse_prelim:
            db.add(AnalyseIA(
                consultation_id=cid,
                modele_ia="RandomForest_v1.0_Preliminaire",
                probabilite=analyse_prelim.get('confiance', 0.0),
                diagnostics_suggeres=analyse_prelim.get('top_predictions', []),
                scoring_confiance=analyse_prelim.get('confiance', 0.0),
                donnees_entree={
                    'phase': 'preliminaire',
                    'symptomes': symptomes_data,
                    'signes_vitaux': vitaux_data,
                },
            ))

        db.commit()
        db.refresh(db_consultation)
        return {
            "success": True,
            "consultation_id": cid,
            "patient_id": patient.patient_id,
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erreur: {str(e)}")


@router.get("/{consultation_id}/donnees-resume")
def get_donnees_resume(consultation_id: int, db: Session = Depends(get_db)):
    """
    Retourne les données pour reprendre une consultation (médecin continue depuis l'étape 5).
    """
    from ..models import AnalyseIA as AnalyseIAModel

    c = db.query(Consultation).filter(Consultation.consultation_id == consultation_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Consultation non trouvée")

    patient   = db.query(Patient).filter(Patient.patient_id == c.patient_id).first()
    symptomes = db.query(Symptome).filter(Symptome.consultation_id == consultation_id).all()
    vitaux    = db.query(SignesVitaux).filter(SignesVitaux.consultation_id == consultation_id).first()
    analyse   = (
        db.query(AnalyseIAModel)
        .filter(AnalyseIAModel.consultation_id == consultation_id)
        .order_by(AnalyseIAModel.analyse_id.desc())
        .first()
    )

    rev_sev = {'LEGER': 'Légère', 'MODERE': 'Modérée', 'SEVERE': 'Sévère'}
    return {
        "consultation_id": c.consultation_id,
        "medecin_id": c.medecin_id,
        "motif": c.motif or '',
        "patient": {
            "nom": patient.nom if patient else '',
            "prenoms": patient.prenoms if patient else '',
            "date_naissance": patient.date_naissance.isoformat() if patient and patient.date_naissance else '',
            "sexe": patient.sexe if patient else 'M',
            "telephone": (patient.telephone or '') if patient else '',
            "email": (patient.email or '') if patient else '',
            "groupe_sanguin": (patient.groupe_sanguin or '') if patient else '',
        },
        "symptomes": [
            {
                "nom": s.nom,
                "severite": rev_sev.get(s.severite, 'Modérée'),
                "duree_jours": s.duree_jours or 1,
                "description": s.description or '',
            }
            for s in symptomes
        ],
        "signes_vitaux": {
            "tension_systolique": vitaux.tension_systolique,
            "tension_diastolique": vitaux.tension_diastolique,
            "frequence_cardiaque": vitaux.frequence_cardiaque,
            "frequence_respiratoire": vitaux.frequence_respiratoire,
            "temperature": vitaux.temperature,
            "saturation_o2": vitaux.saturation_oxygene,
            "poids": vitaux.poids,
            "taille": vitaux.taille,
        } if vitaux else None,
        "analyse_preliminaire": {
            "maladie_predite": (analyse.diagnostics_suggeres or [{}])[0].get('maladie', ''),
            "confiance": analyse.probabilite or 0,
            "top_predictions": analyse.diagnostics_suggeres or [],
        } if analyse else None,
    }


@router.post("/{consultation_id}/workflow-complet", status_code=200)
def complete_consultation_medecin(consultation_id: int, data: dict, db: Session = Depends(get_db)):
    """
    Médecin finalise une consultation démarrée par un infirmier (étapes 5-9).
    """
    try:
        from datetime import datetime
        from ..models import AnalyseIA, Diagnostic, DossierMedical, Examen

        c = db.query(Consultation).filter(Consultation.consultation_id == consultation_id).first()
        if not c:
            raise HTTPException(status_code=404, detail="Consultation non trouvée")

        examens_data     = data.get('examens', [])
        analyse_finale   = data.get('analyse_finale')
        diagnostic_final = data.get('diagnostic_final', '')
        validation_type  = data.get('validation_type', 'confirme')
        notes_validation = data.get('notes_validation', '')

        for ex in examens_data:
            if not (ex.get('nom') or '').strip():
                continue
            de = ex.get('date_examen')
            db.add(Examen(
                consultation_id=consultation_id,
                type=ex.get('type', 'BIOLOGIE'),
                nom=ex['nom'].strip(),
                description=ex.get('description') or None,
                resultats=ex.get('resultats') or None,
                valeur_numerique=ex.get('valeur_numerique'),
                unite_mesure=ex.get('unite_mesure') or None,
                statut='REALISE',
                date_examen=datetime.strptime(de, '%Y-%m-%d').date() if de else None,
                is_suggested=ex.get('isSuggested', False),  # Marquer si suggéré par l'IA
            ))

        dossier = db.query(DossierMedical).filter(DossierMedical.patient_id == c.patient_id).first()
        if not dossier:
            ts = datetime.now().strftime('%Y%m%d%H%M%S')
            dossier = DossierMedical(
                patient_id=c.patient_id,
                numero_dossier=f"DM-{ts}-{c.patient_id}",
            )
            db.add(dossier)
            db.flush()

        finale_id = None
        if analyse_finale:
            rec = AnalyseIA(
                consultation_id=consultation_id,
                modele_ia="RandomForest_v1.0_Finale",
                probabilite=analyse_finale.get('confiance', 0.0),
                diagnostics_suggeres=analyse_finale.get('top_predictions', []),
                scoring_confiance=analyse_finale.get('confiance', 0.0),
                donnees_entree={'phase': 'finale', 'examens': examens_data},
            )
            db.add(rec)
            db.flush()
            finale_id = rec.analyse_id

        if diagnostic_final:
            confiance    = (analyse_finale or {}).get('confiance', 0.0)
            statut_diag  = 'CONFIRMÉ' if validation_type == 'confirme' else 'REJETÉ'
            ia_sugg      = (analyse_finale or {}).get('maladie_predite', 'N/A')
            db.add(Diagnostic(
                consultation_id=consultation_id,
                analyse_ia_id=finale_id,
                medecin_id=None,
                dossier_id=dossier.dossier_id,
                nom_maladie=diagnostic_final,
                description=(
                    f"Validation : {statut_diag}. "
                    f"Suggestion IA : {ia_sugg} ({confiance*100:.1f}%). "
                    f"Notes : {notes_validation}"
                ),
                certitude=confiance,
                statut=statut_diag,
                date_validation=datetime.now().date(),
            ))

        c.statut = "terminée"
        db.commit()
        return {"success": True, "consultation_id": consultation_id}

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erreur: {str(e)}")


@router.get("/{consultation_id}/details-complets")
def get_consultation_details_complets(consultation_id: int, db: Session = Depends(get_db)):
    """
    Retourne tous les détails d'une consultation pour affichage complet.
    Inclut: symptômes, signes vitaux, analyses IA, examens, diagnostic, ordonnance, suivi.
    """
    from ..models import (
        AnalyseIA as AnalyseIAModel,
        Examen,
        Medicament,
        Medecin,
        Traitement,
        Ordonnance,
        Suivi
    )
    from datetime import datetime

    # Récupérer la consultation
    c = db.query(Consultation).filter(Consultation.consultation_id == consultation_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Consultation non trouvée")

    # Récupérer le patient
    patient = db.query(Patient).filter(Patient.patient_id == c.patient_id).first()

    # Récupérer le médecin
    medecin_nom = None
    if c.medecin_id:
        medecin = db.query(Medecin).filter(Medecin.medecin_id == c.medecin_id).first()
        if medecin:
            medecin_nom = f"{medecin.prenoms} {medecin.nom}"

    # Récupérer les symptômes
    symptomes = db.query(Symptome).filter(Symptome.consultation_id == consultation_id).all()
    rev_sev = {'LEGER': 'Légère', 'MODERE': 'Modérée', 'SEVERE': 'Sévère'}
    symptomes_data = [
        {
            "nom": s.nom,
            "severite": rev_sev.get(s.severite, 'Modérée'),
            "duree_jours": s.duree_jours or 1,
            "description": s.description or '',
        }
        for s in symptomes
    ]

    # Récupérer les signes vitaux
    vitaux = db.query(SignesVitaux).filter(SignesVitaux.consultation_id == consultation_id).first()
    signes_vitaux_data = None
    if vitaux:
        signes_vitaux_data = {
            "tension_systolique": vitaux.tension_systolique,
            "tension_diastolique": vitaux.tension_diastolique,
            "frequence_cardiaque": vitaux.frequence_cardiaque,
            "frequence_respiratoire": vitaux.frequence_respiratoire,
            "temperature": vitaux.temperature,
            "saturation_o2": vitaux.saturation_oxygene,
            "poids": vitaux.poids,
            "taille": vitaux.taille,
        }

    # Récupérer les analyses IA (préliminaire et finale)
    analyses = (
        db.query(AnalyseIAModel)
        .filter(AnalyseIAModel.consultation_id == consultation_id)
        .order_by(AnalyseIAModel.analyse_id.asc())
        .all()
    )
    
    analyse_preliminaire = None
    analyse_finale = None
    
    if len(analyses) > 0:
        # Première analyse = préliminaire
        a = analyses[0]
        analyse_preliminaire = {
            "maladie_predite": (a.diagnostics_suggeres or [{}])[0].get('maladie', '') if a.diagnostics_suggeres else '',
            "confiance": a.probabilite or 0,
            "top_predictions": [
                {"maladie": d.get('maladie', ''), "probabilite": d.get('confiance', 0)}
                for d in (a.diagnostics_suggeres or [])
            ],
        }
    
    if len(analyses) > 1:
        # Deuxième analyse = finale
        a = analyses[1]
        analyse_finale = {
            "maladie_predite": (a.diagnostics_suggeres or [{}])[0].get('maladie', '') if a.diagnostics_suggeres else '',
            "confiance": a.probabilite or 0,
            "top_predictions": [
                {"maladie": d.get('maladie', ''), "probabilite": d.get('confiance', 0)}
                for d in (a.diagnostics_suggeres or [])
            ],
        }

    # Récupérer les examens
    examens = db.query(Examen).filter(Examen.consultation_id == consultation_id).all()
    examens_data = [
        {
            "type": e.type,
            "nom": e.nom,
            "description": e.description,
            "resultats": e.resultats,
            "valeur_numerique": e.valeur_numerique,
            "unite_mesure": e.unite_mesure,
            "date_examen": e.date_examen.isoformat() if e.date_examen else None,
            "is_suggested": e.is_suggested if hasattr(e, 'is_suggested') else False,
        }
        for e in examens
    ]

    # Récupérer le diagnostic final
    diagnostic = db.query(Diagnostic).filter(Diagnostic.consultation_id == consultation_id).first()
    diagnostic_final = None
    validation_type = None
    notes_validation = None
    
    if diagnostic:
        diagnostic_final = diagnostic.nom_maladie
        # Map database status to frontend format (without accents)
        status_map = {
            'CONFIRMÉ': 'confirme',
            'REJETÉ': 'rejete',
            'PROVISOIRE': 'provisoire',
            'ARCHIVÉ': 'archive'
        }
        validation_type = status_map.get(diagnostic.statut, 'confirme')
        notes_validation = diagnostic.description

    # Récupérer l'ordonnance via le diagnostic et le traitement
    from ..models import Traitement, Ordonnance
    
    ordonnance_data = []
    diagnostic = db.query(Diagnostic).filter(Diagnostic.consultation_id == consultation_id).first()
    if diagnostic:
        # Récupérer le traitement lié au diagnostic
        traitement = db.query(Traitement).filter(Traitement.diagnostic_id == diagnostic.diagnostic_id).first()
        if traitement:
            # Récupérer l'ordonnance liée au traitement
            ordonnance = db.query(Ordonnance).filter(Ordonnance.traitement_id == traitement.traitement_id).first()
            if ordonnance:
                # Récupérer les médicaments de l'ordonnance
                medicaments = db.query(Medicament).filter(Medicament.ordonnance_id == ordonnance.ordonnance_id).all()
                ordonnance_data = [
                    {
                        "nom": m.nom_commercial or m.denomination_commune or '',
                        "dosage": m.dosage or '',
                        "frequence": m.frequence or '',
                        "duree_jours": m.duree_jours or 0,
                        "instructions": f"{m.forme or ''} - {m.voie_administration or ''}".strip(' -'),
                    }
                    for m in medicaments
                ]

    # Récupérer les informations de suivi
    from ..models import Suivi
    
    suivi_data = None
    suivi = db.query(Suivi).filter(Suivi.consultation_id == consultation_id).first()
    if suivi:
        suivi_data = {
            "date_prochain_rdv": suivi.prochaine_consultation.isoformat() if suivi.prochaine_consultation else None,
            "instructions_patient": f"État général: {suivi.etat_general or 'N/A'}, Amélioration: {suivi.amelioration or 'N/A'}",
            "notes_medecin": f"Adhérence au traitement: {suivi.adherence_traitement or 0}%, Statut: {suivi.statut or 'N/A'}",
        }

    return {
        "consultation_id": c.consultation_id,
        "date_heure": c.date_heure.isoformat() if c.date_heure else None,
        "motif": c.motif or '',
        "statut": c.statut or 'en cours',
        "patient": {
            "nom": patient.nom if patient else '',
            "prenoms": patient.prenoms if patient else '',
            "date_naissance": patient.date_naissance.isoformat() if patient and patient.date_naissance else '',
            "sexe": patient.sexe if patient else 'M',
        },
        "medecin_nom": medecin_nom,
        "symptomes": symptomes_data,
        "signes_vitaux": signes_vitaux_data,
        "analyse_preliminaire": analyse_preliminaire,
        "examens": examens_data,
        "analyse_finale": analyse_finale,
        "diagnostic_final": diagnostic_final,
        "validation_type": validation_type,
        "notes_validation": notes_validation,
        "ordonnance": ordonnance_data,
        "suivi": suivi_data,
    }
