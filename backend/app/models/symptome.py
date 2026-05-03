"""
Symptome database model
"""
from sqlalchemy import Column, String, Text, Date, Integer, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.mysql import CHAR, ENUM
from ..database import Base


class Symptome(Base):
    """Symptome model - corresponds to 'symptomes' table"""
    
    __tablename__ = "symptomes"
    
    # Primary Key (UUID)
    id = Column(CHAR(36), primary_key=True, index=True)
    
    # Foreign Key
    consultation_id = Column(CHAR(36), ForeignKey("consultations.consultation_id"), nullable=False)
    
    # Symptom Information
    nom = Column(String(255), nullable=False)
    description = Column(Text)
    severite = Column(ENUM('LEGER', 'MODERE', 'SEVERE'))
    date_apparition = Column(Date)
    duree_jours = Column(Integer)
    zone_atteinte = Column(String(255))
    frequence = Column(ENUM('CONSTANT', 'INTERMITTENT', 'PROGRESSIF'))
    
    # Relationships
    consultation = relationship("Consultation", back_populates="symptomes")
    
    def __repr__(self):
        return f"<Symptome(id={self.id}, nom='{self.nom}', severite='{self.severite}')>"
