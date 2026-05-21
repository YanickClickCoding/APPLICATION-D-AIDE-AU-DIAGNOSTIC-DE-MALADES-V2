"""
Script pour ajouter de nouveaux examens au dataset et réentraîner le modèle ML

Ce script ajoute les examens suivants au dataset existant :
- BAAR (Bacille Acido-Alcoolo-Résistant) : Test critique pour la tuberculose
- Autres examens microbiologiques si nécessaire

Étapes :
1. Charger le dataset existant (10,000 cas, 400 features)
2. Ajouter les nouvelles colonnes d'examens
3. Générer des valeurs réalistes pour les nouveaux examens basées sur les maladies
4. Sauvegarder le nouveau dataset
5. Réentraîner le modèle avec le nouveau dataset
"""

import pandas as pd
import numpy as np
import os
import sys
from datetime import datetime

# Ajouter le chemin du module app
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.ml.model_manager import ModelManager
from app.ml.data_preprocessing import DataPreprocessor

# ══════════════════════════════════════════════════════════════════════════════
# Configuration
# ══════════════════════════════════════════════════════════════════════════════

DATASET_PATH = "../les ressources dataset/dataset_medical_robust_10000_cas.csv"
NEW_DATASET_PATH = "../les ressources dataset/dataset_medical_robust_enhanced.csv"

# Nouveaux examens à ajouter
NEW_EXAMS = {
    'Lab_BAAR (résultat)': {
        'type': 'binary',  # 0=NÉGATIF, 1=POSITIF
        'default': 0,
        'description': 'Bacille Acido-Alcoolo-Résistant (test pour tuberculose)'
    },
    'Lab_Culture Mycobactéries (résultat)': {
        'type': 'binary',
        'default': 0,
        'description': 'Culture de mycobactéries (confirmation tuberculose)'
    },
    'Lab_Test Xpert MTB/RIF (résultat)': {
        'type': 'binary',
        'default': 0,
        'description': 'Test moléculaire rapide pour tuberculose'
    },
}

# Maladies qui devraient avoir des résultats positifs pour ces examens
DISEASE_EXAM_MAPPING = {
    'Tuberculose': {
        'Lab_BAAR (résultat)': 0.85,  # 85% de probabilité d'être positif
        'Lab_Culture Mycobactéries (résultat)': 0.90,
        'Lab_Test Xpert MTB/RIF (résultat)': 0.95,
    },
    # Autres maladies ont une faible probabilité de faux positifs
    'Pneumonie': {
        'Lab_BAAR (résultat)': 0.02,
        'Lab_Culture Mycobactéries (résultat)': 0.01,
        'Lab_Test Xpert MTB/RIF (résultat)': 0.01,
    },
    'Bronchite': {
        'Lab_BAAR (résultat)': 0.01,
        'Lab_Culture Mycobactéries (résultat)': 0.01,
        'Lab_Test Xpert MTB/RIF (résultat)': 0.01,
    },
}

# ══════════════════════════════════════════════════════════════════════════════
# Fonctions
# ══════════════════════════════════════════════════════════════════════════════

def load_dataset():
    """Charge le dataset existant"""
    print(f"\n[INFO] Chargement du dataset depuis : {DATASET_PATH}")
    
    if not os.path.exists(DATASET_PATH):
        print(f"[ERROR] Dataset introuvable à {DATASET_PATH}")
        return None
    
    df = pd.read_csv(DATASET_PATH)
    print(f"[INFO] Dataset chargé : {len(df)} lignes, {len(df.columns)} colonnes")
    print(f"   Maladies uniques : {df['Maladie_Diagnostic'].nunique()}")
    
    return df


def add_new_exam_columns(df):
    """Ajoute les nouvelles colonnes d'examens au dataset"""
    print(f"\n[INFO] Ajout de {len(NEW_EXAMS)} nouveaux examens...")
    
    for exam_name, exam_config in NEW_EXAMS.items():
        print(f"   • {exam_name} ({exam_config['description']})")
        
        # Initialiser avec la valeur par défaut
        df[exam_name] = exam_config['default']
    
    print(f"[INFO] Nouvelles colonnes ajoutées : {len(df.columns)} colonnes au total")
    return df


def generate_realistic_values(df):
    """Génère des valeurs réalistes pour les nouveaux examens basées sur les maladies"""
    print(f"\n[INFO] Génération de valeurs réalistes pour les nouveaux examens...")
    
    for exam_name in NEW_EXAMS.keys():
        print(f"\n   Examen : {exam_name}")
        
        for disease, probabilities in DISEASE_EXAM_MAPPING.items():
            if exam_name in probabilities:
                prob = probabilities[exam_name]
                
                # Filtrer les lignes pour cette maladie
                disease_mask = df['Maladie_Diagnostic'] == disease
                n_cases = disease_mask.sum()
                
                if n_cases > 0:
                    # Générer des valeurs binaires avec la probabilité spécifiée
                    values = np.random.binomial(1, prob, n_cases)
                    df.loc[disease_mask, exam_name] = values
                    
                    n_positive = values.sum()
                    print(f"      {disease}: {n_positive}/{n_cases} cas positifs ({prob*100:.0f}% attendu)")
    
    # Pour toutes les autres maladies non spécifiées, garder la valeur par défaut (0)
    # avec une très faible probabilité de faux positifs (0.5%)
    for exam_name in NEW_EXAMS.keys():
        specified_diseases = set(DISEASE_EXAM_MAPPING.keys())
        all_diseases = set(df['Maladie_Diagnostic'].unique())
        unspecified_diseases = all_diseases - specified_diseases
        
        for disease in unspecified_diseases:
            disease_mask = df['Maladie_Diagnostic'] == disease
            n_cases = disease_mask.sum()
            
            if n_cases > 0:
                # Très faible probabilité de faux positifs
                values = np.random.binomial(1, 0.005, n_cases)
                df.loc[disease_mask, exam_name] = values
    
    print(f"\n[INFO] Valeurs réalistes générées pour tous les examens")
    return df


def save_enhanced_dataset(df):
    """Sauvegarde le dataset enrichi"""
    print(f"\n[INFO] Sauvegarde du dataset enrichi...")
    
    # Créer le dossier si nécessaire
    os.makedirs(os.path.dirname(NEW_DATASET_PATH), exist_ok=True)
    
    # Sauvegarder en CSV
    df.to_csv(NEW_DATASET_PATH, index=False)
    print(f"[INFO] Dataset enrichi sauvegardé : {NEW_DATASET_PATH}")
    print(f"   Lignes : {len(df)}")
    print(f"   Colonnes : {len(df.columns)} (anciennes: 400, nouvelles: {len(NEW_EXAMS)})")
    
    # Afficher un échantillon
    print(f"\n[INFO] Échantillon des nouvelles colonnes :")
    print(df[list(NEW_EXAMS.keys())].head(10))
    
    return NEW_DATASET_PATH


def retrain_model(dataset_path):
    """Réentraîne le modèle avec le nouveau dataset"""
    print(f"\n[INFO] Réentraînement du modèle ML...")
    print(f"   Dataset : {dataset_path}")
    
    try:
        # Initialiser le model manager
        model_manager = ModelManager()
        
        # Entraîner le nouveau modèle
        print(f"\n[INFO] Entraînement en cours...")
        results = model_manager.train_new_model(
            dataset_path=dataset_path,
            n_estimators=350,  # Même configuration que le modèle actuel
            max_depth=60,
            save=True
        )
        
        if results['success']:
            print(f"\n[INFO] Entraînement réussi !")
            print(f"\n[INFO] Résultats de l'entraînement :")
            print(f"   - Précision : {results['training']['accuracy']:.2%}")
            print(f"   - Nombre de features : {results['training']['n_features']}")
            print(f"   - Nombre de classes : {results['training']['n_classes']}")
            print(f"   - Durée : {results['training']['training_duration_seconds']:.1f}s")
            
            if 'evaluation' in results:
                print(f"\n[INFO] Résultats de l'évaluation :")
                eval_results = results['evaluation']
                if 'accuracy' in eval_results:
                    print(f"   - Précision test : {eval_results['accuracy']:.2%}")
            
            print(f"\n[INFO] Modèle sauvegardé : {results['training'].get('model_path', 'N/A')}")
            
            return True
        else:
            print(f"\n[ERROR] Échec de l'entraînement : {results.get('error', 'Erreur inconnue')}")
            return False
            
    except Exception as e:
        print(f"\n[ERROR] Erreur lors du réentraînement : {e}")
        import traceback
        traceback.print_exc()
        return False


def verify_new_features():
    """Vérifie que les nouvelles features sont bien dans le modèle"""
    print(f"\n[INFO] Vérification des nouvelles features dans le modèle...")
    
    try:
        model_manager = ModelManager()
        model_manager.load_latest_model()
        
        if model_manager.model_loaded:
            feature_names = model_manager.trainer.feature_names
            
            print(f"\n[INFO] Modèle chargé avec {len(feature_names)} features")
            
            # Vérifier que les nouvelles features sont présentes
            new_features_found = []
            for exam_name in NEW_EXAMS.keys():
                if exam_name in feature_names:
                    new_features_found.append(exam_name)
                    print(f"   [FOUND] {exam_name} trouve dans le modele")
                else:
                    print(f"   [NOT FOUND] {exam_name} NON trouve dans le modele")
            
            if len(new_features_found) == len(NEW_EXAMS):
                print(f"\n[INFO] Toutes les nouvelles features sont présentes dans le modèle !")
                return True
            else:
                print(f"\n[WARNING] Certaines features sont manquantes")
                return False
        else:
            print(f"[ERROR] Impossible de charger le modèle")
            return False
            
    except Exception as e:
        print(f"[ERROR] Erreur lors de la vérification : {e}")
        return False


# ══════════════════════════════════════════════════════════════════════════════
# Main
# ══════════════════════════════════════════════════════════════════════════════

def main():
    """Fonction principale"""
    print("="*80)
    print("AJOUT DE NOUVEAUX EXAMENS ET RÉENTRAÎNEMENT DU MODÈLE ML")
    print("="*80)
    print(f"\nDate : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Étape 1 : Charger le dataset
    df = load_dataset()
    if df is None:
        return
    
    # Étape 2 : Ajouter les nouvelles colonnes
    df = add_new_exam_columns(df)
    
    # Étape 3 : Générer des valeurs réalistes
    df = generate_realistic_values(df)
    
    # Étape 4 : Sauvegarder le dataset enrichi
    new_dataset_path = save_enhanced_dataset(df)
    
    # Étape 5 : Réentraîner le modèle
    print(f"\n" + "="*80)
    print("RÉENTRAÎNEMENT DU MODÈLE")
    print("="*80)
    
    success = retrain_model(new_dataset_path)
    
    if success:
        # Étape 6 : Vérifier les nouvelles features
        print(f"\n" + "="*80)
        print("VÉRIFICATION")
        print("="*80)
        
        verify_new_features()
        
        print(f"\n" + "="*80)
        print("[INFO] PROCESSUS TERMINÉ AVEC SUCCÈS !")
        print("="*80)
        print(f"\n[INFO] Prochaines étapes :")
        print(f"   1. Mettre à jour le frontend pour suggérer BAAR pour la tuberculose")
        print(f"   2. Tester le nouveau modèle avec des cas de tuberculose")
        print(f"   3. Vérifier que la précision est maintenue")
    else:
        print(f"\n" + "="*80)
        print("[ERROR] ÉCHEC DU PROCESSUS")
        print("="*80)


if __name__ == "__main__":
    main()
