"""
Router pour l'authentification des utilisateurs
Gère la connexion, déconnexion et génération de tokens JWT
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Optional
import logging
from jose import JWTError, jwt
import bcrypt

from ..database import get_db
from ..models.user import User
from ..config import settings
from pydantic import BaseModel, EmailStr

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)

# Configuration OAuth2
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

# Configuration JWT
SECRET_KEY = settings.SECRET_KEY
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = getattr(settings, 'ACCESS_TOKEN_EXPIRE_MINUTES', 1440)


# ============================================================================
# SCHEMAS PYDANTIC
# ============================================================================

class Token(BaseModel):
    """Schéma de réponse pour le token"""
    access_token: str
    token_type: str
    user: dict


class TokenData(BaseModel):
    """Données contenues dans le token"""
    email: Optional[str] = None
    role: Optional[str] = None


class LoginRequest(BaseModel):
    """Schéma de requête pour la connexion"""
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    """Schéma de réponse pour les informations utilisateur"""
    utilisateur_id: int
    nom: str
    prenoms: str
    email: str
    role: str
    actif: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class RegisterRequest(BaseModel):
    """Schéma de requête pour l'inscription"""
    nom: str
    prenoms: str
    email: EmailStr
    mot_de_passe: str
    role: str = "medecin"
    specialite: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "nom": "DUPONT",
                "prenoms": "Jean",
                "email": "jean.dupont@gasasad.com",
                "mot_de_passe": "motdepasse123",
                "role": "medecin",
                "specialite": "Cardiologie"
            }
        }


# ============================================================================
# FONCTIONS UTILITAIRES
# ============================================================================

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Vérifie si le mot de passe en clair correspond au hash bcrypt
    """
    try:
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
    except Exception as e:
        logger.error(f"Erreur lors de la vérification du mot de passe: {e}")
        return False


def get_password_hash(password: str) -> str:
    """
    Hash un mot de passe avec bcrypt
    """
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """
    Crée un token JWT
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    return encoded_jwt


def authenticate_user(db: Session, email: str, password: str):
    """
    Authentifie un utilisateur
    """
    user = db.query(User).filter(User.email == email).first()
    
    if not user:
        logger.warning(f"Tentative de connexion avec email inexistant: {email}")
        return False
    
    if not user.actif:
        logger.warning(f"Tentative de connexion avec compte inactif: {email}")
        return False
    
    if not verify_password(password, user.mot_de_passe):
        logger.warning(f"Mot de passe incorrect pour: {email}")
        return False
    
    logger.info(f"✅ Authentification réussie: {email} ({user.role})")
    return user


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """
    Récupère l'utilisateur actuel depuis le token JWT
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        
        if email is None:
            raise credentials_exception
        
        token_data = TokenData(email=email, role=payload.get("role"))
        
    except JWTError:
        raise credentials_exception
    
    user = db.query(User).filter(User.email == token_data.email).first()
    
    if user is None:
        raise credentials_exception
    
    if not user.actif:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Compte désactivé"
        )
    
    return user


async def get_current_active_user(current_user: User = Depends(get_current_user)):
    """
    Vérifie que l'utilisateur est actif
    """
    if not current_user.actif:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Compte inactif"
        )
    return current_user


async def get_current_admin(current_user: User = Depends(get_current_user)):
    """
    Vérifie que l'utilisateur est un administrateur actif
    """
    if not current_user.actif:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Compte inactif")
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Accès réservé aux administrateurs",
        )
    return current_user


# ============================================================================
# ENDPOINTS
# ============================================================================

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    register_data: RegisterRequest,
    db: Session = Depends(get_db)
):
    """
    Inscription d'un nouvel utilisateur (médecin ou infirmier)
    
    - **nom**: Nom de famille (en majuscules)
    - **prenoms**: Prénom(s)
    - **email**: Adresse email unique
    - **mot_de_passe**: Mot de passe (min 8 caractères)
    - **role**: Role (medecin ou infirmier)
    
    Le compte est créé avec actif=False et doit être activé par un administrateur
    """
    logger.info(f"Tentative d'inscription: {register_data.email} ({register_data.role})")
    
    # Vérifier si l'email existe déjà
    existing_user = db.query(User).filter(User.email == register_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cette adresse email est déjà utilisée"
        )
    
    # Valider le rôle
    if register_data.role not in ["medecin", "infirmier"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Le rôle doit être 'medecin' ou 'infirmier'"
        )
    
    # Valider le mot de passe
    if len(register_data.mot_de_passe) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Le mot de passe doit faire au moins 8 caractères"
        )
    
    # Hasher le mot de passe
    hashed_password = get_password_hash(register_data.mot_de_passe)
    
    # Créer le nouvel utilisateur (inactif par défaut)
    new_user = User(
        nom=register_data.nom.upper(),
        prenoms=register_data.prenoms,
        email=register_data.email,
        mot_de_passe=hashed_password,
        role=register_data.role,
        actif=False  # Compte inactif jusqu'à activation par admin
    )

    db.add(new_user)
    db.flush()

    # Pré-créer le profil médical (indisponible jusqu'à activation)
    if register_data.role == "medecin":
        from ..models.medecin import Medecin
        existing = db.query(Medecin).filter(
            Medecin.nom == new_user.nom, Medecin.prenoms == new_user.prenoms
        ).first()
        if not existing:
            db.add(Medecin(
                nom=new_user.nom,
                prenoms=new_user.prenoms,
                specialite=register_data.specialite or "Médecine Générale",
                telephone="N/A",
                disponible=False,
            ))
    elif register_data.role == "infirmier":
        from ..models.infirmier import Infirmier
        existing = db.query(Infirmier).filter(
            Infirmier.nom == new_user.nom, Infirmier.prenoms == new_user.prenoms
        ).first()
        if not existing:
            db.add(Infirmier(
                nom=new_user.nom,
                prenoms=new_user.prenoms,
                telephone="N/A",
                email=new_user.email,
                disponible=False,
            ))

    db.commit()
    db.refresh(new_user)

    logger.info(f"✅ Inscription réussie: {new_user.email} ({new_user.role}) - En attente d'activation")

    return new_user


@router.post("/login", response_model=Token)
async def login(
    login_data: LoginRequest,
    db: Session = Depends(get_db)
):
    """
    Connexion d'un utilisateur
    
    - **email**: Email de l'utilisateur
    - **password**: Mot de passe
    
    Retourne un token JWT valide pour 24 heures
    """
    logger.info(f"Tentative de connexion: {login_data.email}")
    
    user = authenticate_user(db, login_data.email, login_data.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou mot de passe incorrect",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Créer le token JWT
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={
            "sub": user.email,
            "role": user.role,
            "user_id": user.utilisateur_id
        },
        expires_delta=access_token_expires
    )
    
    # Mettre à jour la dernière connexion
    user.last_login = datetime.now()
    db.commit()
    
    logger.info(f"✅ Connexion réussie: {user.email} ({user.role})")
    
    # Récupérer l'ID médecin si c'est un médecin
    medecin_id = None
    if user.role == "medecin":
        from ..models.medecin import Medecin
        med = db.query(Medecin).filter(Medecin.nom == user.nom, Medecin.prenoms == user.prenoms).first()
        if med:
            medecin_id = med.medecin_id

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "utilisateur_id": user.utilisateur_id,
            "nom": user.nom,
            "prenoms": user.prenoms,
            "email": user.email,
            "role": user.role,
            "actif": user.actif,
            "medecin_id": medecin_id
        }
    }


@router.post("/login-form", response_model=Token)
async def login_form(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    Connexion avec formulaire OAuth2 (pour Swagger UI)
    """
    logger.info(f"Tentative de connexion (form): {form_data.username}")
    
    user = authenticate_user(db, form_data.username, form_data.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou mot de passe incorrect",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Créer le token JWT
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={
            "sub": user.email,
            "role": user.role,
            "user_id": user.utilisateur_id
        },
        expires_delta=access_token_expires
    )
    
    # Mettre à jour la dernière connexion
    user.last_login = datetime.now()
    db.commit()
    
    # Récupérer l'ID médecin si c'est un médecin
    medecin_id = None
    if user.role == "medecin":
        from ..models.medecin import Medecin
        med = db.query(Medecin).filter(Medecin.nom == user.nom, Medecin.prenoms == user.prenoms).first()
        if med:
            medecin_id = med.medecin_id

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "utilisateur_id": user.utilisateur_id,
            "nom": user.nom,
            "prenoms": user.prenoms,
            "email": user.email,
            "role": user.role,
            "actif": user.actif,
            "medecin_id": medecin_id
        }
    }


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_active_user)):
    """
    Récupère les informations de l'utilisateur connecté
    """
    return current_user


@router.post("/logout")
async def logout():
    """
    Déconnexion — JWT est stateless, rien à invalider côté serveur.
    Retourne toujours 200 ; le client supprime son token local.
    """
    return {"message": "Déconnexion réussie"}


@router.post("/refresh", response_model=Token)
async def refresh_token(current_user: User = Depends(get_current_active_user)):
    """
    Rafraîchit le token JWT
    """
    # Créer un nouveau token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={
            "sub": current_user.email,
            "role": current_user.role,
            "user_id": current_user.utilisateur_id
        },
        expires_delta=access_token_expires
    )
    
    logger.info(f"Token rafraîchi: {current_user.email}")
    
    # Récupérer l'ID médecin si c'est un médecin
    medecin_id = None
    if current_user.role == "medecin":
        from ..models.medecin import Medecin
        med = db.query(Medecin).filter(Medecin.nom == current_user.nom, Medecin.prenoms == current_user.prenoms).first()
        if med:
            medecin_id = med.medecin_id

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "utilisateur_id": current_user.utilisateur_id,
            "nom": current_user.nom,
            "prenoms": current_user.prenoms,
            "email": current_user.email,
            "role": current_user.role,
            "actif": current_user.actif,
            "medecin_id": medecin_id
        }
    }
