"""
User database model - Pour l'authentification
"""
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.dialects.mysql import ENUM
from sqlalchemy.sql import func
from ..database import Base


class User(Base):
    """User model - corresponds to 'utilisateurs' table"""
    
    __tablename__ = "utilisateurs"
    
    # Primary Key
    utilisateur_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # Personal Information
    nom = Column(String(100), nullable=False)
    prenoms = Column(String(150), nullable=False)
    
    # Authentication
    email = Column(String(200), unique=True, nullable=False, index=True)
    mot_de_passe = Column(String(255), nullable=False)
    role = Column(ENUM('admin', 'operateur'), default='operateur')
    
    # Timestamp
    created_at = Column(DateTime, server_default=func.now())
    
    def __repr__(self):
        return f"<User(id={self.utilisateur_id}, email='{self.email}', role='{self.role}')>"
