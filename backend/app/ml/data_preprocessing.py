"""
Data Preprocessing Module (US-006 à US-011)
Nettoyage, normalisation, détection d'anomalies, feature engineering
"""
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler, LabelEncoder
from sklearn.impute import SimpleImputer
from typing import Dict, Tuple, List, Optional
import json
import logging

logger = logging.getLogger(__name__)


class DataPreprocessor:
    """
    Classe pour le prétraitement des données médicales
    Implémente les US-006 à US-011 avec méthodes étendues
    """
    
    def __init__(self):
        self.scaler = MinMaxScaler()
        self.imputer = SimpleImputer(strategy='mean')
        self.label_encoders: Dict[str, LabelEncoder] = {}
        self.feature_names: List[str] = []
        self.normalization_params: Dict[str, Dict[str, float]] = {}
        
    def load_dataset(self, filepath: str) -> pd.DataFrame:
        """
        Charge le dataset depuis un fichier CSV
        """
        try:
            df = pd.read_csv(filepath)
            logger.info(f"Dataset chargé: {len(df)} lignes, {len(df.columns)} colonnes")
            return df
        except Exception as e:
            logger.error(f"Erreur lors du chargement du dataset: {e}")
            raise
    
    def clean_missing_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Impute les valeurs manquantes avec SimpleImputer
        
        Stratégie:
        - Colonnes numériques: moyenne
        - Colonnes catégoriques: mode (valeur la plus fréquente)
        
        Returns:
            DataFrame avec valeurs manquantes imputées
        """
        df_clean = df.copy()
        
        # Imputation des colonnes numériques
        numeric_cols = df_clean.select_dtypes(include=[np.number]).columns.tolist()
        if numeric_cols:
            imputer_numeric = SimpleImputer(strategy='mean')
            df_clean[numeric_cols] = imputer_numeric.fit_transform(df_clean[numeric_cols])
            logger.info(f"Imputation moyenne sur {len(numeric_cols)} colonnes numériques")
        
        # Imputation des colonnes catégoriques
        categorical_cols = df_clean.select_dtypes(include=['object']).columns.tolist()
        if categorical_cols:
            imputer_categorical = SimpleImputer(strategy='most_frequent')
            df_clean[categorical_cols] = imputer_categorical.fit_transform(df_clean[categorical_cols])
            logger.info(f"Imputation mode sur {len(categorical_cols)} colonnes catégoriques")
        
        return df_clean
    
    def clean_data(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict]:
        """
        US-006: Nettoyage des données manquantes (méthode legacy)
        
        Règles:
        - Symptômes manquants → 0 (NON)
        - Analyses manquantes → moyenne
        - Alerter si > 30% de données manquantes
        """
        cleaning_log = {
            "missing_before": df.isnull().sum().to_dict(),
            "actions": []
        }
        
        # Calculer le pourcentage de données manquantes
        missing_percentage = (df.isnull().sum().sum() / (df.shape[0] * df.shape[1])) * 100
        
        if missing_percentage > 30:
            logger.warning(f"⚠️ {missing_percentage:.2f}% de données manquantes (seuil: 30%)")
            cleaning_log["warning"] = f"Trop de données manquantes: {missing_percentage:.2f}%"
        
        # Utiliser la nouvelle méthode clean_missing_data
        df_clean = self.clean_missing_data(df)
        
        # Log des actions
        for col in df.columns:
            missing_count = df[col].isnull().sum()
            if missing_count > 0:
                cleaning_log["actions"].append(f"{col}: {missing_count} valeurs imputées")
        
        logger.info(f"Nettoyage terminé: {len(cleaning_log['actions'])} actions effectuées")
        return df_clean, cleaning_log
    
    def detect_outliers(self, df: pd.DataFrame, columns: List[str]) -> Tuple[pd.DataFrame, Dict]:
        """
        US-008: Détection des anomalies (outliers)
        
        Utilise la méthode IQR (Interquartile Range)
        """
        outliers_log = {"detected": [], "count": 0}
        
        for col in columns:
            if col not in df.columns:
                continue
                
            Q1 = df[col].quantile(0.25)
            Q3 = df[col].quantile(0.75)
            IQR = Q3 - Q1
            
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            
            outliers = df[(df[col] < lower_bound) | (df[col] > upper_bound)]
            
            if len(outliers) > 0:
                outliers_log["detected"].append({
                    "column": col,
                    "count": len(outliers),
                    "bounds": {"lower": float(lower_bound), "upper": float(upper_bound)}
                })
                outliers_log["count"] += len(outliers)
                
                # Marquer les outliers (optionnel: les remplacer par la médiane)
                df.loc[(df[col] < lower_bound) | (df[col] > upper_bound), f"{col}_outlier"] = 1
        
        logger.info(f"Détection d'anomalies: {outliers_log['count']} outliers trouvés")
        return df, outliers_log
    
    def normalize_features(self, df: pd.DataFrame, columns: Optional[List[str]] = None) -> pd.DataFrame:
        """
        Normalise les features numériques à l'échelle 0-1 avec MinMaxScaler
        
        Args:
            df: DataFrame à normaliser
            columns: Liste des colonnes à normaliser (None = toutes les colonnes numériques)
        
        Returns:
            DataFrame avec features normalisées
        """
        df_norm = df.copy()
        
        if columns is None:
            columns = df_norm.select_dtypes(include=[np.number]).columns.tolist()
        
        # Filtrer les colonnes qui existent
        columns = [col for col in columns if col in df_norm.columns]
        
        if columns:
            # Utiliser MinMaxScaler pour normalisation 0-1
            scaler = MinMaxScaler()
            df_norm[columns] = scaler.fit_transform(df_norm[columns])
            
            # Sauvegarder les paramètres pour inverse transform
            for i, col in enumerate(columns):
                self.normalization_params[col] = {
                    "min": float(scaler.data_min_[i]),
                    "max": float(scaler.data_max_[i])
                }
            
            logger.info(f"Normalisation 0-1 effectuée sur {len(columns)} colonnes")
        
        return df_norm
    
    def normalize_data(self, df: pd.DataFrame, columns: List[str]) -> Tuple[pd.DataFrame, Dict]:
        """
        US-007: Normalisation des données (0-1) - méthode legacy
        
        Sauvegarde les paramètres pour pouvoir inverser la normalisation
        """
        df_norm = self.normalize_features(df, columns)
        return df_norm, self.normalization_params
    
    def encode_categorical(self, df: pd.DataFrame, columns: Optional[List[str]] = None) -> pd.DataFrame:
        """
        Encode les variables catégoriques avec LabelEncoder
        
        Args:
            df: DataFrame à encoder
            columns: Liste des colonnes à encoder (None = toutes les colonnes object)
        
        Returns:
            DataFrame avec variables catégoriques encodées
        """
        df_encoded = df.copy()
        
        if columns is None:
            columns = df_encoded.select_dtypes(include=['object']).columns.tolist()
        
        # Filtrer les colonnes qui existent
        columns = [col for col in columns if col in df_encoded.columns]
        
        for col in columns:
            le = LabelEncoder()
            df_encoded[col] = le.fit_transform(df_encoded[col].astype(str))
            
            # Sauvegarder l'encodeur pour décodage ultérieur
            self.label_encoders[col] = le
            logger.debug(f"Encodage {col}: {len(le.classes_)} classes")
        
        logger.info(f"Encodage catégorique effectué sur {len(columns)} colonnes")
        return df_encoded
    
    def create_derived_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Crée de nouvelles features dérivées
        
        Features créées:
        - total_symptomes: nombre total de symptômes
        - categorie_age: catégorie d'âge (enfant, ado, adulte, senior)
        - ratio_fc_o2: ratio fréquence cardiaque / saturation O2
        - score_risque: score de risque basé sur signes vitaux
        - imc: indice de masse corporelle (si poids et taille disponibles)
        
        Returns:
            DataFrame avec nouvelles features
        """
        df_derived = df.copy()
        
        # Total symptômes
        if 'Symptomes_Rapportes' in df_derived.columns:
            df_derived['total_symptomes'] = df_derived['Symptomes_Rapportes'].apply(
                lambda x: len(str(x).split(',')) if pd.notna(x) and str(x) != 'Unknown' else 0
            )
        
        # Catégorie d'âge
        if 'Age' in df_derived.columns:
            df_derived['categorie_age'] = pd.cut(
                df_derived['Age'],
                bins=[0, 12, 18, 60, 120],
                labels=[0, 1, 2, 3]  # Enfant, Ado, Adulte, Senior
            ).astype(float)
        
        # Ratio FC/O2
        if 'Vital_Fréquence Cardiaque (bpm)' in df_derived.columns and 'Vital_Saturation O2 (%)' in df_derived.columns:
            df_derived['ratio_fc_o2'] = df_derived['Vital_Fréquence Cardiaque (bpm)'] / (df_derived['Vital_Saturation O2 (%)'] + 1)
        
        # Score de risque
        if 'Vital_Température (°C)' in df_derived.columns and 'Vital_Saturation O2 (%)' in df_derived.columns:
            df_derived['score_risque'] = (
                (df_derived['Vital_Température (°C)'] > 38.5).astype(int) * 2 +
                (df_derived['Vital_Saturation O2 (%)'] < 95).astype(int) * 3
            )
            if 'total_symptomes' in df_derived.columns:
                df_derived['score_risque'] += df_derived['total_symptomes']
        
        # IMC (Indice de Masse Corporelle)
        if 'poids' in df_derived.columns and 'taille' in df_derived.columns:
            # Convertir taille en mètres si en cm
            taille_m = df_derived['taille'] / 100 if df_derived['taille'].mean() > 3 else df_derived['taille']
            df_derived['imc'] = df_derived['poids'] / (taille_m ** 2)
        
        logger.info(f"Features dérivées créées: {[col for col in df_derived.columns if col not in df.columns]}")
        return df_derived
    
    def create_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        US-010: Création de nouvelles features
        
        Features créées basées sur le dataset réel:
        - Extraction des symptômes individuels (one-hot encoding)
        - Nombre de symptômes
        - Catégorie d'âge
        - Ratios et scores de risque
        """
        # Extraire et encoder les symptômes individuels
        if 'Symptomes_Rapportes' in df.columns:
            # Compter le nombre de symptômes
            df['nombre_symptomes'] = df['Symptomes_Rapportes'].apply(
                lambda x: len(str(x).split(',')) if pd.notna(x) and str(x) != 'Unknown' else 0
            )
            
            # Créer des colonnes binaires pour chaque symptôme unique
            # Collecter tous les symptômes uniques
            all_symptoms = set()
            for symptoms_str in df['Symptomes_Rapportes'].dropna():
                if str(symptoms_str) != 'Unknown':
                    symptoms = [s.strip() for s in str(symptoms_str).split(',')]
                    all_symptoms.update(symptoms)
            
            # Créer une colonne binaire pour chaque symptôme
            logger.info(f"Création de {len(all_symptoms)} colonnes de symptômes...")
            for symptom in all_symptoms:
                col_name = f'symptom_{symptom.replace(" ", "_").replace("/", "_")}'
                df[col_name] = df['Symptomes_Rapportes'].apply(
                    lambda x: 1 if pd.notna(x) and symptom in str(x) else 0
                )
        
        # Catégorie d'âge
        if 'Age' in df.columns:
            df['categorie_age'] = pd.cut(
                df['Age'],
                bins=[0, 12, 18, 60, 120],
                labels=[0, 1, 2, 3]  # Enfant, Ado, Adulte, Senior (numeric)
            )
            df['categorie_age'] = df['categorie_age'].astype(float)
        
        # Ratio FC/O2 si disponible
        if 'Vital_Fréquence Cardiaque (bpm)' in df.columns and 'Vital_Saturation O2 (%)' in df.columns:
            df['ratio_fc_o2'] = df['Vital_Fréquence Cardiaque (bpm)'] / (df['Vital_Saturation O2 (%)'] + 1)
        
        # Score de risque basé sur température et saturation
        if 'Vital_Température (°C)' in df.columns and 'Vital_Saturation O2 (%)' in df.columns:
            df['score_risque'] = (
                (df['Vital_Température (°C)'] > 38.5).astype(int) * 2 +
                (df['Vital_Saturation O2 (%)'] < 95).astype(int) * 3
            )
            if 'nombre_symptomes' in df.columns:
                df['score_risque'] += df['nombre_symptomes']
        
        # Encoder le sexe en numérique
        if 'Sexe' in df.columns:
            df['Sexe_encoded'] = df['Sexe'].map({'M': 1, 'F': 0, 'H': 1}).fillna(0)
        
        # Encoder la sévérité si présente
        if 'Severite' in df.columns:
            severity_map = {'Légère': 1, 'Modérée': 2, 'Sévère': 3, 'Critique': 4}
            df['Severite_encoded'] = df['Severite'].map(severity_map).fillna(0)
        
        logger.info(f"Features créées: symptômes individuels, nombre_symptomes, categorie_age, ratio_fc_o2, score_risque, encodages")
        return df
    
    def prepare_xy(self, df: pd.DataFrame, target_column: str = 'diagnostic') -> Tuple[pd.DataFrame, pd.Series]:
        """
        Prépare les features (X) et la target (y).
        Inclut les symptômes binaires (symptom_*), features dérivées et colonnes numériques.
        """
        if target_column not in df.columns:
            raise ValueError(f"Colonne target '{target_column}' introuvable")

        y = df[target_column]
        X = df.drop(columns=[target_column])

        # Créer les features symptômes + dérivées (ratio_fc_o2, score_risque, etc.)
        X = self.create_features(X)

        # Garder seulement les colonnes numériques (symptom_* sont déjà binaires = numériques)
        X = X.select_dtypes(include=[np.number])

        self.feature_names = X.columns.tolist()

        logger.info(f"Données préparées: X={X.shape}, y={y.shape}")
        return X, y
    
    def generate_quality_report(self, df: pd.DataFrame) -> Dict:
        """
        US-011: Rapport de qualité des données
        """
        report = {
            "total_rows": len(df),
            "total_columns": len(df.columns),
            "completeness": {},
            "statistics": {},
            "correlations": {},
            "quality_score": 0.0
        }
        
        # Complétude par colonne
        for col in df.columns:
            completeness = (1 - df[col].isnull().sum() / len(df)) * 100
            report["completeness"][col] = round(completeness, 2)
        
        # Statistiques pour colonnes numériques
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            report["statistics"][col] = {
                "mean": float(df[col].mean()),
                "min": float(df[col].min()),
                "max": float(df[col].max()),
                "std": float(df[col].std())
            }
        
        # Score de qualité global
        avg_completeness = np.mean(list(report["completeness"].values()))
        report["quality_score"] = round(avg_completeness, 2)
        
        if report["quality_score"] < 80:
            report["alert"] = f"⚠️ Qualité des données faible: {report['quality_score']}%"
        
        logger.info(f"Rapport de qualité généré: score={report['quality_score']}%")
        return report
