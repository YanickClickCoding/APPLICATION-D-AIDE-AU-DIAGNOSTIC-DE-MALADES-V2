"""
Tests unitaires pour l'authentification
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.sql import func
from app.main import app
from app.database import get_db
import bcrypt
import os

# Base de données de test en mémoire
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_auth.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base séparée pour les tests
TestBase = declarative_base()

# Modèle User pour SQLite (sans ENUM)
class TestUser(TestBase):
    """User model pour tests - compatible SQLite"""
    __tablename__ = "utilisateurs"
    
    utilisateur_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nom = Column(String(100), nullable=False)
    prenoms = Column(String(150), nullable=False)
    email = Column(String(200), unique=True, nullable=False, index=True)
    mot_de_passe = Column(String(255), nullable=False)
    role = Column(String(50), default='medecin')  # String au lieu de ENUM pour SQLite
    actif = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    last_login = Column(DateTime, nullable=True)

# Override de la dépendance
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

# Client de test
client = TestClient(app)

@pytest.fixture(scope="module", autouse=True)
def setup_database():
    """Créer les tables et ajouter des utilisateurs de test"""
    # Supprimer la base de test si elle existe
    if os.path.exists("./test_auth.db"):
        os.remove("./test_auth.db")
    
    # Créer les tables
    TestBase.metadata.create_all(bind=engine)
    
    db = TestingSessionLocal()
    
    # Créer un utilisateur de test
    password = "admin123"
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    user = TestUser(
        nom="KOUASSI",
        prenoms="Aya",
        email="aya.kouassi@sante.com",
        mot_de_passe=hashed,
        role="infirmier",
        actif=True
    )
    
    db.add(user)
    db.commit()
    db.close()
    
    yield
    
    # Nettoyer après les tests
    TestBase.metadata.drop_all(bind=engine)
    if os.path.exists("./test_auth.db"):
        os.remove("./test_auth.db")


class TestAuthentication:
    """Tests pour l'authentification"""
    
    def test_login_success(self):
        """Test: Connexion réussie avec identifiants valides"""
        response = client.post(
            "/api/auth/login",
            json={
                "email": "aya.kouassi@sante.com",
                "password": "admin123"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert "user" in data
        assert data["user"]["email"] == "aya.kouassi@sante.com"
        assert data["user"]["nom"] == "KOUASSI"
        assert data["user"]["prenoms"] == "Aya"
        assert data["user"]["role"] == "infirmier"
        
        print("✅ Test connexion réussie: PASSED")
    
    def test_login_wrong_password(self):
        """Test: Connexion échouée avec mauvais mot de passe"""
        response = client.post(
            "/api/auth/login",
            json={
                "email": "aya.kouassi@sante.com",
                "password": "wrongpassword"
            }
        )
        
        assert response.status_code == 401
        data = response.json()
        assert "detail" in data
        assert "incorrect" in data["detail"].lower()
        
        print("✅ Test mauvais mot de passe: PASSED")
    
    def test_login_wrong_email(self):
        """Test: Connexion échouée avec email inexistant"""
        response = client.post(
            "/api/auth/login",
            json={
                "email": "nonexistent@example.com",
                "password": "admin123"
            }
        )
        
        assert response.status_code == 401
        data = response.json()
        assert "detail" in data
        
        print("✅ Test email inexistant: PASSED")
    
    def test_login_invalid_email_format(self):
        """Test: Connexion échouée avec format email invalide"""
        response = client.post(
            "/api/auth/login",
            json={
                "email": "not-an-email",
                "password": "admin123"
            }
        )
        
        assert response.status_code == 422  # Validation error
        
        print("✅ Test format email invalide: PASSED")
    
    def test_get_current_user(self):
        """Test: Récupérer les infos de l'utilisateur connecté"""
        # D'abord se connecter
        login_response = client.post(
            "/api/auth/login",
            json={
                "email": "aya.kouassi@sante.com",
                "password": "admin123"
            }
        )
        
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]
        
        # Ensuite récupérer les infos
        response = client.get(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "aya.kouassi@sante.com"
        assert data["nom"] == "KOUASSI"
        
        print("✅ Test récupération utilisateur: PASSED")
    
    def test_get_current_user_without_token(self):
        """Test: Accès refusé sans token"""
        response = client.get("/api/auth/me")
        
        assert response.status_code == 401
        
        print("✅ Test accès sans token: PASSED")
    
    def test_get_current_user_invalid_token(self):
        """Test: Accès refusé avec token invalide"""
        response = client.get(
            "/api/auth/me",
            headers={"Authorization": "Bearer invalid_token_here"}
        )
        
        assert response.status_code == 401
        
        print("✅ Test token invalide: PASSED")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
