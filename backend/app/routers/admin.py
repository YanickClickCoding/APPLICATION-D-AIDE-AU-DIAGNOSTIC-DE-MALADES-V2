"""
Admin Router - Gestion système, CRUD utilisateurs, CRUD personnel, config IA
Tous les endpoints sont protégés : token JWT admin requis.
"""
import os
import json
import platform
import threading
import logging
from datetime import datetime
from typing import Dict, List, Optional

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr, Field

from ..database import get_db
from ..models.user import User
from ..models.medecin import Medecin
from ..models.infirmier import Infirmier
from ..ml.model_manager import model_manager
from .auth import get_current_admin, get_password_hash

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/admin", tags=["Administration"])

# ─── Config IA en mémoire (persistable si besoin) ─────────────────────────────
_ia_config: Dict = {
    "seuil_confiance_min": 0.60,
    "seuil_alerte_bas": 0.40,
    "n_estimators": 200,
    "max_depth": 30,
}

# ─── Historique des entraînements ────────────────────────────────────────────
_TRAINING_HISTORY_FILE = "./ml_models/training_history.json"


def _load_training_history() -> List[Dict]:
    if not os.path.exists(_TRAINING_HISTORY_FILE):
        return []
    try:
        with open(_TRAINING_HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def _append_training_history(session: Dict):
    history = _load_training_history()
    history.append(session)
    history = history[-20:]  # Garder les 20 dernières sessions
    os.makedirs(os.path.dirname(_TRAINING_HISTORY_FILE), exist_ok=True)
    with open(_TRAINING_HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)


# ─── État entraînement ────────────────────────────────────────────────────────
_training_state: Dict = {
    "status": "idle",
    "started_at": None,
    "finished_at": None,
    "message": "",
    "results": None,
    "error": None,
}
_training_lock = threading.Lock()

# ─── Dataset ─────────────────────────────────────────────────────────────────
# Utiliser le dataset enrichi avec les 3 nouveaux examens microbiologiques (BAAR, Culture, Xpert)
_DATASET_FILENAME = "dataset_medical_robust_enhanced.csv"
_DATASET_FILENAME_FALLBACK = "dataset_medical_robust_10000_cas.csv"  # Fallback si le nouveau n'existe pas
_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
_DATASET_CANDIDATES = [
    # Nouveau dataset enrichi (403 features)
    os.path.join("..", "les ressources dataset", _DATASET_FILENAME),
    os.path.join("..", "..", "les ressources dataset", _DATASET_FILENAME),
    os.path.join(_ROOT, "les ressources dataset", _DATASET_FILENAME),
    # Fallback vers l'ancien dataset (400 features)
    os.path.join("..", "les ressources dataset", _DATASET_FILENAME_FALLBACK),
    os.path.join("..", "..", "les ressources dataset", _DATASET_FILENAME_FALLBACK),
    os.path.join(_ROOT, "les ressources dataset", _DATASET_FILENAME_FALLBACK),
]


def _find_dataset() -> Optional[str]:
    for p in _DATASET_CANDIDATES:
        if os.path.exists(p):
            return os.path.abspath(p)
    return None


# ═══════════════════════════════════════════════════════════════════════════════
# SCHÉMAS PYDANTIC
# ═══════════════════════════════════════════════════════════════════════════════

class UserCreate(BaseModel):
    nom: str = Field(..., min_length=1, max_length=100)
    prenoms: str = Field(..., min_length=1, max_length=150)
    email: EmailStr
    password: str = Field(..., min_length=6)
    role: str = Field("medecin", pattern="^(admin|medecin|infirmier)$")
    specialite: Optional[str] = None
    telephone: Optional[str] = None

class UserUpdate(BaseModel):
    nom: Optional[str] = Field(None, min_length=1, max_length=100)
    prenoms: Optional[str] = Field(None, min_length=1, max_length=150)
    email: Optional[EmailStr] = None
    role: Optional[str] = Field(None, pattern="^(admin|medecin|infirmier)$")
    actif: Optional[bool] = None
    password: Optional[str] = Field(None, min_length=6)
    specialite: Optional[str] = Field(None, max_length=150)

class MedecinCreate(BaseModel):
    nom: str = Field(..., min_length=1, max_length=100)
    prenoms: str = Field(..., min_length=1, max_length=150)
    specialite: str = Field(..., min_length=1, max_length=150)
    role: Optional[str] = Field(None, max_length=100)
    telephone: str = Field(..., min_length=1, max_length=20)
    disponible: bool = True

class MedecinUpdate(BaseModel):
    nom: Optional[str] = None
    prenoms: Optional[str] = None
    specialite: Optional[str] = None
    role: Optional[str] = None
    telephone: Optional[str] = None
    disponible: Optional[bool] = None

class InfirmierCreate(BaseModel):
    nom: str = Field(..., min_length=1, max_length=100)
    prenoms: str = Field(..., min_length=1, max_length=150)
    telephone: str = Field(..., min_length=1, max_length=20)
    email: Optional[str] = None
    disponible: bool = True

class InfirmierUpdate(BaseModel):
    nom: Optional[str] = None
    prenoms: Optional[str] = None
    telephone: Optional[str] = None
    email: Optional[str] = None
    disponible: Optional[bool] = None

class IAConfigUpdate(BaseModel):
    seuil_confiance_min: Optional[float] = Field(None, ge=0.0, le=1.0)
    seuil_alerte_bas: Optional[float] = Field(None, ge=0.0, le=1.0)
    n_estimators: Optional[int] = Field(None, ge=50, le=500)
    max_depth: Optional[int] = Field(None, ge=5, le=60)


# ═══════════════════════════════════════════════════════════════════════════════
# STATUT SYSTÈME
# ═══════════════════════════════════════════════════════════════════════════════

@router.get("/status")
def get_system_status(admin: User = Depends(get_current_admin)):
    try:
        model_info = model_manager.get_model_info()
    except Exception:
        model_info = {
            "loaded": False,
            "version": None,
            "metadata": None,
            "n_features": 0,
            "n_classes": 0,
            "classes": [],
            "normalization_loaded": False,
        }

    resources: Dict = {}
    try:
        import psutil
        resources = {
            "cpu_percent": psutil.cpu_percent(interval=0.2),
            "ram_used_gb": round(psutil.virtual_memory().used / 1024**3, 2),
            "ram_total_gb": round(psutil.virtual_memory().total / 1024**3, 2),
            "ram_percent": psutil.virtual_memory().percent,
            "disk_free_gb": round(psutil.disk_usage(".").free / 1024**3, 2),
        }
    except ImportError:
        resources = {"note": "psutil non installé (pip install psutil)"}

    dataset_path = _find_dataset()
    dataset_info: Dict = {"found": False, "path": None, "size_mb": None}
    if dataset_path:
        try:
            dataset_info = {"found": True, "path": dataset_path,
                            "size_mb": round(os.path.getsize(dataset_path) / 1024**2, 2)}
        except OSError:
            dataset_info = {"found": True, "path": dataset_path, "size_mb": None}

    model_dir = "./ml_models/"
    model_files: List[Dict] = []
    if os.path.exists(model_dir):
        for fname in sorted(os.listdir(model_dir), reverse=True):
            if fname.endswith(".joblib"):
                fpath = os.path.join(model_dir, fname)
                try:
                    model_files.append({
                        "name": fname,
                        "size_mb": round(os.path.getsize(fpath) / 1024**2, 2),
                        "modified": datetime.fromtimestamp(os.path.getmtime(fpath)).isoformat(),
                    })
                except OSError:
                    model_files.append({"name": fname, "size_mb": None, "modified": None})

    log_file = "./logs/app.log"
    log_info = {"exists": os.path.exists(log_file), "path": log_file, "size_kb": None}
    if log_info["exists"]:
        try:
            log_info["size_kb"] = round(os.path.getsize(log_file) / 1024, 1)
        except OSError:
            pass

    return {
        "server": {
            "status": "running",
            "timestamp": datetime.now().isoformat(),
            "platform": platform.system(),
            "python_version": platform.python_version(),
            "uvicorn_port": 8000,
        },
        "model": model_info,
        "ia_config": _ia_config,
        "training": _training_state,
        "dataset": dataset_info,
        "model_files": model_files,
        "resources": resources,
        "logs": log_info,
    }


# ═══════════════════════════════════════════════════════════════════════════════
# CRUD UTILISATEURS
# ═══════════════════════════════════════════════════════════════════════════════

def _user_to_dict(u: User) -> dict:
    return {
        "utilisateur_id": u.utilisateur_id,
        "nom": u.nom,
        "prenoms": u.prenoms,
        "email": u.email,
        "role": u.role,
        "actif": u.actif,
        "created_at": u.created_at.isoformat() if u.created_at else None,
        "last_login": u.last_login.isoformat() if u.last_login else None,
    }


@router.get("/users")
def list_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    users = db.query(User).filter(User.actif == True).offset(skip).limit(limit).all()
    return [_user_to_dict(u) for u in users]


@router.get("/users/pending")
def list_pending_users(
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    users = db.query(User).filter(User.actif == False, User.role != "admin").all()
    return [_user_to_dict(u) for u in users]


@router.post("/users", status_code=status.HTTP_201_CREATED)
def create_user(
    data: UserCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    if db.query(User).filter(User.email == data.email).first():
        raise HTTPException(status_code=400, detail="Email déjà utilisé")

    new_user = User(
        nom=data.nom,
        prenoms=data.prenoms,
        email=data.email,
        mot_de_passe=get_password_hash(data.password),
        role=data.role,
        actif=True,
    )
    db.add(new_user)
    db.flush()

    # Auto-créer le profil médecin si le rôle est 'medecin'
    if data.role == "medecin":
        existing = db.query(Medecin).filter(
            Medecin.nom == data.nom,
            Medecin.prenoms == data.prenoms
        ).first()
        if not existing:
            db.add(Medecin(
                nom=data.nom,
                prenoms=data.prenoms,
                specialite=data.specialite or "Médecin Général",
                telephone=data.telephone or "N/A",
                disponible=True,
            ))

    db.commit()
    db.refresh(new_user)
    return _user_to_dict(new_user)


@router.put("/users/{user_id}")
def update_user(
    user_id: int,
    data: UserUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    user = db.query(User).filter(User.utilisateur_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur introuvable")

    # Empêcher l'admin de se désactiver lui-même
    if data.actif is False and user.utilisateur_id == admin.utilisateur_id:
        raise HTTPException(status_code=400, detail="Impossible de désactiver votre propre compte")

    if data.nom is not None:        user.nom = data.nom
    if data.prenoms is not None:    user.prenoms = data.prenoms
    if data.email is not None:
        existing = db.query(User).filter(User.email == data.email, User.utilisateur_id != user_id).first()
        if existing:
            raise HTTPException(status_code=400, detail="Email déjà utilisé")
        user.email = data.email
    if data.role is not None:       user.role = data.role
    if data.actif is not None:      user.actif = data.actif
    if data.password is not None:   user.mot_de_passe = get_password_hash(data.password)

    # Si l'utilisateur est (ou devient) médecin, synchroniser la fiche Medecin
    if user.role == "medecin":
        medecin = db.query(Medecin).filter(
            Medecin.nom == user.nom, Medecin.prenoms == user.prenoms
        ).first()
        if medecin:
            if data.specialite:
                medecin.specialite = data.specialite
        else:
            db.add(Medecin(
                nom=user.nom,
                prenoms=user.prenoms,
                specialite=data.specialite or "Médecine Générale",
                telephone="N/A",
                disponible=True,
            ))

    db.commit()
    db.refresh(user)
    logger.info(f"✏️ Utilisateur modifié par admin: {user.email} ({user.role})")
    return _user_to_dict(user)


@router.delete("/users/{user_id}")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    if user_id == admin.utilisateur_id:
        raise HTTPException(status_code=400, detail="Impossible de supprimer votre propre compte")

    user = db.query(User).filter(User.utilisateur_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur introuvable")

    db.delete(user)
    db.commit()
    return {"message": f"Utilisateur {user.prenoms} {user.nom} supprimé"}


@router.post("/users/{user_id}/activate")
def activate_user(
    user_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    user = db.query(User).filter(User.utilisateur_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur introuvable")
    if user.actif:
        raise HTTPException(status_code=400, detail="Ce compte est déjà actif")

    user.actif = True

    if user.role == "medecin":
        existing = db.query(Medecin).filter(
            Medecin.nom == user.nom, Medecin.prenoms == user.prenoms
        ).first()
        if existing:
            existing.disponible = True
        else:
            db.add(Medecin(
                nom=user.nom,
                prenoms=user.prenoms,
                specialite="Médecine Générale",
                telephone="N/A",
                disponible=True,
            ))
    elif user.role == "infirmier":
        existing = db.query(Infirmier).filter(
            Infirmier.nom == user.nom, Infirmier.prenoms == user.prenoms
        ).first()
        if existing:
            existing.disponible = True
        else:
            db.add(Infirmier(
                nom=user.nom,
                prenoms=user.prenoms,
                telephone="N/A",
                email=user.email,
                disponible=True,
            ))

    db.commit()
    db.refresh(user)
    logger.info(f"✅ Compte activé par admin: {user.email} ({user.role})")
    return _user_to_dict(user)


# ═══════════════════════════════════════════════════════════════════════════════
# CRUD MÉDECINS
# ═══════════════════════════════════════════════════════════════════════════════

def _medecin_to_dict(m: Medecin) -> dict:
    return {
        "medecin_id": m.medecin_id,
        "nom": m.nom,
        "prenoms": m.prenoms,
        "specialite": m.specialite,
        "telephone": m.telephone,
        "disponible": m.disponible,
        "created_at": m.created_at.isoformat() if m.created_at else None,
    }


@router.get("/personnel/medecins")
def list_medecins(
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    return [_medecin_to_dict(m) for m in db.query(Medecin).all()]


@router.post("/personnel/medecins", status_code=201)
def create_medecin(
    data: MedecinCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    m = Medecin(
        nom=data.nom, prenoms=data.prenoms,
        specialite=data.specialite, role=data.role,
        telephone=data.telephone,
        disponible=data.disponible,
    )
    db.add(m)
    db.commit()
    db.refresh(m)
    return _medecin_to_dict(m)


@router.put("/personnel/medecins/{medecin_id}")
def update_medecin(
    medecin_id: int,
    data: MedecinUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    m = db.query(Medecin).filter(Medecin.medecin_id == medecin_id).first()
    if not m:
        raise HTTPException(status_code=404, detail="Médecin introuvable")

    for field, val in data.model_dump(exclude_none=True).items():
        setattr(m, field, val)

    db.commit()
    db.refresh(m)
    return _medecin_to_dict(m)


@router.delete("/personnel/medecins/{medecin_id}")
def delete_medecin(
    medecin_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    m = db.query(Medecin).filter(Medecin.medecin_id == medecin_id).first()
    if not m:
        raise HTTPException(status_code=404, detail="Médecin introuvable")
    db.delete(m)
    db.commit()
    return {"message": f"Dr {m.prenoms} {m.nom} supprimé"}


# ═══════════════════════════════════════════════════════════════════════════════
# CRUD INFIRMIERS
# ═══════════════════════════════════════════════════════════════════════════════

def _infirmier_to_dict(i: Infirmier) -> dict:
    return {
        "infirmier_id": i.infirmier_id,
        "nom": i.nom,
        "prenoms": i.prenoms,
        "telephone": i.telephone,
        "email": i.email,
        "disponible": i.disponible,
        "created_at": i.created_at.isoformat() if i.created_at else None,
    }


@router.get("/personnel/infirmiers")
def list_infirmiers(
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    return [_infirmier_to_dict(i) for i in db.query(Infirmier).all()]


@router.post("/personnel/infirmiers", status_code=201)
def create_infirmier(
    data: InfirmierCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    inf = Infirmier(
        nom=data.nom, prenoms=data.prenoms,
        telephone=data.telephone, email=data.email,
        disponible=data.disponible,
    )
    db.add(inf)
    db.commit()
    db.refresh(inf)
    return _infirmier_to_dict(inf)


@router.put("/personnel/infirmiers/{infirmier_id}")
def update_infirmier(
    infirmier_id: int,
    data: InfirmierUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    inf = db.query(Infirmier).filter(Infirmier.infirmier_id == infirmier_id).first()
    if not inf:
        raise HTTPException(status_code=404, detail="Infirmier introuvable")

    for field, val in data.model_dump(exclude_none=True).items():
        setattr(inf, field, val)

    db.commit()
    db.refresh(inf)
    return _infirmier_to_dict(inf)


@router.delete("/personnel/infirmiers/{infirmier_id}")
def delete_infirmier(
    infirmier_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    inf = db.query(Infirmier).filter(Infirmier.infirmier_id == infirmier_id).first()
    if not inf:
        raise HTTPException(status_code=404, detail="Infirmier introuvable")
    db.delete(inf)
    db.commit()
    return {"message": f"{inf.prenoms} {inf.nom} supprimé"}


# ═══════════════════════════════════════════════════════════════════════════════
# CONFIG IA
# ═══════════════════════════════════════════════════════════════════════════════

@router.get("/config/ia")
def get_ia_config(admin: User = Depends(get_current_admin)):
    return _ia_config


@router.put("/config/ia")
def update_ia_config(data: IAConfigUpdate, admin: User = Depends(get_current_admin)):
    for field, val in data.model_dump(exclude_none=True).items():
        _ia_config[field] = val
    return _ia_config


# ═══════════════════════════════════════════════════════════════════════════════
# ENTRAÎNEMENT
# ═══════════════════════════════════════════════════════════════════════════════

_SYMPTOMES_CACHE_PATH = "./ml_models/symptomes_cache.json"


def _fix_mojibake(s: str) -> str:
    try:
        return s.encode("latin-1").decode("utf-8")
    except (UnicodeEncodeError, UnicodeDecodeError):
        return s


def _save_symptomes_cache():
    """Sauvegarde la liste des symptômes depuis 3 sources : modèle ML, dataset CSV, règles custom."""
    all_symptomes: set = set()

    # Source 1 : features du modèle ML entraîné
    if model_manager.trainer.feature_names:
        for feat in model_manager.trainer.feature_names:
            if feat.startswith("symptom_"):
                all_symptomes.add(_fix_mojibake(feat[8:].replace("_", " ")))

    # Source 2 : colonne symptômes du dataset CSV
    dataset_path = _find_dataset()
    if dataset_path:
        try:
            import csv as _csv
            with open(dataset_path, "r", encoding="utf-8") as f:
                reader = _csv.DictReader(f)
                # La colonne symptômes peut avoir différents noms
                symp_col = None
                for col in (reader.fieldnames or []):
                    normalized = col.lower().replace("ô", "o").replace("ê", "e").replace("_", "")
                    if normalized in ("symptomesrapportes", "symptomes", "symptômes", "symptoms"):
                        symp_col = col
                        break
                if symp_col:
                    for row in reader:
                        val = row.get(symp_col, "")
                        for s in val.split(","):
                            s = s.strip()
                            if s:
                                all_symptomes.add(s)
        except Exception as e:
            logging.warning(f"[ADMIN] Lecture dataset pour cache symptômes : {e}")

    # Source 3 : règles custom (custom_disease_rules.json)
    _CUSTOM_RULES = os.path.join(".", "ml_models", "custom_disease_rules.json")
    if os.path.exists(_CUSTOM_RULES):
        try:
            with open(_CUSTOM_RULES, "r", encoding="utf-8") as f:
                rules = json.load(f)
            for rule in rules.values() if isinstance(rules, dict) else rules:
                for s in rule.get("symptomes", []):
                    if s:
                        all_symptomes.add(s.strip())
        except Exception as e:
            logging.warning(f"[ADMIN] Lecture custom_rules pour cache symptômes : {e}")

    if not all_symptomes:
        logging.warning("[ADMIN] Cache symptômes vide — aucune source disponible")
        return

    symptomes = sorted(all_symptomes)
    cache = {"symptomes": symptomes, "total": len(symptomes), "updated_at": datetime.now().isoformat()}
    os.makedirs(os.path.dirname(_SYMPTOMES_CACHE_PATH), exist_ok=True)
    with open(_SYMPTOMES_CACHE_PATH, "w", encoding="utf-8") as f:
        json.dump(cache, f, ensure_ascii=False)
    logging.info(f"[ADMIN] Cache symptômes mis à jour : {len(symptomes)} symptômes (ML + CSV + custom)")


def _run_training_task(n_estimators: int, max_depth: int):
    global _training_state
    try:
        dataset_path = _find_dataset()
        if not dataset_path:
            with _training_lock:
                _training_state.update({"status": "error", "error": "Dataset introuvable",
                                        "finished_at": datetime.now().isoformat()})
            return

        with _training_lock:
            _training_state["message"] = f"Entraînement ({n_estimators} arbres, profondeur {max_depth})…"

        results = model_manager.train_new_model(
            dataset_path=dataset_path, n_estimators=n_estimators, max_depth=max_depth, save=True)

        with _training_lock:
            if results.get("success"):
                eval_r, train_r = results.get("evaluation", {}), results.get("training", {})
                session_results = {
                    "accuracy":   round(eval_r.get("accuracy", 0) * 100, 2),
                    "precision":  round(eval_r.get("precision", 0) * 100, 2),
                    "recall":     round(eval_r.get("recall", 0) * 100, 2),
                    "f1_score":   round(eval_r.get("f1_score", 0) * 100, 2),
                    "n_samples":  train_r.get("n_samples"),
                    "n_features": train_r.get("n_features"),
                    "n_classes":  train_r.get("n_classes"),
                    "duration_s": round(train_r.get("training_duration_seconds", 0), 1),
                    "model_path": train_r.get("model_path", ""),
                }
                _training_state.update({
                    "status": "success",
                    "message": "Entraînement terminé ✓",
                    "results": session_results,
                })
                try:
                    _append_training_history({
                        "date": datetime.now().isoformat(),
                        "n_estimators": n_estimators,
                        "max_depth": max_depth,
                        **session_results,
                    })
                except Exception:
                    pass
                # Sauvegarder le cache des symptômes après chaque entraînement réussi
                try:
                    _save_symptomes_cache()
                except Exception:
                    pass
            else:
                _training_state.update({"status": "error", "error": results.get("error", "Erreur inconnue"),
                                        "message": "Entraînement échoué"})
    except Exception as exc:
        with _training_lock:
            _training_state.update({"status": "error", "error": str(exc), "message": "Erreur inattendue"})
    finally:
        with _training_lock:
            _training_state["finished_at"] = datetime.now().isoformat()


@router.post("/train")
def start_training(
    background_tasks: BackgroundTasks,
    n_estimators: int = 200,
    max_depth: int = 30,
    admin: User = Depends(get_current_admin),
):
    with _training_lock:
        if _training_state["status"] == "running":
            raise HTTPException(status_code=409, detail="Entraînement déjà en cours")

    if not _find_dataset():
        raise HTTPException(status_code=404, detail="Dataset introuvable dans 'les ressources dataset/'")

    with _training_lock:
        _training_state.update({
            "status": "running", "started_at": datetime.now().isoformat(),
            "finished_at": None, "message": "Initialisation…", "results": None, "error": None,
        })

    background_tasks.add_task(_run_training_task, n_estimators, max_depth)
    return {"message": "Entraînement démarré", "status": "running"}


@router.get("/train/status")
def get_training_status(admin: User = Depends(get_current_admin)):
    return _training_state


# ═══════════════════════════════════════════════════════════════════════════════
# NETTOYAGE & LOGS
# ═══════════════════════════════════════════════════════════════════════════════

@router.post("/cleanup/models")
def cleanup_old_models(admin: User = Depends(get_current_admin)):
    model_dir = "./ml_models/"
    removed: List[str] = []
    if not os.path.exists(model_dir):
        return {"removed": [], "message": "Dossier ml_models/ introuvable"}

    files = sorted([f for f in os.listdir(model_dir) if f.endswith(".joblib")], reverse=True)
    for fname in files[1:]:
        fpath = os.path.join(model_dir, fname)
        try:
            os.remove(fpath); removed.append(fname)
        except OSError:
            pass
        meta = fpath.replace(".joblib", "_metadata.json")
        if os.path.exists(meta):
            try:
                os.remove(meta); removed.append(os.path.basename(meta))
            except OSError:
                pass

    nb = len([f for f in removed if f.endswith(".joblib")])
    return {"removed": removed, "count": nb, "message": f"{nb} modèle(s) supprimé(s)"}


@router.get("/models/download/{filename}")
def download_model(filename: str, admin: User = Depends(get_current_admin)):
    # Sécurité : nom de fichier strict, pas de traversée de répertoire
    if not filename.endswith(".joblib") or "/" in filename or "\\" in filename or ".." in filename:
        raise HTTPException(status_code=400, detail="Nom de fichier invalide")
    fpath = os.path.join("./ml_models", filename)
    if not os.path.exists(fpath):
        raise HTTPException(status_code=404, detail=f"Fichier '{filename}' introuvable")
    return FileResponse(
        path=fpath,
        filename=filename,
        media_type="application/octet-stream",
    )


@router.post("/cleanup/logs")
def cleanup_logs(admin: User = Depends(get_current_admin)):
    log_file = "./logs/app.log"
    if not os.path.exists(log_file):
        return {"message": "Fichier de log introuvable", "done": False}
    try:
        # Fermer les handlers existants pour libérer le fichier (important sur Windows)
        for handler in logging.root.handlers[:]:
            if isinstance(handler, logging.FileHandler):
                handler.close()
                logging.root.removeHandler(handler)
        
        # Vider le fichier
        with open(log_file, "w", encoding="utf-8") as f:
            f.write(f"--- Logs réinitialisés le {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ---\n")
        
        # Réinitialiser le logging
        from ..utils.logger import setup_logging
        from ..config import settings
        setup_logging(log_level=settings.LOG_LEVEL, log_file=settings.LOG_FILE)
        
        logger = logging.getLogger(__name__)
        logger.info("♻️ Système de logs réinitialisé après nettoyage")
        
        return {"message": "Logs vidés et système de logging redémarré", "done": True}
    except Exception as exc:
        # Tenter de restaurer le logging en cas d'erreur
        try:
            from ..utils.logger import setup_logging
            from ..config import settings
            setup_logging(log_level=settings.LOG_LEVEL, log_file=settings.LOG_FILE)
        except:
            pass
        raise HTTPException(status_code=500, detail=str(exc))


# ═══════════════════════════════════════════════════════════════════════════════
# PERFORMANCES DU MODÈLE & FEATURE IMPORTANCE
# ═══════════════════════════════════════════════════════════════════════════════

@router.get("/model/performance")
def get_model_performance(admin: User = Depends(get_current_admin)):
    """Retourne les métriques du modèle chargé et le top feature importance."""
    if not model_manager.model_loaded:
        return {"available": False, "message": "Aucun modèle chargé"}

    feature_importance: Dict = {"features": [], "importances": []}
    try:
        feature_importance = model_manager.trainer.get_feature_importance(top_n=20)
    except Exception:
        pass

    # Métriques : priorité à l'état d'entraînement courant, sinon métadonnées du fichier
    metrics: Dict = {}
    if _training_state.get("results"):
        metrics = dict(_training_state["results"])
    elif model_manager.model_metadata:
        meta = model_manager.model_metadata
        # training_history peut contenir accuracy / precision / recall directement
        metrics = {
            "accuracy":   round(float(meta.get("accuracy", 0)) * 100, 2),
            "precision":  round(float(meta.get("precision", 0)) * 100, 2),
            "recall":     round(float(meta.get("recall", 0)) * 100, 2),
            "f1_score":   round(float(meta.get("f1_score", 0)) * 100, 2),
            "n_samples":  meta.get("n_samples"),
            "n_features": meta.get("n_features"),
            "n_classes":  meta.get("n_classes"),
        }

    return {
        "available": True,
        "model_version": model_manager.model_version,
        "metrics": metrics,
        "feature_importance": feature_importance,
    }


# ═══════════════════════════════════════════════════════════════════════════════
# STATISTIQUES D'UTILISATION DE L'IA
# ═══════════════════════════════════════════════════════════════════════════════

@router.get("/ai-stats")
def get_ai_usage_stats(
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    """Statistiques d'utilisation de l'IA depuis la table historique_prediction."""
    from ..models.prediction_history import PredictionHistory
    from sqlalchemy import func

    total = db.query(func.count(PredictionHistory.id)).scalar() or 0

    avg_conf_raw = db.query(func.avg(PredictionHistory.confidence)).scalar()
    avg_conf_pct = round(float(avg_conf_raw) * 100, 1) if avg_conf_raw else 0.0

    def _count_level(level: str) -> int:
        return db.query(func.count(PredictionHistory.id)).filter(
            PredictionHistory.confidence_level == level
        ).scalar() or 0

    high   = _count_level("HIGH")
    medium = _count_level("MEDIUM")
    low    = _count_level("LOW")

    top_diseases_rows = (
        db.query(
            PredictionHistory.predicted_disease,
            func.count(PredictionHistory.id).label("cnt"),
        )
        .group_by(PredictionHistory.predicted_disease)
        .order_by(func.count(PredictionHistory.id).desc())
        .limit(5)
        .all()
    )

    return {
        "total_predictions": total,
        "avg_confidence_pct": avg_conf_pct,
        "confidence_distribution": {"HIGH": high, "MEDIUM": medium, "LOW": low},
        "top_diseases": [{"disease": r[0], "count": r[1]} for r in top_diseases_rows],
    }


# ═══════════════════════════════════════════════════════════════════════════════
# HISTORIQUE DES ENTRAÎNEMENTS
# ═══════════════════════════════════════════════════════════════════════════════

@router.get("/training/history")
def get_training_history_endpoint(admin: User = Depends(get_current_admin)):
    """Retourne l'historique des sessions d'entraînement (fichier JSON persistant)."""
    sessions = _load_training_history()
    # Compléter avec la session courante si pas encore sauvegardée
    if _training_state.get("status") == "success" and _training_state.get("results"):
        current = {
            "date": _training_state.get("finished_at"),
            "n_estimators": _ia_config.get("n_estimators", "—"),
            "max_depth": _ia_config.get("max_depth", "—"),
            **_training_state["results"],
        }
        if not sessions or sessions[-1].get("model_path") != current.get("model_path"):
            sessions = sessions + [current]
    return {"sessions": list(reversed(sessions))}  # Plus récent en premier


@router.get("/logs")
def get_logs(lines: int = 150, admin: User = Depends(get_current_admin)):
    log_file = "./logs/app.log"
    if not os.path.exists(log_file):
        return {"lines": [], "total": 0, "exists": False}
    try:
        with open(log_file, "r", encoding="utf-8", errors="replace") as f:
            all_lines = f.readlines()
        tail = all_lines[-lines:] if len(all_lines) > lines else all_lines
        return {"lines": [l.rstrip() for l in tail], "total": len(all_lines), "exists": True}
    except OSError as exc:
        return {"lines": [], "total": 0, "exists": False, "error": str(exc)}


# ─── Ajout d'une nouvelle maladie dans le dataset ─────────────────────────────

CATEGORIES_MEDICALES = [
    "Infectieuses", "Cardiovasculaires", "Respiratoires", "Gastro-intestinales",
    "Endocriniennes / Métaboliques", "Hépatiques", "Neurologiques", "Rhumatologiques",
    "Dermatologiques", "Ophtalmologiques", "Hématologiques", "Rénales / Urinaires", "Autres",
]

_DATASET_CANDIDATES_ADMIN = [
    os.path.join("..", "les ressources dataset", "dataset_medical_robust_enhanced.csv"),
    os.path.join("..", "..", "les ressources dataset", "dataset_medical_robust_enhanced.csv"),
    os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))),
        "les ressources dataset", "dataset_medical_robust_enhanced.csv",
    ),
]
DATASET_PATH = next((p for p in _DATASET_CANDIDATES_ADMIN if os.path.exists(p)), None)


class NouvellesMaladieRequest(BaseModel):
    nom_maladie: str = Field(..., min_length=2, max_length=100)
    categorie: str
    symptomes: List[str] = Field(..., min_length=1)
    n_cas: int = Field(default=80, ge=20, le=300)
    reentrainer: bool = Field(default=False, description="Lancer le réentraînement aussitôt après l'ajout")


def _valider_symptomes_saisis(symptomes: List[str]) -> List[str]:
    """
    Valide et nettoie une liste de symptômes saisis par l'admin.
    Bloque les entrées parasites (vides, purement numériques, caractères répétés
    anormaux type 'rororor'/'dedededeeded', absence de voyelle) qui pollueraient
    définitivement le modèle en créant des features symptom_* parasites.
    Retourne la liste nettoyée (espaces normalisés, doublons retirés).
    """
    import re

    propres: List[str] = []
    vus = set()
    for s in symptomes:
        nom = " ".join(str(s).strip().split())  # normalise les espaces
        if not nom:
            continue
        bas = nom.lower()
        if bas in vus:
            continue
        # Refus : trop court
        if len(nom) < 3:
            raise HTTPException(status_code=400, detail=f"Symptôme trop court : '{nom}'")
        # Refus : purement numérique
        if re.fullmatch(r"[\d\s.,/-]+", nom):
            raise HTTPException(status_code=400, detail=f"Symptôme invalide (numérique) : '{nom}'")
        # Refus : aucune voyelle (mot non prononçable, ex. 'qsdfg')
        if not re.search(r"[aeiouyàâäéèêëîïôöùûü]", bas):
            raise HTTPException(status_code=400, detail=f"Symptôme invalide (non prononçable) : '{nom}'")
        # Refus : même caractère répété 3+ fois d'affilée (ex. 'aaaa')
        if re.search(r"(.)\1{2,}", bas):
            raise HTTPException(status_code=400, detail=f"Symptôme invalide (caractères répétés) : '{nom}'")
        # Refus : motif court (1-3 lettres) répété 3+ fois n'importe où
        # (ex. 'rororor' = 'ro'×, 'dedededeeded' = 'de'×, 'ababab')
        sans_espace = bas.replace(" ", "")
        if re.search(r"(.{1,3})\1{2,}", sans_espace):
            raise HTTPException(status_code=400, detail=f"Symptôme invalide (motif répété) : '{nom}'")
        propres.append(nom)
        vus.add(bas)

    if not propres:
        raise HTTPException(status_code=400, detail="Aucun symptôme valide fourni.")
    return propres


def _generer_cas_synthetiques(nom_maladie: str, symptomes: List[str], n_cas: int) -> List[List]:
    """Génère n_cas lignes CSV synthétiques pour une nouvelle maladie."""
    import random
    import csv

    # Lire le CSV pour connaître les colonnes et l'ID courant
    with open(DATASET_PATH, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        headers = next(reader)
        rows = list(reader)

    n_existant = len(rows)
    colonnes_vitaux = [h for h in headers if h.startswith("Vital_")]
    colonnes_labs   = [h for h in headers if h.startswith("Lab_")]

    # Valeurs normales moyennes pour les vitaux (mu, sigma)
    vitaux_normaux = {
        "Vital_Tension Systolique (mmHg)":       (120.0, 15.0),
        "Vital_Tension Diastolique (mmHg)":      (80.0,  10.0),
        "Vital_Fréquence Cardiaque (bpm)":       (75.0,  12.0),
        "Vital_Fréquence Respiratoire (resp/min)":(16.0, 3.0),
        "Vital_Température (°C)":                (37.0,  0.5),
        "Vital_Saturation O2 (%)":               (97.5,  1.5),
        "Vital_IMC (kg/m²)":                     (24.0,  4.0),
    }
    # Valeurs normales moyennes pour les labs (mu, sigma)
    labs_normaux = {
        "Lab_Hémoglobine (g/dL)":              (14.0, 1.5),
        "Lab_Hématocrite (%)":                 (42.0, 4.0),
        "Lab_Globules Rouges (M/µL)":          (4.8,  0.5),
        "Lab_Globules Blancs (K/µL)":          (7.5,  2.0),
        "Lab_Neutrophiles (%)":                (60.0, 8.0),
        "Lab_Lymphocytes (%)":                 (30.0, 6.0),
        "Lab_Monocytes (%)":                   (6.0,  1.5),
        "Lab_Eosinophiles (%)":                (2.5,  1.0),
        "Lab_Basophiles (%)":                  (0.5,  0.2),
        "Lab_Plaquettes (K/µL)":               (250.0,50.0),
        "Lab_VGM (fL)":                        (88.0, 6.0),
        "Lab_CCMH (g/dL)":                     (34.0, 1.5),
        "Lab_Glucose (mg/dL)":                 (95.0, 15.0),
        "Lab_Glucose à jeun (mg/dL)":          (92.0, 12.0),
        "Lab_Glucose post-prandial (mg/dL)":   (120.0,20.0),
        "Lab_HbA1c (%)":                       (5.4,  0.4),
        "Lab_Cholestérol total (mg/dL)":       (185.0,30.0),
        "Lab_Cholestérol HDL (mg/dL)":         (50.0, 10.0),
        "Lab_Cholestérol LDL (mg/dL)":         (110.0,25.0),
        "Lab_Triglycérides (mg/dL)":           (130.0,40.0),
        "Lab_Acide urique (mg/dL)":            (5.5,  1.2),
        "Lab_Créatinine (mg/dL)":              (1.0,  0.2),
        "Lab_Urée (mg/dL)":                    (30.0, 8.0),
        "Lab_TFG (mL/min/1.73m²)":             (90.0, 15.0),
        "Lab_Sodium (mEq/L)":                  (140.0,3.0),
        "Lab_Potassium (mEq/L)":               (4.2,  0.4),
        "Lab_Chlore (mEq/L)":                  (102.0,4.0),
        "Lab_Calcium (mg/dL)":                 (9.5,  0.6),
        "Lab_Phosphore (mg/dL)":               (3.5,  0.5),
        "Lab_Magnésium (mg/dL)":               (2.0,  0.3),
        "Lab_ALT/SGPT (U/L)":                  (25.0, 10.0),
        "Lab_AST/SGOT (U/L)":                  (22.0, 8.0),
        "Lab_Bilirubine totale (mg/dL)":       (0.7,  0.3),
        "Lab_Bilirubine conjuguée (mg/dL)":    (0.15, 0.05),
        "Lab_Bilirubine non-conjuguée (mg/dL)":(0.55, 0.25),
        "Lab_Phosphatase alcaline (U/L)":      (75.0, 20.0),
        "Lab_GGT (U/L)":                       (25.0, 10.0),
        "Lab_Albumine (g/dL)":                 (4.2,  0.4),
        "Lab_Protéine totale (g/dL)":          (7.2,  0.6),
        "Lab_Globulines (g/dL)":               (2.8,  0.4),
        "Lab_Ratio A/G":                       (1.6,  0.2),
        "Lab_CK (U/L)":                        (100.0,40.0),
        "Lab_Myoglobine (ng/mL)":              (50.0, 20.0),
        "Lab_Troponine (ng/mL)":               (0.02, 0.01),
        "Lab_BNP (pg/mL)":                     (50.0, 20.0),
        "Lab_ProBNP (pg/mL)":                  (120.0,50.0),
        "Lab_PT/INR":                          (1.05, 0.1),
        "Lab_aPTT (sec)":                      (30.0, 4.0),
        "Lab_TT (sec)":                        (14.0, 2.0),
        "Lab_Fibrinogène (mg/dL)":             (300.0,60.0),
        "Lab_CRP (mg/L)":                      (2.0,  2.0),
        "Lab_ESR (mm/h)":                      (15.0, 8.0),
        "Lab_PSA (ng/mL)":                     (1.0,  0.5),
        "Lab_BAAR (résultat)":                 (0.0,  0.0),
        "Lab_Culture Mycobactéries (résultat)":(0.0,  0.0),
        "Lab_Test Xpert MTB/RIF (résultat)":   (0.0,  0.0),
    }

    groupes = {"0-14": (0, 14), "15-24": (15, 24), "25-44": (25, 44),
               "45-64": (45, 64), "65+": (65, 90)}

    nouveaux_cas = []
    for i in range(n_cas):
        idx = n_existant + i + 1
        cas_id = f"CAS_{idx:07d}"

        sexe = random.choice(["M", "F"])
        age  = random.randint(10, 85)
        groupe_age = next((g for g, (lo, hi) in groupes.items() if lo <= age <= hi), "45-64")
        severite = random.choices(["Légère", "Modérée", "Sévère"], weights=[30, 50, 20])[0]
        duree = random.randint(1, 21)
        date_c = f"202{random.randint(4,5)}-{random.randint(1,12):02d}-{random.randint(1,28):02d}"

        # Symptômes : prend 60-100% de la liste fournie + éventuellement 0-2 symptômes supplémentaires
        k = max(1, int(len(symptomes) * random.uniform(0.6, 1.0)))
        symptomes_cas = random.sample(symptomes, k)
        symptomes_str = ", ".join(symptomes_cas)

        row = {
            "ID": cas_id,
            "Maladie_Diagnostic": nom_maladie,
            "Symptomes_Rapportes": symptomes_str,
            "Sexe": sexe,
            "Age": age,
            "Groupe_Age": groupe_age,
            "Severite": severite,
            "Duree_Symptomes_Jours": duree,
            "Date_Consultation": date_c,
            "Antecedents_Medicaux": "Aucun",
            "Medicaments_Actuels": "Aucun",
        }

        # Labs/Vitaux : valeurs NEUTRES constantes (= moyenne normale, sigma 0).
        # Le modèle est entraîné uniquement sur les symptômes ; générer des
        # labs/vitaux aléatoires n'apportait que du bruit (cf. règle d'entraînement).
        # On met la valeur normale moyenne, identique pour tous les cas, ce qui rend
        # ces colonnes non-discriminantes plutôt que bruitées.
        for col in colonnes_vitaux:
            mu, _ = vitaux_normaux.get(col, (50.0, 5.0))
            row[col] = mu

        for col in colonnes_labs:
            mu, _ = labs_normaux.get(col, (10.0, 2.0))
            row[col] = mu

        nouveaux_cas.append([row.get(h, "") for h in headers])

    return nouveaux_cas, headers


@router.post("/dataset/add-disease")
def add_disease_to_dataset(
    payload: NouvellesMaladieRequest,
    background_tasks: BackgroundTasks,
    n_estimators: int = 300,
    max_depth: int = 0,
    admin: User = Depends(get_current_admin),
):
    """
    Ajoute une nouvelle maladie au dataset d'entraînement en générant des cas synthétiques.
    """
    import csv

    if not DATASET_PATH or not os.path.exists(DATASET_PATH):
        raise HTTPException(status_code=404, detail=f"Dataset introuvable. Chemins testés : {_DATASET_CANDIDATES_ADMIN}")

    if payload.categorie not in CATEGORIES_MEDICALES:
        raise HTTPException(status_code=400, detail=f"Catégorie invalide. Choisir parmi : {CATEGORIES_MEDICALES}")

    # Vérifier si la maladie existe déjà
    with open(DATASET_PATH, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        next(reader)  # skip header
        maladies_existantes = {row[1].strip().lower() for row in reader if row}

    if payload.nom_maladie.strip().lower() in maladies_existantes:
        raise HTTPException(
            status_code=409,
            detail=f"La maladie '{payload.nom_maladie}' existe déjà dans le dataset."
        )

    # Valider/nettoyer les symptômes avant toute écriture (bloque les parasites)
    symptomes_propres = _valider_symptomes_saisis(payload.symptomes)

    try:
        nouveaux_cas, headers = _generer_cas_synthetiques(
            payload.nom_maladie, symptomes_propres, payload.n_cas
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur génération des cas : {str(e)}")

    # Compter total avant
    with open(DATASET_PATH, "r", encoding="utf-8") as f:
        total_avant = sum(1 for _ in f) - 1  # -1 pour l'en-tête

    # Appendre au CSV
    with open(DATASET_PATH, "a", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(nouveaux_cas)

    # ── Générer et sauvegarder les synonymes automatiques pour cette maladie ──
    try:
        _SYNONYMES_CACHE_PATH_JSON = os.path.join(".", "ml_models", "custom_synonymes.json")
        custom_syn: dict = {}
        if os.path.exists(_SYNONYMES_CACHE_PATH_JSON):
            with open(_SYNONYMES_CACHE_PATH_JSON, "r", encoding="utf-8") as f:
                custom_syn = json.load(f)

        PATTERNS_AUTO = {
            "fièvre":       ["corps chaud", "chaud", "température", "avoir de la fièvre"],
            "toux":         ["tousser", "toux sèche", "toux grasse"],
            "dyspnée":      ["mal à respirer", "essoufflement", "manque d'air"],
            "céphalées":    ["mal de tête", "maux de tête", "mal à la tête"],
            "nausées":      ["nausée", "envie de vomir", "mal au coeur"],
            "vomissements": ["vomir", "vomi"],
            "diarrhée":     ["selles liquides", "ventre qui dérange"],
            "douleurs abdominales": ["mal au ventre", "ventre qui fait mal"],
            "fatigue":      ["très fatigué", "épuisé", "sans énergie"],
            "arthralgie":   ["mal aux articulations", "rhumatisme"],
            "prurit":       ["démangeaisons", "ça gratte", "peau qui gratte"],
            "éruption":     ["boutons", "rash", "plaques rouges"],
        }
        for symptome in symptomes_propres:
            s_lower = symptome.lower()
            for terme, variantes in PATTERNS_AUTO.items():
                if terme in s_lower:
                    for var in variantes:
                        if var not in custom_syn:
                            custom_syn[var] = symptome

        with open(_SYNONYMES_CACHE_PATH_JSON, "w", encoding="utf-8") as f:
            json.dump(custom_syn, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logging.warning(f"[ADMIN] Synonymes auto non générés: {e}")

    # ── Sauvegarder les règles cliniques dynamiques ───────────────────────────
    _CUSTOM_RULES_PATH = os.path.join(".", "ml_models", "custom_disease_rules.json")
    try:
        existing_rules: dict = {}
        if os.path.exists(_CUSTOM_RULES_PATH):
            with open(_CUSTOM_RULES_PATH, "r", encoding="utf-8") as f:
                existing_rules = json.load(f)

        # Normaliser les symptômes en minuscules pour la correspondance
        existing_rules[payload.nom_maladie] = {
            "symptomes_boost": symptomes_propres,
            "boost_factor": 4.0,
            "min_symptomes_match": max(1, len(symptomes_propres) // 3),
        }
        os.makedirs(os.path.dirname(_CUSTOM_RULES_PATH), exist_ok=True)
        with open(_CUSTOM_RULES_PATH, "w", encoding="utf-8") as f:
            json.dump(existing_rules, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logging.warning(f"[ADMIN] Impossible de sauvegarder les règles cliniques: {e}")

    logging.info(
        f"[ADMIN] Nouvelle maladie ajoutée au dataset : '{payload.nom_maladie}' "
        f"({payload.n_cas} cas, catégorie: {payload.categorie}) par {admin.email}"
    )

    # Réentraînement immédiat optionnel — le modèle est un singleton global, donc
    # train_new_model recharge automatiquement le predictor en mémoire à la fin.
    reentrainement_lance = False
    if payload.reentrainer:
        with _training_lock:
            if _training_state["status"] == "running":
                raise HTTPException(status_code=409, detail="Un entraînement est déjà en cours. Réessayez après.")
            _training_state.update({
                "status": "running", "started_at": datetime.now().isoformat(),
                "finished_at": None, "message": "Initialisation…", "results": None, "error": None,
            })
        depth = None if max_depth in (0, None) else max_depth
        background_tasks.add_task(_run_training_task, n_estimators, depth)
        reentrainement_lance = True

    message = f"{payload.n_cas} cas synthétiques ajoutés pour '{payload.nom_maladie}'."
    if reentrainement_lance:
        message += " Réentraînement lancé — suivez l'état via /admin/train/status."
    else:
        message += " Relancez l'entraînement pour activer la détection."

    return {
        "success": True,
        "maladie": payload.nom_maladie,
        "categorie": payload.categorie,
        "cas_ajoutes": payload.n_cas,
        "total_dataset": total_avant + payload.n_cas,
        "reentrainement_lance": reentrainement_lance,
        "message": message,
    }


@router.delete("/dataset/maladies/{nom_maladie}")
def delete_disease_from_dataset(nom_maladie: str, admin: User = Depends(get_current_admin)):
    """
    Supprime toutes les lignes d'une maladie du dataset (réécriture du CSV) et
    retire ses règles cliniques custom. Il faut ensuite relancer l'entraînement
    pour que la classe disparaisse réellement du modèle.
    """
    import csv

    if not DATASET_PATH or not os.path.exists(DATASET_PATH):
        raise HTTPException(status_code=404, detail="Dataset introuvable.")

    cible = nom_maladie.strip().lower()

    with open(DATASET_PATH, "r", encoding="utf-8", newline="") as f:
        reader = csv.reader(f)
        headers = next(reader)
        rows = list(reader)

    # Index de la colonne maladie (normalement 1 = Maladie_Diagnostic)
    try:
        idx_maladie = headers.index("Maladie_Diagnostic")
    except ValueError:
        idx_maladie = 1

    restantes = [r for r in rows if r and r[idx_maladie].strip().lower() != cible]
    supprimees = len(rows) - len(restantes)

    if supprimees == 0:
        raise HTTPException(status_code=404, detail=f"Maladie '{nom_maladie}' introuvable dans le dataset.")

    with open(DATASET_PATH, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(restantes)

    # Retirer les règles cliniques custom de cette maladie, si présentes
    _CUSTOM_RULES_PATH = os.path.join(".", "ml_models", "custom_disease_rules.json")
    try:
        if os.path.exists(_CUSTOM_RULES_PATH):
            with open(_CUSTOM_RULES_PATH, "r", encoding="utf-8") as f:
                rules = json.load(f)
            removed = None
            for k in list(rules.keys()):
                if k.strip().lower() == cible:
                    removed = rules.pop(k)
            if removed is not None:
                with open(_CUSTOM_RULES_PATH, "w", encoding="utf-8") as f:
                    json.dump(rules, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logging.warning(f"[ADMIN] Règles custom non nettoyées pour '{nom_maladie}': {e}")

    logging.info(f"[ADMIN] Maladie supprimée du dataset : '{nom_maladie}' ({supprimees} cas) par {admin.email}")

    return {
        "success": True,
        "maladie": nom_maladie,
        "cas_supprimes": supprimees,
        "total_restant": len(restantes),
        "message": f"{supprimees} cas supprimés. Relancez l'entraînement pour retirer la maladie du modèle.",
    }


@router.post("/symptomes/refresh")
def refresh_symptomes_cache(admin: User = Depends(get_current_admin)):
    """Force la mise à jour du cache des symptômes (sans réentraîner)."""
    try:
        _save_symptomes_cache()
        cache_size = 0
        if os.path.exists(_SYMPTOMES_CACHE_PATH):
            with open(_SYMPTOMES_CACHE_PATH, encoding="utf-8") as f:
                cache_size = len(json.load(f).get("symptomes", []))
        return {"success": True, "total": cache_size, "message": f"Cache mis à jour : {cache_size} symptômes"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/dataset/maladies")
def list_maladies_dataset(admin: User = Depends(get_current_admin)):
    """Retourne la liste des maladies présentes dans le dataset avec leur nombre de cas."""
    import csv
    from collections import Counter

    if not DATASET_PATH or not os.path.exists(DATASET_PATH):
        raise HTTPException(status_code=404, detail="Dataset introuvable.")

    with open(DATASET_PATH, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        next(reader)
        compteur = Counter(row[1].strip() for row in reader if row)

    return {
        "total_maladies": len(compteur),
        "total_cas": sum(compteur.values()),
        "maladies": sorted(
            [{"nom": m, "cas": c} for m, c in compteur.items()],
            key=lambda x: x["cas"], reverse=True
        ),
    }


# ─── Détail des symptômes d'une maladie dans le dataset ──────────────────────

@router.get("/dataset/maladies/{nom_maladie}")
def get_maladie_details(nom_maladie: str, admin: User = Depends(get_current_admin)):
    """Retourne les symptômes distincts d'une maladie et son nombre de cas."""
    import csv
    from collections import Counter
    import urllib.parse

    nom_decode = urllib.parse.unquote(nom_maladie).strip()

    if not DATASET_PATH or not os.path.exists(DATASET_PATH):
        raise HTTPException(status_code=404, detail="Dataset introuvable.")

    symptomes_counter: Counter = Counter()
    n_cas = 0

    with open(DATASET_PATH, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get("Maladie_Diagnostic", "").strip().lower() == nom_decode.lower():
                n_cas += 1
                for s in row.get("Symptomes_Rapportes", "").split(","):
                    s = s.strip()
                    if s:
                        symptomes_counter[s] += 1

    if n_cas == 0:
        raise HTTPException(status_code=404, detail=f"Maladie '{nom_decode}' introuvable dans le dataset.")

    symptomes_tries = sorted(symptomes_counter.items(), key=lambda x: -x[1])

    # Règles cliniques custom si elles existent
    custom_rules: dict = {}
    _CUSTOM_RULES_PATH = os.path.join(".", "ml_models", "custom_disease_rules.json")
    if os.path.exists(_CUSTOM_RULES_PATH):
        try:
            with open(_CUSTOM_RULES_PATH, "r", encoding="utf-8") as f:
                all_rules = json.load(f)
                custom_rules = all_rules.get(nom_decode, {})
        except Exception:
            pass

    return {
        "nom": nom_decode,
        "n_cas": n_cas,
        "symptomes": [{"nom": s, "frequence": c} for s, c in symptomes_tries],
        "custom_rules": custom_rules,
    }


# ─── Mise à jour d'une maladie existante dans le dataset ─────────────────────

class UpdateMaladieRequest(BaseModel):
    symptomes: List[str] = Field(..., min_length=1)
    n_cas_supplementaires: int = Field(default=0, ge=0, le=300)
    remplacer_cas_existants: bool = Field(default=False)
    boost_factor: Optional[float] = Field(default=None, ge=1.0, le=10.0)


@router.put("/dataset/update-disease/{nom_maladie}")
def update_disease_in_dataset(
    nom_maladie: str,
    payload: UpdateMaladieRequest,
    admin: User = Depends(get_current_admin),
):
    """
    Met à jour une maladie existante dans le dataset :
    - Met à jour ses règles cliniques (symptômes boost)
    - Optionnellement ajoute des cas supplémentaires avec les nouveaux symptômes
    - Optionnellement remplace les cas existants par de nouveaux cas générés
    """
    import csv
    import urllib.parse

    nom_decode = urllib.parse.unquote(nom_maladie).strip()

    if not DATASET_PATH or not os.path.exists(DATASET_PATH):
        raise HTTPException(status_code=404, detail="Dataset introuvable.")

    # Vérifier que la maladie existe
    with open(DATASET_PATH, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        headers = next(reader)
        rows = list(reader)

    maladies_existantes = {row[1].strip().lower() for row in rows if row}
    if nom_decode.strip().lower() not in maladies_existantes:
        raise HTTPException(status_code=404, detail=f"Maladie '{nom_decode}' introuvable dans le dataset.")

    cas_avant = sum(1 for row in rows if row and row[1].strip().lower() == nom_decode.strip().lower())
    cas_supprimes = 0
    nouvelles_lignes = []

    if payload.remplacer_cas_existants:
        # Filtrer les cas de cette maladie (les supprimer)
        nouvelles_lignes = [row for row in rows if not (row and row[1].strip().lower() == nom_decode.strip().lower())]
        cas_supprimes = len(rows) - len(nouvelles_lignes)
    else:
        nouvelles_lignes = rows

    # Générer des cas supplémentaires si demandé
    cas_ajoutes = 0
    if payload.n_cas_supplementaires > 0 or payload.remplacer_cas_existants:
        n_gen = payload.n_cas_supplementaires if not payload.remplacer_cas_existants else max(cas_avant, payload.n_cas_supplementaires or cas_avant)
        if n_gen > 0:
            try:
                # Réutiliser la logique de génération avec le dataset temporairement sans les cas supprimés
                import tempfile, io, random
                vitaux_normaux = {
                    "Vital_Tension Systolique (mmHg)": (120.0, 15.0),
                    "Vital_Tension Diastolique (mmHg)": (80.0, 10.0),
                    "Vital_Fréquence Cardiaque (bpm)": (75.0, 12.0),
                    "Vital_Fréquence Respiratoire (resp/min)": (16.0, 3.0),
                    "Vital_Température (°C)": (37.0, 0.5),
                    "Vital_Saturation O2 (%)": (97.5, 1.5),
                    "Vital_IMC (kg/m²)": (24.0, 4.0),
                }
                labs_normaux = {
                    "Lab_Hémoglobine (g/dL)": (14.0, 1.5), "Lab_Hématocrite (%)": (42.0, 4.0),
                    "Lab_Globules Rouges (M/µL)": (4.8, 0.5), "Lab_Globules Blancs (K/µL)": (7.5, 2.0),
                    "Lab_Neutrophiles (%)": (60.0, 8.0), "Lab_Lymphocytes (%)": (30.0, 6.0),
                    "Lab_Monocytes (%)": (6.0, 1.5), "Lab_Eosinophiles (%)": (2.5, 1.0),
                    "Lab_Basophiles (%)": (0.5, 0.2), "Lab_Plaquettes (K/µL)": (250.0, 50.0),
                    "Lab_VGM (fL)": (88.0, 6.0), "Lab_CCMH (g/dL)": (34.0, 1.5),
                    "Lab_Glucose (mg/dL)": (95.0, 15.0), "Lab_Glucose à jeun (mg/dL)": (92.0, 12.0),
                    "Lab_Glucose post-prandial (mg/dL)": (120.0, 20.0), "Lab_HbA1c (%)": (5.4, 0.4),
                    "Lab_Cholestérol total (mg/dL)": (185.0, 30.0), "Lab_Cholestérol HDL (mg/dL)": (50.0, 10.0),
                    "Lab_Cholestérol LDL (mg/dL)": (110.0, 25.0), "Lab_Triglycérides (mg/dL)": (130.0, 40.0),
                    "Lab_Acide urique (mg/dL)": (5.5, 1.2), "Lab_Créatinine (mg/dL)": (1.0, 0.2),
                    "Lab_Urée (mg/dL)": (30.0, 8.0), "Lab_TFG (mL/min/1.73m²)": (90.0, 15.0),
                    "Lab_Sodium (mEq/L)": (140.0, 3.0), "Lab_Potassium (mEq/L)": (4.2, 0.4),
                    "Lab_Chlore (mEq/L)": (102.0, 4.0), "Lab_Calcium (mg/dL)": (9.5, 0.6),
                    "Lab_Phosphore (mg/dL)": (3.5, 0.5), "Lab_Magnésium (mg/dL)": (2.0, 0.3),
                    "Lab_ALT/SGPT (U/L)": (25.0, 10.0), "Lab_AST/SGOT (U/L)": (22.0, 8.0),
                    "Lab_Bilirubine totale (mg/dL)": (0.7, 0.3), "Lab_Bilirubine conjuguée (mg/dL)": (0.15, 0.05),
                    "Lab_Bilirubine non-conjuguée (mg/dL)": (0.55, 0.25), "Lab_Phosphatase alcaline (U/L)": (75.0, 20.0),
                    "Lab_GGT (U/L)": (25.0, 10.0), "Lab_Albumine (g/dL)": (4.2, 0.4),
                    "Lab_Protéine totale (g/dL)": (7.2, 0.6), "Lab_Globulines (g/dL)": (2.8, 0.4),
                    "Lab_Ratio A/G": (1.6, 0.2), "Lab_CK (U/L)": (100.0, 40.0),
                    "Lab_Myoglobine (ng/mL)": (50.0, 20.0), "Lab_Troponine (ng/mL)": (0.02, 0.01),
                    "Lab_BNP (pg/mL)": (50.0, 20.0), "Lab_ProBNP (pg/mL)": (120.0, 50.0),
                    "Lab_PT/INR": (1.05, 0.1), "Lab_aPTT (sec)": (30.0, 4.0),
                    "Lab_TT (sec)": (14.0, 2.0), "Lab_Fibrinogène (mg/dL)": (300.0, 60.0),
                    "Lab_CRP (mg/L)": (2.0, 2.0), "Lab_ESR (mm/h)": (15.0, 8.0),
                    "Lab_PSA (ng/mL)": (1.0, 0.5), "Lab_BAAR (résultat)": (0.0, 0.0),
                    "Lab_Culture Mycobactéries (résultat)": (0.0, 0.0), "Lab_Test Xpert MTB/RIF (résultat)": (0.0, 0.0),
                }
                colonnes_vitaux = [h for h in headers if h.startswith("Vital_")]
                colonnes_labs = [h for h in headers if h.startswith("Lab_")]
                groupes = {"0-14": (0, 14), "15-24": (15, 24), "25-44": (25, 44), "45-64": (45, 64), "65+": (65, 90)}
                n_existant = len(nouvelles_lignes)

                for i in range(n_gen):
                    idx = n_existant + i + 1
                    cas_id = f"CAS_{idx:07d}"
                    sexe = random.choice(["M", "F"])
                    age = random.randint(10, 85)
                    groupe_age = next((g for g, (lo, hi) in groupes.items() if lo <= age <= hi), "45-64")
                    severite = random.choices(["Légère", "Modérée", "Sévère"], weights=[30, 50, 20])[0]
                    duree = random.randint(1, 21)
                    date_c = f"202{random.randint(4,5)}-{random.randint(1,12):02d}-{random.randint(1,28):02d}"
                    k = max(1, int(len(payload.symptomes) * random.uniform(0.6, 1.0)))
                    symptomes_cas = random.sample(payload.symptomes, k)
                    row_dict = {
                        "ID": cas_id, "Maladie_Diagnostic": nom_decode,
                        "Symptomes_Rapportes": ", ".join(symptomes_cas),
                        "Sexe": sexe, "Age": age, "Groupe_Age": groupe_age,
                        "Severite": severite, "Duree_Symptomes_Jours": duree,
                        "Date_Consultation": date_c, "Antecedents_Medicaux": "Aucun",
                        "Medicaments_Actuels": "Aucun",
                    }
                    for col in colonnes_vitaux:
                        mu, sigma = vitaux_normaux.get(col, (50.0, 5.0))
                        row_dict[col] = round(random.gauss(mu, sigma), 2)
                    for col in colonnes_labs:
                        mu, sigma = labs_normaux.get(col, (10.0, 2.0))
                        row_dict[col] = max(0.0, round(random.gauss(mu, sigma), 3))
                    nouvelles_lignes.append([row_dict.get(h, "") for h in headers])
                    cas_ajoutes += 1
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Erreur génération des cas : {str(e)}")

    # Réécrire le fichier CSV
    with open(DATASET_PATH, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(nouvelles_lignes)

    # Mettre à jour les règles cliniques custom
    _CUSTOM_RULES_PATH = os.path.join(".", "ml_models", "custom_disease_rules.json")
    try:
        existing_rules: dict = {}
        if os.path.exists(_CUSTOM_RULES_PATH):
            with open(_CUSTOM_RULES_PATH, "r", encoding="utf-8") as f:
                existing_rules = json.load(f)

        boost = payload.boost_factor if payload.boost_factor else existing_rules.get(nom_decode, {}).get("boost_factor", 4.0)
        existing_rules[nom_decode] = {
            "symptomes_boost": payload.symptomes,
            "boost_factor": boost,
            "min_symptomes_match": max(1, len(payload.symptomes) // 3),
        }
        os.makedirs(os.path.dirname(_CUSTOM_RULES_PATH), exist_ok=True)
        with open(_CUSTOM_RULES_PATH, "w", encoding="utf-8") as f:
            json.dump(existing_rules, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logging.warning(f"[ADMIN] Impossible de mettre à jour les règles cliniques: {e}")

    logging.info(
        f"[ADMIN] Maladie mise à jour : '{nom_decode}' — "
        f"{cas_supprimes} cas supprimés, {cas_ajoutes} cas ajoutés par {admin.email}"
    )

    cas_apres = sum(1 for row in nouvelles_lignes if row and row[1].strip().lower() == nom_decode.strip().lower())

    return {
        "success": True,
        "maladie": nom_decode,
        "cas_avant": cas_avant,
        "cas_supprimes": cas_supprimes,
        "cas_ajoutes": cas_ajoutes,
        "cas_apres": cas_apres,
        "symptomes_mis_a_jour": payload.symptomes,
        "message": (
            f"Maladie '{nom_decode}' mise à jour : {cas_supprimes} cas remplacés, "
            f"{cas_ajoutes} nouveaux cas ajoutés. Règles cliniques mises à jour. "
            f"Relancez l'entraînement pour appliquer les changements."
        ),
    }
