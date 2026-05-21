#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script d'injection d'outliers (valeurs atypiques) et de bruit clinique
dans le dataset médical pour le rendre réaliste et provoquer une confusion saine.
"""
import pandas as pd
import numpy as np
import shutil
import os

# Configurer le générateur de nombres aléatoires pour la reproductibilité
np.random.seed(42)

DATASET_DIR = "c:/Users/Lenovo/APPLICATION-D-AIDE-AU-DIAGNOSTIC-DE-MALADES-V2/les ressources dataset"
CSV_PATH = os.path.join(DATASET_DIR, "dataset_medical_robust_10000_cas.csv")
JSON_PATH = os.path.join(DATASET_DIR, "dataset_medical_robust_10000_cas.json")
BACKUP_PATH = os.path.join(DATASET_DIR, "dataset_medical_robust_10000_cas_original.csv.bak")

# Définition des groupes de maladies cliniquement similaires et facilement confondues par les médecins
CONFUSABLE_DISEASES = {
    'COVID-19': ['Grippe', 'Bronchite', 'Influenza A/B', 'Pneumonie'],
    'Grippe': ['COVID-19', 'Influenza A/B', 'Bronchite'],
    'Influenza A/B': ['Grippe', 'COVID-19', 'Bronchite'],
    'Pneumonie': ['Tuberculose', 'Bronchite', 'Emphysème', 'COVID-19'],
    'Tuberculose': ['Pneumonie', 'Bronchite'],
    'Gastrite': ['Ulcère gastro-duodénal', 'Gastroentérite', 'RGO'],
    'Ulcère gastro-duodénal': ['Gastrite', 'Hernie hiatale', 'Gastroentérite'],
    'Gastroentérite': ['Gastrite', 'Syndrome du côlon irritable', 'Ulcère gastro-duodénal'],
    'Asthme': ['BPCO', 'Rhinite allergique', 'Bronchite'],
    'BPCO': ['Asthme', 'Emphysème', 'Bronchite'],
    'Cystite': ['Pyélonéphrite', 'Prostatite', 'Urétrite'],
    'Pyélonéphrite': ['Cystite', 'Insuffisance rénale aiguë'],
    'Insuffisance rénale aiguë': ['Insuffisance rénale chronique', 'Pyélonéphrite', 'Glomérulonéphrite'],
    'Insuffisance rénale chronique': ['Insuffisance rénale aiguë', 'Glomérulonéphrite'],
    'Migraine': ['Céphalée de tension'],
    'Céphalée de tension': ['Migraine'],
    'Angine de poitrine': ['Infarctus du myocarde', 'Péricardite', 'Myocardite'],
    'Infarctus du myocarde': ['Angine de poitrine', 'Myocardite', 'Péricardite'],
    'Hypothyroïdie': ['Thyroïdite'],
    'Hyperthyroïdie': ['Thyroïdite'],
    'Anémie ferriprive': ['Anémie aplasique', 'Anémie hemolytique'],
}

def main():
    print("=" * 80)
    print("INJECTION D'OUTLIERS ET DE BRUIT DANS LE DATASET MEDICAL")
    print("=" * 80)
    
    # 1. Restauration/Sauvegarde
    if not os.path.exists(CSV_PATH):
        print(f"[ERROR] Le fichier {CSV_PATH} n'existe pas.")
        return
        
    # Si le fichier de sauvegarde original existe, on repart de lui pour repartir sur une base propre
    if os.path.exists(BACKUP_PATH):
        print("[INFO] Restauration du dataset depuis la sauvegarde originale pour repartir sur une base propre...")
        shutil.copy(BACKUP_PATH, CSV_PATH)
    else:
        print(f"[INFO] Creation d'une sauvegarde de securite : {BACKUP_PATH}")
        shutil.copy(CSV_PATH, BACKUP_PATH)

    # 2. Chargement du dataset
    df = pd.read_csv(CSV_PATH)
    n_rows = len(df)
    print(f"[INFO] Dataset charge : {n_rows} lignes, {len(df.columns)} colonnes.")

    # 3. Extraction de tous les symptômes uniques pour pouvoir en injecter des faux
    all_symptoms = set()
    for s_str in df['Symptomes_Rapportes'].dropna():
        for s in s_str.split(','):
            all_symptoms.add(s.strip())
    all_symptoms = sorted(list(all_symptoms))
    print(f"[INFO] {len(all_symptoms)} symptomes distincts detectes.")

    # 4. Injection d'Outliers / Erreurs de mesure extrêmes (pour faire apparaître des points sur les boxplots)
    print("\n[INFO] 1. Injection d'erreurs de mesure et d'outliers extremes...")
    
    # Températures extrêmes (ex: sonde défaillante ou hyperpyrexie mal saisie)
    temp_idx = np.random.choice(df.index, size=200, replace=False)
    df.loc[temp_idx[:100], 'Vital_Température (°C)'] = np.round(np.random.uniform(31.0, 34.0, size=100), 1)  # Hypothermie
    df.loc[temp_idx[100:], 'Vital_Température (°C)'] = np.round(np.random.uniform(41.5, 44.0, size=100), 1)  # Hyperpyrexie

    # Saturations O2 aberrantes
    spo2_idx = np.random.choice(df.index, size=200, replace=False)
    df.loc[spo2_idx, 'Vital_Saturation O2 (%)'] = np.round(np.random.uniform(35.0, 72.0, size=200), 1)

    # Fréquences cardiaques aberrantes
    fc_idx = np.random.choice(df.index, size=200, replace=False)
    df.loc[fc_idx[:100], 'Vital_Fréquence Cardiaque (bpm)'] = np.random.randint(200, 250, size=100)
    df.loc[fc_idx[100:], 'Vital_Fréquence Cardiaque (bpm)'] = np.random.randint(20, 32, size=100)

    # Tensions Systoliques extrêmes
    sys_idx = np.random.choice(df.index, size=220, replace=False)
    df.loc[sys_idx[:110], 'Vital_Tension Systolique (mmHg)'] = np.random.randint(40, 60, size=110)
    df.loc[sys_idx[110:], 'Vital_Tension Systolique (mmHg)'] = np.random.randint(235, 290, size=110)

    # Glycémies extrêmes
    glyc_idx = np.random.choice(df.index, size=220, replace=False)
    df.loc[glyc_idx[:110], 'Lab_Glucose (mg/dL)'] = np.round(np.random.uniform(10.0, 32.0, size=110), 1)
    df.loc[glyc_idx[110:], 'Lab_Glucose (mg/dL)'] = np.round(np.random.uniform(500.0, 850.0, size=110), 1)

    # Hémoglobines extrêmes
    hb_idx = np.random.choice(df.index, size=150, replace=False)
    df.loc[hb_idx, 'Lab_Hémoglobine (g/dL)'] = np.round(np.random.uniform(2.5, 5.0, size=150), 1)

    print(f"  -> Outliers extremes injectes sur {200*3 + 220*2 + 150} valeurs.")

    # 5. Injection de Présentations Cliniques Atypiques (Mélange de symptômes et de bilans biologiques)
    print("\n[INFO] 2. Injection de presentations cliniques atypiques par maladie...")

    # A. Infarctus du myocarde atypique (sans douleur thoracique)
    mi_mask = df['Maladie_Diagnostic'] == 'Infarctus du myocarde'
    mi_indices = df[mi_mask].index
    mi_atyp_size = int(len(mi_indices) * 0.40)
    mi_atyp_indices = np.random.choice(mi_indices, size=mi_atyp_size, replace=False)
    for idx in mi_atyp_indices:
        symptomes = str(df.loc[idx, 'Symptomes_Rapportes']).split(', ')
        symptomes = [s for s in symptomes if s != 'Douleur thoracique']
        if 'Nausées' not in symptomes:
            symptomes.append('Nausées')
        if 'Fatigue' not in symptomes:
            symptomes.append('Fatigue')
        df.loc[idx, 'Symptomes_Rapportes'] = ', '.join(symptomes)

    # B. Diabète de Type 2 atypique / contrôlé (avec glycémie normale)
    diab_mask = df['Maladie_Diagnostic'] == 'Diabète Type 2'
    diab_indices = df[diab_mask].index
    diab_atyp_size = int(len(diab_indices) * 0.40)
    diab_atyp_indices = np.random.choice(diab_indices, size=diab_atyp_size, replace=False)
    df.loc[diab_atyp_indices, 'Lab_Glucose (mg/dL)'] = np.round(np.random.uniform(75.0, 110.0, size=diab_atyp_size), 1)
    df.loc[diab_atyp_indices, 'Lab_HbA1c (%)'] = np.round(np.random.uniform(5.0, 5.6, size=diab_atyp_size), 1)

    # C. Hyperglycémie transitoire chez un non-diabétique (Stress biologique dû à une infection sévère)
    inf_mask = df['Maladie_Diagnostic'].isin(['Pneumonie', 'Salmonellose', 'Typhoïde'])
    inf_indices = df[inf_mask].index
    inf_hyper_size = int(len(inf_indices) * 0.35)
    inf_hyper_indices = np.random.choice(inf_indices, size=inf_hyper_size, replace=False)
    df.loc[inf_hyper_indices, 'Lab_Glucose (mg/dL)'] = np.round(np.random.uniform(180.0, 260.0, size=inf_hyper_size), 1)

    # D. Grippe et COVID-19 apyrétiques (sans fièvre)
    viral_mask = df['Maladie_Diagnostic'].isin(['Grippe', 'COVID-19'])
    viral_indices = df[viral_mask].index
    viral_atyp_size = int(len(viral_indices) * 0.35)
    viral_atyp_indices = np.random.choice(viral_indices, size=viral_atyp_size, replace=False)
    df.loc[viral_atyp_indices, 'Vital_Température (°C)'] = np.round(np.random.uniform(36.4, 37.0, size=viral_atyp_size), 1)
    for idx in viral_atyp_indices:
        symptomes = str(df.loc[idx, 'Symptomes_Rapportes']).split(', ')
        symptomes = [s for s in symptomes if s != 'Fièvre']
        df.loc[idx, 'Symptomes_Rapportes'] = ', '.join(symptomes)

    # E. Pneumonie ou Tuberculose sans hyperleucocytose (Globules blancs normaux)
    tb_mask = df['Maladie_Diagnostic'].isin(['Tuberculose', 'Pneumonie'])
    tb_indices = df[tb_mask].index
    tb_atyp_size = int(len(tb_indices) * 0.35)
    tb_atyp_indices = np.random.choice(tb_indices, size=tb_atyp_size, replace=False)
    df.loc[tb_atyp_indices, 'Lab_Globules Blancs (K/µL)'] = np.round(np.random.uniform(4.5, 7.5, size=tb_atyp_size), 1)

    print("  -> Cas cliniques atypiques injectes.")

    # 6. Injection de bruit sur les symptômes (Omissions et Symptômes parasites)
    # Pour simuler la réalité clinique où la documentation des symptômes est imparfaite
    print("\n[INFO] 3. Injection de bruit sur les symptomes...")
    omission_count = 0
    addition_count = 0
    
    for idx in df.index:
        symptomes_str = df.loc[idx, 'Symptomes_Rapportes']
        if pd.isna(symptomes_str) or not symptomes_str.strip():
            continue
        
        s_list = [s.strip() for s in symptomes_str.split(',') if s.strip()]
        
        # A. Omission aléatoire de symptômes (30% de chance d'enlever 1 ou plusieurs symptômes)
        if np.random.random() < 0.30 and len(s_list) > 1:
            n_remove = np.random.randint(1, min(3, len(s_list)))
            indices_to_remove = np.random.choice(range(len(s_list)), size=n_remove, replace=False)
            s_list = [s_list[i] for i in range(len(s_list)) if i not in indices_to_remove]
            omission_count += n_remove
            
        # B. Ajout aléatoire de symptômes parasitaires (20% de chance d'ajouter 1 symptôme sans rapport)
        if np.random.random() < 0.20:
            # Choisir un symptôme aléatoire qui n'est pas déjà présent
            possible_additions = [s for s in all_symptoms if s not in s_list]
            if possible_additions:
                extra_symptom = np.random.choice(possible_additions)
                s_list.append(extra_symptom)
                addition_count += 1
                
        df.at[idx, 'Symptomes_Rapportes'] = ', '.join(s_list)
        
    print(f"  -> {omission_count} symptomes oublies (omissions).")
    print(f"  -> {addition_count} symptomes additionnels parasites (bruit).")

    # 7. Injection de Label Noise / Erreurs de diagnostic (physician classification error)
    # Nous augmentons le taux d'erreur de diagnostic à 18% pour les maladies à symptômes proches
    print("\n[INFO] 4. Injection d'erreurs de diagnostic (Label Noise)...")
    swap_count = 0
    for disease, conf_list in CONFUSABLE_DISEASES.items():
        disease_mask = df['Maladie_Diagnostic'] == disease
        disease_indices = df[disease_mask].index
        
        # Sélectionner 18% des lignes pour cette maladie
        swap_size = int(len(disease_indices) * 0.18)
        if swap_size > 0:
            swap_indices = np.random.choice(disease_indices, size=swap_size, replace=False)
            for idx in swap_indices:
                new_disease = np.random.choice(conf_list)
                df.at[idx, 'Maladie_Diagnostic'] = new_disease
                swap_count += 1
                
    print(f"  -> {swap_count} diagnostics inter-maladies modifies (Label Noise a 18%).")

    # 8. Injection de bruit gaussien statistique général
    # Nous ajoutons du bruit gaussien sur 55% des lignes pour toutes les colonnes biologiques
    print("\n[INFO] 5. Injection de bruit gaussien clinique global...")
    lab_cols = [c for c in df.columns if c.startswith('Lab_') and c not in ['Lab_BAAR (résultat)', 'Lab_Culture Mycobactéries (résultat)', 'Lab_Test Xpert MTB/RIF (résultat)']]
    noise_rows = np.random.choice(df.index, size=int(n_rows * 0.55), replace=False)
    
    for col in lab_cols:
        if pd.api.types.is_numeric_dtype(df[col]):
            std_val = df[col].std()
            noise = np.random.normal(0, std_val * 0.12, size=len(noise_rows))
            df.loc[noise_rows, col] = np.round(df.loc[noise_rows, col] + noise, 2)
            
            min_val = df[col].min()
            if min_val > 0:
                df.loc[noise_rows, col] = df.loc[noise_rows, col].clip(lower=min_val * 0.3)
            else:
                df.loc[noise_rows, col] = df.loc[noise_rows, col].clip(lower=0)

    print("  -> Bruit gaussien injecte sur 55% des lignes.")

    # 9. Sauvegarde des datasets
    print("\n[INFO] 6. Sauvegarde des nouveaux fichiers...")
    
    df.to_csv(CSV_PATH, index=False)
    print(f"  -> CSV sauvegarde avec succes : {CSV_PATH}")
    
    df.to_json(JSON_PATH, orient="records", force_ascii=False, indent=2)
    print(f"  -> JSON sauvegarde avec succes : {JSON_PATH}")
    
    print("\n[INFO] Processus d'injection d'anomalies complete !")
    print("=" * 80)

if __name__ == '__main__':
    main()
