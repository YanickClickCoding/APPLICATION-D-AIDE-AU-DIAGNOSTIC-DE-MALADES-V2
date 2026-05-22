#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Régénère uniquement la figure 11 (métriques globales) avec le modèle régularisé."""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, MultiLabelBinarizer
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import warnings, os

warnings.filterwarnings('ignore')
plt.rcParams['figure.dpi'] = 150
plt.rcParams['font.size'] = 10
plt.rcParams['figure.facecolor'] = 'white'
os.makedirs('figures', exist_ok=True)

print("Chargement du dataset...")
df = pd.read_csv("../les ressources dataset/dataset_medical_robust_10000_cas.csv", encoding='utf-8')
n_obs = len(df)

numerical_cols = df.select_dtypes(include=[np.number]).columns.tolist()
numerical_cols = [c for c in numerical_cols if c != 'ID']

le_sexe = LabelEncoder()
df['Sexe_enc'] = le_sexe.fit_transform(df['Sexe'].fillna('M'))
severity_map = {'Légère': 1, 'Modérée': 2, 'Sévère': 3, 'Critique': 4}
df['Severite_enc'] = df['Severite'].map(severity_map).fillna(2).astype(int)
groupe_age_map = {'0-10': 0, '11-17': 1, '18-30': 2, '31-50': 3, '50-65': 4, '65+': 5}
df['Groupe_Age_enc'] = df['Groupe_Age'].map(groupe_age_map).fillna(3).astype(int)

# Features d'ingénierie (identiques au pipeline backend)
df['categorie_age'] = pd.cut(df['Age'], bins=[0, 12, 18, 60, 120],
                              labels=[0, 1, 2, 3]).astype(float).fillna(2)
fc_col  = 'Vital_Fréquence Cardiaque (bpm)'
o2_col  = 'Vital_Saturation O2 (%)'
tmp_col = 'Vital_Température (°C)'
if fc_col in df.columns and o2_col in df.columns:
    df['ratio_fc_o2'] = df[fc_col] / (df[o2_col] + 1)

symptoms_lists = df['Symptomes_Rapportes'].fillna('').apply(
    lambda s: [x.strip() for x in s.split(',') if x.strip()])
df['nombre_symptomes'] = symptoms_lists.apply(len)

if tmp_col in df.columns and o2_col in df.columns:
    df['score_risque'] = ((df[tmp_col] > 38.5).astype(int) * 2
                          + (df[o2_col] < 95).astype(int) * 3
                          + df['nombre_symptomes'])

mlb = MultiLabelBinarizer()
symptom_matrix = mlb.fit_transform(symptoms_lists)
symptom_cols = [f'SYM_{s.replace(" ", "_").replace("/", "_")}' for s in mlb.classes_]
df_symptoms = pd.DataFrame(symptom_matrix, columns=symptom_cols, index=df.index)

eng_cols = ['categorie_age', 'ratio_fc_o2', 'score_risque', 'nombre_symptomes']
num_cat_cols = numerical_cols + ['Sexe_enc', 'Severite_enc', 'Groupe_Age_enc'] + [c for c in eng_cols if c in df.columns]
num_cat_cols = [c for c in num_cat_cols if c in df.columns]
X_num = df[num_cat_cols].fillna(df[num_cat_cols].median())
X = pd.concat([X_num.reset_index(drop=True), df_symptoms.reset_index(drop=True)], axis=1)

le_target = LabelEncoder()
y = le_target.fit_transform(df['Maladie_Diagnostic'])
n_classes = len(le_target.classes_)

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y)

print(f"Dataset: {n_obs} obs | {X.shape[1]} features | {n_classes} classes")
print("Entraînement du modèle régularisé (max_depth=18)...")

rf_model = RandomForestClassifier(
    n_estimators=200,
    max_depth=30,
    min_samples_split=5,
    min_samples_leaf=2,
    max_features='sqrt',
    class_weight='balanced',
    n_jobs=-1,
    random_state=42
)
rf_model.fit(X_train, y_train)
y_pred = rf_model.predict(X_test)

accuracy  = accuracy_score(y_test, y_pred)
precision = precision_score(y_test, y_pred, average='weighted', zero_division=0)
recall    = recall_score(y_test, y_pred, average='weighted', zero_division=0)
f1        = f1_score(y_test, y_pred, average='weighted', zero_division=0)

print(f"  Accuracy  : {accuracy*100:.2f}%")
print(f"  Precision : {precision*100:.2f}%")
print(f"  Rappel    : {recall*100:.2f}%")
print(f"  F1-Score  : {f1*100:.2f}%")

print("\nGénération figure 11 – Métriques globales...")

metrics_labels = ['Accuracy', 'Précision\n(weighted)', 'Rappel\n(weighted)', 'F1-Score\n(weighted)']
metrics_values = [accuracy, precision, recall, f1]
colors_metrics = ['#2196F3', '#4CAF50', '#FF9800', '#E91E63']

fig, ax = plt.subplots(figsize=(10, 6))
bars = ax.bar(metrics_labels, metrics_values,
              color=colors_metrics, edgecolor='white', linewidth=1.5, width=0.5)
ax.set_ylim([0, 1.18])
ax.set_ylabel('Score', fontsize=12, fontweight='bold')
ax.set_title(
    "Métriques d'Évaluation – Random Forest\n"
    f"({n_classes} classes  |  {n_obs:,} observations  |  200 arbres  |  max_depth=30)",
    fontsize=13, fontweight='bold'
)
ax.axhline(y=1.0, color='gray', linestyle='--', alpha=0.4, linewidth=1)
for bar, val in zip(bars, metrics_values):
    ax.text(
        bar.get_x() + bar.get_width() / 2,
        bar.get_height() + 0.015,
        f'{val:.4f}\n({val*100:.2f} %)',
        ha='center', va='bottom',
        fontsize=12, fontweight='bold'
    )
ax.tick_params(axis='x', labelsize=11)

plt.tight_layout()
plt.savefig('figures/11_metriques_globales.png', bbox_inches='tight')
plt.close()
print("  -> figures/11_metriques_globales.png  OK")
