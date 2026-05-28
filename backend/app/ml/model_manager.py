"""
Model Manager Module - Singleton pour gérer le cycle de vie du modèle
Gère le chargement, l'entraînement et les prédictions
"""
import os
import json
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
# Traduction des noms de maladies : labels internes du modèle → noms affichés
DISEASE_DISPLAY_NAMES: dict[str, str] = {
    "Malaria": "Paludisme",
}

# ============================================================
# TABLE DE SYNONYMES — normalise TOUS les termes alternatifs
# vers le nom canonique utilisé dans le dataset d'entraînement.
# Clés en minuscules, valeurs = nom exact du dataset.
# ============================================================
SYNONYMES_SYMPTOMES: dict[str, str] = {
    # ── RÉNAUX / ŒDÈMES ──────────────────────────────────────
    "gonflement des pieds":              "Gonflement des chevilles",
    "pieds gonflés":                     "Gonflement des chevilles",
    "chevilles gonflées":                "Gonflement des chevilles",
    "oedème des pieds":                  "Gonflement des chevilles",
    "oedème des chevilles":              "Gonflement des chevilles",
    "œdème des pieds":                   "Gonflement des chevilles",
    "œdème des chevilles":               "Gonflement des chevilles",
    "jambes gonflées":                   "Gonflement des chevilles",
    "gonflement des membres inférieurs": "Gonflement des chevilles",
    "rétention d'eau":                   "Oedèmes",
    "rétention hydrique":                "Oedèmes",
    "corps gonflé":                      "Oedèmes",
    "gonflement du corps":               "Oedèmes",
    "absence d'urine":                   "Anurie",
    "pas d'urine":                       "Anurie",
    "urine absente":                     "Anurie",
    "pas uriner":                        "Anurie",
    "peu d'urine":                       "Oligurie ou polyurie",
    "urine rare":                        "Oligurie ou polyurie",
    "urine abondante":                   "Oligurie ou polyurie",
    "polyurie":                          "Oligurie ou polyurie",
    "oligurie":                          "Oligurie ou polyurie",
    "urine écumeuse":                    "Urine mousseuse",
    "urine avec mousse":                 "Urine mousseuse",
    "urine trouble":                     "Urine mousseuse",
    "sang dans les urines":              "Hématurie",
    "urines rouges":                     "Hématurie",
    "urines roses":                      "Hématurie",
    "uriner la nuit":                    "Nycturie",
    "se lever la nuit pour uriner":      "Nycturie",
    "odeur d'urine dans l'haleine":      "Haleine urémique",
    "haleine ammoniacale":               "Haleine urémique",
    "odeur ammoniaque":                  "Haleine urémique",
    "mauvaise haleine":                  "Haleine urémique",
    "goût amer":                         "Goût métallique",
    "arrière-goût métallique":           "Goût métallique",
    "crampes dans les jambes":           "Crampes musculaires",
    "crampes nocturnes":                 "Crampes musculaires",
    "fourmillements":                    "Engourdissements",
    "fourmillements dans les membres":   "Engourdissements",
    "engourdissement":                   "Engourdissements",
    "picotements":                       "Engourdissements",
    "peau qui gratte":                   "Démangeaisons",
    "prurit cutané":                     "Démangeaisons",
    "peau grise":                        "Teint grisâtre",
    "teint pâle grisâtre":               "Teint grisâtre",

    # ── CARDIOVASCULAIRES ─────────────────────────────────────
    "point dans la poitrine":            "Douleur thoracique",
    "douleur dans la poitrine":          "Douleur thoracique",
    "poitrine serrée":                   "Oppression thoracique",
    "chest pain":                        "Douleur thoracique",
    "battements du cœur rapides":        "Palpitations",
    "cœur qui bat vite":                 "Palpitations",
    "rythme cardiaque irrégulier":       "Palpitations",
    "battements irréguliers":            "Palpitations",
    "cœur qui saute":                    "Palpitations",
    "difficultés à respirer":            "Essoufflement",
    "manque d'air":                      "Essoufflement",
    "souffle court":                     "Essoufflement",
    "essoufflement":                     "Essoufflement",
    "dyspnée":                           "Essoufflement",
    "pression sanguine élevée":          "Hypertension",
    "tension artérielle élevée":         "Hypertension",
    "tension haute":                     "Hypertension",
    "jambe rouge et gonflée":            "Gonflement d'un membre",
    "jambe enflée":                      "Gonflement d'un membre",

    # ── RESPIRATOIRES ─────────────────────────────────────────
    "crachat":                           "Crachats purulents",
    "crachats":                          "Crachats purulents",
    "expectoration":                     "Expectorations",
    "mucus":                             "Expectorations",
    "toux grasse":                       "Toux productive",
    "toux avec mucus":                   "Toux productive",
    "sifflement en respirant":           "Respiration sifflante",
    "respiration difficile":             "Essoufflement",
    "halètement":                        "Essoufflement",
    "apnée":                             "Apnée du sommeil",
    "ronflement fort":                   "Ronflement",

    # ── DIGESTIFS ─────────────────────────────────────────────
    "douleur au ventre":                 "Douleurs abdominales",
    "ventre qui fait mal":               "Douleurs abdominales",
    "mal au ventre":                     "Douleurs abdominales",
    "crampes au ventre":                 "Crampes abdominales",
    "sang dans les selles":              "Diarrhée sanguinolente",
    "selles sanglantes":                 "Diarrhée sanguinolente",
    "selles noires":                     "Méléna",
    "sang noir dans les selles":         "Méléna",
    "vomissements de sang":              "Hématémèse",
    "vomir du sang":                     "Hématémèse",
    "brûlures à l'estomac":             "Brûlures d'estomac",
    "acidité":                           "Brûlures d'estomac",
    "reflux acide":                      "Régurgitation",
    "remontées acides":                  "Régurgitation",
    "remontées gastriques":              "Régurgitation",
    "reflux":                            "Reflux gastro-esophagien",
    "aller aux toilettes souvent":       "Diarrhée",
    "selles liquides":                   "Diarrhée",
    "pas de selles":                     "Constipation",
    "difficultés à déféquer":            "Constipation",
    "ventre gonflé":                     "Ballonnements",
    "ballonnement":                      "Ballonnements",

    # ── NEUROLOGIQUES ─────────────────────────────────────────
    "mal de tête":                       "Maux de tête",
    "mal à la tête":                     "Maux de tête",
    "céphalée":                          "Maux de tête",
    "céphalées":                         "Maux de tête",
    "migraine":                          "Maux de tête sévères",
    "tête qui tourne":                   "Vertiges",
    "vertiges":                          "Vertiges",
    "étourdissements":                   "Vertiges",
    "trous de mémoire":                  "Perte de mémoire",
    "oublis fréquents":                  "Perte de mémoire",
    "crise d'épilepsie":                 "Convulsions",
    "crise convulsive":                  "Convulsions",
    "attaque épileptique":               "Convulsions",
    "tremblements des mains":            "Tremblements",
    "mains qui tremblent":               "Tremblements",
    "brûlures dans les pieds":           "Engourdissement des pieds",
    "pieds qui brûlent":                 "Engourdissement des pieds",
    "picotements dans les pieds":        "Engourdissement des pieds",

    # ── ENDOCRINIENNES ────────────────────────────────────────
    "soif anormale":                     "Soif excessive",
    "soif intense":                      "Soif excessive",
    "grande soif":                       "Soif excessive",
    "uriner souvent":                    "Urination fréquente",
    "envies fréquentes d'uriner":        "Urination fréquente",
    "polyurie fréquente":               "Urination fréquente",
    "grossir sans raison":               "Prise de poids",
    "prise de poids inexpliquée":        "Prise de poids",
    "maigrir sans raison":               "Perte de poids",
    "perte de poids inexpliquée":        "Perte de poids",
    "pas d'appétit":                     "Anorexie",
    "manque d'appétit":                  "Perte d'appétit",
    "sans appétit":                      "Perte d'appétit",

    # ── DOULEURS GÉNÉRALES ────────────────────────────────────
    "courbatures":                       "Douleurs musculaires",
    "douleurs dans les muscles":         "Douleurs musculaires",
    "douleurs dans les os":              "Douleurs osseuses",
    "douleurs articulaires":             "Douleurs articulaires",
    "articulations douloureuses":        "Douleurs articulaires",
    "douleur aux articulations":         "Douleurs articulaires",
    "douleur au dos":                    "Douleur lombaire",
    "mal de dos":                        "Douleur lombaire",
    "douleur dans le dos":               "Douleur lombaire",
    "douleur au flanc":                  "Douleur lombaire",
    "douleur au rein":                   "Douleur lombaire",

    # ── CUTANÉS ───────────────────────────────────────────────
    "peau sèche":                        "Peau sèche",
    "peau qui pèle":                     "Desquamation",
    "peau qui s'écaille":                "Desquamation",
    "plaques rouges":                    "Éruption cutanée",
    "rougeurs cutanées":                 "Éruption cutanée",
    "boutons":                           "Pustules",
    "points noirs":                      "Comédones",
    "taches blanches sur la peau":       "Taches blanches",
    "peau décolorée":                    "Dépigmentation",
    "ampoules":                          "Bulles",
    "cloques":                           "Vésicules",

    # ── OCULAIRES ─────────────────────────────────────────────
    "vue brouillée":                     "Vision floue",
    "trouble de la vision":              "Vision floue",
    "voir flou":                         "Vision floue",
    "double vision":                     "Diplopie monoculaire",
    "voir double":                       "Diplopie monoculaire",
    "mouches volantes":                  "Flotteurs",
    "points noirs dans la vision":       "Flotteurs",
    "yeux qui piquent":                  "Démangeaisons oculaires",
    "yeux qui brûlent":                  "Démangeaisons oculaires",
    "yeux qui coulent":                  "Larmoiement",
    "larmes":                            "Larmoiement",
    "yeux rouges":                       "Rougeur oculaire",

    # ── GÉNÉRAUX ──────────────────────────────────────────────
    "fatigue intense":                   "Fatigue",
    "épuisement":                        "Fatigue",
    "se sentir fatigué":                 "Fatigue",
    "faiblesse générale":                "Faiblesse",
    "fièvre":                            "Fièvre",
    "température élevée":                "Fièvre",
    "fièvre élevée":                     "Fièvre élevée",
    "grosse fièvre":                     "Fièvre élevée",
    "frissons":                          "Frissons",
    "avoir froid":                       "Frissons",
    "nausée":                            "Nausées",
    "envie de vomir":                    "Nausées",
    "mal au cœur":                       "Nausées",
    "vomissement":                       "Vomissements",
    "vomir":                             "Vomissements",
    "perte de connaissance":             "Perte de conscience",
    "évanouissement":                    "Syncope",
    "tomber dans les pommes":            "Syncope",
    "ganglions":                         "Ganglions enflés",
    "ganglions gonflés":                 "Ganglions enflés",
    "sueurs nocturnes":                  "Sueurs nocturnes",
    "transpiration nocturne":            "Sueurs nocturnes",
    "pâleur":                            "Pâleur",
    "teint pâle":                        "Pâleur",
    "jaunisse":                          "Ictère",
    "peau jaune":                        "Ictère",
    "yeux jaunes":                       "Ictère",
    "saignement de nez":                 "Épistaxis",
    "saignement du nez":                 "Épistaxis",
    "nez qui saigne":                    "Épistaxis",
    "confusion mentale":                 "Confusion",
    "désorientation":                    "Confusion",
    "ne reconnaît plus":                 "Confusion",
}

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
            self.model_metadata = dict(self.trainer.training_history)

            # Compléter les métriques manquantes depuis le fichier _metadata.json
            missing = [k for k in ("precision", "recall", "f1_score") if k not in self.model_metadata]
            if missing:
                json_path = latest_model.replace(".joblib", "_metadata.json")
                if os.path.exists(json_path):
                    try:
                        with open(json_path, "r", encoding="utf-8") as f:
                            saved = json.load(f)
                        hist = saved.get("training_history", {})
                        for k in missing:
                            if k in hist:
                                self.model_metadata[k] = hist[k]
                        logger.info(f"Metriques supplementaires chargees depuis {os.path.basename(json_path)}")
                    except Exception as e:
                        logger.warning(f"Impossible de lire {json_path}: {e}")

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
    # Normalisation des synonymes de symptômes
    # ------------------------------------------------------------------

    @staticmethod
    def _normaliser_symptomes(symptomes: List[str]) -> List[str]:
        """
        Remplace chaque synonyme par son terme canonique du dataset.
        Permet au médecin de saisir "Gonflement des pieds" et que le modèle
        comprenne "Gonflement des chevilles", etc.
        """
        normalises = []
        for s in symptomes:
            s_clean = s.strip()
            canonique = SYNONYMES_SYMPTOMES.get(s_clean.lower())
            normalises.append(canonique if canonique else s_clean)
        return normalises

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

        # Calculer l'IMC si poids+taille fournis mais pas l'IMC directement
        imc = vitaux.get("imc")
        if imc is None:
            poids = vitaux.get("poids")
            taille = vitaux.get("taille")
            if poids and taille and taille > 0:
                imc = poids / ((taille / 100) ** 2)
            else:
                imc = 22.0

        vital_map = {
            "Vital_Tension Systolique (mmHg)":         vitaux.get("tension_systolique",     120),
            "Vital_Tension Diastolique (mmHg)":        vitaux.get("tension_diastolique",    80),
            "Vital_Fréquence Cardiaque (bpm)":         vitaux.get("frequence_cardiaque",    75),
            "Vital_Fréquence Respiratoire (resp/min)": vitaux.get("frequence_respiratoire", 16),
            "Vital_Température (°C)":                  vitaux.get("temperature",            37.0),
            "Vital_Saturation O2 (%)":                 vitaux.get("saturation_oxygene",     98.0),
            "Vital_IMC (kg/m²)":                       imc,
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
        symptome_names_raw: List[str] = consultation_data.get("symptomes") or []
        # Normaliser les synonymes avant tout traitement
        symptome_names: List[str] = self._normaliser_symptomes(symptome_names_raw)

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

    def _apply_clinical_rules(self, proba: np.ndarray, consultation_data: Dict) -> np.ndarray:
        """
        Post-traitement clinique : booste les probabilités de certains diagnostics
        quand les signes vitaux dépassent des seuils reconnus.
        Préserve la somme = 1 (renormalisation après boost).
        """
        if self.predictor is None:
            return proba

        classes = list(self.predictor.label_encoder.classes_)
        proba = proba.copy()

        vitaux = consultation_data.get("vitaux") or {}
        sys_bp = vitaux.get("tension_systolique", 0) or 0
        dia_bp = vitaux.get("tension_diastolique", 0) or 0
        temp   = vitaux.get("temperature", 37.0) or 37.0
        spo2   = vitaux.get("saturation_oxygene", 98.0) or 98.0
        fc     = vitaux.get("frequence_cardiaque", 75) or 75
        fr     = vitaux.get("frequence_respiratoire", 16) or 16
        imc_val = vitaux.get("imc") or 0
        if not imc_val:
            poids = vitaux.get("poids") or 0
            taille = vitaux.get("taille") or 0
            imc_val = (poids / ((taille / 100) ** 2)) if (poids and taille > 0) else 22.0

        # Normaliser les synonymes AVANT d'appliquer les règles cliniques
        _symptomes_raw = consultation_data.get("symptomes") or []
        _symptomes_norm = self._normaliser_symptomes(_symptomes_raw)
        symptomes = set(s.strip().lower() for s in _symptomes_norm if s)

        def boost(diag: str, factor: float):
            if diag in classes:
                idx = classes.index(diag)
                proba[idx] *= factor

        # ================================================================
        # REGLES VITAUX
        # ================================================================

        # --- Cardiovasculaire ---
        if sys_bp >= 160 or dia_bp >= 100:
            boost("Hypertension", 6.0)
            boost("Insuffisance cardiaque", 1.5)
            boost("Infarctus du myocarde", 1.5)
            boost("Accident vasculaire cérébral", 1.5)
        elif sys_bp >= 140 or dia_bp >= 90:
            boost("Hypertension", 3.5)
            boost("Accident vasculaire cérébral", 1.2)
        if sys_bp < 90 or dia_bp < 60:
            boost("Hypotension", 3.5)
            boost("Infarctus du myocarde", 1.5)
            boost("Embolie pulmonaire", 1.5)
        if fc > 140:
            boost("Arythmie cardiaque", 4.0)
            boost("Embolie pulmonaire", 2.0)
        elif fc > 100:
            boost("Arythmie cardiaque", 2.0)
            boost("Hyperthyroïdie", 1.5)
            boost("Embolie pulmonaire", 1.3)
        if fc < 50:
            boost("Arythmie cardiaque", 2.5)
            boost("Hypothyroïdie", 1.5)

        # --- Respiratoire ---
        if spo2 < 88:
            boost("Embolie pulmonaire", 4.0)
            boost("Pneumonie", 3.0)
            boost("BPCO", 2.5)
        elif spo2 < 92:
            boost("Embolie pulmonaire", 3.0)
            boost("Pneumonie", 2.5)
            boost("BPCO", 2.0)
            boost("COVID-19", 2.0)
            boost("Asthme", 1.8)
        elif spo2 < 95:
            boost("Pneumonie", 1.8)
            boost("BPCO", 1.8)
            boost("COVID-19", 1.5)
            boost("Asthme", 1.5)
        if fr >= 30:
            boost("Embolie pulmonaire", 3.5)
            boost("Pneumonie", 2.5)
        elif fr > 25:
            boost("Pneumonie", 2.0)
            boost("Embolie pulmonaire", 2.0)
            boost("Asthme", 1.5)
            boost("COVID-19", 1.5)

        # --- Fièvre / Infectieux ---
        if temp >= 40.0:
            boost("Malaria", 3.0)
            boost("Typhoïde", 2.5)
            boost("Dengue", 2.0)
            boost("Pneumonie", 1.8)
        elif temp >= 39.5:
            boost("Malaria", 2.5)
            boost("Typhoïde", 2.0)
            boost("Dengue", 1.8)
            boost("Pneumonie", 1.8)
            boost("Grippe", 1.8)
            boost("COVID-19", 1.6)
        elif temp >= 38.5:
            boost("Grippe", 1.8)
            boost("COVID-19", 1.6)
            boost("Pneumonie", 1.6)
            boost("Malaria", 1.5)
            boost("Dengue", 1.5)
            boost("Tuberculose", 1.3)
        elif temp < 36.0:
            boost("Hypothyroïdie", 2.0)
            boost("Insuffisance cardiaque", 1.5)

        # --- Métabolique ---
        if imc_val >= 35:
            boost("Diabète Type 2", 2.0)
            boost("Apnée du sommeil", 2.5)
            boost("Hypertension", 1.5)
            boost("Stéatose hépatique", 2.0)
        elif imc_val >= 30:
            boost("Diabète Type 2", 1.5)
            boost("Apnée du sommeil", 2.0)
            boost("Hypertension", 1.3)

        # ================================================================
        # REGLES SYMPTOMES — très spécifiques (priorité haute)
        # ================================================================

        # COVID-19 : anosmie/agueusie = pathognomonique
        if "perte de goût" in symptomes or "perte d'odorat" in symptomes:
            boost("COVID-19", 8.0)

        # Infarctus du myocarde
        if "douleur thoracique sévère" in symptomes or "douleur thoracique" in symptomes:
            if fc > 100 or spo2 < 95:
                boost("Infarctus du myocarde", 4.0)
                boost("Angine de poitrine", 2.0)
            else:
                boost("Angine de poitrine", 3.0)
                boost("Infarctus du myocarde", 1.5)
        if "douleur au bras épaule" in symptomes or "douleur au bras" in symptomes:
            boost("Infarctus du myocarde", 2.5)
            boost("Angine de poitrine", 2.0)
        if "sueurs froides" in symptomes:
            boost("Infarctus du myocarde", 2.0)

        # AVC
        if "paralysie" in symptomes or "faiblesse soudaine" in symptomes:
            boost("Accident vasculaire cérébral", 5.0)
        if "difficulté à parler" in symptomes or "dysphagie" in symptomes:
            boost("Accident vasculaire cérébral", 3.0)
        if ("paralysie" in symptomes or "faiblesse soudaine" in symptomes) and (sys_bp >= 160 or dia_bp >= 100):
            boost("Accident vasculaire cérébral", 2.5)  # cumul

        # Tuberculose
        if "hémoptysie" in symptomes:
            boost("Tuberculose", 5.0)
        if "sueurs nocturnes" in symptomes and "perte de poids" in symptomes and "toux persistante" in symptomes:
            boost("Tuberculose", 4.0)
        elif "sueurs nocturnes" in symptomes and "toux persistante" in symptomes:
            boost("Tuberculose", 2.5)

        # Dengue
        if "douleur oculaire" in symptomes:
            boost("Dengue", 5.0)
        if "douleurs articulaires" in symptomes and "rash" in symptomes and temp >= 38.5:
            boost("Dengue", 3.5)

        # Sclérose en plaques
        if "engourdissement" in symptomes or "spasticité" in symptomes:
            boost("Sclérose en plaques", 4.0)
        if "vision floue" in symptomes and "faiblesse" in symptomes and "fatigue" in symptomes:
            boost("Sclérose en plaques", 3.0)
        if "difficulté à marcher" in symptomes and "engourdissement" in symptomes:
            boost("Sclérose en plaques", 2.5)

        # Diabète — glycémie très élevée ou symptômes typiques
        if "soif excessive" in symptomes or "fréquence urinaire" in symptomes:
            boost("Diabète Type 1", 2.5)
            boost("Diabète Type 2", 2.5)

        # Hépatique / ictère
        if "ictère" in symptomes or "jaunisse" in symptomes:
            boost("Hépatite A", 2.5)
            boost("Hépatite B", 2.5)
            boost("Cirrhose", 2.0)
        if "urine foncée" in symptomes and "selles pâles" in symptomes:
            boost("Hépatite B", 2.5)
            boost("Hépatite A", 2.0)
            boost("Cirrhose", 1.8)

        # Embolie pulmonaire
        if "essoufflement soudain" in symptomes and spo2 < 92:
            boost("Embolie pulmonaire", 3.0)
        if "syncope" in symptomes and (spo2 < 92 or fr >= 25):
            boost("Embolie pulmonaire", 2.5)

        # Anémie ferriprive : microcytose + symptômes
        if "pâleur" in symptomes and "cheveux cassants" in symptomes:
            boost("Anémie ferriprive", 3.0)
        if "pâleur" in symptomes and "vertiges" in symptomes and "palpitations" in symptomes:
            boost("Anémie ferriprive", 2.0)

        # Thrombose veineuse
        if "thrombose" in symptomes or "claudication" in symptomes:
            boost("Thrombose veineuse", 4.0)
        if "gonflement d'un membre" in symptomes and "chaleur" in symptomes and "rougeur cutanée" in symptomes:
            boost("Thrombose veineuse", 3.0)

        # Glaucome
        if "vision tunnel" in symptomes or "halos colorés" in symptomes:
            boost("Glaucome", 5.0)
        if "perte de vision progressive" in symptomes and "douleur oculaire" in symptomes:
            boost("Glaucome", 3.5)

        # Eczéma vs Conjonctivite
        if "vésicules" in symptomes or "crevasses" in symptomes or "sécheresse cutanée" in symptomes:
            boost("Eczéma", 4.0)
        if "éruption prurigineuse" in symptomes and "démangeaisons" in symptomes:
            boost("Eczéma", 2.5)
            boost("Urticaire", 1.5)

        # Urticaire
        if "angioedème" in symptomes or "gonflement des lèvres" in symptomes:
            boost("Urticaire", 5.0)
        if "histaminémie" in symptomes:
            boost("Urticaire", 4.0)

        # Cushing
        if "vergetures" in symptomes or "grossissement du visage" in symptomes:
            boost("Syndrome de Cushing", 6.0)
        if "prise de poids rapide" in symptomes and "hypertension" in symptomes:
            boost("Syndrome de Cushing", 3.0)

        # Lithiase rénale
        if "douleur colique intense" in symptomes and "hématurie" in symptomes:
            boost("Lithiase rénale", 5.0)

        # Cystite / Pyélonéphrite
        if "dysurie" in symptomes and "urgence urinaire" in symptomes:
            boost("Cystite", 4.0)
            boost("Pyélonéphrite", 2.0)

        # ----------------------------------------------------------------
        # INSUFFISANCE RÉNALE (aiguë & chronique)
        # ----------------------------------------------------------------
        symptomes_renaux = {
            "oligurie ou polyurie", "anurie", "hématurie", "urine foncée",
            "urine mousseuse", "nycturie", "oedèmes", "gonflement des chevilles",
            "démangeaisons", "prurit", "haleine urémique", "goût métallique",
            "crampes musculaires", "engourdissements", "peau sèche", "teint grisâtre",
            "prise de poids rapide",
        }
        nb_renaux = len(symptomes & symptomes_renaux)

        # Oligurie/anurie = signe cardinal de l'insuffisance rénale aiguë
        if "anurie" in symptomes:
            boost("Insuffisance rénale aiguë", 8.0)
            boost("Insuffisance rénale chronique", 3.0)
        elif "oligurie ou polyurie" in symptomes:
            boost("Insuffisance rénale aiguë", 5.0)
            boost("Insuffisance rénale chronique", 2.0)

        # Urine mousseuse = protéinurie → IRC très probable
        if "urine mousseuse" in symptomes:
            boost("Insuffisance rénale chronique", 4.0)
            boost("Syndrome néphrotique", 3.0)
            boost("Insuffisance rénale aiguë", 2.0)

        # Haleine urémique ou goût métallique = urémie → insuffisance rénale avancée
        if "haleine urémique" in symptomes or "goût métallique" in symptomes:
            boost("Insuffisance rénale aiguë", 5.0)
            boost("Insuffisance rénale chronique", 5.0)

        # Nycturie = symptôme classique IRC
        if "nycturie" in symptomes:
            boost("Insuffisance rénale chronique", 3.5)
            boost("Insuffisance rénale aiguë", 1.5)

        # Démangeaisons/prurit sans cause cutanée évidente = IRC
        if ("démangeaisons" in symptomes or "prurit" in symptomes) and nb_renaux >= 2:
            boost("Insuffisance rénale chronique", 3.0)

        # Teint grisâtre = anémie rénale (IRC)
        if "teint grisâtre" in symptomes:
            boost("Insuffisance rénale chronique", 3.0)

        # Cumul de signes rénaux : plus il y en a, plus c'est probable
        if nb_renaux >= 4:
            boost("Insuffisance rénale aiguë", 3.5)
            boost("Insuffisance rénale chronique", 3.5)
        elif nb_renaux >= 3:
            boost("Insuffisance rénale aiguë", 2.0)
            boost("Insuffisance rénale chronique", 2.0)
        elif nb_renaux >= 2:
            boost("Insuffisance rénale aiguë", 1.5)
            boost("Insuffisance rénale chronique", 1.5)

        # Hypertension + oedèmes + fatigue = triade rénale
        if ("hypertension" in symptomes and
                ("oedèmes" in symptomes or "gonflement des chevilles" in symptomes) and
                "fatigue" in symptomes):
            boost("Insuffisance rénale chronique", 2.5)
            boost("Insuffisance rénale aiguë", 2.0)

        # Hématurie + douleurs abdominales sans colique → rénale possible
        if "hématurie" in symptomes and "douleurs abdominales" in symptomes:
            if "douleur colique intense" not in symptomes:
                boost("Insuffisance rénale aiguë", 2.0)
                boost("Glomérulonéphrite", 2.5)

        # Convulsions + confusion + urémie = encéphalopathie urémique (IRA sévère)
        if "convulsions" in symptomes and "confusion" in symptomes and nb_renaux >= 2:
            boost("Insuffisance rénale aiguë", 4.0)

        # Données biologiques rénales critiques (si disponibles)
        examens = {
            (e.get("nom") or "").lower(): e.get("valeur_numerique")
            for e in (consultation_data.get("examens") or [])
            if e.get("valeur_numerique") is not None
        }
        creatinine = examens.get("créatinine") or examens.get("creatinine")
        tfg = examens.get("tfg") or examens.get("débit de filtration glomérulaire")
        uree = examens.get("urée") or examens.get("uree")
        potassium = examens.get("potassium")

        if creatinine is not None:
            if creatinine > 5.0:
                boost("Insuffisance rénale aiguë", 6.0)
                boost("Insuffisance rénale chronique", 4.0)
            elif creatinine > 2.0:
                boost("Insuffisance rénale aiguë", 3.0)
                boost("Insuffisance rénale chronique", 3.0)
            elif creatinine > 1.3:
                boost("Insuffisance rénale aiguë", 1.8)
                boost("Insuffisance rénale chronique", 1.8)

        if tfg is not None:
            if tfg < 15:
                boost("Insuffisance rénale chronique", 7.0)
                boost("Insuffisance rénale aiguë", 4.0)
            elif tfg < 30:
                boost("Insuffisance rénale chronique", 4.0)
                boost("Insuffisance rénale aiguë", 2.5)
            elif tfg < 60:
                boost("Insuffisance rénale chronique", 2.5)
                boost("Insuffisance rénale aiguë", 1.5)

        if uree is not None and uree > 100:
            boost("Insuffisance rénale aiguë", 3.0)
            boost("Insuffisance rénale chronique", 2.5)

        if potassium is not None and potassium > 5.5:
            boost("Insuffisance rénale aiguë", 2.5)
            boost("Insuffisance rénale chronique", 2.0)

        # Goutte
        if "tophi" in symptomes:
            boost("Goutte", 6.0)
        if "douleur articulaire soudaine" in symptomes and "chaleur" in symptomes and "rougeur" in symptomes:
            boost("Goutte", 3.5)

        # Lupus
        if "éruption malaire" in symptomes or "rash photosensible" in symptomes:
            boost("Lupus érythémateux systémique", 6.0)
        if "photosensibilité" in symptomes and "ulcères buccaux" in symptomes:
            boost("Lupus érythémateux systémique", 3.5)

        # Psoriasis
        if "plaques rouges squameuses" in symptomes or "desquamation" in symptomes:
            boost("Psoriasis", 5.0)
        if "saignement des plaques" in symptomes:
            boost("Psoriasis", 3.0)

        # Epilepsie
        if "convulsions" in symptomes:
            boost("Épilepsie", 6.0)

        # Parkinson
        if "lenteur de mouvement" in symptomes or "rigidité" in symptomes:
            boost("Parkinson", 4.0)
        if "tremblements" in symptomes and "rigidité" in symptomes:
            boost("Parkinson", 3.0)

        # Migraine
        if "photophobie" in symptomes and "phonophobie" in symptomes:
            boost("Migraine", 4.0)
        if "aura" in symptomes:
            boost("Migraine", 3.5)

        # Cirrhose
        if "ascite" in symptomes:
            boost("Cirrhose", 5.0)
        if "varices œsophagiennes" in symptomes or "hépatomégalie" in symptomes:
            boost("Cirrhose", 3.0)

        # Leucémie
        if "bleus faciles" in symptomes and "ganglions enflés" in symptomes and "douleurs osseuses" in symptomes:
            boost("Leucémie", 5.0)
        if "bleus faciles" in symptomes and "saignements" in symptomes:
            boost("Leucémie", 2.5)
            boost("Trouble de coagulation", 2.0)

        # RGO
        if "reflux gastro-esophagien" in symptomes or "régurgitation" in symptomes:
            boost("RGO", 5.0)
        if "difficulté à avaler" in symptomes and "brûlures d'estomac" in symptomes:
            boost("RGO", 2.5)
            boost("Hernie hiatale", 2.0)

        # ================================================================
        # REGLES SUPPLEMENTAIRES — maladies restantes
        # ================================================================

        # --- Infectieuses ---
        if "hémoptysie" not in symptomes:  # déjà géré plus haut
            pass
        if "taches de koplik" in symptomes:
            boost("Rougeole", 8.0)
        if "éruption vésiculaire" in symptomes or "vésicules" in symptomes:
            boost("Varicelle", 5.0)
            boost("Herpès génital", 3.0)
        if "rash rose" in symptomes and temp >= 38.5:
            boost("Typhoïde", 4.0)
        if "chancre" in symptomes:
            boost("Syphilis", 8.0)
        if ("rash" in symptomes or "lymphadénopathie" in symptomes) and "chancre" in symptomes:
            boost("Syphilis", 4.0)
        if "douleur oculaire" in symptomes and "douleurs articulaires" in symptomes:
            boost("Dengue", 3.0)
        if "fièvre intermittente" in symptomes:
            boost("Malaria", 4.0)
        if "toux aboyante" in symptomes or "stridor inspiratoire" in symptomes:
            boost("Trachéite", 6.0)
        if "perte de voix" in symptomes or "enrouement" in symptomes:
            boost("Laryngite", 5.0)
        if "otalgie" in symptomes or "écoulement auriculaire" in symptomes:
            boost("Otite", 6.0)
        if "douleur faciale" in symptomes and "congestion nasale" in symptomes:
            boost("Sinusite", 5.0)
        if "éternuements" in symptomes and "congestion nasale" in symptomes:
            boost("Rhinite allergique", 4.0)
            boost("Sinusite", 1.5)
        if "candidose buccale" in symptomes or "infections récurrentes" in symptomes:
            boost("VIH/SIDA", 4.0)
        if "ganglions enflés" in symptomes and "mal de gorge" in symptomes and temp >= 38.0:
            boost("Mononucléose", 4.0)
        if "démangeaisons" in symptomes and "éruption vésiculaire" in symptomes:
            boost("Varicelle", 3.0)
        if "crampes abdominales" in symptomes and "diarrhée" in symptomes and temp >= 38.0:
            boost("Salmonellose", 3.5)
            boost("Gastroentérite", 2.5)
        if "rougeur pharyngée" in symptomes or "taches blanches pharyngées" in symptomes:
            boost("Angine streptococcique", 5.0)
        if "écoulement urétral" in symptomes:
            boost("Gonorrhée", 5.0)
            boost("Chlamydia", 4.0)
            boost("Urétrite", 4.0)
        if "souvent asymptomatique" in symptomes or "cervicite" in symptomes:
            boost("Chlamydia", 3.0)
        if "verrues génitales" in symptomes:
            boost("Condylomes", 8.0)
        if "petites bosses ombiliquées" in symptomes:
            boost("Molluscum contagiosum", 8.0)
        if "excroissance cutanée" in symptomes or "verrue plantaire douloureuse" in symptomes:
            boost("Verrue", 6.0)
        if "récidives" in symptomes and ("vésicules" in symptomes or "brûlures génitales" in symptomes):
            boost("Herpès génital", 5.0)

        # --- Cardiovasculaires ---
        if "douleur au bras/épaule" in symptomes or "douleur à la mâchoire" in symptomes:
            boost("Angine de poitrine", 4.0)
            boost("Infarctus du myocarde", 2.0)
        if "frottement péricardique" in symptomes or "douleur calmée penché en avant" in symptomes:
            boost("Péricardite", 7.0)
        if "douleur thoracique pleurétique" in symptomes:
            boost("Péricardite", 4.0)
            boost("Embolie pulmonaire", 2.0)
        if "sensation d'accélération" in symptomes or "pouls irrégulier" in symptomes:
            boost("Arythmie cardiaque", 4.0)
        if "claudication" not in symptomes:
            pass
        if "érythromélalgie" in symptomes or "paresthésies" in symptomes:
            boost("Thrombocytémie", 4.0)
        if "thrombose" in symptomes and "rougeur cutanée" in symptomes:
            boost("Thrombocytémie", 3.0)
        if "visage rouge" in symptomes and "prurit" in symptomes and "vertiges" in symptomes:
            boost("Polyglobulie", 5.0)

        # --- Respiratoires ---
        if "barrel chest" in symptomes or "utilisation muscles accessoires" in symptomes:
            boost("Emphysème", 5.0)
            boost("BPCO", 3.0)
        if "ronflement" in symptomes and "somnolence diurne" in symptomes:
            boost("Apnée du sommeil", 6.0)
        if "maux de tête matinaux" in symptomes and "ronflement" in symptomes:
            boost("Apnée du sommeil", 4.0)
        if "crachats purulents" in symptomes or "expectorations" in symptomes:
            boost("Pneumonie", 2.5)
            boost("Bronchite", 2.0)
            boost("BPCO", 1.5)

        # --- Gastro-intestinales ---
        if "brûlures épigastriques" in symptomes or "douleur à jeun" in symptomes:
            boost("Ulcère gastro-duodénal", 5.0)
        if "méléna" in symptomes or "hématémèse" in symptomes:
            boost("Ulcère gastro-duodénal", 4.0)
            boost("Cirrhose", 2.0)
        if "diarrhée sanguinolente" in symptomes:
            boost("Colite ulcéreuse", 6.0)
            boost("Crohn", 3.0)
        if "besoin impérieux de déféquer" in symptomes:
            boost("Colite ulcéreuse", 3.0)
        if "fistules" in symptomes:
            boost("Crohn", 6.0)
        if ("diarrhée" in symptomes and "constipation" in symptomes) or "alternance diarrhée-constipation" in symptomes:
            boost("Syndrome du côlon irritable", 5.0)
        if "mucus dans les selles" in symptomes:
            boost("Syndrome du côlon irritable", 4.0)
            boost("Colite ulcéreuse", 2.0)
        if "selles dures" in symptomes and "efforts pour défécation" in symptomes:
            boost("Constipation chronique", 5.0)
        if "ballonnements" in symptomes and "brûlures d'estomac" in symptomes:
            boost("Gastrite", 3.0)
            boost("RGO", 2.0)
        if "douleur irradiant dans le dos" in symptomes and "nausées" in symptomes:
            boost("Pancréatite", 5.0)
        if "douleur après repas gras" in symptomes or "douleur irradiant épaule droite" in symptomes:
            boost("Cholécystite", 5.0)
        if "ictère" in symptomes and "fièvre" in symptomes and "douleur abdominale" in symptomes:
            boost("Cholangite", 5.0)
        if "gynécomastie" in symptomes or "érythème palmaire" in symptomes:
            boost("Cirrhose", 4.0)
        if "hépatomégalie" in symptomes and "souvent asymptomatique" in symptomes:
            boost("Stéatose hépatique", 4.0)

        # --- Endocriniennes ---
        if "agrandissement des mains/pieds" in symptomes or "grossissement du visage" in symptomes:
            boost("Acromégalie", 8.0)
        if "hyperpigmentation" in symptomes and "hypotension" in symptomes:
            boost("Maladie d'Addison", 7.0)
        if ("sal craving" in symptomes or "sel craving" in symptomes) and "hypotension" in symptomes:
            boost("Maladie d'Addison", 4.0)
        if "intolérance à la chaleur" in symptomes and "yeux saillants" in symptomes:
            boost("Hyperthyroïdie", 5.0)
        if "myxoedème" in symptomes or "voix rauque" in symptomes:
            boost("Hypothyroïdie", 4.0)
        if "engourdissement des pieds" in symptomes and "ulcères des pieds" in symptomes:
            boost("Neuropathie diabétique", 6.0)
        if "douleur neuropathique" in symptomes and "perte de réflexes" in symptomes:
            boost("Neuropathie diabétique", 5.0)
        if "brûlures aux pieds" in symptomes or "fourmillements" in symptomes:
            boost("Neuropathie diabétique", 3.0)
            boost("Diabète Type 2", 1.5)
        if "flotteurs" in symptomes or "hémorragie rétinienne" in symptomes:
            boost("Rétinopathie diabétique", 6.0)
        if "scotome central" in symptomes or "métamorphopsies" in symptomes:
            boost("Dégénérescence maculaire", 5.0)
        if "dépôts lipidiques aux paupières" in symptomes or "xanthomes" in symptomes:
            boost("Hypercholestérolémie", 6.0)
        if "douleur thyroïdienne" in symptomes or "gonflement thyroïde" in symptomes:
            boost("Thyroïdite", 6.0)
        if "bosse de bison" in symptomes or "vergetures" in symptomes:
            boost("Syndrome de Cushing", 5.0)

        # --- Neurologiques ---
        if "perte de mémoire" in symptomes and "désorientation" in symptomes:
            boost("Alzheimer", 6.0)
        if "comportement inapproprié" in symptomes and "perte de mémoire" in symptomes:
            boost("Alzheimer", 4.0)
        if "lenteur de mouvement" in symptomes and "écriture micrographique" in symptomes:
            boost("Parkinson", 5.0)
        if "faiblesse ascendante" in symptomes or "réflexes abolis" in symptomes:
            boost("Syndrome de Guillain-Barré", 7.0)
        if "fasciculations" in symptomes or "atrophie musculaire" in symptomes:
            boost("Sclérose latérale amyotrophique", 6.0)
        if "douleur unilatérale" in symptomes and "pulsation céphalique" in symptomes:
            boost("Migraine", 4.0)
        if "sensation de pression" in symptomes and "douleur bilatérale" in symptomes:
            boost("Céphale de tension", 5.0)
            boost("Céphalée de tension", 5.0)
        if "névrite optique" in symptomes:
            boost("Sclérose en plaques", 6.0)
        if "douleurs musculaires diffuses" in symptomes and "fatigue" in symptomes:
            boost("Fibromyalgie", 4.0)
        if "hyperesthésie" in symptomes:
            boost("Fibromyalgie", 5.0)

        # --- Rhumatologiques ---
        if "raideur matinale" in symptomes and "douleur articulaire" in symptomes:
            boost("Arthrite rhumatoïde", 4.0)
            boost("Spondylarthrite ankylosante", 3.0)
        if "nodules rhumatoïdes" in symptomes:
            boost("Arthrite rhumatoïde", 5.0)
        if "uvéite" in symptomes and "douleur lombaire" in symptomes:
            boost("Spondylarthrite ankylosante", 5.0)
        if "enthésite" in symptomes:
            boost("Spondylarthrite ankylosante", 6.0)
        if "sécheresse oculaire" in symptomes and "sécheresse buccale" in symptomes:
            boost("Syndrome de Sjögren", 7.0)
        if "gonflement parotides" in symptomes:
            boost("Syndrome de Sjögren", 5.0)
        if "papules de gottron" in symptomes or "héliotrope éruption" in symptomes:
            boost("Polymyosite/Dermatomyosite", 8.0)
        if "faiblesse musculaire" in symptomes and "rash photosensible" in symptomes:
            boost("Polymyosite/Dermatomyosite", 4.0)
        if "raynaud" in symptomes and "durcissement cutané" in symptomes:
            boost("Sclérodermie", 7.0)
        if "télangiectasies" in symptomes and "fibrose pulmonaire" in symptomes:
            boost("Sclérodermie", 5.0)
        if "douleurs musculaires diffuses" in symptomes and "raideur matinale" in symptomes:
            boost("Fibromyalgie", 3.0)

        # --- Dermatologiques ---
        if "comédones" in symptomes or "pustules" in symptomes:
            boost("Acné", 6.0)
        if "prurit sévère" in symptomes and "sécheresse cutanée" in symptomes:
            boost("Dermatite atopique", 5.0)
            boost("Eczéma", 3.0)
        if "taches blanches" in symptomes or "dépigmentation" in symptomes:
            boost("Vitiligo", 7.0)
        if "bulles" in symptomes and "érosions" in symptomes:
            boost("Pemphigus", 7.0)
        if "ulcérations" in symptomes and "bulles" in symptomes:
            boost("Pemphigus", 5.0)
        if "squames argentées" in symptomes or "plaques rouges squameuses" in symptomes:
            boost("Psoriasis", 5.0)

        # --- Ophtalmologiques ---
        if "vision tunnel" in symptomes or "perte de vision périphérique" in symptomes:
            boost("Glaucome", 5.0)
        if "vision jaunâtre" in symptomes or "diplopie monoculaire" in symptomes:
            boost("Cataracte", 5.0)
        if "halos autour des lumières" in symptomes:
            boost("Cataracte", 3.0)
            boost("Glaucome", 2.0)
        if "ulcère cornéen" in symptomes or "blépharospasme" in symptomes:
            boost("Kératite", 6.0)
        if "sensation de corps étranger" in symptomes and "douleur oculaire" in symptomes:
            boost("Kératite", 3.0)
        if "lignes ondulées" in symptomes or "métamorphopsies" in symptomes:
            boost("Dégénérescence maculaire", 5.0)
        if "vision floue de loin" in symptomes and "plissement des yeux" in symptomes:
            boost("Myopie", 5.0)
        if "vision floue de près" in symptomes or "vision rapprochée floue" in symptomes:
            boost("Hypermétropie", 4.0)
            boost("Presbytie", 3.0)
        if "difficulté de lecture" in symptomes and "fatigue oculaire" in symptomes:
            boost("Presbytie", 4.0)
        if "vision floue à toutes distances" in symptomes:
            boost("Astigmatisme", 5.0)
        if "rougeur oculaire" in symptomes and "larmoiement" in symptomes:
            boost("Conjonctivite", 4.0)
            boost("Kératite", 2.0)
        if "démangeaisons oculaires" in symptomes:
            boost("Conjonctivite", 3.0)
            boost("Rhinite allergique", 2.0)

        # --- Hématologiques ---
        if "adénopathie" in symptomes and "sueurs nocturnes" in symptomes and "perte de poids" in symptomes:
            boost("Lymphome", 6.0)
        if "splénomégalie" in symptomes and "adénopathie" in symptomes:
            boost("Lymphome", 3.0)
            boost("Leucémie", 2.0)
        if "épistaxis" in symptomes and "saignement gencives" in symptomes:
            boost("Anémie aplasique", 4.0)
            boost("Trouble de coagulation", 3.0)
        if "pétéchies" in symptomes or "purpura" in symptomes:
            boost("Trouble de coagulation", 4.0)
            boost("Anémie aplasique", 3.0)
        if "urines foncées" in symptomes and "ictère" in symptomes and "splénomégalie" in symptomes:
            boost("Anémie hémolytique", 5.0)
        if "ménorragie" in symptomes or "hémarthrose" in symptomes:
            boost("Trouble de coagulation", 4.0)
        if "céphalées" in symptomes and "visage rouge" in symptomes:
            boost("Polyglobulie", 3.0)

        # --- Rénales/Urinaires ---
        if "protéinurie" in symptomes and "oedèmes" in symptomes:
            boost("Syndrome néphrotique", 5.0)
            boost("Glomérulonéphrite", 3.0)
        if "albuminémie basse" in symptomes or "hyperlipidémie" in symptomes:
            boost("Syndrome néphrotique", 5.0)
        if "hématurie" in symptomes and "hypertension" in symptomes and "oedèmes" in symptomes:
            boost("Glomérulonéphrite", 5.0)
        if "nocturia" in symptomes or "nycturie" in symptomes:
            boost("Hypertrophie bénigne de prostate", 3.0)
            boost("Prostatite", 2.0)
        if "difficultés à uriner" in symptomes and "flux faible" in symptomes:
            boost("Hypertrophie bénigne de prostate", 5.0)
        if "éjaculation douloureuse" in symptomes or "douleur périnéale" in symptomes:
            boost("Prostatite", 6.0)
        if "douleur costovertébrale" in symptomes:
            boost("Pyélonéphrite", 4.0)
            boost("Lithiase rénale", 2.0)

        # --- Myocardite / Péricardite (compléments) ---
        if "fièvre" in symptomes and "douleur thoracique" in symptomes and fc > 100:
            boost("Myocardite", 3.0)
            boost("Péricardite", 2.0)

        # Arthrite rhumatoïde vs Goutte vs Lupus (triade articulaire)
        if "rougeur" in symptomes and "chaleur" in symptomes and "gonflement" in symptomes:
            boost("Goutte", 2.0)
            boost("Arthrite rhumatoïde", 1.5)

        # ----------------------------------------------------------------
        # CORRECTIONS SPECIFIQUES — maladies sous-détectées
        # ----------------------------------------------------------------

        # Insuffisance cardiaque : triade essoufflement + oedèmes + gonflement chevilles
        if ("essoufflement" in symptomes or "dyspnée de décubitus" in symptomes or "orthopnée" in symptomes):
            boost("Insuffisance cardiaque", 2.0)
        if ("toux nocturne" in symptomes or "dyspnée de décubitus" in symptomes) and \
                ("oedèmes" in symptomes or "gonflement des chevilles" in symptomes):
            boost("Insuffisance cardiaque", 4.0)
        if "prise de poids rapide" in symptomes and \
                ("essoufflement" in symptomes or "gonflement des chevilles" in symptomes):
            boost("Insuffisance cardiaque", 3.0)
        if "oedèmes" in symptomes and "essoufflement" in symptomes and "fatigue" in symptomes:
            boost("Insuffisance cardiaque", 3.5)

        # Cholécystite : douleur abdominale haute + fièvre + repas gras
        if "douleur après repas gras" in symptomes:
            boost("Cholécystite", 6.0)
        if "douleur irradiant épaule droite" in symptomes:
            boost("Cholécystite", 5.0)
        if "douleur abdominale supérieure" in symptomes and temp >= 38.0:
            boost("Cholécystite", 4.0)
        if "ictère léger" in symptomes and "fièvre" in symptomes and "nausées" in symptomes:
            boost("Cholécystite", 3.5)

        # Maladie d'Addison : hyperpigmentation + hypotension + sel craving
        if "hyperpigmentation" in symptomes:
            boost("Maladie d'Addison", 8.0)
        if (sys_bp < 100 or dia_bp < 65) and "fatigue" in symptomes and "nausées" in symptomes:
            boost("Maladie d'Addison", 4.0)
        if "hyperpigmentation" in symptomes and (sys_bp < 110 or "hypotension" in symptomes):
            boost("Maladie d'Addison", 5.0)

        # Renormaliser
        total = proba.sum()
        if total > 0:
            proba = proba / total
        return proba

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

            # Prédiction brute du modèle ML
            y_pred_proba = self.predictor.model.predict_proba(df)[0]

            # Post-traitement clinique
            y_pred_proba = self._apply_clinical_rules(y_pred_proba, consultation_data)

            # Reconstruire la réponse
            classes = self.predictor.label_encoder.classes_
            top_idx = int(np.argmax(y_pred_proba))
            top_3_indices = np.argsort(y_pred_proba)[-3:][::-1]

            alternatives = [
                {"diagnostic": classes[i], "confiance": float(y_pred_proba[i])}
                for i in top_3_indices
            ]

            main_confidence = float(y_pred_proba[top_idx])
            if main_confidence >= 0.80:
                confidence_level, confidence_color = "high", "green"
            elif main_confidence >= 0.60:
                confidence_level, confidence_color = "medium", "yellow"
            else:
                confidence_level, confidence_color = "low", "red"

            def _display(name: str) -> str:
                return DISEASE_DISPLAY_NAMES.get(name, name)

            return {
                "diagnostic_propose": _display(classes[top_idx]),
                "confiance": main_confidence,
                "niveau_confiance": confidence_level,
                "couleur_confiance": confidence_color,
                "diagnostics_alternatifs": [
                    {"diagnostic": _display(a["diagnostic"]), "confiance": a["confiance"]}
                    for a in alternatives[1:]
                ],
                "temps_prediction_secondes": 0.0,
                "timestamp": datetime.now().isoformat(),
                "explication": None,
                "features_importantes": None,
            }

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
            result = self.predictor.explain_prediction(df)
            if "diagnostic" in result:
                result["diagnostic"] = DISEASE_DISPLAY_NAMES.get(result["diagnostic"], result["diagnostic"])
            return result

        except Exception as e:
            logger.error(f"❌ Erreur explication: {e}")
            raise

    def get_model_info(self) -> Dict:
        return {
            "loaded": self.model_loaded,
            "version": self.model_version,
            "metadata": self.model_metadata,
            "n_features": len(self.trainer.feature_names) if self.trainer.feature_names else 0,
            "n_classes": len(self.trainer.label_encoder.classes_) if self.trainer.label_encoder and hasattr(self.trainer.label_encoder, 'classes_') else 0,
            "classes": self.trainer.label_encoder.classes_.tolist() if self.trainer.label_encoder and hasattr(self.trainer.label_encoder, 'classes_') else [],
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
