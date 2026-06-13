import json
import math
import os
from typing import Any, Dict, List, Tuple

import pandas as pd
import requests


API_URL = os.environ.get("API_URL", "http://localhost:8000")
DATASET_CSV = os.environ.get(
    "DATASET_CSV",
    os.path.join(
        "les ressources dataset",
        "dataset_medical_robust_10000_cas.csv",
    ),
)


def login() -> str:
    resp = requests.post(
        f"{API_URL}/api/auth/login",
        json={"email": "marie.dossou@sante.com", "password": "admin123"},
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()["access_token"]


def _safe_float(x: Any) -> float:
    if x is None:
        return None
    try:
        if isinstance(x, float) and math.isnan(x):
            return None
        if isinstance(x, str) and x.strip() == "":
            return None
        return float(x)
    except Exception:
        return None


def build_payload_from_row(row: pd.Series, sexe_override: str = None) -> Dict[str, Any]:
    maladie = str(row.get("Maladie_Diagnostic", "")).strip()

    sexe = sexe_override or str(row.get("Sexe", "")).strip()
    if sexe not in {"M", "F"}:
        sexe = "M" if sexe.lower().startswith("m") else "F"

    age = int(_safe_float(row.get("Age", 0)) or 40)
    age = max(1, min(100, age))

    severite_raw = str(row.get("Severite", "")).strip()
    sev_map = {
        "Légère": "LEGER",
        "Legere": "LEGER",
        "LEGER": "LEGER",
        "Modérée": "MODERE",
        "Modere": "MODERE",
        "MODERE": "MODERE",
        "Sévère": "SEVERE",
        "Severe": "SEVERE",
        "SEVERE": "SEVERE",
        "Critique": "CRITIQUE",
        "CRITIQUE": "CRITIQUE",
        "grave": "SEVERE",
    }
    severite = sev_map.get(severite_raw, "MODERE")

    # Durée: dataset doc says 1-90. API/ML accepte int.
    duree_symptomes = int(_safe_float(row.get("Duree_Symptomes_Jours", 7)) or 7)
    duree_symptomes = max(0, min(365, duree_symptomes))

    # Symptômes: format doc: "Fièvre, Toux, Fatigue" => liste strings
    sym_str = str(row.get("Symptomes_Rapportes", "") or "").strip()
    # Certains dataset peuvent utiliser un séparateur différent ; on force virgule.
    raw_syms = [s.strip() for s in sym_str.split(",") if s.strip()]
    # On garde 3-6 max (sinon ça pénalise souvent)
    # et on évite les valeurs vides.
    symptomes = raw_syms[:6]
    if not symptomes:
        symptomes = ["Aucun symptôme habituellement"]

    # Vitaux
    vitaux = {
        "tension_systolique": _safe_float(row.get("Vital_Tension Systolique (mmHg)"))
        or _safe_float(row.get("Tension Systolique (mmHg)"))
        or 120,
        "tension_diastolique": _safe_float(row.get("Vital_Tension Diastolique (mmHg)"))
        or _safe_float(row.get("Tension Diastolique (mmHg)"))
        or 80,
        "frequence_cardiaque": _safe_float(row.get("Vital_Fréquence Cardiaque (bpm)"))
        or _safe_float(row.get("Frequence Cardiaque (bpm)"))
        or 70,
        "frequence_respiratoire": _safe_float(row.get("Vital_Fréquence Respiratoire (resp/min)"))
        or _safe_float(row.get("Frequence Respiratoire (resp/min)"))
        or 16,
        "temperature": _safe_float(row.get("Vital_Température (°C)"))
        or _safe_float(row.get("Température (°C)"))
        or 37.0,
        "saturation_oxygene": _safe_float(row.get("Vital_Saturation O2 (%)"))
        or _safe_float(row.get("Saturation O2 (%)"))
        or 98,
    }

    poids = _safe_float(row.get("Poids (kg)")) if "Poids (kg)" in row.index else None
    taille = _safe_float(row.get("Taille (cm)")) if "Taille (cm)" in row.index else None
    if poids is not None:
        vitaux["poids"] = poids
    if taille is not None:
        vitaux["taille"] = taille

    # Examens biologiques: on utilise les colonnes Lab_* du dataset.
    # ML backend attend uniquement les examens avec valeur_numerique != None.
    examens: List[Dict[str, Any]] = []

    # On map chaque colonne Lab_* vers nom exam canonique utilisé par ton frontend/backend.
    # (Dans le repo, les noms attendus sont ceux listés dans frontend/src/pages/ConsultationWorkflow.tsx)
    # Ici on ne fait que les noms qui existent dans le dataset documentation.
    lab_map: List[Tuple[str, str]] = [
        ("Lab_Hémoglobine (g/dL)", "Hémoglobine"),
        ("Lab_Hématocrite (%)", "Hématocrite"),
        ("Lab_Globules Rouges (M/µL)", "Globules Rouges"),
        ("Lab_Globules Blancs (K/µL)", "Globules Blancs"),
        ("Lab_Neutrophiles (%)", "Neutrophiles"),
        ("Lab_Lymphocytes (%)", "Lymphocytes"),
        ("Lab_Monocytes (%)", "Monocytes"),
        ("Lab_Eosinophiles (%)", "Eosinophiles"),
        ("Lab_Basophiles (%)", "Basophiles"),
        ("Lab_Plaquettes (K/µL)", "Plaquettes"),
        ("Lab_VGM (fL)", "VGM"),
        ("Lab_CCMH (g/dL)", "CCMH"),
        ("Lab_Glucose (mg/dL)", "Glucose"),
        ("Lab_Glucose à jeun (mg/dL)", "Glucose à jeun"),
        ("Lab_Glucose post-prandial (mg/dL)", "Glucose post-prandial"),
        ("Lab_HbA1c (%)", "HbA1c"),
        ("Lab_Cholestérol total (mg/dL)", "Cholestérol total"),
        ("Lab_Triglycérides (mg/dL)", "Triglycérides"),
        ("Lab_Cholestérol HDL (mg/dL)", "Cholestérol HDL"),
        ("Lab_Cholestérol LDL (mg/dL)", "Cholestérol LDL"),
        ("Lab_Acide urique (mg/dL)", "Acide urique"),
        ("Lab_Créatinine (mg/dL)", "Créatinine"),
        ("Lab_Urée (mg/dL)", "Urée"),
        ("Lab_TFG (mL/min/1.73m²)", "TFG"),
        ("Lab_Sodium (mEq/L)", "Sodium"),
        ("Lab_Potassium (mEq/L)", "Potassium"),
        ("Lab_Chlore (mEq/L)", "Chlore"),
        ("Lab_Calcium (mg/dL)", "Calcium"),
        ("Lab_Phosphore (mg/dL)", "Phosphore"),
        ("Lab_Magnésium (mg/dL)", "Magnésium"),
        ("Lab_ALT/SGPT (U/L)", "ALT/SGPT"),
        ("Lab_AST/SGOT (U/L)", "AST/SGOT"),
        ("Lab_Bilirubine totale (mg/dL)", "Bilirubine totale"),
        ("Lab_Albumine (g/dL)", "Albumine"),
        ("Lab_Protéine totale (g/dL)", "Protéine totale"),
        ("Lab_Globulines (g/dL)", "Globulines"),
        ("Lab_Ratio A/G", "Ratio A/G"),
        ("Lab_CK (U/L)", "CK"),
        ("Lab_Myoglobine (ng/mL)", "Myoglobine"),
        ("Lab_Troponine (ng/mL)", "Troponine"),
        ("Lab_BNP (pg/mL)", "BNP"),
        ("Lab_ProBNP (pg/mL)", "ProBNP"),
        ("Lab_PT/INR", "PT/INR"),
        ("Lab_aPTT (sec)", "aPTT"),
        ("Lab_TT (sec)", "TT"),
        ("Lab_Fibrinogène (mg/dL)", "Fibrinogène"),
        ("Lab_CRP (mg/L)", "CRP"),
        ("Lab_ESR (mm/h)", "ESR"),
        ("Lab_PSA (ng/mL)", "PSA"),
    ]

    # Unité: on laisse vide si inconnu. Le backend accepte unite_mesure non obligatoire.
    for col, exam_nom in lab_map:
        if col not in row.index:
            continue
        val = _safe_float(row.get(col))
        if val is None:
            continue
        examens.append({"nom": exam_nom, "valeur_numerique": val, "unite_mesure": ""})

    # Antecedents & allergies si présents dans dataset (sinon None)
    antecedents_personnels = row.get("Antecedents_Medicaux")
    antecedents_familiaux = None
    allergies = row.get("Allergies") if "Allergies" in row.index else None

    # Le modèle ML backend aime les strings simples.
    if isinstance(antecedents_personnels, float) and math.isnan(antecedents_personnels):
        antecedents_personnels = None
    if isinstance(allergies, float) and math.isnan(allergies):
        allergies = None

    return {
        "age": age,
        "sexe": sexe,
        "severite": severite,
        "duree_symptomes_jours": duree_symptomes,
        "vitaux": vitaux,
        "symptomes": symptomes,
        "examens": examens,
        "antecedents_personnels": antecedents_personnels,
        "antecedents_familiaux": antecedents_familiaux,
        "allergies": allergies,
        "expected": maladie,
    }


def main():
    print(f"Dataset CSV: {DATASET_CSV}")
    if not os.path.exists(DATASET_CSV):
        raise FileNotFoundError(
            f"Impossible de trouver le dataset: {DATASET_CSV}. Ajuste la variable d'environnement DATASET_CSV."
        )

    token = login()
    headers = {"Authorization": f"Bearer {token}"}

    df = pd.read_csv(DATASET_CSV)
    if "Maladie_Diagnostic" not in df.columns:
        raise RuntimeError("Colonnes inattendues dans le dataset: Maladie_Diagnostic introuvable")

    # Objectif: couvrir toutes les maladies (selon doc: 121). Si tu veux 123, c'est mismatch dataset.
    maladies = sorted(df["Maladie_Diagnostic"].dropna().astype(str).unique().tolist())
    print(f"Maladies détectées dans dataset: {len(maladies)}")

    # Prendre 1 ligne par maladie (première) pour générer un jeu de test.
    # Option: si tu veux plusieurs lignes par maladie, augmente samples_per_disease.
    samples_per_disease = 1

    cases: List[Dict[str, Any]] = []
    for maladie in maladies:
        sub = df[df["Maladie_Diagnostic"].astype(str) == maladie]
        sub = sub.head(samples_per_disease)
        for _, r in sub.iterrows():
            cases.append(build_payload_from_row(r))

    # Si le besoin strict est 123 maladies, on tronque ou complète.
    target = 123
    if len(cases) > target:
        cases = cases[:target]

    correct = 0
    top3_count = 0
    results = []

    for case in cases:
        expected = case.pop("expected")
        payload = {k: case[k] for k in [
            "age",
            "sexe",
            "severite",
            "duree_symptomes_jours",
            "vitaux",
            "symptomes",
            "examens",
            "antecedents_personnels",
            "antecedents_familiaux",
            "allergies",
        ]}

        r = requests.post(
            f"{API_URL}/api/ml/predict-direct",
            json=payload,
            headers=headers,
            timeout=60,
        )
        d = r.json()

        predicted = d.get("diagnostic_propose", "?")
        conf = float(d.get("confiance", 0) or 0)
        alts = [a.get("diagnostic") for a in d.get("diagnostics_alternatifs", []) if a.get("diagnostic")]
        all_top3 = [predicted] + alts[:2]

        ok = predicted == expected
        ok3 = expected in all_top3
        if ok:
            correct += 1
        if ok3:
            top3_count += 1

        status = "OK" if ok else ("TOP3" if ok3 else "FAIL")
        results.append((status, expected, predicted, conf))

        if len(results) % 10 == 0:
            print(f"Progress: {len(results)}/{len(cases)}")

    print(f"=== RESULTATS BATCH TEST MALADIES ({len(cases)}) ===")
    print(f"Top-1 correct : {correct}/{len(cases)} ({correct/len(cases)*100:.1f}%)")
    print(f"Top-3 correct : {top3_count}/{len(cases)} ({top3_count/len(cases)*100:.1f}%)")

    for i, (status, expected, predicted, conf) in enumerate(results, 1):
        icon = "V" if status == "OK" else ("~" if status == "TOP3" else "X")
        print(f"[{icon}] {i:3d}. Attendu: {expected:<45} | Prédit: {predicted} ({conf*100:.0f}%)")


if __name__ == "__main__":
    main()

