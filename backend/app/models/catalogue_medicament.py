"""Catalogue de référence des médicaments par maladie"""
from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.dialects.mysql import ENUM
from ..database import Base


class CatalogueMedicament(Base):
    __tablename__ = "catalogue_medicaments"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    maladie = Column(String(200), nullable=False, index=True)
    nom_commercial = Column(String(255), nullable=False)
    denomination_commune = Column(String(255), nullable=False)
    dosage_standard = Column(String(100), nullable=True)
    forme = Column(
        ENUM('COMPRIME', 'INJECTION', 'SIROP', 'CREME', 'COLLYRE',
             'POUDRE', 'PATCH', 'SPRAY', 'CAPSULE', 'SOLUTION'),
        default='COMPRIME',
    )
    voie_administration = Column(
        ENUM('ORALE', 'INTRAVEINEUSE', 'CUTANEE', 'INTRAMUSCULAIRE',
             'OPHTALMIQUE', 'NASALE', 'INHALATION', 'SOUS-CUTANEE', 'RECTALE'),
        default='ORALE',
    )
    frequence_habituelle = Column(String(100), nullable=True)
    duree_standard_jours = Column(Integer, nullable=True)
    categorie = Column(
        ENUM('PREMIERE_INTENTION', 'DEUXIEME_INTENTION', 'ADJUVANT', 'SYMPTOMATIQUE'),
        default='PREMIERE_INTENTION',
    )
    notes = Column(Text, nullable=True)
