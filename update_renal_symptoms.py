import pandas as pd
import random
import collections

random.seed(42)

df = pd.read_csv("les ressources dataset/dataset_medical_robust_enhanced.csv")

# === POOLS DE SYMPTOMES COMPLETS ===

SYMPTOMES_AIGUE = [
    # Urinaires caractéristiques
    "Oligurie ou polyurie", "Anurie", "Hématurie", "Urine foncée",
    "Urine mousseuse", "Dysurie", "Nycturie",
    # Rétention hydrique
    "Oedèmes", "Gonflement des chevilles", "Prise de poids rapide",
    # Généraux
    "Fatigue", "Nausées", "Vomissements", "Anorexie",
    # Cardiovasculaires
    "Hypertension", "Douleur thoracique", "Palpitations", "Essoufflement",
    # Digestifs
    "Douleurs abdominales", "Haleine urémique", "Goût métallique",
    # Neurologiques
    "Confusion", "Maux de tête", "Crampes musculaires", "Convulsions",
    # Cutanés
    "Démangeaisons", "Peau sèche", "Pâleur",
]

SYMPTOMES_CHRONIQUE = [
    # Urinaires chroniques
    "Urination fréquente", "Nycturie", "Urine mousseuse", "Hématurie",
    "Oligurie ou polyurie", "Anurie",
    # Généraux
    "Fatigue", "Perte de poids", "Anorexie",
    # Rétention
    "Oedèmes", "Gonflement des chevilles", "Prise de poids rapide",
    # Cutanés (très fréquents en IRC)
    "Démangeaisons", "Peau sèche", "Pâleur", "Teint grisâtre",
    # Cardiovasculaires
    "Hypertension", "Essoufflement", "Palpitations", "Douleur thoracique",
    # Neurologique/musculaire
    "Crampes musculaires", "Engourdissements", "Confusion", "Maux de tête",
    # Digestif
    "Nausées", "Vomissements", "Douleurs abdominales",
    "Haleine urémique", "Goût métallique",
    # Osseux (IRC stade avancé)
    "Douleurs osseuses",
]


def choisir_symptomes(pool, nb_min=3, nb_max=6):
    n = random.randint(nb_min, nb_max)
    return ", ".join(random.sample(pool, min(n, len(pool))))


idx_aigue = df[df["Maladie_Diagnostic"] == "Insuffisance rénale aiguë"].index.tolist()
idx_chron = df[df["Maladie_Diagnostic"] == "Insuffisance rénale chronique"].index.tolist()

# Aiguë : oligourie ou anurie dans 70% des cas
for idx in idx_aigue:
    pool = SYMPTOMES_AIGUE.copy()
    if random.random() < 0.70:
        obligatoire = random.choice(["Oligurie ou polyurie", "Anurie"])
        pool = [s for s in pool if s != obligatoire]
        autres = random.sample(pool, random.randint(2, 5))
        df.at[idx, "Symptomes_Rapportes"] = obligatoire + ", " + ", ".join(autres)
    else:
        df.at[idx, "Symptomes_Rapportes"] = choisir_symptomes(pool)

# Chronique : démangeaisons / fatigue / nycturie dans 65% des cas
for idx in idx_chron:
    pool = SYMPTOMES_CHRONIQUE.copy()
    if random.random() < 0.65:
        obligatoire = random.choice(["Démangeaisons", "Fatigue", "Nycturie"])
        pool = [s for s in pool if s != obligatoire]
        autres = random.sample(pool, random.randint(2, 5))
        df.at[idx, "Symptomes_Rapportes"] = obligatoire + ", " + ", ".join(autres)
    else:
        df.at[idx, "Symptomes_Rapportes"] = choisir_symptomes(pool)

df.to_csv("les ressources dataset/dataset_medical_robust_enhanced.csv", index=False)

print(f"Dataset mis à jour. Aiguë: {len(idx_aigue)} cas | Chronique: {len(idx_chron)} cas")

renal = df[df["Maladie_Diagnostic"].isin(["Insuffisance rénale aiguë", "Insuffisance rénale chronique"])]
all_s = []
for s in renal["Symptomes_Rapportes"]:
    for item in str(s).split(","):
        all_s.append(item.strip())
ctr = collections.Counter(all_s)
print("\nTop 30 symptômes après mise à jour:")
for sym, cnt in ctr.most_common(30):
    print(f"  {cnt:3d}x  {sym}")
