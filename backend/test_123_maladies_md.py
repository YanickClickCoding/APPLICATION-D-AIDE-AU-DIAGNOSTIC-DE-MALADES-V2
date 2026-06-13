"""
Test automatisé — 123 maladies depuis JEUX_DE_TEST_123_MALADIES_SUITE.md
Lit directement le fichier Markdown, construit les payloads et appelle l'API /api/ml/predict-direct.
"""

import os
import re
import sys
import json
import requests

API_URL = os.environ.get("API_URL", "http://localhost:8000")
MD_FILE = os.environ.get(
    "MD_FILE",
    os.path.join(os.path.dirname(__file__), "..", "JEUX_DE_TEST_123_MALADIES_SUITE.md"),
)

SEV_MAP = {
    "severe": "SEVERE", "sévère": "SEVERE", "sevère": "SEVERE",
    "modere": "MODERE", "modéré": "MODERE", "modérée": "MODERE", "moderate": "MODERE",
    "leger": "LEGER", "léger": "LEGER", "légère": "LEGER", "legere": "LEGER", "light": "LEGER",
    "critique": "CRITIQUE", "critical": "CRITIQUE",
}

# Noms équivalents : si le test attend A et le modèle retourne B (ou vice versa), c'est OK
DISEASE_ALIASES: dict[str, set[str]] = {
    "grippe": {"grippe (influenza)", "grippe"},
    "grippe (influenza)": {"grippe (influenza)", "grippe"},
    "malaria (paludisme)": {"malaria (paludisme)", "paludisme", "malaria"},
    "paludisme": {"malaria (paludisme)", "paludisme", "malaria"},
    "malaria": {"malaria (paludisme)", "paludisme", "malaria"},
    "accident vasculaire cérébral (avc)": {"accident vasculaire cérébral (avc)", "accident vasculaire cérébral", "avc"},
    "thrombose veineuse profonde": {"thrombose veineuse profonde", "thrombose veineuse"},
    "eczéma (dermatite atopique)": {"eczéma (dermatite atopique)", "eczéma", "dermatite atopique"},
    "mononucléose infectieuse": {"mononucléose infectieuse", "mononucléose"},
    "rgo (reflux gastro-œsophagien)": {"rgo (reflux gastro-œsophagien)", "rgo", "reflux gastro-oesophagien"},
    "anémie hemolytique": {"anémie hemolytique", "anémie hémolytique"},
    "scléroderomie": {"scléroderomie", "sclérodermie"},
    "néphrotique": {"néphrotique", "syndrome néphrotique"},
}

# Seuils valides pour l'API
VITAL_BOUNDS = {
    "tension_systolique": (70, 250),
    "tension_diastolique": (40, 150),
    "frequence_cardiaque": (40, 200),
    "temperature": (35.0, 42.0),
    "frequence_respiratoire": (12, 40),
    "saturation_oxygene": (70, 100),
}

LAB_NAME_MAP = {
    "hémoglobine": "Hémoglobine",
    "globules rouges": "Globules Rouges",
    "globules blancs": "Globules Blancs",
    "neutrophiles": "Neutrophiles",
    "lymphocytes": "Lymphocytes",
    "monocytes": "Monocytes",
    "eosinophiles": "Eosinophiles",
    "éosinophiles": "Eosinophiles",
    "basophiles": "Basophiles",
    "plaquettes": "Plaquettes",
    "vgm": "VGM",
    "ccmh": "CCMH",
    "hématocrite": "Hématocrite",
    "glucose": "Glucose",
    "glucose à jeun": "Glucose à jeun",
    "glucose post-prandial": "Glucose post-prandial",
    "hba1c": "HbA1c",
    "cholestérol total": "Cholestérol total",
    "triglycérides": "Triglycérides",
    "cholestérol hdl": "Cholestérol HDL",
    "cholestérol ldl": "Cholestérol LDL",
    "acide urique": "Acide urique",
    "créatinine": "Créatinine",
    "urée": "Urée",
    "tfg": "TFG",
    "sodium": "Sodium",
    "potassium": "Potassium",
    "chlore": "Chlore",
    "calcium": "Calcium",
    "phosphore": "Phosphore",
    "magnésium": "Magnésium",
    "alt/sgpt": "ALT/SGPT",
    "ast/sgot": "AST/SGOT",
    "bilirubine totale": "Bilirubine totale",
    "albumine": "Albumine",
    "protéine totale": "Protéine totale",
    "globulines": "Globulines",
    "ratio a/g": "Ratio A/G",
    "ck": "CK",
    "myoglobine": "Myoglobine",
    "troponine": "Troponine",
    "bnp": "BNP",
    "probnp": "ProBNP",
    "pt/inr": "PT/INR",
    "aptt": "aPTT",
    "tt": "TT",
    "fibrinogène": "Fibrinogène",
    "crp": "CRP",
    "esr": "ESR",
    "psa": "PSA",
}


def _clamp(val, lo, hi):
    return max(lo, min(hi, val))


def _safe_float(s):
    if s is None:
        return None
    s = str(s).strip().replace(",", ".")
    # Extraire uniquement le premier nombre
    m = re.search(r"[-+]?\d+\.?\d*", s)
    if not m:
        return None
    try:
        return float(m.group())
    except ValueError:
        return None


def login():
    resp = requests.post(
        f"{API_URL}/api/auth/login",
        json={"email": "marie.dossou@sante.com", "password": "admin123"},
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()["access_token"]


def parse_md(path):
    """
    Parse le fichier MD et retourne une liste de cas :
    [{ "maladie": str, "age": int, "sexe": str, "severite": str,
       "duree": int, "vitaux": {...}, "symptomes": [...], "examens": [...],
       "antecedents_personnels": str|None, "antecedents_familiaux": str|None,
       "allergies": str|None }]
    """
    with open(path, encoding="utf-8") as f:
        content = f.read()

    # Découper par section ### N. Nom
    sections = re.split(r"\n### \d+\. ", content)
    cases = []

    for sec in sections[1:]:  # skip header
        lines = sec.strip().splitlines()
        maladie_raw = lines[0].strip()
        # Enlever éventuels caractères parasites
        maladie = maladie_raw.rstrip("|").strip()

        # --- signes vitaux (tableau markdown) ---
        age, sexe = 40, "M"
        ts, td, fc, temp, fr, spo2 = 120, 80, 75, 37.0, 16, 98
        poids, taille = None, None
        duree = 7
        severite_raw = "modere"
        antecedents_personnels = None
        antecedents_familiaux = None
        allergies = None

        for line in lines:
            line = line.strip()
            # Ligne tableau vitaux : | Âge | 55 ans, M |
            if line.startswith("|"):
                cols = [c.strip() for c in line.split("|") if c.strip()]
                if len(cols) < 2:
                    continue
                key = cols[0].lower()
                val = cols[1] if len(cols) > 1 else ""

                if "âge" in key or "age" in key:
                    m = re.search(r"(\d+)", val)
                    if m:
                        age = int(m.group(1))
                    sexe = "F" if "f" in val.lower() else "M"
                elif "antécédents personnels" in key or "antecedents personnels" in key:
                    antecedents_personnels = val if val.lower() not in ("aucun", "aucune", "-", "") else None
                elif "antécédents familiaux" in key or "antecedents familiaux" in key:
                    antecedents_familiaux = val if val.lower() not in ("aucun", "aucune", "-", "") else None
                elif "allergies" in key:
                    allergies = val if val.lower() not in ("aucun", "aucune", "-", "") else None
                elif "tension systolique" in key:
                    v = _safe_float(val)
                    if v:
                        ts = v
                elif "tension diastolique" in key:
                    v = _safe_float(val)
                    if v:
                        td = v
                elif "fréquence cardiaque" in key or "frequence cardiaque" in key:
                    v = _safe_float(val)
                    if v:
                        fc = v
                elif "température" in key or "temperature" in key:
                    v = _safe_float(val)
                    if v:
                        temp = v
                elif "fréquence respiratoire" in key or "frequence respiratoire" in key:
                    v = _safe_float(val)
                    if v:
                        fr = v
                elif "saturation" in key:
                    v = _safe_float(val)
                    if v:
                        spo2 = v
                elif "poids" in key and "taille" in key:
                    m1 = re.search(r"(\d+)\s*kg", val)
                    m2 = re.search(r"(\d+)\s*cm", val)
                    if m1:
                        poids = float(m1.group(1))
                    if m2:
                        taille = float(m2.group(1))
                elif "poids" in key:
                    v = _safe_float(val)
                    if v:
                        poids = v
                elif "taille" in key:
                    v = _safe_float(val)
                    if v:
                        taille = v
                elif "imc" in key:
                    pass  # on ignore, pas nécessaire
                elif "durée" in key or "duree" in key:
                    v = _safe_float(val)
                    if v:
                        duree = int(v)
                elif "sévérité" in key or "severite" in key:
                    severite_raw = val.lower().strip()

        # Normaliser sévérité
        sev = "MODERE"
        for k, v in SEV_MAP.items():
            if k in severite_raw:
                sev = v
                break
        if "grave" in severite_raw:
            sev = "SEVERE"
        if "critique" in severite_raw or "critical" in severite_raw:
            sev = "CRITIQUE"

        # Clamp vitaux
        ts = _clamp(ts or 120, 70, 250)
        td = _clamp(td or 80, 40, 150)
        fc = _clamp(fc or 75, 40, 200)
        temp = _clamp(temp or 37.0, 35.0, 42.0)
        fr = _clamp(fr or 16, 12, 40)
        spo2 = _clamp(spo2 or 98, 70, 100)
        duree = _clamp(duree, 0, 365)
        age = _clamp(age, 1, 100)

        vitaux = {
            "tension_systolique": ts,
            "tension_diastolique": td,
            "frequence_cardiaque": fc,
            "temperature": temp,
            "frequence_respiratoire": fr,
            "saturation_oxygene": spo2,
        }
        if poids:
            vitaux["poids"] = poids
        if taille:
            vitaux["taille"] = taille

        # --- Symptômes ---
        symptomes = []
        in_sym_table = False
        sym_header_seen = False
        for line in lines:
            l = line.strip()
            if "**Symptômes" in l or "**Symptomes" in l:
                in_sym_table = True
                sym_header_seen = False
                continue
            if in_sym_table:
                if l.startswith("|") and "---" in l:
                    sym_header_seen = True
                    continue
                if l.startswith("|") and sym_header_seen:
                    cols = [c.strip() for c in l.split("|") if c.strip()]
                    if cols and cols[0].lower() not in ("symptôme", "symptome"):
                        symptomes.append(cols[0])
                elif l.startswith("**") or (l.startswith("#") and not l.startswith("#")):
                    in_sym_table = False

        if not symptomes:
            symptomes = ["Fatigue"]  # fallback minimal

        # --- Examens biologiques ---
        examens = []
        for line in lines:
            l = line.strip()
            # Lignes type: - BIOLOGIE → Hémoglobine (g/dL): `17.25`
            if "biologie" in l.lower() and "→" in l:
                # Extraire nom et valeur
                after_arrow = l.split("→", 1)[-1].strip()
                # "Hémoglobine (g/dL): `17.25`"  ou  "Hémoglobine (g/dL): 17.25"
                m = re.match(r"^([^:(]+?)(?:\s*\([^)]*\))?\s*:\s*[`']?([\d.,]+)[`']?", after_arrow)
                if m:
                    nom_raw = m.group(1).strip().lower()
                    valeur = _safe_float(m.group(2))
                    if valeur is not None:
                        nom_canon = LAB_NAME_MAP.get(nom_raw)
                        if nom_canon:
                            examens.append({
                                "nom": nom_canon,
                                "valeur_numerique": valeur,
                                "unite_mesure": "",
                            })

        cases.append({
            "maladie": maladie,
            "age": age,
            "sexe": sexe,
            "severite": sev,
            "duree_symptomes_jours": duree,
            "vitaux": vitaux,
            "symptomes": symptomes[:6],
            "examens": examens,
            "antecedents_personnels": antecedents_personnels,
            "antecedents_familiaux": antecedents_familiaux,
            "allergies": allergies,
        })

    return cases


def run_tests(cases, token):
    headers = {"Authorization": f"Bearer {token}"}
    correct = 0
    top3_count = 0
    results = []
    errors = []

    total = len(cases)
    for i, case in enumerate(cases, 1):
        maladie = case["maladie"]
        payload = {k: case[k] for k in [
            "age", "sexe", "severite", "duree_symptomes_jours",
            "vitaux", "symptomes", "examens",
            "antecedents_personnels", "antecedents_familiaux", "allergies",
        ]}

        try:
            r = requests.post(
                f"{API_URL}/api/ml/predict-direct",
                json=payload,
                headers=headers,
                timeout=60,
            )
            if r.status_code != 200:
                errors.append(f"[{i}] HTTP {r.status_code} pour {maladie}: {r.text[:200]}")
                results.append(("ERR", maladie, f"HTTP {r.status_code}", 0.0))
                continue

            d = r.json()
            predicted = d.get("diagnostic_propose", "?")
            conf = float(d.get("confiance", 0) or 0)
            alts = [a.get("diagnostic") for a in d.get("diagnostics_alternatifs", []) if a.get("diagnostic")]
            top3 = [predicted] + alts[:2]

            def names_match(a: str, b: str) -> bool:
                al, bl = a.lower(), b.lower()
                if al == bl:
                    return True
                aliases_a = DISEASE_ALIASES.get(al, {al})
                aliases_b = DISEASE_ALIASES.get(bl, {bl})
                return bool(aliases_a & aliases_b)

            ok1 = names_match(predicted, maladie)
            ok3 = any(names_match(p, maladie) for p in top3)

            if ok1:
                correct += 1
                status = "OK"
            elif ok3:
                top3_count += 1
                status = "TOP3"
            else:
                status = "FAIL"

            results.append((status, maladie, predicted, conf))

        except Exception as e:
            errors.append(f"[{i}] Exception pour {maladie}: {e}")
            results.append(("ERR", maladie, str(e)[:60], 0.0))

        if i % 10 == 0 or i == total:
            done_ok = sum(1 for s, *_ in results if s == "OK")
            done_t3 = sum(1 for s, *_ in results if s == "TOP3")
            print(f"  Progression: {i}/{total} | Top-1: {done_ok} | Top-3: {done_ok+done_t3}", flush=True)

    return results, errors, correct, top3_count


def main():
    md_path = os.path.abspath(MD_FILE)
    print(f"Fichier MD : {md_path}")
    if not os.path.exists(md_path):
        print(f"ERREUR: Fichier introuvable: {md_path}")
        sys.exit(1)

    print("Parsing du fichier MD...")
    cases = parse_md(md_path)
    print(f"  -> {len(cases)} cas parses")

    # Afficher aperçu
    for i, c in enumerate(cases[:3], 1):
        print(f"  [{i}] {c['maladie']} | {c['age']}a {c['sexe']} | {len(c['symptomes'])} sym | {len(c['examens'])} exam")

    print("\nConnexion à l'API...")
    try:
        token = login()
        print("  → Authentification OK")
    except Exception as e:
        print(f"  ERREUR auth: {e}")
        sys.exit(1)

    print(f"\nLancement des tests ({len(cases)} maladies)...")
    results, errors, correct, top3_count = run_tests(cases, token)

    total = len(cases)
    top1_pct = correct / total * 100 if total else 0
    top3_total = correct + top3_count
    top3_pct = top3_total / total * 100 if total else 0

    print("\n" + "=" * 70)
    print(f"  RÉSULTATS — {total} maladies testées")
    print("=" * 70)
    print(f"  Top-1 exact  : {correct:3d}/{total} ({top1_pct:.1f}%)")
    print(f"  Top-3 inclus : {top3_total:3d}/{total} ({top3_pct:.1f}%)")
    print("=" * 70)

    print("\nDétail par maladie :")
    for i, (status, expected, predicted, conf) in enumerate(results, 1):
        icon = "V" if status == "OK" else ("~" if status == "TOP3" else ("!" if status == "ERR" else "X"))
        expected_pad = expected[:40].ljust(41)
        predicted_pad = str(predicted)[:40]
        conf_str = f"{conf*100:.0f}%" if conf else "  -"
        print(f"  [{icon}] {i:3d}. {expected_pad} | {predicted_pad} ({conf_str})")

    if errors:
        print(f"\n⚠ {len(errors)} erreur(s) rencontrée(s) :")
        for e in errors:
            print(f"  {e}")

    # Résumé des FAIL
    fails = [(i+1, ex, pr) for i, (st, ex, pr, _) in enumerate(results) if st == "FAIL"]
    if fails:
        print(f"\nMaladies non reconnues ({len(fails)}) :")
        for n, ex, pr in fails:
            print(f"  [{n:3d}] {ex} → {pr}")

    print()


if __name__ == "__main__":
    main()
