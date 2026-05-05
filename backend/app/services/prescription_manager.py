"""
Prescription Manager Service
Gestion des prescriptions médicales avec contre-indications
Requirements: 6.1, 6.2, 6.3, 6.4, 6.5
"""
from sqlalchemy.orm import Session
from typing import List, Dict, Optional, Any
from datetime import datetime
import hashlib
import json
import logging

from app.models.prescription import Prescription

logger = logging.getLogger(__name__)


class PrescriptionManager:
    """
    Gestionnaire pour les prescriptions médicales
    Implémente les Requirements 6.1 à 6.5
    """
    
    # Base de données de traitements par diagnostic
    TREATMENT_DATABASE = {
        "Grippe": [
            {"nom": "Paracétamol", "dosage": "500mg", "frequence": "3x/jour", "duree": "5 jours"},
            {"nom": "Ibuprofène", "dosage": "400mg", "frequence": "2x/jour", "duree": "5 jours"}
        ],
        "COVID-19": [
            {"nom": "Paracétamol", "dosage": "1g", "frequence": "3x/jour", "duree": "7 jours"},
            {"nom": "Vitamine C", "dosage": "1000mg", "frequence": "1x/jour", "duree": "14 jours"}
        ],
        "Pneumonie": [
            {"nom": "Amoxicilline", "dosage": "1g", "frequence": "3x/jour", "duree": "7 jours"},
            {"nom": "Azithromycine", "dosage": "500mg", "frequence": "1x/jour", "duree": "5 jours"}
        ],
        "Bronchite": [
            {"nom": "Amoxicilline", "dosage": "500mg", "frequence": "3x/jour", "duree": "7 jours"},
            {"nom": "Sirop antitussif", "dosage": "10ml", "frequence": "3x/jour", "duree": "5 jours"}
        ],
        "Asthme": [
            {"nom": "Salbutamol", "dosage": "100mcg", "frequence": "2 bouffées si besoin", "duree": "continu"},
            {"nom": "Corticoïde inhalé", "dosage": "250mcg", "frequence": "2x/jour", "duree": "continu"}
        ],
        "Hypertension": [
            {"nom": "Amlodipine", "dosage": "5mg", "frequence": "1x/jour", "duree": "continu"},
            {"nom": "Lisinopril", "dosage": "10mg", "frequence": "1x/jour", "duree": "continu"}
        ],
        "Diabète": [
            {"nom": "Metformine", "dosage": "500mg", "frequence": "2x/jour", "duree": "continu"},
            {"nom": "Insuline", "dosage": "selon glycémie", "frequence": "variable", "duree": "continu"}
        ]
    }
    
    # Base de données d'interactions médicamenteuses
    DRUG_INTERACTIONS = {
        ("Paracétamol", "Warfarine"): {"severity": "MEDIUM", "description": "Risque d'augmentation de l'effet anticoagulant"},
        ("Ibuprofène", "Aspirine"): {"severity": "HIGH", "description": "Risque d'ulcère gastrique et saignement"},
        ("Amoxicilline", "Méthotrexate"): {"severity": "HIGH", "description": "Risque de toxicité du méthotrexate"},
        ("Azithromycine", "Warfarine"): {"severity": "MEDIUM", "description": "Risque d'augmentation de l'effet anticoagulant"},
        ("Amlodipine", "Simvastatine"): {"severity": "MEDIUM", "description": "Risque de myopathie"},
        ("Metformine", "Alcool"): {"severity": "HIGH", "description": "Risque d'acidose lactique"}
    }
    
    # Substances allergènes communes
    COMMON_ALLERGENS = {
        "Pénicilline": ["Amoxicilline", "Ampicilline", "Pénicilline G"],
        "Sulfamides": ["Sulfaméthoxazole", "Sulfasalazine"],
        "Aspirine": ["Aspirine", "Acide acétylsalicylique"],
        "Iode": ["Produits de contraste iodés"]
    }
    
    def __init__(self, db: Session):
        """
        Initialise le gestionnaire
        
        Args:
            db: Session de base de données SQLAlchemy
        """
        self.db = db
    
    def suggest_treatments(self, diagnostic: str) -> List[Dict]:
        """
        Suggère des traitements appropriés basés sur le diagnostic
        
        Args:
            diagnostic: Nom du diagnostic
            
        Returns:
            Liste de médicaments suggérés
        """
        # Rechercher dans la base de données de traitements
        treatments = self.TREATMENT_DATABASE.get(diagnostic, [])
        
        if not treatments:
            logger.warning(f"Aucun traitement trouvé pour: {diagnostic}")
            # Traitement par défaut
            treatments = [
                {"nom": "Consultation spécialisée recommandée", "dosage": "N/A", "frequence": "N/A", "duree": "N/A"}
            ]
        
        logger.info(f"Traitements suggérés pour {diagnostic}: {len(treatments)} médicaments")
        
        return treatments
    
    def check_contraindications(self, 
                                medications: List[Dict],
                                patient_allergies: Optional[List[str]] = None,
                                current_medications: Optional[List[str]] = None) -> Dict:
        """
        Vérifie les contre-indications pour une liste de médicaments
        
        Args:
            medications: Liste de médicaments à prescrire
            patient_allergies: Liste des allergies du patient
            current_medications: Liste des médicaments actuels du patient
            
        Returns:
            Dictionnaire contenant les contre-indications détectées
        """
        contraindications = []
        drug_interactions = []
        warnings = []
        has_critical_warning = False
        
        patient_allergies = patient_allergies or []
        current_medications = current_medications or []
        
        # Vérifier les allergies
        for med in medications:
            med_name = med.get("nom", "")
            
            # Vérifier contre les allergies connues
            for allergen, related_drugs in self.COMMON_ALLERGENS.items():
                if allergen in patient_allergies:
                    if any(drug.lower() in med_name.lower() for drug in related_drugs):
                        contraindications.append({
                            "type": "allergie",
                            "substance": allergen,
                            "medication": med_name,
                            "severity": "CRITICAL",
                            "message": f"⚠️ ALLERGIE CRITIQUE: Patient allergique à {allergen}"
                        })
                        has_critical_warning = True
            
            # Vérifier allergie directe
            if med_name in patient_allergies:
                contraindications.append({
                    "type": "allergie",
                    "substance": med_name,
                    "medication": med_name,
                    "severity": "CRITICAL",
                    "message": f"⚠️ ALLERGIE CRITIQUE: Patient allergique à {med_name}"
                })
                has_critical_warning = True
        
        # Vérifier les interactions médicamenteuses
        all_medications = [med.get("nom", "") for med in medications] + current_medications
        
        for i, med1 in enumerate(all_medications):
            for med2 in all_medications[i+1:]:
                # Vérifier interaction dans les deux sens
                interaction = self.DRUG_INTERACTIONS.get((med1, med2)) or \
                             self.DRUG_INTERACTIONS.get((med2, med1))
                
                if interaction:
                    drug_interactions.append({
                        "medication1": med1,
                        "medication2": med2,
                        "severity": interaction["severity"],
                        "description": interaction["description"]
                    })
                    
                    if interaction["severity"] == "HIGH":
                        has_critical_warning = True
                        warnings.append(f"⚠️ INTERACTION CRITIQUE: {med1} + {med2}")
        
        # Avertissements généraux
        for med in medications:
            med_name = med.get("nom", "")
            
            # Avertissements spécifiques
            if "Aspirine" in med_name or "Ibuprofène" in med_name:
                warnings.append(f"⚠️ {med_name}: À prendre avec de la nourriture")
            
            if "Antibiotique" in med_name or "cilline" in med_name:
                warnings.append(f"ℹ️ {med_name}: Compléter le traitement même si amélioration")
        
        result = {
            "contraindications": contraindications,
            "drug_interactions": drug_interactions,
            "warnings": warnings,
            "has_critical_warning": has_critical_warning,
            "safe_to_prescribe": len(contraindications) == 0 and not has_critical_warning
        }
        
        logger.info(f"Vérification contre-indications: {len(contraindications)} trouvées, critique={has_critical_warning}")
        
        return result
    
    def create_prescription(self,
                           patient_id: int,
                           medecin_id: int,
                           diagnostic: str,
                           medications: List[Dict],
                           consultation_id: Optional[int] = None,
                           patient_allergies: Optional[List[str]] = None,
                           current_medications: Optional[List[str]] = None,
                           special_instructions: Optional[str] = None) -> Prescription:
        """
        Crée une nouvelle prescription
        
        Args:
            patient_id: ID du patient
            medecin_id: ID du médecin prescripteur
            diagnostic: Diagnostic associé
            medications: Liste des médicaments à prescrire
            consultation_id: ID de la consultation (optionnel)
            patient_allergies: Allergies du patient
            current_medications: Médicaments actuels
            special_instructions: Instructions spéciales
            
        Returns:
            Objet Prescription créé
        """
        # Vérifier les contre-indications
        check_result = self.check_contraindications(
            medications=medications,
            patient_allergies=patient_allergies,
            current_medications=current_medications
        )
        
        # Créer la prescription
        prescription = Prescription(
            patient_id=patient_id,
            medecin_id=medecin_id,
            consultation_id=consultation_id,
            diagnostic=diagnostic,
            medications=medications,
            contraindications=check_result["contraindications"],
            patient_allergies=patient_allergies,
            drug_interactions=check_result["drug_interactions"],
            warnings=check_result["warnings"],
            has_critical_warning=check_result["has_critical_warning"],
            special_instructions=special_instructions,
            status="draft",
            created_at=datetime.utcnow()
        )
        
        # Sauvegarder dans la base de données
        self.db.add(prescription)
        self.db.commit()
        self.db.refresh(prescription)
        
        logger.info(f"Prescription créée: id={prescription.id}, patient_id={patient_id}, critique={check_result['has_critical_warning']}")
        
        return prescription
    
    def sign_prescription(self,
                         prescription_id: int,
                         medecin_id: int,
                         signature_data: Optional[str] = None) -> Prescription:
        """
        Signe électroniquement une prescription
        
        Args:
            prescription_id: ID de la prescription
            medecin_id: ID du médecin signataire
            signature_data: Données de signature (optionnel)
            
        Returns:
            Prescription signée
        """
        # Récupérer la prescription
        prescription = self.db.query(Prescription).filter(
            Prescription.id == prescription_id
        ).first()
        
        if not prescription:
            raise ValueError(f"Prescription {prescription_id} introuvable")
        
        # Vérifier qu'il n'y a pas d'alerte critique
        if prescription.has_critical_warning:
            logger.warning(f"Tentative de signature d'une prescription avec alerte critique: {prescription_id}")
            raise ValueError("Impossible de signer une prescription avec des alertes critiques")
        
        # Générer le hash de signature
        signature_content = f"{prescription_id}_{medecin_id}_{datetime.utcnow().isoformat()}"
        if signature_data:
            signature_content += f"_{signature_data}"
        
        signature_hash = hashlib.sha256(signature_content.encode()).hexdigest()
        
        # Mettre à jour la prescription
        prescription.is_signed = True
        prescription.signed_by = medecin_id
        prescription.signed_at = datetime.utcnow()
        prescription.signature_hash = signature_hash
        prescription.status = "signed"
        
        self.db.commit()
        self.db.refresh(prescription)
        
        logger.info(f"Prescription signée: id={prescription_id}, medecin_id={medecin_id}")
        
        return prescription
    
    def get_prescription(self, prescription_id: int) -> Optional[Prescription]:
        """
        Récupère une prescription par son ID
        
        Args:
            prescription_id: ID de la prescription
            
        Returns:
            Objet Prescription ou None
        """
        prescription = self.db.query(Prescription).filter(
            Prescription.id == prescription_id
        ).first()
        
        return prescription
    
    def get_patient_prescriptions(self, 
                                  patient_id: int,
                                  limit: Optional[int] = None) -> List[Prescription]:
        """
        Récupère toutes les prescriptions d'un patient
        
        Args:
            patient_id: ID du patient
            limit: Nombre maximum de prescriptions à retourner
            
        Returns:
            Liste des prescriptions
        """
        query = self.db.query(Prescription).filter(
            Prescription.patient_id == patient_id
        ).order_by(Prescription.created_at.desc())
        
        if limit:
            query = query.limit(limit)
        
        prescriptions = query.all()
        
        logger.info(f"Prescriptions récupérées: patient_id={patient_id}, count={len(prescriptions)}")
        
        return prescriptions
    
    def update_prescription_status(self,
                                   prescription_id: int,
                                   status: str) -> Prescription:
        """
        Met à jour le statut d'une prescription
        
        Args:
            prescription_id: ID de la prescription
            status: Nouveau statut (draft, signed, delivered, cancelled)
            
        Returns:
            Prescription mise à jour
        """
        prescription = self.db.query(Prescription).filter(
            Prescription.id == prescription_id
        ).first()
        
        if not prescription:
            raise ValueError(f"Prescription {prescription_id} introuvable")
        
        prescription.status = status
        
        if status == "delivered":
            prescription.delivered_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(prescription)
        
        logger.info(f"Statut prescription mis à jour: id={prescription_id}, status={status}")
        
        return prescription
    
    def get_prescription_summary(self, prescription_id: int) -> Dict:
        """
        Génère un résumé de la prescription
        
        Args:
            prescription_id: ID de la prescription
            
        Returns:
            Dictionnaire contenant le résumé
        """
        prescription = self.get_prescription(prescription_id)
        
        if not prescription:
            raise ValueError(f"Prescription {prescription_id} introuvable")
        
        summary = {
            "id": prescription.id,
            "patient_id": prescription.patient_id,
            "diagnostic": prescription.diagnostic,
            "medications_count": len(prescription.medications) if prescription.medications else 0,
            "medications": prescription.medications,
            "has_contraindications": len(prescription.contraindications or []) > 0,
            "has_critical_warning": prescription.has_critical_warning,
            "is_signed": prescription.is_signed,
            "status": prescription.status,
            "created_at": prescription.created_at.isoformat() if prescription.created_at else None,
            "signed_at": prescription.signed_at.isoformat() if prescription.signed_at else None
        }
        
        return summary


def demo_prescription_manager():
    """
    Fonction de démonstration du gestionnaire de prescriptions
    """
    from app.database import SessionLocal
    
    db = SessionLocal()
    manager = PrescriptionManager(db)
    
    # Suggérer des traitements
    treatments = manager.suggest_treatments("Grippe")
    print(f"Traitements suggérés pour Grippe: {treatments}")
    
    # Vérifier contre-indications
    check = manager.check_contraindications(
        medications=treatments,
        patient_allergies=["Pénicilline"],
        current_medications=["Warfarine"]
    )
    print(f"Contre-indications: {check}")
    
    # Créer une prescription
    prescription = manager.create_prescription(
        patient_id=1,
        medecin_id=1,
        diagnostic="Grippe",
        medications=treatments,
        patient_allergies=[]
    )
    print(f"Prescription créée: {prescription.id}")
    
    db.close()


if __name__ == "__main__":
    demo_prescription_manager()
