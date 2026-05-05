"""
Data Validation Module
Validation et vérification de la qualité des données patient
"""
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import pandas as pd
import numpy as np
from datetime import datetime


class ValidationLevel(Enum):
    """Niveaux de sévérité des erreurs de validation"""
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


@dataclass
class ValidationError:
    """Représente une erreur de validation"""
    field: str
    message: str
    level: ValidationLevel
    current_value: Any = None
    expected_range: Optional[Tuple[float, float]] = None


@dataclass
class ValidationResult:
    """Résultat de la validation"""
    is_valid: bool
    errors: List[ValidationError]
    warnings: List[ValidationError]
    completeness_score: float  # 0-1
    quality_score: float  # 0-1
    
    def has_errors(self) -> bool:
        return len(self.errors) > 0
    
    def has_warnings(self) -> bool:
        return len(self.warnings) > 0
    
    def get_error_messages(self) -> List[str]:
        return [f"{e.field}: {e.message}" for e in self.errors]
    
    def get_warning_messages(self) -> List[str]:
        return [f"{w.field}: {w.message}" for w in self.warnings]


class DataValidator:
    """
    Validateur de données patient
    Vérifie la complétude, les plages de valeurs, et détecte les outliers
    """
    
    # Champs obligatoires
    REQUIRED_FIELDS = {
        'patient': ['nom', 'prenoms', 'date_naissance', 'sexe'],
        'symptomes': ['nom', 'severite', 'duree_jours'],
        'signes_vitaux': [
            'tension_systolique', 'tension_diastolique',
            'frequence_cardiaque', 'frequence_respiratoire',
            'temperature', 'saturation_o2'
        ]
    }
    
    # Plages de valeurs acceptables
    VALUE_RANGES = {
        'tension_systolique': (70, 250),
        'tension_diastolique': (40, 150),
        'frequence_cardiaque': (30, 220),
        'frequence_respiratoire': (8, 60),
        'temperature': (35.0, 42.0),
        'saturation_o2': (70, 100),
        'poids': (2, 300),  # kg
        'taille': (40, 250),  # cm
        'duree_jours': (0, 365),
    }
    
    def __init__(self):
        self.validation_log = []
    
    def validate_patient_data(self, data: Dict[str, Any]) -> ValidationResult:
        """
        Valide les données complètes d'un patient
        
        Args:
            data: Dictionnaire contenant patient, symptomes, signes_vitaux, etc.
        
        Returns:
            ValidationResult avec erreurs et warnings
        """
        errors = []
        warnings = []
        
        # Vérifier la complétude
        completeness_errors = self._check_completeness(data)
        errors.extend(completeness_errors)
        
        # Vérifier les plages de valeurs
        range_errors, range_warnings = self._check_value_ranges(data)
        errors.extend(range_errors)
        warnings.extend(range_warnings)
        
        # Calculer les scores
        completeness_score = self._calculate_completeness_score(data)
        quality_score = self._calculate_quality_score(data, errors, warnings)
        
        # Log de validation
        self._log_validation(data, errors, warnings)
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            completeness_score=completeness_score,
            quality_score=quality_score
        )
    
    def check_completeness(self, data: Dict[str, Any]) -> bool:
        """
        Vérifie que tous les champs obligatoires sont présents
        
        Args:
            data: Données à vérifier
        
        Returns:
            True si toutes les données obligatoires sont présentes
        """
        errors = self._check_completeness(data)
        return len(errors) == 0
    
    def check_value_ranges(self, data: Dict[str, Any]) -> List[ValidationError]:
        """
        Vérifie que les valeurs numériques sont dans les plages acceptables
        
        Args:
            data: Données à vérifier
        
        Returns:
            Liste des erreurs de plage
        """
        errors, _ = self._check_value_ranges(data)
        return errors
    
    def detect_outliers(self, df: pd.DataFrame, columns: Optional[List[str]] = None) -> pd.DataFrame:
        """
        Détecte les valeurs aberrantes avec la méthode IQR (Interquartile Range)
        
        Args:
            df: DataFrame à analyser
            columns: Colonnes à analyser (None = toutes les colonnes numériques)
        
        Returns:
            DataFrame avec colonne 'is_outlier' pour chaque ligne
        """
        if columns is None:
            columns = df.select_dtypes(include=[np.number]).columns.tolist()
        
        df_result = df.copy()
        df_result['is_outlier'] = False
        df_result['outlier_fields'] = ''
        
        outlier_fields_list = []
        
        for col in columns:
            if col not in df.columns:
                continue
            
            # Calculer Q1, Q3 et IQR
            Q1 = df[col].quantile(0.25)
            Q3 = df[col].quantile(0.75)
            IQR = Q3 - Q1
            
            # Définir les limites
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            
            # Identifier les outliers
            outliers = (df[col] < lower_bound) | (df[col] > upper_bound)
            
            # Marquer les outliers
            for idx in df[outliers].index:
                df_result.at[idx, 'is_outlier'] = True
                current_fields = df_result.at[idx, 'outlier_fields']
                if current_fields:
                    df_result.at[idx, 'outlier_fields'] = f"{current_fields}, {col}"
                else:
                    df_result.at[idx, 'outlier_fields'] = col
        
        return df_result
    
    def _check_completeness(self, data: Dict[str, Any]) -> List[ValidationError]:
        """Vérifie la complétude des données"""
        errors = []
        
        # Vérifier les données patient
        if 'patient' in data:
            patient = data['patient']
            for field in self.REQUIRED_FIELDS['patient']:
                if field not in patient or not patient[field]:
                    errors.append(ValidationError(
                        field=f"patient.{field}",
                        message=f"Le champ '{field}' est obligatoire",
                        level=ValidationLevel.ERROR
                    ))
        else:
            errors.append(ValidationError(
                field="patient",
                message="Les données patient sont manquantes",
                level=ValidationLevel.ERROR
            ))
        
        # Vérifier les symptômes
        if 'symptomes' in data and data['symptomes']:
            for i, symptome in enumerate(data['symptomes']):
                for field in self.REQUIRED_FIELDS['symptomes']:
                    if field not in symptome or not symptome[field]:
                        errors.append(ValidationError(
                            field=f"symptomes[{i}].{field}",
                            message=f"Le champ '{field}' est obligatoire pour le symptôme {i+1}",
                            level=ValidationLevel.ERROR
                        ))
        else:
            errors.append(ValidationError(
                field="symptomes",
                message="Au moins un symptôme est requis",
                level=ValidationLevel.ERROR
            ))
        
        # Vérifier les signes vitaux
        if 'signes_vitaux' in data:
            signes = data['signes_vitaux']
            for field in self.REQUIRED_FIELDS['signes_vitaux']:
                if field not in signes or signes[field] is None:
                    errors.append(ValidationError(
                        field=f"signes_vitaux.{field}",
                        message=f"Le champ '{field}' est obligatoire",
                        level=ValidationLevel.ERROR
                    ))
        else:
            errors.append(ValidationError(
                field="signes_vitaux",
                message="Les signes vitaux sont manquants",
                level=ValidationLevel.ERROR
            ))
        
        return errors
    
    def _check_value_ranges(self, data: Dict[str, Any]) -> Tuple[List[ValidationError], List[ValidationError]]:
        """Vérifie les plages de valeurs"""
        errors = []
        warnings = []
        
        # Vérifier les signes vitaux
        if 'signes_vitaux' in data:
            signes = data['signes_vitaux']
            for field, (min_val, max_val) in self.VALUE_RANGES.items():
                if field in signes and signes[field] is not None:
                    value = signes[field]
                    if value < min_val or value > max_val:
                        # Erreur si très hors plage (>50% de la plage)
                        range_size = max_val - min_val
                        deviation = abs(value - (min_val + max_val) / 2)
                        
                        if deviation > range_size * 0.5:
                            errors.append(ValidationError(
                                field=f"signes_vitaux.{field}",
                                message=f"Valeur hors plage acceptable: {value} (attendu: {min_val}-{max_val})",
                                level=ValidationLevel.ERROR,
                                current_value=value,
                                expected_range=(min_val, max_val)
                            ))
                        else:
                            warnings.append(ValidationError(
                                field=f"signes_vitaux.{field}",
                                message=f"Valeur inhabituelle: {value} (normal: {min_val}-{max_val})",
                                level=ValidationLevel.WARNING,
                                current_value=value,
                                expected_range=(min_val, max_val)
                            ))
        
        # Vérifier la durée des symptômes
        if 'symptomes' in data:
            for i, symptome in enumerate(data['symptomes']):
                if 'duree_jours' in symptome:
                    duree = symptome['duree_jours']
                    min_val, max_val = self.VALUE_RANGES['duree_jours']
                    if duree < min_val or duree > max_val:
                        warnings.append(ValidationError(
                            field=f"symptomes[{i}].duree_jours",
                            message=f"Durée inhabituelle: {duree} jours",
                            level=ValidationLevel.WARNING,
                            current_value=duree,
                            expected_range=(min_val, max_val)
                        ))
        
        return errors, warnings
    
    def _calculate_completeness_score(self, data: Dict[str, Any]) -> float:
        """Calcule le score de complétude (0-1)"""
        total_fields = 0
        filled_fields = 0
        
        # Compter les champs patient
        if 'patient' in data:
            patient = data['patient']
            for field in self.REQUIRED_FIELDS['patient']:
                total_fields += 1
                if field in patient and patient[field]:
                    filled_fields += 1
        
        # Compter les champs signes vitaux
        if 'signes_vitaux' in data:
            signes = data['signes_vitaux']
            for field in self.REQUIRED_FIELDS['signes_vitaux']:
                total_fields += 1
                if field in signes and signes[field] is not None:
                    filled_fields += 1
        
        # Compter les symptômes (au moins 1 requis)
        if 'symptomes' in data and data['symptomes']:
            filled_fields += 1
        total_fields += 1
        
        return filled_fields / total_fields if total_fields > 0 else 0.0
    
    def _calculate_quality_score(self, data: Dict[str, Any], errors: List[ValidationError], warnings: List[ValidationError]) -> float:
        """Calcule le score de qualité (0-1)"""
        # Score de base = complétude
        score = self._calculate_completeness_score(data)
        
        # Pénalité pour les erreurs
        error_penalty = len(errors) * 0.1
        warning_penalty = len(warnings) * 0.05
        
        score = max(0.0, score - error_penalty - warning_penalty)
        
        return score
    
    def _log_validation(self, data: Dict[str, Any], errors: List[ValidationError], warnings: List[ValidationError]):
        """Enregistre le log de validation"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'patient_id': data.get('patient', {}).get('id', 'unknown'),
            'errors_count': len(errors),
            'warnings_count': len(warnings),
            'is_valid': len(errors) == 0
        }
        self.validation_log.append(log_entry)
    
    def get_validation_statistics(self) -> Dict[str, Any]:
        """Retourne les statistiques de validation"""
        if not self.validation_log:
            return {
                'total_validations': 0,
                'valid_count': 0,
                'invalid_count': 0,
                'success_rate': 0.0
            }
        
        total = len(self.validation_log)
        valid = sum(1 for log in self.validation_log if log['is_valid'])
        
        return {
            'total_validations': total,
            'valid_count': valid,
            'invalid_count': total - valid,
            'success_rate': valid / total if total > 0 else 0.0,
            'avg_errors': sum(log['errors_count'] for log in self.validation_log) / total,
            'avg_warnings': sum(log['warnings_count'] for log in self.validation_log) / total
        }
