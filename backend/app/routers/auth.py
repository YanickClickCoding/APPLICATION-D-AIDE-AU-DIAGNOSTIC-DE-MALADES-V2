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
    prefix="/api/auth",
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
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "utilisateur_id": user.utilisateur_id,
            "nom": user.nom,
            "prenoms": user.prenoms,
            "email": user.email,
            "role": user.role,
            "actif": user.actif
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
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "utilisateur_id": user.utilisateur_id,
            "nom": user.nom,
            "prenoms": user.prenoms,
            "email": user.email,
            "role": user.role,
            "actif": user.actif
        }
    }


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_active_user)):
    """
    Récupère les informations de l'utilisateur connecté
    """
    return current_user


@router.post("/logout")
async def logout(current_user: User = Depends(get_current_active_user)):
    """
    Déconnexion (côté client, supprimer le token)
    """
    logger.info(f"Déconnexion: {current_user.email}")
    
    return {
        "message": "Déconnexion réussie",
        "detail": "Supprimez le token côté client"
    }


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
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "utilisateur_id": current_user.utilisateur_id,
            "nom": current_user.nom,
            "prenoms": current_user.prenoms,
            "email": current_user.email,
            "role": current_user.role,
            "actif": current_user.actif
        }
    }
