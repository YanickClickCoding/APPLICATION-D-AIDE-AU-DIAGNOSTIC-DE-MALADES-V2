"""
Audit trail médical — trace toutes les décisions cliniques importantes.
Chaque ligne est immuable (append-only) et horodatée.
"""
import logging
import json
from datetime import datetime
from pathlib import Path

# Logger dédié audit (séparé du logger applicatif)
_audit_logger = logging.getLogger("medical_audit")
_audit_logger.setLevel(logging.INFO)
_audit_logger.propagate = False  # ne pas remonter au root logger

def _ensure_handler():
    if not _audit_logger.handlers:
        audit_path = Path("./logs/audit_medical.log")
        audit_path.parent.mkdir(parents=True, exist_ok=True)
        h = logging.FileHandler(audit_path, encoding="utf-8", mode="a")
        h.setFormatter(logging.Formatter("%(message)s"))
        _audit_logger.addHandler(h)


def _write(event: str, payload: dict):
    _ensure_handler()
    entry = {
        "ts": datetime.utcnow().isoformat() + "Z",
        "event": event,
        **payload,
    }
    _audit_logger.info(json.dumps(entry, ensure_ascii=False))


# ── API publique ──────────────────────────────────────────────────────────────

def audit_diagnostic_valide(
    medecin_id: int | None,
    patient_id: int | None,
    consultation_id: int,
    maladie: str,
    validation_type: str,
    confiance_ia: float,
    suggestion_ia: str,
):
    """Médecin confirme ou rejette le diagnostic IA."""
    _write("DIAGNOSTIC_VALIDE", {
        "medecin_id": medecin_id,
        "patient_id": patient_id,
        "consultation_id": consultation_id,
        "maladie_retenue": maladie,
        "decision": validation_type,          # 'confirme' | 'rejete'
        "confiance_ia_pct": round(confiance_ia * 100, 1) if confiance_ia <= 1 else round(confiance_ia, 1),
        "suggestion_ia": suggestion_ia,
    })


def audit_ordonnance_emise(
    medecin_id: int | None,
    patient_id: int | None,
    consultation_id: int,
    maladie: str,
    medicaments: list[str],
):
    """Médecin émet une ordonnance."""
    _write("ORDONNANCE_EMISE", {
        "medecin_id": medecin_id,
        "patient_id": patient_id,
        "consultation_id": consultation_id,
        "maladie": maladie,
        "nb_medicaments": len(medicaments),
        "medicaments": medicaments,
    })


def audit_prediction_ia(
    consultation_id: int,
    phase: str,
    maladie_predite: str,
    confiance: float,
    top3: list[dict],
):
    """Prédiction IA effectuée (préliminaire ou finale)."""
    _write("PREDICTION_IA", {
        "consultation_id": consultation_id,
        "phase": phase,  # 'preliminaire' | 'finale'
        "maladie_predite": maladie_predite,
        "confiance_pct": round(confiance * 100, 1) if confiance <= 1 else round(confiance, 1),
        "top3": top3[:3],
    })


def audit_connexion(utilisateur_id: int, email: str, role: str, succes: bool):
    """Connexion d'un utilisateur."""
    _write("CONNEXION", {
        "utilisateur_id": utilisateur_id,
        "email": email,
        "role": role,
        "succes": succes,
    })
