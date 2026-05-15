"""
Admin Router - Gestion système, CRUD utilisateurs, CRUD personnel, config IA
Tous les endpoints sont protégés : token JWT admin requis.
"""
import os
import platform
import threading
import logging
from datetime import datetime
from typing import Dict, List, Optional

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr, Field

from ..database import get_db
from ..models.user import User
from ..models.medecin import Medecin
from ..models.infirmier import Infirmier
from ..ml.model_manager import model_manager
from .auth import get_current_admin, get_password_hash

router = APIRouter(prefix="/admin", tags=["Administration"])

# ─── Config IA en mémoire (persistable si besoin) ─────────────────────────────
_ia_config: Dict = {
    "seuil_confiance_min": 0.60,
    "seuil_alerte_bas": 0.40,
    "n_estimators": 200,
    "max_depth": 30,
}

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

    db.commit()
    db.refresh(user)
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
                _training_state.update({
                    "status": "success",
                    "message": "Entraînement terminé ✓",
                    "results": {
                        "accuracy":   round(eval_r.get("accuracy", 0) * 100, 2),
                        "precision":  round(eval_r.get("precision", 0) * 100, 2),
                        "recall":     round(eval_r.get("recall", 0) * 100, 2),
                        "f1_score":   round(eval_r.get("f1_score", 0) * 100, 2),
                        "n_samples":  train_r.get("n_samples"),
                        "n_features": train_r.get("n_features"),
                        "n_classes":  train_r.get("n_classes"),
                        "duration_s": round(train_r.get("training_duration_seconds", 0), 1),
                        "model_path": train_r.get("model_path", ""),
                    },
                })
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
