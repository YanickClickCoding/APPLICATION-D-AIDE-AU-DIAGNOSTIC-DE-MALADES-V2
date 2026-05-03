"""
Analytics API Router (US-034, US-036, US-044)
Dashboard et statistiques
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Dict, List
from datetime import datetime, timedelta

from ..database import get_db
from ..models import Patient, Consultation, Diagnostic, AnalyseIA, Medecin, Infirmier

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/dashboard")
def get_dashboard_stats(db: Session = Depends(get_db)) -> Dict:
    """
    US-044: Dashboard avec statistiques globales
    """
    # KPI 1: Nombre total de patients
    total_patients = db.query(func.count(Patient.id)).scalar()
    
    # KPI 2: Nombre de patients ce mois
    first_day_month = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    patients_this_month = db.query(func.count(Patient.id)).filter(
        Patient.created_at >= first_day_month
    ).scalar()
    
    # KPI 3: Nombre de consultations
    total_consultations = db.query(func.count(Consultation.consultation_id)).scalar()
    
    # KPI 3b: Consultations par statut
    consultations_en_attente = db.query(func.count(Consultation.consultation_id)).filter(
        Consultation.statut == "en attente"
    ).scalar() or 0
    
    consultations_en_cours = db.query(func.count(Consultation.consultation_id)).filter(
        Consultation.statut == "en cours"
    ).scalar() or 0
    
    consultations_terminees = db.query(func.count(Consultation.consultation_id)).filter(
        Consultation.statut == "terminée"
    ).scalar() or 0
    
    # KPI 4: Nombre de diagnostics
    total_diagnostics = db.query(func.count(Diagnostic.id)).scalar() or 0
    
    # KPI 5: Taux d'approbation
    diagnostics_approuves = db.query(func.count(Diagnostic.id)).filter(
        Diagnostic.statut == "CONFIRMÉ"
    ).scalar() or 0
    
    taux_approbation = (diagnostics_approuves / total_diagnostics * 100) if total_diagnostics > 0 else 0
    
    # KPI 6: Confiance moyenne (si la colonne existe)
    # Note: La table diagnostics utilise 'certitude' pas 'confiance'
    avg_confidence = db.query(func.avg(Diagnostic.certitude)).scalar() or 0
    
    # Tendance patients par jour (7 derniers jours)
    seven_days_ago = datetime.now() - timedelta(days=7)
    daily_patients = db.query(
        func.date(Patient.created_at).label('date'),
        func.count(Patient.id).label('count')
    ).filter(
        Patient.created_at >= seven_days_ago
    ).group_by(func.date(Patient.created_at)).all()
    
    # Top 5 diagnostics (utiliser nom_maladie)
    top_diagnostics = db.query(
        Diagnostic.nom_maladie,
        func.count(Diagnostic.id).label('count')
    ).filter(
        Diagnostic.nom_maladie.isnot(None)
    ).group_by(Diagnostic.nom_maladie).order_by(
        func.count(Diagnostic.id).desc()
    ).limit(5).all()
    
    return {
        "kpis": {
            "total_patients": total_patients,
            "patients_ce_mois": patients_this_month,
            "total_consultations": total_consultations,
            "consultations_en_attente": consultations_en_attente,
            "consultations_en_cours": consultations_en_cours,
            "consultations_terminees": consultations_terminees,
            "total_diagnostics": total_diagnostics,
            "taux_approbation": round(taux_approbation, 2),
            "confiance_moyenne": round(float(avg_confidence) * 100, 2)
        },
        "tendance_patients": [
            {"date": str(row.date), "count": row.count}
            for row in daily_patients
        ],
        "top_diagnostics": [
            {"diagnostic": row.nom_maladie, "count": row.count}
            for row in top_diagnostics
        ]
    }


@router.get("/diagnostics/distribution")
def get_diagnostics_distribution(db: Session = Depends(get_db)) -> Dict:
    """
    US-036: Distribution des diagnostics
    """
    # Compter par diagnostic (utiliser nom_maladie au lieu de diagnostic_final)
    distribution = db.query(
        Diagnostic.nom_maladie,
        func.count(Diagnostic.id).label('count')
    ).filter(
        Diagnostic.nom_maladie.isnot(None)
    ).group_by(Diagnostic.nom_maladie).all()
    
    total = sum([row.count for row in distribution])
    
    return {
        "diagnostics": [
            {
                "nom": row.nom_maladie,
                "count": row.count,
                "pourcentage": round(row.count / total * 100, 2) if total > 0 else 0
            }
            for row in distribution
        ],
        "total": total
    }


@router.get("/performance/model")
def get_model_performance(db: Session = Depends(get_db)) -> Dict:
    """
    US-038: Performance du modèle
    """
    # Précision par niveau de sévérité (pas de niveau_confiance dans le schéma)
    high_confidence = db.query(func.count(Diagnostic.id)).filter(
        Diagnostic.severite == "CRITIQUE",
        Diagnostic.statut == "CONFIRMÉ"
    ).scalar() or 0
    
    medium_confidence = db.query(func.count(Diagnostic.id)).filter(
        Diagnostic.severite == "GRAVE",
        Diagnostic.statut == "CONFIRMÉ"
    ).scalar() or 0
    
    low_confidence = db.query(func.count(Diagnostic.id)).filter(
        Diagnostic.severite == "MODERE",
        Diagnostic.statut == "CONFIRMÉ"
    ).scalar() or 0
    
    # Taux de rejet
    total_diagnostics = db.query(func.count(Diagnostic.id)).scalar() or 0
    rejetes = db.query(func.count(Diagnostic.id)).filter(
        Diagnostic.statut == "REJETÉ"
    ).scalar() or 0
    
    taux_rejet = (rejetes / total_diagnostics * 100) if total_diagnostics > 0 else 0
    
    return {
        "par_confiance": {
            "high": high_confidence,
            "medium": medium_confidence,
            "low": low_confidence
        },
        "taux_rejet": round(taux_rejet, 2),
        "total_diagnostics": total_diagnostics
    }


@router.get("/consultations/recent")
def get_recent_consultations(limit: int = 10, db: Session = Depends(get_db)) -> List[Dict]:
    """
    Consultations récentes
    """
    consultations = db.query(Consultation).order_by(
        Consultation.date_heure.desc()
    ).limit(limit).all()
    
    return [
        {
            "id": c.consultation_id,
            "nom_patient": c.nom_patient,
            "date": c.date_heure.isoformat(),
            "motif": c.motif,
            "statut": c.statut
        }
        for c in consultations
    ]


@router.get("/personnel/disponible")
def get_personnel_disponible(db: Session = Depends(get_db)) -> Dict:
    """
    Personnel médical disponible (médecins et infirmiers)
    """
    # Médecins disponibles
    medecins_dispo = db.query(Medecin).filter(
        Medecin.disponible == True
    ).all()
    
    total_medecins = db.query(func.count(Medecin.medecin_id)).scalar() or 0
    
    # Infirmiers disponibles
    infirmiers_dispo = db.query(Infirmier).filter(
        Infirmier.disponible == True
    ).all()
    
    total_infirmiers = db.query(func.count(Infirmier.infirmier_id)).scalar() or 0
    
    return {
        "medecins": {
            "disponibles": len(medecins_dispo),
            "total": total_medecins,
            "liste": [
                {
                    "id": m.medecin_id,
                    "nom": m.nom,
                    "prenoms": m.prenoms,
                    "specialite": m.specialite,
                    "telephone": m.telephone
                }
                for m in medecins_dispo
            ]
        },
        "infirmiers": {
            "disponibles": len(infirmiers_dispo),
            "total": total_infirmiers,
            "liste": [
                {
                    "id": i.infirmier_id,
                    "nom": i.nom,
                    "prenoms": i.prenoms,
                    "telephone": i.telephone,
                    "email": i.email
                }
                for i in infirmiers_dispo
            ]
        }
    }
