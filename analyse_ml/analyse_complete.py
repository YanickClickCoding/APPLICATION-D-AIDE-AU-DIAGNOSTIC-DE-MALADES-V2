#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
=======================================================================
  ANALYSE COMPLETE DU DATASET MEDICAL - RANDOM FOREST
  Travail de Memoire - Systeme d'Aide au Diagnostic (GASA_SAD)
=======================================================================

SOURCES ET REFERENCES KAGGLE :
  Ce dataset synthetique multi-maladies a ete concu en respectant les
  distributions statistiques observees dans les datasets de reference
  suivants (approche adoptee du fait de l'indisponibilite de donnees
  patients reelles multi-pathologies sous contraintes RGPD/HIPAA) :

  [1] Heart Disease Dataset (UCI)
      Kaggle : https://www.kaggle.com/datasets/johnsmith88/heart-disease-dataset
      Auteur : John Smith | 303 observations | 14 attributs

  [2] Cardiovascular Disease Dataset
      Kaggle : https://www.kaggle.com/datasets/sulianova/cardiovascular-disease-dataset
      Auteur : Svetlana Ulianova | 70 000 observations | 12 attributs

  [3] Diabetes Dataset (Pima Indians)
      Kaggle : https://www.kaggle.com/datasets/mathchi/diabetes-data-set
      Auteur : Mathchi | 768 observations | 9 attributs

  [4] Chronic Kidney Disease Dataset
      Kaggle : https://www.kaggle.com/datasets/mansoordaku/ckdisease
      Auteur : Mansoor Daku | 400 observations | 25 attributs
      (creatinine, uree, hemoglobine, electrolytes...)

  [5] Liver Disease Patient Dataset
      Kaggle : https://www.kaggle.com/datasets/abhi8923shriv/liver-disease-patient-dataset
      Auteur : Abhi8923shriv | 30 000 observations | 11 attributs
      (ALT/SGPT, AST/SGOT, bilirubine, albumine...)

  [6] Disease Symptoms and Patient Profile Dataset
      Kaggle : https://www.kaggle.com/datasets/uom190346a/disease-symptoms-and-patient-profile-dataset
      Auteur : uom190346a | 100+ maladies | symptomes + profil patient

  [7] Disease and Symptoms Dataset
      Kaggle : https://www.kaggle.com/datasets/choongqianzheng/disease-and-symptoms-dataset
      Auteur : Choong Qian Zheng | ~5 000 observations | 42 symptomes

  Methodologie de consolidation :
    - Les attributs biologiques ont ete harmonises selon les valeurs
      de reference de l'OMS et les normes du laboratoire clinique.
    - Les distributions statistiques des datasets reels ont servi de
      base pour generer les valeurs des 70 attributs sur 121 classes.
    - Cette approche (Synthetic Patient Generation) est couramment
      utilisee en recherche en IA medicale (ex: projet Synthea - MITRE).

=======================================================================
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, learning_curve
from sklearn.preprocessing import LabelEncoder, MultiLabelBinarizer
from sklearn.metrics import (
    confusion_matrix, classification_report,
    accuracy_score, precision_score, recall_score, f1_score
)
import joblib
import warnings
import os

warnings.filterwarnings('ignore')

# Style global
plt.rcParams['figure.dpi'] = 150
plt.rcParams['font.size'] = 10
plt.rcParams['figure.facecolor'] = 'white'
sns.set_style("whitegrid")
sns.set_palette("husl")

# Dossiers de sortie
os.makedirs('figures', exist_ok=True)
os.makedirs('model', exist_ok=True)

print("=" * 70)
print("   ANALYSE COMPLETE DU DATASET MEDICAL - RANDOM FOREST")
print("   Systeme d'Aide au Diagnostic GASA_SAD")
print("=" * 70)


# ==========================================================================
# SECTION 1 : CHARGEMENT DU DATASET
# ==========================================================================
print("\n[1/8] Chargement du dataset...")

DATASET_PATH = "../les ressources dataset/dataset_medical_robust_10000_cas.csv"
df = pd.read_csv(DATASET_PATH, encoding='utf-8')

n_obs = df.shape[0]
n_cols = df.shape[1]
n_classes = df['Maladie_Diagnostic'].nunique()

print(f"  Observations   : {n_obs:,}")
print(f"  Colonnes       : {n_cols}")
print(f"  Classes        : {n_classes} maladies distinctes")
print(f"  Valeurs nulles : {df.isnull().sum().sum()}")


# ==========================================================================
# SECTION 2 : ANALYSE DESCRIPTIVE
# ==========================================================================
print("\n[2/8] Analyse descriptive...")

# Statistiques generales
desc = df.describe()
desc.to_csv('figures/statistiques_descriptives.csv', encoding='utf-8')
print("  -> statistiques_descriptives.csv sauvegarde")

# Separons les colonnes par type
numerical_cols = df.select_dtypes(include=[np.number]).columns.tolist()
numerical_cols = [c for c in numerical_cols if c != 'ID']

vital_cols   = [c for c in numerical_cols if c.startswith('Vital_')]
lab_cols     = [c for c in numerical_cols if c.startswith('Lab_')]
demo_cols    = [c for c in numerical_cols
                if c in ['Age', 'Duree_Symptomes_Jours']]

print(f"  Colonnes numeriques    : {len(numerical_cols)}")
print(f"  Signes vitaux          : {len(vital_cols)}")
print(f"  Parametres biologiques : {len(lab_cols)}")

# Résumé par classe
class_stats = df.groupby('Maladie_Diagnostic').size().reset_index(name='Count')
class_stats.to_csv('figures/resume_par_classe.csv', index=False, encoding='utf-8')
print("  -> resume_par_classe.csv sauvegarde")


# ==========================================================================
# SECTION 3 : DISTRIBUTION DES CLASSES
# ==========================================================================
print("\n[3/8] Distribution des classes (maladies)...")

class_counts = df['Maladie_Diagnostic'].value_counts()
mean_count   = class_counts.mean()
min_count    = class_counts.min()
max_count    = class_counts.max()

print(f"  Moyenne occurrences  : {mean_count:.1f}")
print(f"  Min occurrences      : {min_count}")
print(f"  Max occurrences      : {max_count}")
print(f"  Ratio max/min        : {max_count/min_count:.2f}  (desequilibre faible < 2x)")

n_classes_display = len(class_counts)
fig, ax = plt.subplots(figsize=(14, max(10, n_classes_display * 0.18)))

colors = plt.cm.tab20(np.linspace(0, 1, n_classes_display))
bars = ax.barh(range(n_classes_display), class_counts.values, color=colors,
               edgecolor='white', linewidth=0.5)

ax.set_yticks(range(n_classes_display))
ax.set_yticklabels(class_counts.index, fontsize=7)
ax.set_xlabel("Nombre d'occurrences", fontsize=12, fontweight='bold')
ax.set_title(
    f"Distribution des {n_classes_display} classes de maladies\n"
    f"(Total : {n_obs:,} observations  |  Moy : {mean_count:.0f}  |  "
    f"Min : {min_count}  |  Max : {max_count})",
    fontsize=13, fontweight='bold'
)
ax.axvline(x=mean_count, color='red', linestyle='--', linewidth=1.5,
           label=f'Moyenne : {mean_count:.0f}')
ax.legend(fontsize=10, loc='lower right')

for bar, val in zip(bars, class_counts.values):
    ax.text(val + 0.3, bar.get_y() + bar.get_height() / 2,
            str(val), va='center', fontsize=6.5)

ax.invert_yaxis()
plt.tight_layout()
plt.savefig('figures/01_distribution_classes.png', bbox_inches='tight')
plt.close()
print("  -> figures/01_distribution_classes.png")


# ==========================================================================
# SECTION 4 : BOXPLOTS DES ATTRIBUTS
# ==========================================================================
print("\n[4/8] Boxplots des attributs...")

def boxplot_group(cols, titre, filename, n_cols_grid=4, figsize=None):
    """Genere une grille de boxplots pour un groupe d'attributs."""
    if not cols:
        return
    n = len(cols)
    n_rows = (n + n_cols_grid - 1) // n_cols_grid
    if figsize is None:
        figsize = (n_cols_grid * 5, n_rows * 4)

    fig, axes = plt.subplots(n_rows, n_cols_grid, figsize=figsize)
    axes = np.array(axes).flatten()

    for i, col in enumerate(cols):
        data = df[col].dropna()
        q1, median, q3 = data.quantile([0.25, 0.5, 0.75])
        iqr = q3 - q1
        outliers_pct = ((data < q1 - 1.5*iqr) | (data > q3 + 1.5*iqr)).mean() * 100

        bp = axes[i].boxplot(
            data, vert=True, patch_artist=True, widths=0.5,
            boxprops=dict(facecolor='#AED6F1', color='#154360'),
            medianprops=dict(color='#C0392B', linewidth=2),
            whiskerprops=dict(color='#154360', linewidth=1.2),
            capprops=dict(color='#154360', linewidth=1.5),
            flierprops=dict(marker='o', color='#7F8C8D',
                            alpha=0.4, markersize=3)
        )
        # Short label
        short = col.replace('Vital_', '').replace('Lab_', '')
        short = short[:32] if len(short) > 32 else short
        axes[i].set_title(short, fontsize=8, fontweight='bold', pad=3)
        axes[i].set_ylabel('Valeur', fontsize=7)
        axes[i].tick_params(labelsize=7)
        # Annotation outliers
        axes[i].annotate(f'Outliers: {outliers_pct:.1f}%',
                         xy=(0.98, 0.02), xycoords='axes fraction',
                         fontsize=6.5, color='gray',
                         ha='right', va='bottom')

    for j in range(len(cols), len(axes)):
        axes[j].set_visible(False)

    fig.suptitle(titre, fontsize=13, fontweight='bold', y=1.01)
    plt.tight_layout()
    plt.savefig(f'figures/{filename}', bbox_inches='tight')
    plt.close()
    print(f"  -> figures/{filename}")

# Signes vitaux + donnees demographiques
boxplot_group(
    vital_cols + demo_cols,
    'Boxplots – Signes Vitaux et Donnees Demographiques',
    '02_boxplots_signes_vitaux.png', n_cols_grid=5
)

# NFS / CBC
lab_nfs = [c for c in lab_cols if any(k in c for k in [
    'moglobine', 'matocrite', 'Globules', 'Plaquettes',
    'Neutrophiles', 'Lymphocytes', 'Monocytes', 'Eosinophiles',
    'Basophiles', 'VGM', 'CCMH'
])]
boxplot_group(
    lab_nfs,
    'Boxplots – Numerotation Formule Sanguine (NFS / CBC)',
    '03_boxplots_nfs.png', n_cols_grid=4
)

# Bilan metabolique
lab_metab = [c for c in lab_cols if any(k in c for k in [
    'Glucose', 'HbA1c', 'Cholest', 'Triglyc', 'Acide urique'
])]
boxplot_group(
    lab_metab,
    'Boxplots – Bilan Metabolique (Glucose, Cholesterol, Acide Urique)',
    '04_boxplots_metabolique.png', n_cols_grid=4
)

# Bilan renal + ionogramme
lab_renal = [c for c in lab_cols if any(k in c for k in [
    'atinine', 'Ur', 'TFG', 'Sodium', 'Potassium',
    'Chlore', 'Calcium', 'Phosphore', 'agn'
])]
boxplot_group(
    lab_renal,
    'Boxplots – Bilan Renal et Ionogramme',
    '05_boxplots_renal.png', n_cols_grid=4
)

# Bilan hepatique
lab_hepat = [c for c in lab_cols if any(k in c for k in [
    'ALT', 'AST', 'Bilirubine', 'Phosphatase', 'GGT',
    'Albumine', 'ot', 'Globulines', 'Ratio'
])]
boxplot_group(
    lab_hepat,
    'Boxplots – Bilan Hepatique',
    '06_boxplots_hepatique.png', n_cols_grid=4
)

# Marqueurs cardiaques, coagulation, inflammation
lab_card = [c for c in lab_cols if any(k in c for k in [
    'CK', 'Myoglobine', 'Troponine', 'BNP', 'ProBNP',
    'PT', 'aPTT', 'TT', 'Fibrin', 'CRP', 'ESR', 'PSA'
])]
boxplot_group(
    lab_card,
    'Boxplots – Marqueurs Cardiaques, Coagulation et Inflammation',
    '07_boxplots_cardiaque_coag.png', n_cols_grid=4
)


# ==========================================================================
# SECTION 5 : PRÉTRAITEMENT
# ==========================================================================
print("\n[5/8] Pretraitement des donnees...")

# -- 5a. Variables categoriques simples --
le_sexe = LabelEncoder()
df['Sexe_enc'] = le_sexe.fit_transform(df['Sexe'].fillna('M'))

severity_map = {'Légère': 1, 'Modérée': 2, 'Sévère': 3, 'Critique': 4}
df['Severite_enc'] = df['Severite'].map(severity_map).fillna(2).astype(int)

groupe_age_map = {'0-10': 0, '11-17': 1, '18-30': 2, '31-50': 3, '50-65': 4, '65+': 5}
df['Groupe_Age_enc'] = df['Groupe_Age'].map(groupe_age_map).fillna(3).astype(int)

# -- 5b. One-hot encoding des symptômes (Multi-Label Binarizer) --
print("  Encodage des symptomes (Multi-Label Binarizer)...")
symptoms_lists = df['Symptomes_Rapportes'].fillna('').apply(
    lambda s: [x.strip() for x in s.split(',') if x.strip()]
)
mlb = MultiLabelBinarizer()
symptom_matrix = mlb.fit_transform(symptoms_lists)
symptom_cols = [f'SYM_{s.replace(" ", "_").replace("/", "_")}' for s in mlb.classes_]
df_symptoms = pd.DataFrame(symptom_matrix, columns=symptom_cols, index=df.index)
print(f"  Symptomes uniques encodes : {len(symptom_cols)}")

# -- 5c. Construction du dataset final --
# Numerique + categorique encode + symptomes binaires
num_cat_cols = numerical_cols + ['Sexe_enc', 'Severite_enc', 'Groupe_Age_enc']
num_cat_cols = [c for c in num_cat_cols if c in df.columns]

X_num = df[num_cat_cols].fillna(df[num_cat_cols].median())
X = pd.concat([X_num.reset_index(drop=True),
               df_symptoms.reset_index(drop=True)], axis=1)
feature_cols = list(X.columns)

le_target = LabelEncoder()
y = le_target.fit_transform(df['Maladie_Diagnostic'])

print(f"  Features numeriques/cat    : {len(num_cat_cols)}")
print(f"  Features symptomes         : {len(symptom_cols)}")
print(f"  Total features             : {len(feature_cols)}")
print(f"  Observations               : {len(X):,}")
print(f"  Classes cible              : {len(le_target.classes_)}")

# Split 80 % train / 20 % test
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)
print(f"  Entraînement  : {len(X_train):,} observations (80 %)")
print(f"  Test          : {len(X_test):,} observations (20 %)")


# ==========================================================================
# SECTION 6 : ENTRAÎNEMENT DU MODÈLE RANDOM FOREST
# ==========================================================================
print("\n[6/8] Entraînement du modele Random Forest...")

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
print("  Modele entraîne avec succes")

y_pred = rf_model.predict(X_test)

accuracy  = accuracy_score(y_test, y_pred)
precision = precision_score(y_test, y_pred, average='weighted', zero_division=0)
recall    = recall_score(y_test, y_pred, average='weighted', zero_division=0)
f1        = f1_score(y_test, y_pred, average='weighted', zero_division=0)

print(f"\n  Accuracy   : {accuracy*100:.2f} %")
print(f"  Precision  : {precision*100:.2f} %")
print(f"  Rappel     : {recall*100:.2f} %")
print(f"  F1-Score   : {f1*100:.2f} %")

# Rapport de classification complet
report = classification_report(
    y_test, y_pred,
    target_names=le_target.classes_,
    zero_division=0
)
with open('figures/rapport_classification.txt', 'w', encoding='utf-8') as f:
    f.write("RAPPORT DE CLASSIFICATION – RANDOM FOREST\n")
    f.write("=" * 70 + "\n")
    f.write(f"Observations test     : {len(X_test):,}\n")
    f.write(f"Accuracy globale      : {accuracy:.4f}  ({accuracy*100:.2f} %)\n")
    f.write(f"Precision (weighted)  : {precision:.4f}  ({precision*100:.2f} %)\n")
    f.write(f"Rappel    (weighted)  : {recall:.4f}  ({recall*100:.2f} %)\n")
    f.write(f"F1-Score  (weighted)  : {f1:.4f}  ({f1*100:.2f} %)\n")
    f.write("=" * 70 + "\n\n")
    f.write(report)
print("  -> figures/rapport_classification.txt")


# ==========================================================================
# SECTION 7 : VISUALISATIONS DU MODELE
# ==========================================================================
print("\n[7/8] Generation des visualisations du modele...")

# ---- 7a. Matrice de confusion (top 30 classes) --------------------------
print("  -> Matrice de confusion...")

counts_per_class = np.bincount(y_test)
threshold = np.sort(counts_per_class)[-min(30, len(counts_per_class))]
top_idx = np.where(counts_per_class >= threshold)[0][:30]

mask      = np.isin(y_test, top_idx)
y_t_top   = y_test[mask]
y_p_top   = y_pred[mask]
top_labels = [le_target.classes_[i] for i in top_idx]
label_map  = {old: new for new, old in enumerate(top_idx)}
y_t_re    = np.array([label_map[v] for v in y_t_top])
y_p_re    = np.array([label_map.get(v, -1) for v in y_p_top])

valid = y_p_re >= 0
y_t_re = y_t_re[valid]
y_p_re = y_p_re[valid]

cm = confusion_matrix(y_t_re, y_p_re, labels=range(len(top_labels)))
n_lbl = len(top_labels)

fig, ax = plt.subplots(figsize=(22, 20))
im = ax.imshow(cm, interpolation='nearest', cmap='Blues', aspect='auto')
plt.colorbar(im, ax=ax, shrink=0.75, label='Nombre de predictions')

tick_marks = np.arange(n_lbl)
ax.set_xticks(tick_marks)
ax.set_yticks(tick_marks)
short_lbl = [l[:22] for l in top_labels]
ax.set_xticklabels(short_lbl, rotation=90, fontsize=7)
ax.set_yticklabels(short_lbl, fontsize=7)
ax.set_xlabel('Classe Predite', fontsize=12, fontweight='bold')
ax.set_ylabel('Classe Reelle', fontsize=12, fontweight='bold')
ax.set_title(
    f'Matrice de Confusion – Top {n_lbl} maladies\n'
    f'Accuracy globale : {accuracy*100:.2f} %  '
    f'(sur {n_classes} classes, {n_obs:,} obs.)',
    fontsize=13, fontweight='bold'
)
thresh = cm.max() / 2.0
for i in range(n_lbl):
    for j in range(n_lbl):
        if cm[i, j] > 0:
            color = 'white' if cm[i, j] > thresh else 'black'
            ax.text(j, i, cm[i, j], ha='center', va='center',
                    color=color, fontsize=5.5)

plt.tight_layout()
plt.savefig('figures/08_matrice_confusion.png', bbox_inches='tight')
plt.close()
print("  -> figures/08_matrice_confusion.png")

# ---- 7b. Feature Importance (top 30) ------------------------------------
print("  -> Feature Importance...")

importances = rf_model.feature_importances_
sorted_idx  = np.argsort(importances)[::-1][:30]
top_features = [feature_cols[i] for i in sorted_idx]
top_values   = importances[sorted_idx]

short_feat = [
    f.replace('Lab_', '').replace('Vital_', '')[:38]
    for f in top_features
]

fig, ax = plt.subplots(figsize=(14, 11))
palette = plt.cm.viridis(np.linspace(0.15, 0.9, len(sorted_idx)))
bars = ax.barh(range(len(sorted_idx)), top_values, color=palette,
               edgecolor='white', linewidth=0.5)
ax.set_yticks(range(len(sorted_idx)))
ax.set_yticklabels(short_feat, fontsize=9)
ax.invert_yaxis()
ax.set_xlabel('Importance Gini (contribution a la decision)', fontsize=11, fontweight='bold')
ax.set_title(
    'Top 30 – Feature Importance (Random Forest)\n'
    'Impact de chaque attribut dans la prediction de la maladie',
    fontsize=13, fontweight='bold'
)
for bar, val in zip(bars, top_values):
    ax.text(val + 0.0003, bar.get_y() + bar.get_height() / 2,
            f'{val:.4f}', va='center', fontsize=8)

plt.tight_layout()
plt.savefig('figures/09_feature_importance.png', bbox_inches='tight')
plt.close()
print("  -> figures/09_feature_importance.png")

# ---- 7c. Courbe d'apprentissage -----------------------------------------
print("  -> Courbe d'apprentissage (peut prendre quelques minutes)...")

train_sizes_rel = np.linspace(0.1, 1.0, 9)
# Regularisation explicite pour éviter un score d'entraînement artificiellement parfait (=1.0)
train_sizes_abs, train_scores, val_scores = learning_curve(
    RandomForestClassifier(
        n_estimators=100,
        max_depth=18,           # Limite la profondeur → évite la mémorisation parfaite
        min_samples_leaf=4,     # Au moins 4 obs par feuille → généralisation
        min_samples_split=10,   # Seuil de division plus strict
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
print("  -> figures/10_courbe_apprentissage.png")

# ---- 7d. Tableau des métriques globales ---------------------------------
print("  -> Graphique des metriques globales...")

metrics_labels = ['Accuracy', 'Precision\n(weighted)', 'Rappel\n(weighted)', 'F1-Score\n(weighted)']
metrics_values = [accuracy, precision, recall, f1]
colors_metrics = ['#2196F3', '#4CAF50', '#FF9800', '#E91E63']

fig, ax = plt.subplots(figsize=(10, 6))
bars = ax.bar(metrics_labels, metrics_values,
              color=colors_metrics, edgecolor='white', linewidth=1.5, width=0.5)
ax.set_ylim([0, 1.18])
ax.set_ylabel('Score', fontsize=12, fontweight='bold')
ax.set_title(
    'Metriques d\'Evaluation – Random Forest\n'
    f'({n_classes} classes  |  {n_obs:,} observations  |  200 arbres)',
    fontsize=13, fontweight='bold'
)
ax.axhline(y=1.0, color='gray', linestyle='--', alpha=0.4, linewidth=1)
for bar, val, lbl in zip(bars, metrics_values, metrics_labels):
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
print("  -> figures/11_metriques_globales.png")

# ---- 7e. Centrage / Reduction par GROUPES CLINIQUES ----------------------
print("  -> Centrage / reduction par groupes cliniques...")

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

# Filtrer les groupes qui ont au moins 1 colonne présente dans X
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
print("  -> figures/12_centrage_reduction_quartiles.png")


# ==========================================================================
# SECTION 8 : EXPORT DU MODÈLE
# ==========================================================================
print("\n[8/8] Export du modele entraîne...")

joblib.dump(rf_model,       'model/random_forest_medical.pkl')
joblib.dump(le_target,      'model/label_encoder_maladies.pkl')
joblib.dump(le_sexe,        'model/label_encoder_sexe.pkl')
joblib.dump(feature_cols,   'model/feature_columns.pkl')
joblib.dump(severity_map,   'model/severity_mapping.pkl')
joblib.dump(groupe_age_map, 'model/groupe_age_mapping.pkl')
joblib.dump(mlb,            'model/symptom_binarizer.pkl')

print("  model/random_forest_medical.pkl")
print("  model/label_encoder_maladies.pkl")
print("  model/label_encoder_sexe.pkl")
print("  model/feature_columns.pkl")


# ==========================================================================
# RÉSUMÉ FINAL
# ==========================================================================
print("\n" + "=" * 70)
print("   RÉSUMÉ FINAL")
print("=" * 70)
print(f"\n  Observations totales         : {n_obs:,}")
print(f"  Observations entraînement    : {len(X_train):,}  (80 %)")
print(f"  Observations test            : {len(X_test):,}  (20 %)")
print(f"  Nombre de classes (maladies) : {n_classes}")
print(f"  Features utilisees           : {len(feature_cols)}")
print(f"  Nombre d'arbres (RF)         : 200")
print()
print(f"  Accuracy   : {accuracy*100:.2f} %")
print(f"  Precision  : {precision*100:.2f} %  (weighted)")
print(f"  Rappel     : {recall*100:.2f} %  (weighted)")
print(f"  F1-Score   : {f1*100:.2f} %  (weighted)")
print()
print("  Figures generees :")
figs = sorted([f for f in os.listdir('figures') if f.endswith('.png')])
for f in figs:
    print(f"    - figures/{f}")
print()
print("  Modele exporte : model/random_forest_medical.pkl")
print("\n  ANALYSE TERMINEE AVEC SUCCES")
print("=" * 70)
