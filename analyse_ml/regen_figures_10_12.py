#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Régénère uniquement les figures 10 et 12 sans réentraîner le modèle complet."""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, learning_curve
from sklearn.preprocessing import LabelEncoder, MultiLabelBinarizer
import warnings, os

warnings.filterwarnings('ignore')
plt.rcParams['figure.dpi'] = 150
plt.rcParams['font.size'] = 10
plt.rcParams['figure.facecolor'] = 'white'
sns.set_style("whitegrid")
os.makedirs('figures', exist_ok=True)

print("Chargement du dataset...")
df = pd.read_csv("../les ressources dataset/dataset_medical_robust_10000_cas.csv", encoding='utf-8')
n_obs = len(df)

# ── Prétraitement identique à analyse_complete.py ──
numerical_cols = df.select_dtypes(include=[np.number]).columns.tolist()
numerical_cols = [c for c in numerical_cols if c != 'ID']

le_sexe = LabelEncoder()
df['Sexe_enc'] = le_sexe.fit_transform(df['Sexe'].fillna('M'))
severity_map = {'Légère': 1, 'Modérée': 2, 'Sévère': 3, 'Critique': 4}
df['Severite_enc'] = df['Severite'].map(severity_map).fillna(2).astype(int)
groupe_age_map = {'0-10': 0, '11-17': 1, '18-30': 2, '31-50': 3, '50-65': 4, '65+': 5}
df['Groupe_Age_enc'] = df['Groupe_Age'].map(groupe_age_map).fillna(3).astype(int)

symptoms_lists = df['Symptomes_Rapportes'].fillna('').apply(
    lambda s: [x.strip() for x in s.split(',') if x.strip()])
mlb = MultiLabelBinarizer()
symptom_matrix = mlb.fit_transform(symptoms_lists)
symptom_cols = [f'SYM_{s.replace(" ", "_").replace("/", "_")}' for s in mlb.classes_]
df_symptoms = pd.DataFrame(symptom_matrix, columns=symptom_cols, index=df.index)

num_cat_cols = numerical_cols + ['Sexe_enc', 'Severite_enc', 'Groupe_Age_enc']
num_cat_cols = [c for c in num_cat_cols if c in df.columns]
X_num = df[num_cat_cols].fillna(df[num_cat_cols].median())
X = pd.concat([X_num.reset_index(drop=True), df_symptoms.reset_index(drop=True)], axis=1)
feature_cols = list(X.columns)

le_target = LabelEncoder()
y = le_target.fit_transform(df['Maladie_Diagnostic'])

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y)

print(f"Dataset: {n_obs} obs | {len(feature_cols)} features | {len(le_target.classes_)} classes")

# ══════════════════════════════════════════════════════════════
# FIGURE 10 — Courbe d'apprentissage (modèle régularisé)
# ══════════════════════════════════════════════════════════════
print("\nGénération figure 10 – Courbe d'apprentissage...")

train_sizes_rel = np.linspace(0.1, 1.0, 9)
train_sizes_abs, train_scores, val_scores = learning_curve(
    RandomForestClassifier(
        n_estimators=100,
        max_depth=18,
        min_samples_leaf=4,
        min_samples_split=10,
        max_features='sqrt',
        class_weight='balanced',
        random_state=42,
        n_jobs=-1
    ),
    X_train, y_train,
    train_sizes=train_sizes_rel,
    cv=3,
    scoring='accuracy',
    n_jobs=-1,
    shuffle=True,
    random_state=42
)

tr_mean = np.mean(train_scores, axis=1)
tr_std  = np.std(train_scores, axis=1)
vl_mean = np.mean(val_scores, axis=1)
vl_std  = np.std(val_scores, axis=1)

fig, ax = plt.subplots(figsize=(13, 7))
ax.plot(train_sizes_abs, tr_mean, 'o-', color='#2980B9',
        label='Score Entraînement', linewidth=2.5, markersize=8)
ax.fill_between(train_sizes_abs, tr_mean - tr_std, tr_mean + tr_std,
                alpha=0.15, color='#2980B9')
ax.plot(train_sizes_abs, vl_mean, 's-', color='#27AE60',
        label='Score Validation (CV=3)', linewidth=2.5, markersize=8)
ax.fill_between(train_sizes_abs, vl_mean - vl_std, vl_mean + vl_std,
                alpha=0.15, color='#27AE60')

for x, yt, yv in zip(train_sizes_abs, tr_mean, vl_mean):
    ax.annotate(f'{yt:.3f}', (x, yt),
                textcoords='offset points', xytext=(0, 8),
                fontsize=8.5, color='#2980B9', fontweight='bold')
    ax.annotate(f'{yv:.3f}', (x, yv),
                textcoords='offset points', xytext=(0, -16),
                fontsize=8.5, color='#27AE60', fontweight='bold')

gap_final = tr_mean[-1] - vl_mean[-1]
ax.set_xlabel("Nombre d'exemples d'entraînement", fontsize=12, fontweight='bold')
ax.set_ylabel("Score (Accuracy)", fontsize=12, fontweight='bold')
ax.set_title(
    "Courbe d'Apprentissage – Random Forest\n"
    f"Evolution de la performance selon la taille du dataset  |  Ecart train/val final : {gap_final:.3f}",
    fontsize=13, fontweight='bold'
)
ax.legend(loc='lower right', fontsize=11)
y_min = max(0.5, min(vl_mean) - 0.08)
ax.set_ylim([y_min, min(1.0, max(tr_mean)) + 0.06])
ax.grid(True, alpha=0.3)
ax.set_xticks(train_sizes_abs)
ax.set_xticklabels([f'{int(s):,}' for s in train_sizes_abs], rotation=25)
plt.tight_layout()
plt.savefig('figures/10_courbe_apprentissage.png', bbox_inches='tight')
plt.close()
print("  -> figures/10_courbe_apprentissage.png  OK")

# ══════════════════════════════════════════════════════════════
# FIGURE 12 — Centrage/Réduction par groupes cliniques
# ══════════════════════════════════════════════════════════════
print("\nGénération figure 12 – Centrage/Réduction par groupes cliniques...")

GROUPES_CLINIQUES = {
    'Signes Vitaux': {
        'cols': [c for c in numerical_cols if c.startswith('Vital_')],
        'color': '#2980B9', 'facecolor': '#AED6F1'
    },
    'Hématologie (NFS)': {
        'cols': [c for c in numerical_cols if c.startswith('Lab_') and any(k in c for k in [
            'moglobine', 'matocrite', 'Globules', 'Plaquettes',
            'Neutrophiles', 'Lymphocytes', 'Monocytes', 'Eosinophiles', 'Basophiles', 'VGM', 'CCMH'
        ])],
        'color': '#8E44AD', 'facecolor': '#D7BDE2'
    },
    'Bilan Métabolique': {
        'cols': [c for c in numerical_cols if c.startswith('Lab_') and any(k in c for k in [
            'Glucose', 'HbA1c', 'Cholest', 'Triglyc', 'Acide urique'
        ])],
        'color': '#D35400', 'facecolor': '#FAD7A0'
    },
    'Bilan Rénal & Ionogramme': {
        'cols': [c for c in numerical_cols if c.startswith('Lab_') and any(k in c for k in [
            'atinine', 'Ur', 'TFG', 'Sodium', 'Potassium', 'Chlore', 'Calcium', 'Phosphore', 'agn'
        ])],
        'color': '#1A8A4A', 'facecolor': '#A9DFBF'
    },
    'Bilan Hépatique': {
        'cols': [c for c in numerical_cols if c.startswith('Lab_') and any(k in c for k in [
            'ALT', 'AST', 'Bilirubine', 'Phosphatase', 'GGT', 'Albumine', 'ot', 'Globulines', 'Ratio'
        ])],
        'color': '#B7950B', 'facecolor': '#F9E79F'
    },
    'Marqueurs Cardiaques & Coagulation': {
        'cols': [c for c in numerical_cols if c.startswith('Lab_') and any(k in c for k in [
            'CK', 'Myoglobine', 'Troponine', 'BNP', 'ProBNP',
            'PT', 'aPTT', 'TT', 'Fibrin', 'CRP', 'ESR', 'PSA'
        ])],
        'color': '#C0392B', 'facecolor': '#F5B7B1'
    },
}

GROUPES_CLINIQUES = {
    nom: g for nom, g in GROUPES_CLINIQUES.items()
    if any(c in X.columns for c in g['cols'])
}

n_groupes = len(GROUPES_CLINIQUES)
fig, axes = plt.subplots(n_groupes, 1, figsize=(20, 5 * n_groupes))
if n_groupes == 1:
    axes = [axes]

for ax, (nom_groupe, ginfo) in zip(axes, GROUPES_CLINIQUES.items()):
    cols_g = [c for c in ginfo['cols'] if c in X.columns]
    if not cols_g:
        ax.set_visible(False)
        continue

    data_g  = X[cols_g].copy()
    means_g = data_g.mean()
    stds_g  = data_g.std().replace(0, 1)
    data_z  = (data_g - means_g) / stds_g

    ax.boxplot(
        [data_z[c].dropna() for c in cols_g],
        vert=True, patch_artist=True, widths=0.55,
        boxprops=dict(facecolor=ginfo['facecolor'], color=ginfo['color']),
        medianprops=dict(color='#C0392B', linewidth=2),
        whiskerprops=dict(color=ginfo['color'], linewidth=1.2),
        capprops=dict(color=ginfo['color'], linewidth=1.5),
        flierprops=dict(marker='o', color='#7F8C8D', alpha=0.25, markersize=3)
    )

    short_lbl = [c.replace('Lab_', '').replace('Vital_', '')[:28] for c in cols_g]
    ax.set_xticks(range(1, len(cols_g) + 1))
    ax.set_xticklabels(short_lbl, rotation=35, ha='right', fontsize=8.5)
    ax.set_ylabel('z-score', fontsize=9, fontweight='bold')
    ax.set_title(f'{nom_groupe}  ({len(cols_g)} attributs)', fontsize=11,
                 fontweight='bold', color=ginfo['color'], pad=6)
    ax.axhline(y=0,  color='red',    linestyle='--', alpha=0.45, linewidth=1)
    ax.axhline(y=1,  color='orange', linestyle=':',  alpha=0.35, linewidth=1)
    ax.axhline(y=-1, color='orange', linestyle=':',  alpha=0.35, linewidth=1)
    ax.grid(axis='y', alpha=0.25)

fig.suptitle(
    'Centrage / Réduction (z-score) par Groupes Cliniques\n'
    'Variabilité et dispersion des attributs biologiques après standardisation',
    fontsize=14, fontweight='bold', y=1.002
)
plt.tight_layout()
plt.savefig('figures/12_centrage_reduction_quartiles.png', bbox_inches='tight')
plt.close()
print("  -> figures/12_centrage_reduction_quartiles.png  OK")
print("\nTerminé.")
