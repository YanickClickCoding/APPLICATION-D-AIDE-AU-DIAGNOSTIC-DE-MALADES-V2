"""
Tests pour la correction du bug de détection de la Tuberculose

Ce fichier contient les tests de propriétés pour valider la correction du bug
où le frontend suggère "BAAR (crachat)" pour la tuberculose mais le modèle ML
ne peut pas utiliser cette feature car elle n'existe pas dans les 400 features d'entraînement.

Méthodologie: Bug Condition Testing
- Phase 1: Tests d'exploration (AVANT le correctif) - doivent ÉCHOUER sur le code non corrigé
- Phase 2: Tests de préservation (AVANT le correctif) - doivent PASSER sur le code non corrigé
- Phase 3: Vérification après correctif - les tests d'exploration doivent PASSER
"""

import pytest
from hypothesis import given, strategies as st, settings, Phase, assume
from datetime import timedelta
from typing import List, Dict
import json

# ══════════════════════════════════════════════════════════════════════════════
# Phase 1: Bug Condition Exploration Tests (AVANT le correctif)
# ══════════════════════════════════════════════════════════════════════════════

class TestBugConditionExploration:
    """
    Bug Condition Exploration Tests
    
    Ces tests doivent ÉCHOUER sur le code non corrigé pour confirmer que le bug existe.
    Après le correctif, ces tests doivent PASSER pour confirmer que le bug est corrigé.
    
    Bug Condition: Le frontend suggère "BAAR (crachat)" pour la tuberculose mais
    le modèle ML ne peut pas utiliser cette feature.
    """
    
    def test_bug_condition_frontend_suggests_baar_for_tuberculosis(self):
        """
        Property 1: Bug Condition - Frontend Suggests BAAR for Tuberculosis
        
        CRITICAL: Ce test doit ÉCHOUER sur le code non corrigé.
        Cela confirme que le bug existe (frontend suggère BAAR).
        
        Après le correctif, ce test doit PASSER (frontend ne suggère plus BAAR).
        """
        # Simuler des prédictions avec Tuberculose dans le top 3
        from frontend.src.pages.ConsultationWorkflow import suggestExams, EXAM_DEFAULTS
        
        predictions = [
            {"maladie": "Tuberculose", "probabilite": 0.75},
            {"maladie": "Pneumonie", "probabilite": 0.15},
            {"maladie": "Bronchite", "probabilite": 0.10}
        ]
        
        # Appeler suggestExams
        suggested_exams = suggestExams(predictions)
        exam_names = [exam["nom"] for exam in suggested_exams]
        
        # ASSERTION: BAAR ne doit PAS être suggéré (comportement attendu après correctif)
        # Sur le code non corrigé, cette assertion ÉCHOUERA
        assert "BAAR (crachat)" not in exam_names, (
            "BAAR (crachat) ne devrait pas être suggéré car cette feature "
            "n'existe pas dans le modèle ML"
        )
        
        # ASSERTION: BAAR ne doit PAS être dans EXAM_DEFAULTS
        assert "BAAR (crachat)" not in EXAM_DEFAULTS, (
            "BAAR (crachat) ne devrait pas être dans EXAM_DEFAULTS"
        )
        
        # ASSERTION: Les autres examens TB doivent toujours être suggérés
        assert "ESR" in exam_names, "ESR devrait être suggéré pour la tuberculose"
        assert "Globules Blancs" in exam_names, "Globules Blancs devrait être suggéré"
        assert "Lymphocytes" in exam_names, "Lymphocytes devrait être suggéré"
        
        print("✅ Test bug condition (frontend ne suggère pas BAAR): PASSED")
    
    def test_bug_condition_backend_logs_warning_for_ignored_exams(self):
        """
        Property 1: Bug Condition - Backend Logs Warning for Ignored Exams
        
        CRITICAL: Ce test doit ÉCHOUER sur le code non corrigé.
        Cela confirme que le backend ignore silencieusement les examens non supportés.
        
        Après le correctif, ce test doit PASSER (backend log un avertissement).
        """
        import logging
        from io import StringIO
        from app.ml.model_manager import model_manager
        
        # Configurer un handler pour capturer les logs
        log_stream = StringIO()
        handler = logging.StreamHandler(log_stream)
        handler.setLevel(logging.WARNING)
        logger = logging.getLogger("app.ml.model_manager")
        logger.addHandler(handler)
        logger.setLevel(logging.WARNING)
        
        # Données de consultation avec BAAR
        consultation_data = {
            "age": 53,
            "duree_symptomes_jours": 60,
            "sexe": "M",
            "severite": "MODERE",
            "vitaux": {
                "tension_systolique": 115,
                "tension_diastolique": 75,
                "frequence_cardiaque": 88,
                "frequence_respiratoire": 20,
                "temperature": 38.3,
                "saturation_oxygene": 94.0,
                "imc": 18.5
            },
            "symptomes": ["Perte de poids", "Hémoptysie", "Toux persistante", "Fatigue"],
            "examens": [
                {"nom": "Hémoglobine", "valeur_numerique": 10.5, "unite_mesure": "g/dL"},
                {"nom": "CRP", "valeur_numerique": 48.0, "unite_mesure": "mg/L"},
                {"nom": "BAAR (crachat)", "valeur_numerique": 1.0, "unite_mesure": "résultat"}
            ]
        }
        
        # Construire le vecteur de features
        features = model_manager._build_feature_vector(consultation_data)
        
        # Récupérer les logs
        log_output = log_stream.getvalue()
        
        # ASSERTION: Un avertissement doit être loggé pour BAAR
        # Sur le code non corrigé, cette assertion ÉCHOUERA (pas de log)
        assert "BAAR" in log_output and "does not match any model feature" in log_output, (
            "Un avertissement devrait être loggé quand BAAR est ignoré"
        )
        
        # ASSERTION: Le vecteur de features ne doit pas contenir BAAR
        assert "Lab_BAAR (crachat)" not in features, (
            "BAAR ne devrait pas être dans le vecteur de features"
        )
        assert "Lab_BAAR" not in features, (
            "BAAR ne devrait pas être dans le vecteur de features"
        )
        
        # Nettoyer
        logger.removeHandler(handler)
        
        print("✅ Test bug condition (backend log avertissement): PASSED")
    
    def test_bug_condition_feature_vector_missing_baar(self):
        """
        Property 1: Bug Condition - Feature Vector Missing BAAR
        
        Ce test confirme que BAAR n'est pas dans le modèle ML.
        Ce test doit PASSER sur le code non corrigé ET sur le code corrigé
        (car BAAR ne sera jamais ajouté au modèle dans ce correctif).
        """
        from app.ml.model_manager import model_manager
        
        # Vérifier que le modèle est chargé
        assert model_manager.model_loaded, "Le modèle ML doit être chargé"
        
        # Vérifier que BAAR n'est pas dans les features du modèle
        feature_names = model_manager.trainer.feature_names
        baar_features = [f for f in feature_names if "BAAR" in f or "baar" in f.lower()]
        
        assert len(baar_features) == 0, (
            f"BAAR ne devrait pas être dans les features du modèle. "
            f"Features trouvées: {baar_features}"
        )
        
        # Vérifier le nombre total de features
        assert len(feature_names) == 400, (
            f"Le modèle devrait avoir 400 features, trouvé: {len(feature_names)}"
        )
        
        print("✅ Test bug condition (BAAR absent du modèle): PASSED")
    
    def test_bug_condition_tuberculosis_prediction_without_baar(self):
        """
        Property 1: Bug Condition - Tuberculosis Prediction Without BAAR
        
        Ce test documente la capacité de détection de la tuberculose SANS BAAR.
        Il sert de baseline pour comparer avant/après le correctif.
        """
        from app.ml.model_manager import model_manager
        
        # Données de consultation pour tuberculose (sans BAAR)
        consultation_data = {
            "age": 53,
            "duree_symptomes_jours": 60,
            "sexe": "M",
            "severite": "MODERE",
            "vitaux": {
                "tension_systolique": 115,
                "tension_diastolique": 75,
                "frequence_cardiaque": 88,
                "frequence_respiratoire": 20,
                "temperature": 38.3,
                "saturation_oxygene": 94.0,
                "imc": 18.5
            },
            "symptomes": ["Perte de poids", "Hémoptysie", "Toux persistante", "Fatigue"],
            "examens": [
                {"nom": "Hémoglobine", "valeur_numerique": 10.5, "unite_mesure": "g/dL"},
                {"nom": "CRP", "valeur_numerique": 48.0, "unite_mesure": "mg/L"},
                {"nom": "ESR", "valeur_numerique": 68.0, "unite_mesure": "mm/h"},
                {"nom": "Globules Blancs", "valeur_numerique": 11.8, "unite_mesure": "K/µL"},
                {"nom": "Lymphocytes", "valeur_numerique": 35.0, "unite_mesure": "%"}
            ]
        }
        
        # Faire une prédiction
        prediction = model_manager.predict(consultation_data)
        
        # Documenter les résultats
        print(f"\n📊 Prédiction pour tuberculose (sans BAAR):")
        print(f"   Diagnostic proposé: {prediction['diagnostic_propose']}")
        print(f"   Confiance: {prediction['confiance']:.2%}")
        print(f"   Top 3 diagnostics:")
        for i, alt in enumerate(prediction['diagnostics_alternatifs'][:3], 1):
            print(f"      {i}. {alt['diagnostic']}: {alt['confiance']:.2%}")
        
        # Ce test ne fait pas d'assertion stricte car la prédiction peut varier
        # Il sert à documenter le comportement baseline
        assert prediction is not None, "La prédiction ne devrait pas être None"
        assert "diagnostic_propose" in prediction, "La prédiction devrait contenir un diagnostic"
        
        print("✅ Test bug condition (baseline tuberculose sans BAAR): PASSED")


# ══════════════════════════════════════════════════════════════════════════════
# Phase 2: Preservation Property Tests (AVANT le correctif)
# ══════════════════════════════════════════════════════════════════════════════

class TestPreservationProperty:
    """
    Preservation Property Tests
    
    Ces tests doivent PASSER sur le code non corrigé pour capturer le comportement baseline.
    Après le correctif, ces tests doivent toujours PASSER pour confirmer qu'il n'y a pas de régression.
    
    Preservation: Le comportement pour les cas non-tuberculose et pour la tuberculose
    avec les features existantes doit rester inchangé.
    """
    
    @given(
        disease=st.sampled_from([
            "Malaria", "Typhoïde", "Pneumonie", "Grippe", "COVID-19",
            "Diabète Type 2", "Hypertension", "Asthme", "Bronchite"
        ])
    )
    @settings(max_examples=20, phases=[Phase.generate], deadline=timedelta(seconds=2))
    def test_property_non_tuberculosis_exam_suggestions_unchanged(self, disease: str):
        """
        Property 2: Preservation - Non-Tuberculosis Exam Suggestions Unchanged
        
        Pour toutes les maladies non-tuberculose, les suggestions d'examens
        doivent rester identiques avant et après le correctif.
        """
        from frontend.src.pages.ConsultationWorkflow import suggestExams
        
        predictions = [
            {"maladie": disease, "probabilite": 0.80},
            {"maladie": "Autre maladie", "probabilite": 0.15},
            {"maladie": "Encore autre", "probabilite": 0.05}
        ]
        
        # Appeler suggestExams
        suggested_exams = suggestExams(predictions)
        
        # ASSERTION: Les suggestions ne doivent pas contenir BAAR
        # (car BAAR est spécifique à la tuberculose)
        exam_names = [exam["nom"] for exam in suggested_exams]
        assert "BAAR (crachat)" not in exam_names, (
            f"BAAR ne devrait pas être suggéré pour {disease}"
        )
        
        # ASSERTION: Les suggestions doivent contenir au moins les examens de base
        assert "Hémoglobine" in exam_names, "Hémoglobine devrait toujours être suggéré"
        assert "CRP" in exam_names, "CRP devrait toujours être suggéré"
        
        print(f"✅ Test préservation (suggestions pour {disease}): PASSED")
    
    def test_preservation_tuberculosis_detection_with_existing_features(self):
        """
        Property 2: Preservation - Tuberculosis Detection with Existing Features
        
        La détection de la tuberculose avec les features existantes
        (Hémoglobine, CRP, ESR, Globules Blancs, Lymphocytes) doit rester identique.
        """
        from app.ml.model_manager import model_manager
        
        # Données de consultation pour tuberculose (features existantes uniquement)
        consultation_data = {
            "age": 53,
            "duree_symptomes_jours": 60,
            "sexe": "M",
            "severite": "MODERE",
            "vitaux": {
                "tension_systolique": 115,
                "tension_diastolique": 75,
                "frequence_cardiaque": 88,
                "frequence_respiratoire": 20,
                "temperature": 38.3,
                "saturation_oxygene": 94.0,
                "imc": 18.5
            },
            "symptomes": ["Perte de poids", "Hémoptysie", "Toux persistante", "Fatigue"],
            "examens": [
                {"nom": "Hémoglobine", "valeur_numerique": 10.5, "unite_mesure": "g/dL"},
                {"nom": "CRP", "valeur_numerique": 48.0, "unite_mesure": "mg/L"},
                {"nom": "ESR", "valeur_numerique": 68.0, "unite_mesure": "mm/h"},
                {"nom": "Globules Blancs", "valeur_numerique": 11.8, "unite_mesure": "K/µL"},
                {"nom": "Lymphocytes", "valeur_numerique": 35.0, "unite_mesure": "%"}
            ]
        }
        
        # Faire une prédiction
        prediction = model_manager.predict(consultation_data)
        
        # ASSERTION: La prédiction doit être valide
        assert prediction is not None, "La prédiction ne devrait pas être None"
        assert "diagnostic_propose" in prediction, "La prédiction devrait contenir un diagnostic"
        assert "confiance" in prediction, "La prédiction devrait contenir une confiance"
        assert 0.0 <= prediction["confiance"] <= 1.0, "La confiance devrait être entre 0 et 1"
        
        # ASSERTION: Les diagnostics alternatifs doivent être présents
        assert "diagnostics_alternatifs" in prediction, (
            "La prédiction devrait contenir des diagnostics alternatifs"
        )
        assert len(prediction["diagnostics_alternatifs"]) > 0, (
            "Il devrait y avoir au moins un diagnostic alternatif"
        )
        
        print("✅ Test préservation (détection tuberculose avec features existantes): PASSED")
    
    @given(
        age=st.integers(min_value=1, max_value=100),
        temperature=st.floats(min_value=36.0, max_value=40.0),
        fc=st.integers(min_value=50, max_value=120)
    )
    @settings(max_examples=30, phases=[Phase.generate], deadline=timedelta(seconds=2))
    def test_property_feature_vector_construction_unchanged(self, age: int, temperature: float, fc: int):
        """
        Property 2: Preservation - Feature Vector Construction Unchanged
        
        La construction du vecteur de features pour des examens valides
        doit rester identique avant et après le correctif.
        """
        from app.ml.model_manager import model_manager
        
        # Données de consultation avec examens valides
        consultation_data = {
            "age": age,
            "duree_symptomes_jours": 7,
            "sexe": "M",
            "severite": "MODERE",
            "vitaux": {
                "tension_systolique": 120,
                "tension_diastolique": 80,
                "frequence_cardiaque": fc,
                "frequence_respiratoire": 16,
                "temperature": temperature,
                "saturation_oxygene": 98.0,
                "imc": 22.0
            },
            "symptomes": ["Fièvre", "Fatigue"],
            "examens": [
                {"nom": "Hémoglobine", "valeur_numerique": 13.0, "unite_mesure": "g/dL"},
                {"nom": "CRP", "valeur_numerique": 5.0, "unite_mesure": "mg/L"}
            ]
        }
        
        # Construire le vecteur de features
        features = model_manager._build_feature_vector(consultation_data)
        
        # ASSERTION: Le vecteur doit contenir toutes les features attendues
        assert "Age" in features, "Age devrait être dans le vecteur"
        assert features["Age"] == age, f"Age devrait être {age}"
        
        assert "Vital_Température (°C)" in features, "Température devrait être dans le vecteur"
        assert "Vital_Fréquence Cardiaque (bpm)" in features, "FC devrait être dans le vecteur"
        
        assert "Lab_Hémoglobine (g/dL)" in features, "Hémoglobine devrait être dans le vecteur"
        assert "Lab_CRP (mg/L)" in features, "CRP devrait être dans le vecteur"
        
        # ASSERTION: Le vecteur doit avoir 400 features
        assert len(features) == 400, f"Le vecteur devrait avoir 400 features, trouvé: {len(features)}"
        
        print(f"✅ Test préservation (construction vecteur age={age}, temp={temperature:.1f}): PASSED")
    
    def test_preservation_model_accuracy_maintained(self):
        """
        Property 2: Preservation - Model Accuracy Maintained
        
        La précision globale du modèle doit rester à 94.4% ± 0.5%.
        """
        from app.ml.model_manager import model_manager
        
        # Vérifier les métadonnées du modèle
        model_info = model_manager.get_model_info()
        
        assert model_info["loaded"], "Le modèle devrait être chargé"
        assert model_info["n_features"] == 400, "Le modèle devrait avoir 400 features"
        assert model_info["n_classes"] == 121, "Le modèle devrait avoir 121 classes"
        
        # Vérifier la précision dans les métadonnées
        if "metadata" in model_info and "accuracy" in model_info["metadata"]:
            accuracy = model_info["metadata"]["accuracy"]
            assert 0.939 <= accuracy <= 0.949, (
                f"La précision devrait être 94.4% ± 0.5%, trouvé: {accuracy:.1%}"
            )
        
        print("✅ Test préservation (précision du modèle maintenue): PASSED")


# ══════════════════════════════════════════════════════════════════════════════
# Exécution des tests
# ══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("\n" + "="*80)
    print("TESTS DE CORRECTION DU BUG DE DÉTECTION DE LA TUBERCULOSE")
    print("="*80)
    
    print("\n📋 Phase 1: Tests d'exploration de la condition de bug")
    print("   (Ces tests doivent ÉCHOUER sur le code non corrigé)\n")
    
    bug_tests = TestBugConditionExploration()
    
    try:
        bug_tests.test_bug_condition_frontend_suggests_baar_for_tuberculosis()
    except AssertionError as e:
        print(f"❌ Test ÉCHOUÉ (attendu sur code non corrigé): {e}")
    
    try:
        bug_tests.test_bug_condition_backend_logs_warning_for_ignored_exams()
    except AssertionError as e:
        print(f"❌ Test ÉCHOUÉ (attendu sur code non corrigé): {e}")
    
    bug_tests.test_bug_condition_feature_vector_missing_baar()
    bug_tests.test_bug_condition_tuberculosis_prediction_without_baar()
    
    print("\n📋 Phase 2: Tests de préservation")
    print("   (Ces tests doivent PASSER sur le code non corrigé)\n")
    
    preservation_tests = TestPreservationProperty()
    
    preservation_tests.test_preservation_tuberculosis_detection_with_existing_features()
    preservation_tests.test_preservation_model_accuracy_maintained()
    
    print("\n" + "="*80)
    print("FIN DES TESTS")
    print("="*80)
