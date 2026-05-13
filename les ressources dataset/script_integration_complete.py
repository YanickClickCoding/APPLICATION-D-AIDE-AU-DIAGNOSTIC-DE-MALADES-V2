"""
SCRIPT D'INTÉGRATION COMPLÈTE - SYSTÈME D'AIDE AU DIAGNOSTIC
============================================================
Ce script montre comment intégrer et utiliser le dataset médical robuste
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import json
import warnings
warnings.filterwarnings('ignore')

print("=" * 80)
print("SYSTÈME D'AIDE AU DIAGNOSTIC - INTÉGRATION DU DATASET")
print("=" * 80)

# ============================================================================
# ÉTAPE 1: CHARGER ET EXPLORER LE DATASET
# ============================================================================
print("\n📂 ÉTAPE 1: Chargement du dataset...")
df = pd.read_csv('dataset_medical_robust_10000_cas.csv')

print(f"  ✓ Dataset chargé: {df.shape[0]} cas, {df.shape[1]} colonnes")
print(f"  ✓ Maladies: {df['Maladie_Diagnostic'].nunique()}")
print(f"  ✓ Période: {df['Date_Consultation'].min()} à {df['Date_Consultation'].max()}")

# ============================================================================
# ÉTAPE 2: NETTOYAGE & PRÉPARATION DES DONNÉES
# ============================================================================
print("\n🧹 ÉTAPE 2: Préparation des données...")

# Créer une copie pour traitement
df_processed = df.copy()

# Convertir les symptômes en liste
df_processed['Symptomes_List'] = df_processed['Symptomes_Rapportes'].apply(
    lambda x: [s.strip() for s in str(x).split(',')]
)

# Extraire tous les symptômes uniques
all_symptoms = []
for symptom_list in df_processed['Symptomes_List']:
    all_symptoms.extend(symptom_list)
unique_symptoms = list(set(all_symptoms))
print(f"  ✓ Symptômes uniques détectés: {len(unique_symptoms)}")

# Créer des features binaires pour les symptômes
for symptom in unique_symptoms[:50]:  # Top 50 symptômes pour ne pas exploser les features
    df_processed[f'symptom_{symptom.lower().replace(" ", "_")}'] = (
        df_processed['Symptomes_List'].apply(lambda x: 1 if symptom in x else 0)
    )

print(f"  ✓ Features symptômes créées: 50")

# Encoder les variables catégoriques
encoders = {}

# Sexe
le_sexe = LabelEncoder()
df_processed['Sexe_Encoded'] = le_sexe.fit_transform(df_processed['Sexe'])
encoders['Sexe'] = le_sexe

# Groupe d'âge
le_groupe = LabelEncoder()
df_processed['Groupe_Age_Encoded'] = le_groupe.fit_transform(df_processed['Groupe_Age'])
encoders['Groupe_Age'] = le_groupe

# Sévérité
le_severite = LabelEncoder()
df_processed['Severite_Encoded'] = le_severite.fit_transform(df_processed['Severite'])
encoders['Severite'] = le_severite

# Maladie (cible)
le_maladie = LabelEncoder()
df_processed['Maladie_Encoded'] = le_maladie.fit_transform(df_processed['Maladie_Diagnostic'])
encoders['Maladie'] = le_maladie

print(f"  ✓ Variables catégoriques encodées")

# ============================================================================
# ÉTAPE 3: PRÉPARATION DES FEATURES & TARGET
# ============================================================================
print("\n🔧 ÉTAPE 3: Préparation des features...")

# Sélectionner les colonnes pour l'entraînement
feature_cols = [col for col in df_processed.columns if col.startswith('Vital_') or col.startswith('Lab_')]
feature_cols.extend(['Age', 'Sexe_Encoded', 'Groupe_Age_Encoded', 'Severite_Encoded', 'Duree_Symptomes_Jours'])
feature_cols.extend([col for col in df_processed.columns if col.startswith('symptom_')])

X = df_processed[feature_cols].fillna(0)
y = df_processed['Maladie_Encoded']

print(f"  ✓ Features sélectionnées: {X.shape[1]}")
print(f"  ✓ Target: {len(np.unique(y))} maladies")

# ============================================================================
# ÉTAPE 4: NORMALISATION & SPLIT
# ============================================================================
print("\n⚖️  ÉTAPE 4: Normalisation et split...")

# Split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# Normalisation
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

print(f"  ✓ Entraînement: {X_train_scaled.shape[0]} cas")
print(f"  ✓ Test: {X_test_scaled.shape[0]} cas")
print(f"  ✓ Normalisation effectuée")

# ============================================================================
# ÉTAPE 5: ENTRAÎNEMENT DU MODÈLE
# ============================================================================
print("\n🤖 ÉTAPE 5: Entraînement du modèle...")

model = RandomForestClassifier(
    n_estimators=150,
    max_depth=20,
    min_samples_split=5,
    min_samples_leaf=2,
    random_state=42,
    n_jobs=-1,
    class_weight='balanced'
)

# Utiliser les données non-normalisées pour Random Forest (il ne le nécessite pas)
X_train_rf = X_train.fillna(0)
X_test_rf = X_test.fillna(0)

model.fit(X_train_rf, y_train)
print(f"  ✓ Modèle entraîné")

# ============================================================================
# ÉTAPE 6: ÉVALUATION
# ============================================================================
print("\n📊 ÉTAPE 6: Évaluation du modèle...")

y_pred_train = model.predict(X_train_rf)
y_pred_test = model.predict(X_test_rf)

train_accuracy = accuracy_score(y_train, y_pred_train)
test_accuracy = accuracy_score(y_test, y_pred_test)

print(f"  ✓ Accuracy Entraînement: {train_accuracy:.4f}")
print(f"  ✓ Accuracy Test: {test_accuracy:.4f}")

# Features importance
feature_importance = pd.DataFrame({
    'Feature': feature_cols,
    'Importance': model.feature_importances_
}).sort_values('Importance', ascending=False)

print(f"\n  Top 10 Features les plus importantes:")
for idx, row in feature_importance.head(10).iterrows():
    print(f"    {idx+1:2d}. {row['Feature']:40s} : {row['Importance']*100:6.2f}%")

# ============================================================================
# ÉTAPE 7: FONCTION DE PRÉDICTION POUR NOUVEAUX CAS
# ============================================================================
print("\n🔮 ÉTAPE 7: Fonction de diagnostic...")

def diagnose_patient(symptoms_str, age, sexe, glucose=None, hb=None, leucocytes=None, 
                    tension_sys=None, fc=None, temp=None, severite='Modérée'):
    """
    Fonction pour diagnostiquer un nouveau patient
    
    Parameters:
    -----------
    symptoms_str : str
        Symptômes séparés par des virgules (ex: "Fièvre, Toux, Fatigue")
    age : int
        Âge du patient
    sexe : str
        'M' ou 'F'
    glucose : float, optional
        Glucose (mg/dL)
    hb : float, optional
        Hémoglobine (g/dL)
    leucocytes : float, optional
        Globules blancs (K/µL)
    tension_sys : float, optional
        Tension systolique (mmHg)
    fc : float, optional
        Fréquence cardiaque (bpm)
    temp : float, optional
        Température (°C)
    severite : str
        'Légère', 'Modérée', 'Sévère', ou 'Critique'
    
    Returns:
    --------
    dict : Dictionnaire contenant les diagnostics prédits avec confidences
    """
    
    # Créer le vecteur de features
    new_case = {}
    
    # Features numériques basiques
    new_case['Age'] = age
    new_case['Sexe_Encoded'] = le_sexe.transform([sexe])[0]
    new_case['Severite_Encoded'] = le_severite.transform([severite])[0]
    new_case['Duree_Symptomes_Jours'] = 7  # Par défaut
    
    # Signes vitaux
    for col in feature_cols:
        if col.startswith('Vital_'):
            # Utiliser des valeurs normales par défaut
            if 'Glucose' in col:
                new_case[col] = glucose if glucose else 95.0
            elif 'Tension Systolique' in col:
                new_case[col] = tension_sys if tension_sys else 120.0
            elif 'Fréquence Cardiaque' in col:
                new_case[col] = fc if fc else 75.0
            elif 'Température' in col:
                new_case[col] = temp if temp else 37.0
            else:
                new_case[col] = 0  # Défaut pour autres signes vitaux
    
    # Analyses biologiques
    for col in feature_cols:
        if col.startswith('Lab_'):
            if 'Hémoglobine' in col:
                new_case[col] = hb if hb else 14.0
            elif 'Globules Blancs' in col:
                new_case[col] = leucocytes if leucocytes else 7.0
            elif 'Glucose' in col:
                new_case[col] = glucose if glucose else 95.0
            else:
                new_case[col] = 0  # Défaut
    
    # Symptômes
    symptoms_list = [s.strip() for s in symptoms_str.split(',')]
    for symptom in unique_symptoms[:50]:
        col_name = f'symptom_{symptom.lower().replace(" ", "_")}'
        if col_name in feature_cols:
            new_case[col_name] = 1 if symptom in symptoms_list else 0
    
    # Remplir les colonnes manquantes avec 0
    for col in feature_cols:
        if col not in new_case:
            new_case[col] = 0
    
    # Créer le dataframe et prédire
    case_df = pd.DataFrame([new_case])
    proba = model.predict_proba(case_df)[0]
    
    # Top 5 diagnostics
    top_indices = np.argsort(proba)[-5:][::-1]
    
    results = []
    for idx in top_indices:
        disease_name = le_maladie.inverse_transform([idx])[0]
        confidence = float(proba[idx])
        results.append({
            'disease': disease_name,
            'confidence': confidence,
            'confidence_percentage': f"{confidence * 100:.2f}%"
        })
    
    return {
        'symptoms': symptoms_list,
        'patient_info': {
            'age': age,
            'sexe': sexe,
            'severite': severite
        },
        'top_diagnostics': results,
        'model_accuracy': f"{test_accuracy * 100:.2f}%"
    }

# ============================================================================
# ÉTAPE 8: EXEMPLES DE DIAGNOSTIC
# ============================================================================
print("\n" + "=" * 80)
print("EXEMPLES DE DIAGNOSTIC")
print("=" * 80)

# Cas 1: Symptômes de grippe
print("\n\n🔹 CAS 1: Patient avec symptômes de grippe")
print("-" * 80)
result1 = diagnose_patient(
    symptoms_str="Fièvre, Toux, Mal de gorge, Fatigue, Maux de tête",
    age=35,
    sexe='M',
    temp=38.5,
    hb=13.5,
    leucocytes=8.5
)
print(f"Symptômes: {', '.join(result1['symptoms'])}")
print(f"Info patient: Age {result1['patient_info']['age']} ans, {result1['patient_info']['sexe']}")
print(f"\nTop Diagnostics:")
for i, diag in enumerate(result1['top_diagnostics'], 1):
    print(f"  {i}. {diag['disease']:40s} : {diag['confidence_percentage']:>6s} confiance")

# Cas 2: Symptômes diabétiques
print("\n\n🔹 CAS 2: Patient avec symptômes de diabète")
print("-" * 80)
result2 = diagnose_patient(
    symptoms_str="Soif excessive, Urination fréquente, Fatigue, Vision floue",
    age=55,
    sexe='F',
    glucose=250,
    hb=12.0,
    leucocytes=6.5
)
print(f"Symptômes: {', '.join(result2['symptoms'])}")
print(f"Info patient: Age {result2['patient_info']['age']} ans, {result2['patient_info']['sexe']}")
print(f"Glucose: {glucose} mg/dL (anormal)")
print(f"\nTop Diagnostics:")
for i, diag in enumerate(result2['top_diagnostics'], 1):
    print(f"  {i}. {diag['disease']:40s} : {diag['confidence_percentage']:>6s} confiance")

# Cas 3: Symptômes cardiovasculaires
print("\n\n🔹 CAS 3: Patient avec symptômes cardiovasculaires")
print("-" * 80)
result3 = diagnose_patient(
    symptoms_str="Douleur thoracique, Essoufflement, Sueurs froides, Nausées",
    age=65,
    sexe='M',
    tension_sys=160,
    fc=110,
    temp=36.8,
    severite='Critique'
)
print(f"Symptômes: {', '.join(result3['symptoms'])}")
print(f"Info patient: Age {result3['patient_info']['age']} ans, {result3['patient_info']['sexe']}")
print(f"Signes vitaux: TA {tension_sys}/?, FC {fc} bpm")
print(f"\nTop Diagnostics:")
for i, diag in enumerate(result3['top_diagnostics'], 1):
    print(f"  {i}. {diag['disease']:40s} : {diag['confidence_percentage']:>6s} confiance")

# ============================================================================
# ÉTAPE 9: EXPORT DU MODÈLE
# ============================================================================
print("\n\n" + "=" * 80)
print("EXPORT & SAUVEGARDE")
print("=" * 80)

# Sauvegarder la configuration
config = {
    'n_diseases': len(np.unique(y)),
    'n_features': X.shape[1],
    'model_type': 'RandomForestClassifier',
    'test_accuracy': float(test_accuracy),
    'train_accuracy': float(train_accuracy),
    'symptoms_used': list(unique_symptoms[:50]),
    'diseases': list(le_maladie.classes_)
}

with open('model_config.json', 'w', encoding='utf-8') as f:
    json.dump(config, f, ensure_ascii=False, indent=2)
print(f"\n✓ Configuration sauvegardée: model_config.json")

# Sauvegarder les encoders
import pickle
with open('encoders.pkl', 'wb') as f:
    pickle.dump(encoders, f)
print(f"✓ Encoders sauvegardés: encoders.pkl")

# Sauvegarder le modèle
with open('model.pkl', 'wb') as f:
    pickle.dump(model, f)
print(f"✓ Modèle sauvegardé: model.pkl")

print("\n" + "=" * 80)
print("✅ INTÉGRATION COMPLÈTE TERMINÉE")
print("=" * 80)
print(f"\nVous pouvez maintenant utiliser ce système pour diagnostiquer de nouveaux patients!")
print(f"Précision du modèle: {test_accuracy*100:.2f}%")
print(f"Capable de diagnostiquer {len(np.unique(y))} maladies différentes")
