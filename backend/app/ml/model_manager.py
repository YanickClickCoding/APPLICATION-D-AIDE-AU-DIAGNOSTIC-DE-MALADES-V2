"""
Model Manager Module - Singleton pour gérer le cycle de vie du modèle
Gère le chargement, l'entraînement et les prédictions
"""
import os
import logging
from typing import Optional, Dict, List
from datetime import datetime
import pandas as pd
import numpy as np

from .data_preprocessing import DataPreprocessor
from .model_training import ModelTrainer
from .predictor import Predictor

logger = logging.getLogger(__name__)

# Chemins candidats pour trouver le dataset CSV
# Utiliser le dataset enrichi avec les 3 nouveaux examens microbiologiques (BAAR, Culture, Xpert)
_DATASET_FILENAME = "dataset_medical_robust_enhanced.csv"
_DATASET_FILENAME_FALLBACK = "dataset_medical_robust_10000_cas.csv"  # Fallback si le nouveau n'existe pas
_DATASET_CANDIDATES = [
    # Nouveau dataset enrichi (403 features)
    os.path.join("..", "les ressources dataset", _DATASET_FILENAME),
    os.path.join("..", "..", "les ressources dataset", _DATASET_FILENAME),
    os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))),
        "les ressources dataset",
        _DATASET_FILENAME,
    ),
    # Fallback vers l'ancien dataset (400 features)
    os.path.join("..", "les ressources dataset", _DATASET_FILENAME_FALLBACK),
    os.path.join("..", "..", "les ressources dataset", _DATASET_FILENAME_FALLBACK),
    os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))),
        "les ressources dataset",
        _DATASET_FILENAME_FALLBACK,
    ),
]


class ModelManager:
    """
    Singleton pour gérer le modèle ML
    Assure qu'un seul modèle est chargé en mémoire
    """

    _instance: Optional["ModelManager"] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self.preprocessor = DataPreprocessor()
        self.trainer = ModelTrainer()
        self.predictor: Optional[Predictor] = None
        self.model_loaded = False
        self.model_version = None
        self.model_metadata = {}
        self.normalization_params: Dict = {}
        self.dataset_means: Dict = {}
        self._initialized = True

        logger.info("🤖 ModelManager initialisé")

    # ------------------------------------------------------------------
    # Chargement du modèle
    # ------------------------------------------------------------------

    def load_latest_model(self, model_path: str = "./ml_models/") -> bool:
        """Charge le dernier modèle entraîné"""
        try:
            if not os.path.exists(model_path):
                logger.warning(f"⚠️ Dossier modèles introuvable: {model_path}")
                return False

            model_files = [f for f in os.listdir(model_path) if f.endswith(".joblib")]
            if not model_files:
                logger.warning("⚠️ Aucun modèle trouvé")
                return False

            model_files.sort(reverse=True)
            latest_model = os.path.join(model_path, model_files[0])

            self.trainer.load_model(latest_model)

            self.predictor = Predictor(
                model=self.trainer.model,
                label_encoder=self.trainer.label_encoder,
                feature_names=self.trainer.feature_names,
            )

            self.model_loaded = True
            self.model_version = model_files[0]
            self.model_metadata = self.trainer.training_history

            # Récupérer les params de normalisation sauvegardés avec le modèle
            self.normalization_params = self.trainer.normalization_params
            self.dataset_means = self.trainer.dataset_means

            # Fallback : calculer depuis le dataset si manquants
            if not self.normalization_params:
                logger.info("📊 Params de normalisation absents — calcul depuis le dataset...")
                self._load_normalization_from_dataset()

            logger.info(f"✅ Modèle chargé: {self.model_version}")
            logger.info(f"   Paramètres de normalisation: {len(self.normalization_params)} colonnes")
            return True

        except Exception as e:
            logger.error(f"❌ Erreur chargement modèle: {e}")
            return False

    # ------------------------------------------------------------------
    # Normalisation
    # ------------------------------------------------------------------

    def _find_dataset_path(self) -> Optional[str]:
        """Cherche le fichier CSV du dataset dans plusieurs emplacements"""
        for path in _DATASET_CANDIDATES:
            if os.path.exists(path):
                logger.info(f"✅ Dataset trouvé: {path}")
                return path
        logger.warning("⚠️ Dataset CSV introuvable dans les emplacements connus")
        return None

    def _load_normalization_from_dataset(self) -> bool:
        """
        Calcule les paramètres de normalisation (min/max) et les moyennes
        en chargeant le dataset CSV d'entraînement.
        Utilisé en fallback quand le modèle .joblib ne les contient pas.
        """
        try:
            dataset_path = self._find_dataset_path()
            if not dataset_path:
                logger.warning("⚠️ Utilisation de plages médicales par défaut pour la normalisation")
                self._use_default_normalization()
                return False

            logger.info(f"📂 Calcul normalisation depuis: {dataset_path}")
            df = self.preprocessor.load_dataset(dataset_path)
            df, _ = self.preprocessor.clean_data(df)
            # Pas besoin de create_features() : Vital_ et Lab_ sont déjà dans le CSV brut
            norm_cols = [c for c in df.columns if c.startswith("Vital_") or c.startswith("Lab_")]
            for col in norm_cols:
                if col in df.columns and pd.api.types.is_numeric_dtype(df[col]):
                    raw_min  = float(df[col].min())
                    raw_max  = float(df[col].max())
                    raw_mean = float(df[col].mean())
                    self.normalization_params[col] = {"min": raw_min, "max": raw_max}
                    # Stocker la moyenne NORMALISÉE pour l'utiliser directement comme défaut
                    if raw_max > raw_min:
                        self.dataset_means[col] = (raw_mean - raw_min) / (raw_max - raw_min)
                    else:
                        self.dataset_means[col] = 0.5

            # Moyennes pour les features non normalisées (valeurs brutes)
            for col in ["Age", "Duree_Symptomes_Jours", "nombre_symptomes"]:
                if col in df.columns:
                    self.dataset_means[col] = float(df[col].mean())

            logger.info(f"✅ Normalisation calculée: {len(self.normalization_params)} colonnes")
            return True

        except Exception as e:
            logger.error(f"❌ Erreur calcul normalisation depuis dataset: {e}")
            self._use_default_normalization()
            return False

    def _use_default_normalization(self):
        """Plages médicales de référence en dernier recours"""
        defaults = {
            "Vital_Tension Systolique (mmHg)":       {"min": 60,   "max": 250},
            "Vital_Tension Diastolique (mmHg)":      {"min": 30,   "max": 150},
            "Vital_Fréquence Cardiaque (bpm)":       {"min": 30,   "max": 200},
            "Vital_Fréquence Respiratoire (resp/min)": {"min": 8,  "max": 40},
            "Vital_Température (°C)":                {"min": 34,   "max": 42},
            "Vital_Saturation O2 (%)":               {"min": 70,   "max": 100},
            "Vital_IMC (kg/m²)":                     {"min": 10,   "max": 60},
            "Lab_Hémoglobine (g/dL)":                {"min": 3,    "max": 20},
            "Lab_Hématocrite (%)":                   {"min": 10,   "max": 65},
            "Lab_Globules Rouges (M/µL)":            {"min": 1,    "max": 8},
            "Lab_Globules Blancs (K/µL)":            {"min": 1,    "max": 50},
            "Lab_Neutrophiles (%)":                  {"min": 10,   "max": 95},
            "Lab_Lymphocytes (%)":                   {"min": 5,    "max": 60},
            "Lab_Monocytes (%)":                     {"min": 1,    "max": 20},
            "Lab_Eosinophiles (%)":                  {"min": 0,    "max": 30},
            "Lab_Basophiles (%)":                    {"min": 0,    "max": 5},
            "Lab_Plaquettes (K/µL)":                 {"min": 50,   "max": 600},
            "Lab_VGM (fL)":                          {"min": 60,   "max": 110},
            "Lab_CCMH (g/dL)":                       {"min": 28,   "max": 38},
            "Lab_Glucose (mg/dL)":                   {"min": 50,   "max": 500},
            "Lab_Glucose à jeun (mg/dL)":            {"min": 50,   "max": 500},
            "Lab_Glucose post-prandial (mg/dL)":     {"min": 70,   "max": 500},
            "Lab_HbA1c (%)":                         {"min": 3,    "max": 15},
            "Lab_Cholestérol total (mg/dL)":         {"min": 100,  "max": 400},
            "Lab_Cholestérol HDL (mg/dL)":           {"min": 20,   "max": 120},
            "Lab_Cholestérol LDL (mg/dL)":           {"min": 30,   "max": 300},
            "Lab_Triglycérides (mg/dL)":             {"min": 30,   "max": 800},
            "Lab_Acide urique (mg/dL)":              {"min": 1,    "max": 15},
            "Lab_Créatinine (mg/dL)":                {"min": 0.3,  "max": 15},
            "Lab_Urée (mg/dL)":                      {"min": 10,   "max": 200},
            "Lab_TFG (mL/min/1.73m²)":               {"min": 5,    "max": 120},
            "Lab_Sodium (mEq/L)":                    {"min": 120,  "max": 160},
            "Lab_Potassium (mEq/L)":                 {"min": 2,    "max": 8},
            "Lab_Chlore (mEq/L)":                    {"min": 90,   "max": 120},
            "Lab_Calcium (mg/dL)":                   {"min": 6,    "max": 14},
            "Lab_Phosphore (mg/dL)":                 {"min": 1,    "max": 8},
            "Lab_Magnésium (mg/dL)":                 {"min": 0.5,  "max": 4},
            "Lab_ALT/SGPT (U/L)":                    {"min": 5,    "max": 500},
            "Lab_AST/SGOT (U/L)":                    {"min": 5,    "max": 500},
            "Lab_Bilirubine totale (mg/dL)":         {"min": 0.1,  "max": 20},
            "Lab_Bilirubine conjuguée (mg/dL)":      {"min": 0,    "max": 15},
            "Lab_Bilirubine non-conjuguée (mg/dL)":  {"min": 0,    "max": 15},
            "Lab_Phosphatase alcaline (U/L)":        {"min": 20,   "max": 500},
            "Lab_GGT (U/L)":                         {"min": 5,    "max": 500},
            "Lab_Albumine (g/dL)":                   {"min": 1,    "max": 6},
            "Lab_Protéine totale (g/dL)":            {"min": 3,    "max": 10},
            "Lab_Globulines (g/dL)":                 {"min": 1,    "max": 6},
            "Lab_Ratio A/G":                         {"min": 0.5,  "max": 3},
            "Lab_CK (U/L)":                          {"min": 10,   "max": 5000},
            "Lab_Myoglobine (ng/mL)":                {"min": 5,    "max": 1000},
            "Lab_Troponine (ng/mL)":                 {"min": 0,    "max": 10},
            "Lab_BNP (pg/mL)":                       {"min": 0,    "max": 5000},
            "Lab_ProBNP (pg/mL)":                    {"min": 0,    "max": 10000},
            "Lab_PT/INR":                            {"min": 0.5,  "max": 5},
            "Lab_aPTT (sec)":                        {"min": 20,   "max": 100},
            "Lab_TT (sec)":                          {"min": 10,   "max": 60},
            "Lab_Fibrinogène (mg/dL)":               {"min": 100,  "max": 800},
            "Lab_CRP (mg/L)":                        {"min": 0,    "max": 300},
            "Lab_ESR (mm/h)":                        {"min": 0,    "max": 120},
            "Lab_PSA (ng/mL)":                       {"min": 0,    "max": 50},
        }
        for feat, params in defaults.items():
            if feat not in self.normalization_params:
                self.normalization_params[feat] = params

    def _normalize_value(self, feature_name: str, raw_value: float) -> float:
        """Normalise une valeur entre 0 et 1 selon les paramètres du dataset"""
        if feature_name in self.normalization_params:
            p = self.normalization_params[feature_name]
            min_v, max_v = p["min"], p["max"]
            if max_v > min_v:
                return float(max(0.0, min(1.0, (raw_value - min_v) / (max_v - min_v))))
        return float(raw_value)

    def _get_default_lab_value(self, feature_name: str) -> float:
        """
        Valeur par défaut pour un examen de labo absent.
        dataset_means stocke déjà des valeurs normalisées (0-1) pour les Lab_.
        """
        if feature_name in self.dataset_means:
            return float(self.dataset_means[feature_name])
        return 0.5

    # ------------------------------------------------------------------
    # Construction du vecteur de features
    # ------------------------------------------------------------------

    def _build_feature_vector(self, consultation_data: Dict) -> Dict:
        """
        Construit le vecteur complet des 400 features attendues par le modèle
        à partir des données brutes de consultation.

        Format attendu de consultation_data:
        {
            "age": int,
            "duree_symptomes_jours": int,
            "sexe": "M" | "F",
            "severite": "LEGER" | "MODERE" | "SEVERE",
            "vitaux": {
                "tension_systolique": float,       # mmHg
                "tension_diastolique": float,      # mmHg
                "frequence_cardiaque": float,      # bpm
                "frequence_respiratoire": float,   # /min
                "temperature": float,              # °C
                "saturation_oxygene": float,       # %
                "imc": float,                      # kg/m²
            },
            "symptomes": [list of str],  # noms des symptômes en français
            "examens": [
                {"nom": str, "valeur_numerique": float, "unite_mesure": str}
            ]
        }
        """
        features: Dict[str, float] = {}

        # --- Données démographiques ---
        age = float(consultation_data.get("age") or 40)
        features["Age"] = age
        features["Duree_Symptomes_Jours"] = float(consultation_data.get("duree_symptomes_jours") or 7)

        # --- Signes vitaux (normalisation 0-1) ---
        vitaux = consultation_data.get("vitaux") or {}

        vital_map = {
            "Vital_Tension Systolique (mmHg)":         vitaux.get("tension_systolique",     120),
            "Vital_Tension Diastolique (mmHg)":        vitaux.get("tension_diastolique",    80),
            "Vital_Fréquence Cardiaque (bpm)":         vitaux.get("frequence_cardiaque",    75),
            "Vital_Fréquence Respiratoire (resp/min)": vitaux.get("frequence_respiratoire", 16),
            "Vital_Température (°C)":                  vitaux.get("temperature",            37.0),
            "Vital_Saturation O2 (%)":                 vitaux.get("saturation_oxygene",     98.0),
            "Vital_IMC (kg/m²)":                       vitaux.get("imc",                    22.0),
        }
        for feat, raw in vital_map.items():
            features[feat] = self._normalize_value(feat, float(raw or 0))

        # --- Analyses de laboratoire (normalisation 0-1, défaut = moyenne dataset) ---
        exam_lookup: Dict[str, float] = {}
        for exam in consultation_data.get("examens") or []:
            nom = (exam.get("nom") or "").strip()
            unite = (exam.get("unite_mesure") or "").strip()
            valeur = exam.get("valeur_numerique")
            if valeur is None or nom == "":
                continue
            
            matched = False
            # Essayer les formats de nommage du dataset
            for candidate in [
                f"Lab_{nom} ({unite})" if unite else None,
                f"Lab_{nom}",
            ]:
                if candidate and candidate in self.trainer.feature_names:
                    exam_lookup[candidate] = float(valeur)
                    matched = True
                    break
            
            # Log warning if exam was not matched to any model feature
            if not matched:
                logger.warning(
                    f"⚠️ Examen '{nom}' (unité: '{unite}') ne correspond à aucune feature du modèle et sera ignoré. "
                    f"Features lab disponibles: {[f for f in self.trainer.feature_names if f.startswith('Lab_')][:10]}..."
                )

        for feat in self.trainer.feature_names:
            if feat.startswith("Lab_"):
                if feat in exam_lookup:
                    features[feat] = self._normalize_value(feat, exam_lookup[feat])
                else:
                    features[feat] = self._get_default_lab_value(feat)

        # --- Symptômes (one-hot) ---
        symptome_names: List[str] = consultation_data.get("symptomes") or []

        # Construire l'ensemble des feature-names de symptômes du patient
        patient_symptom_feats = {
            "symptom_" + nom.strip().replace(" ", "_").replace("/", "_")
            for nom in symptome_names
            if nom
        }

        features["nombre_symptomes"] = float(len(symptome_names))

        for feat in self.trainer.feature_names:
            if feat.startswith("symptom_"):
                features[feat] = 1.0 if feat in patient_symptom_feats else 0.0

        # --- Features dérivées (valeurs brutes, sans normalisation) ---
        if age <= 12:
            features["categorie_age"] = 0.0
        elif age <= 18:
            features["categorie_age"] = 1.0
        elif age <= 60:
            features["categorie_age"] = 2.0
        else:
            features["categorie_age"] = 3.0

        fc_raw  = float(vitaux.get("frequence_cardiaque",  75)  or 75)
        o2_raw  = float(vitaux.get("saturation_oxygene",  98.0) or 98.0)
        temp_raw = float(vitaux.get("temperature",         37.0) or 37.0)

        features["ratio_fc_o2"] = fc_raw / (o2_raw + 1.0)
        features["score_risque"] = (
            (2.0 if temp_raw > 38.5 else 0.0)
            + (3.0 if o2_raw < 95.0 else 0.0)
            + float(len(symptome_names))
        )

        sexe = consultation_data.get("sexe") or "M"
        features["Sexe_encoded"] = 1.0 if sexe.upper() in ("M", "H") else 0.0

        sev_map = {
            "LEGER": 1.0, "Légère": 1.0, "légère": 1.0, "léger": 1.0,
            "MODERE": 2.0, "Modérée": 2.0, "modérée": 2.0, "modéré": 2.0,
            "SEVERE": 3.0, "Sévère": 3.0, "sévère": 3.0,
            "Critique": 4.0, "critique": 4.0, "CRITIQUE": 4.0,
        }
        severite = consultation_data.get("severite") or "MODERE"
        features["Severite_encoded"] = sev_map.get(severite, 2.0)

        return features

    # ------------------------------------------------------------------
    # Entraînement
    # ------------------------------------------------------------------

    def train_new_model(
        self,
        dataset_path: str,
        n_estimators: int = 100,
        max_depth: int = 20,
        save: bool = True,
    ) -> Dict:
        """Entraîne un nouveau modèle sur le dataset"""
        try:
            logger.info("🚀 Début entraînement nouveau modèle...")
            logger.info(f"   Dataset: {dataset_path}")

            # 1. Charger
            df = self.preprocessor.load_dataset(dataset_path)

            # 2. Nettoyage
            df, cleaning_log = self.preprocessor.clean_data(df)

            # 3. Feature engineering
            df = self.preprocessor.create_features(df)

            # 4. Normalisation des colonnes Vital_ et Lab_
            numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
            if "Maladie_Diagnostic" in numeric_cols:
                numeric_cols.remove("Maladie_Diagnostic")

            cols_to_normalize = [
                c for c in numeric_cols
                if c.startswith("Vital_") or c.startswith("Lab_")
            ]
            if cols_to_normalize:
                df, _ = self.preprocessor.normalize_data(df, cols_to_normalize)

            # Capturer les paramètres de normalisation (contiennent les min/max RAW)
            self.normalization_params = self.preprocessor.normalization_params.copy()
            # Après normalize_data(), les colonnes Vital_ et Lab_ sont déjà en 0-1
            # → leurs moyennes dans df sont déjà normalisées, on les stocke telles quelles
            for col in df.columns:
                if col != "Maladie_Diagnostic" and pd.api.types.is_numeric_dtype(df[col]):
                    self.dataset_means[col] = float(df[col].mean())

            # Transmettre au trainer pour la sauvegarde
            self.trainer.normalization_params = self.normalization_params
            self.trainer.dataset_means = self.dataset_means

            # 5. Garder seulement target + colonnes numériques
            cols_to_keep = ["Maladie_Diagnostic"] + [
                c for c in df.select_dtypes(include=[np.number]).columns
                if c != "Maladie_Diagnostic" and c != "ID"
            ]
            df = df[[c for c in cols_to_keep if c in df.columns]]

            # 6. Préparer X et y
            X, y = self.preprocessor.prepare_xy(df, target_column="Maladie_Diagnostic")

            # 7. Entraîner
            training_results = self.trainer.train(
                X, y, n_estimators=n_estimators, max_depth=max_depth
            )

            # 8. Évaluer
            from sklearn.model_selection import train_test_split

            y_encoded = self.trainer.label_encoder.transform(y)
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42, stratify=y_encoded
            )
            evaluation_results = self.trainer.evaluate(X_test, y_test)

            # 9. Sauvegarder
            if save:
                model_path = self.trainer.save_model(version="1.0")
                training_results["model_path"] = model_path

            # 10. Activer le predictor
            self.predictor = Predictor(
                model=self.trainer.model,
                label_encoder=self.trainer.label_encoder,
                feature_names=self.trainer.feature_names,
            )
            self.model_loaded = True
            self.model_metadata = training_results

            logger.info("✅ Entraînement terminé avec succès!")
            return {"training": training_results, "evaluation": evaluation_results, "success": True}

        except Exception as e:
            logger.error(f"❌ Erreur entraînement: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return {"success": False, "error": str(e)}

    # ------------------------------------------------------------------
    # Prédiction
    # ------------------------------------------------------------------

    def predict(self, consultation_data: Dict) -> Dict:
        """
        Fait une prédiction à partir des données structurées de consultation.

        consultation_data: voir _build_feature_vector() pour le format attendu.
        """
        if not self.model_loaded or self.predictor is None:
            raise ValueError("Modèle non chargé. Appelez load_latest_model() d'abord.")

        try:
            features = self._build_feature_vector(consultation_data)

            df = pd.DataFrame([features])

            # Compléter les features manquantes avec 0.0
            for feat in self.trainer.feature_names:
                if feat not in df.columns:
                    df[feat] = 0.0

            # Ordonner selon l'ordre d'entraînement
            df = df[self.trainer.feature_names]

            return self.predictor.predict(df)

        except Exception as e:
            logger.error(f"❌ Erreur prédiction: {e}")
            import traceback
            logger.error(traceback.format_exc())
            raise

    def explain_prediction(self, consultation_data: Dict) -> Dict:
        """Explique une prédiction (top features)"""
        if not self.model_loaded or self.predictor is None:
            raise ValueError("Modèle non chargé.")

        try:
            features = self._build_feature_vector(consultation_data)
            df = pd.DataFrame([features])

            for feat in self.trainer.feature_names:
                if feat not in df.columns:
                    df[feat] = 0.0

            df = df[self.trainer.feature_names]
            return self.predictor.explain_prediction(df)

        except Exception as e:
            logger.error(f"❌ Erreur explication: {e}")
            raise

    def get_model_info(self) -> Dict:
        return {
            "loaded": self.model_loaded,
            "version": self.model_version,
            "metadata": self.model_metadata,
            "n_features": len(self.trainer.feature_names) if self.trainer.feature_names else 0,
            "n_classes": len(self.trainer.label_encoder.classes_) if self.trainer.label_encoder else 0,
            "classes": self.trainer.label_encoder.classes_.tolist() if self.trainer.label_encoder else [],
            "normalization_loaded": len(self.normalization_params) > 0,
        }

    def get_supported_lab_features(self) -> List[str]:
        """
        Retourne la liste de toutes les features de laboratoire supportées par le modèle.
        
        Returns:
            List[str]: Liste des noms de features commençant par "Lab_"
        """
        if not self.trainer.feature_names:
            return []
        return [f for f in self.trainer.feature_names if f.startswith("Lab_")]

    def retrain_with_new_data(self, new_data_path: str) -> Dict:
        """Réentraîne le modèle avec de nouvelles données"""
        logger.info("🔄 Réentraînement avec nouvelles données...")
        results = self.train_new_model(new_data_path, save=True)
        if results["success"]:
            logger.info("✅ Réentraînement réussi!")
        return results


# Instance globale (singleton)
model_manager = ModelManager()
